"""Извлечение данных из postgresql."""
import os

from psycopg2 import DatabaseError, connect
from psycopg2.extras import DictCursor

from .backoff import backoff
from .logger import Logger
from .state import State


class Extractor(Logger):
    """Класс для извлечения данных из postgresql.

    Следует понимать, что фактически MODIFIED_MOVIES_SQL - это пять запросов,
    выполняемые последовательно на уровне СУБД, а не один гигантский
    multi-JOIN который "ай-яй-яй, берет разом всю базу".При этом, последний
    запрос в целочке ограничен batch size и явно использует JOIN вместо IN,
    что, как правило, эффективнее. Overhead по сравнению с 4/5 py-вызовами в
    моем понимании будет меньше. Технически вопросы использования сортировок
    закрываются (при желании и объеме) индексированием. Написанное - это
    'почти тот самый код, предлагаемый к реализации в python, но на SQL',
    что избавляет от поддержки 'безумного количества императивной лапши'
    """

    MODIFIED_MOVIES_SQL = """
        WITH MOVIES_CHANGED_DIRECT AS (
            SELECT ID, MODIFIED
            FROM CONTENT.film_work
            WHERE modified >= TO_DATE('{0}', 'YYYY-MM-DD HH24:MI:SS')
        ), MOVIES_CHANGED_VIA_PERSONS AS (
            SELECT FW.ID, P.MODIFIED
            FROM CONTENT.film_work FW
            INNER JOIN CONTENT.person_film_work PFW
                ON PFW.film_work_id = FW.id
            INNER JOIN CONTENT.person P
                ON P.id = PFW.person_id
            WHERE P.modified >= TO_DATE('{0}', 'YYYY-MM-DD HH24:MI:SS')
        ), MOVIES_CHANGED_VIA_GENRES AS (
            SELECT FW.ID, G.MODIFIED
            FROM CONTENT.film_work FW
            INNER JOIN CONTENT.genre_film_work GFW
                ON GFW.film_work_id = FW.id
            INNER JOIN CONTENT.genre G
                ON G.id = GFW.genre_id
            WHERE G.modified >= TO_DATE('{0}', 'YYYY-MM-DD HH24:MI:SS')
        ), MOVIES_CHANGED_UNIQUE_IDS AS (
            SELECT DISTINCT MOVIES.ID FROM (
                SELECT ID, MODIFIED FROM (
                    (SELECT ID, MODIFIED FROM MOVIES_CHANGED_DIRECT)
                    UNION ALL
                    (SELECT ID, MODIFIED FROM MOVIES_CHANGED_VIA_PERSONS)
                    UNION ALL
                    (SELECT ID, MODIFIED FROM MOVIES_CHANGED_VIA_GENRES)
                ) AS IDS ORDER BY MODIFIED 
            ) AS MOVIES LIMIT {1} OFFSET {2} 
        )  SELECT
                fw.id as fw_id, 
                fw.title, 
                fw.description, 
                fw.rating, 
                fw.type, 
                fw.created, 
                fw.modified,                   
                JSON_OBJECT_AGG(
                    COALESCE(p.id, '00000000-0000-0000-0000-000000000000'),
                    COALESCE(p.full_name,'None')) as "person",
                JSON_OBJECT_AGG(
                    COALESCE(p.id, '00000000-0000-0000-0000-000000000000'), 
                    COALESCE(pfw.role,'None')) as "pers_role",
                JSON_OBJECT_AGG(
                    COALESCE(g.id, '00000000-0000-0000-0000-000000000000'), 
                    COALESCE(g.name,'None')) as "genres"
            FROM content.film_work fw
            INNER JOIN MOVIES_CHANGED_UNIQUE_IDS ufw ON fw.ID = ufw.ID
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            GROUP BY fw.id
        ;
    """

    MODIFIED_PERSONS_SQL = """    
            SELECT id, full_name, birth_date
            FROM CONTENT.person
            WHERE modified >= TO_DATE('{0}', 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY modified
            LIMIT {1} OFFSET {2} 
        ;
    """

    MODIFIED_GENRES_SQL = """    
            SELECT id, name
            FROM CONTENT.genre
            WHERE modified >= TO_DATE('{0}', 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY modified
            LIMIT {1} OFFSET {2} 
        ;
    """

    def __init__(
        self,
        state: State,
        batch_size: int = 100,
        key: str = 'Extractor',
    ):
        """Инициализация.

        Args:
            state (State): State для отслеживания состояния
            batch_size (int): размер батча
            key (str): имя для журналирования
        """
        super().__init__(key)
        self.state = state
        self.batch_size = batch_size
        self.key = key
        self.dsl = {
            'dbname': os.environ.get('DB_NAME'),
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'host': os.environ.get('DB_HOST'),
            'port': os.environ.get('DB_PORT'),
        }
        self.conn = None

    @backoff(
        Logger('Extractor/BO'),
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
    )
    def reconnect(self):
        """Выполнить переподключение к БД."""
        self.conn = connect(**self.dsl, cursor_factory=DictCursor)
        self.log('postgres connection opened')

    # review MatMerd: думаю отлавливать все подряд исключения не является
    # хорошей практикой. При действиях с курсором точно можно узнать какие
    # исключения возникают
    def _next_batch(
        self,
        time: str,
        batch_size: int,
        offset: int,
        sqls: str,
    ) -> dict:
        """Получение следующего батча из БД (внутренний).

        Args:
            time (str): отметка времени для использования в запросе
            batch_size (int): размер батча для запроса
            offset (int): отступ в запросе
            sqls (str): исполняемый sql для выгрузки данных из БД

        Returns:
            dict: записи в виде словаря
        """
        sql = sqls.format(
            time,
            batch_size,
            offset,
        )
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql)
            except Exception as ex:
                self.log(ex)
            return cursor.fetchall()

    def next_batch(self, stamp, batch_size, offset, sql, name) -> dict:
        """Получение следующего батча из БД (публичный).

        Args:
            stamp (str): отметка времени для использования в запросе
            batch_size (int): размер батча для запроса
            offset (int): отступ в запросе
            sql (str): sql для исполнения
            name (str): наименование для логгирования

        Returns:
            dict: записи в виде словаря
        """
        batch = None
        while True:
            try:
                batch = self._next_batch(stamp, batch_size, offset, sql)
                self.log(
                    '{0}: s = {1}, b = {2}, o = {3}, r = {4}'.format(
                        name,
                        stamp,
                        batch_size,
                        offset,
                        len(batch),
                    ),
                )
                if len(batch) == 0:
                    break
                return batch
            except (DatabaseError, AttributeError):
                self.reconnect()
        self.log('no more results for stamp = {0}'.format(stamp))
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.log('postgres connection closed')
        return batch
