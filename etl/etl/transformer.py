"""Трансформация данных из postgres под elasticsearch."""
from .logger import Logger

TRANSFORMATIONS_MOVIES = [
    lambda rec: {'_id': rec['fw_id'], '_index': 'movies'},
    lambda rec: {'uuid': rec['fw_id']},
    lambda rec: {'imdb_rating': rec['rating']},
    lambda rec: {'title': rec['title']},
    lambda rec: {'description': rec['description']},
    lambda re: {
        'actors': [
            {
                'uuid': id, 'full_name': re['person'][id]
            } for id in re['pers_role']
            if re['pers_role'][id] == 'actor'
        ],
    },
    lambda re: {
        'writers': [
            {
                'uuid': id, 'full_name': re['person'][id]
            } for id in re['pers_role']
            if re['pers_role'][id] == 'writer'
        ],
    },
    lambda re: {
        'directors': [
            {
                'uuid': id, 'full_name': re['person'][id]
            } for id in re['pers_role']
            if re['pers_role'][id] == 'director'
        ],
    },
    lambda re: {
        'genres': [
            {
                'uuid': uuid, 'name': name
            } for uuid, name in re['genres'].items()
        ],
    },
]

TRANSFORMATIONS_PERSONS = [
    lambda rec: {'_id': rec['id'], '_index': 'persons'},
    lambda rec: {'uuid': rec['id']},
    lambda rec: {'full_name': rec['full_name']},
    lambda rec: {'birth_date': rec['birth_date']},
]

TRANSFORMATIONS_GENRES = [
    lambda rec: {'_id': rec['id'], '_index': 'genres'},
    lambda rec: {'uuid': rec['id']},
    lambda rec: {'name': rec['name']},
]

# review MatMerd: думаю нужно вынести TRANSFORMATIONS_* из класса
class Transformer(Logger):
    """Класс транформации."""

    def __init__(self, key: str = 'Transformer'):
        """Инициализация.

        Args:
            key (str): наименование для журналирования
        """
        self.key = key
        super().__init__(key)

    def transform(self, batch: list, transformations: list, name: str) -> list:
        """Выполнение преобразования.

        Args:
            batch (list): список словарей из БД для преобразования
            transformations (list): список из lambda-функций трансформации
            name (str): имя для логгирования
        Returns:
            list: список словарей в формате elasticsearch-документов
        """
        transformed_batch = []
        for record in batch:
            transformed_record = {}
            for transformation in transformations:
                transformed_record.update(transformation(record))
            transformed_batch.append(transformed_record)
        self.log('{0}: in = {1}, out = {2}'.format(
            name,
            len(batch),
            len(transformed_batch),
        ))
        return transformed_batch
