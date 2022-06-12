"""Управляющая логика ETL-процесса."""
import os
from datetime import date, datetime
from time import sleep

from dotenv import load_dotenv
from etl.extractor import Extractor
from etl.loader import Loader
from etl.state import State
from etl.transformer import (
    Transformer,
    TRANSFORMATIONS_PERSONS,
    TRANSFORMATIONS_GENRES,
    TRANSFORMATIONS_MOVIES
)

load_dotenv(
    dotenv_path=os.path.dirname(os.path.abspath(__file__)) + '/../.env',
)


def initiate_updates_check(state: State, dt: datetime) -> None:
    """Устанавливает переменные состояния для начала нового цикла проверки.

    Args:
        state (State): состояние для изменения
        dt (datetime): отметка, с которой начать проверку
    """
    state.set_state(
        State.KEY_LAST_DATETIME,
        dt.strftime('%Y-%m-%d %H:%M:%S+0000'),
    )
    state.set_state(State.KEY_OFFSET, 0)


def extract_next_batch(
    extractor: Extractor,
    state: State,
    sql: str,
    name: str,
) -> dict:
    """Получить следующий батч из БД.

    Args:
        extractor (Extractor): Extractor для получения батча
        state (State): состояние для изменения offset
        sql (str): sql для выполнения
        name (str): sql наименование для логгирования
    Returns:
        dict: следующий батч с обновлениями
    """
    batch = extractor.next_batch(
        state.get_state(State.KEY_LAST_DATETIME),
        state.get_state(State.KEY_BATCH_SIZE),
        state.get_state(State.KEY_OFFSET),
        sql,
        name
    )
    state.set_state(
        State.KEY_OFFSET,
        int(state.get_state(State.KEY_OFFSET)) +
        int(state.get_state(State.KEY_BATCH_SIZE)),
    )
    return batch


def main():
    """Точка входа."""
    updates_check_interval = int(os.environ.get('ETL_UPDATES_CHECK_INTERVAL'))
    state = State.via_redis(base_key='state', batch_size=100, offset=0)
    extractor = Extractor(state)
    transformer = Transformer()
    loader = Loader()
    initiate_updates_check(state, dt=date.min)
    while state.get_state(State.KEY_QUIT) == State.KEY_QUIT_VALUE_RUN:
        parametrized_pipelines = [
            {
                'E': Extractor.MODIFIED_MOVIES_SQL,
                'T': TRANSFORMATIONS_MOVIES,
                'N': 'Movies'
            },
            {
                'E': Extractor.MODIFIED_PERSONS_SQL,
                'T': TRANSFORMATIONS_PERSONS,
                'N': 'Persons'
            },
            {
                'E': Extractor.MODIFIED_GENRES_SQL,
                'T': TRANSFORMATIONS_GENRES,
                'N': 'Genres'
            },

        ]
        for et in parametrized_pipelines:
            state.set_state(State.KEY_OFFSET, 0)
            extracted_batch = [None]
            while len(extracted_batch) > 0:
                # Гарантированное время, до которого точно все
                # проанализировано. Это породит повторные обновления,
                # но позволит избежать сложной императивной логики,
                # в т.ч. хранения пар (uuid, modified) как индикации
                # индексации в каком-либо хранилище (БД, redis, файл)
                dt_candidate = datetime.utcnow()
                # Получаем батч с сортировкой по modified. Все новые
                # обновленияс момента dt_candidate будут в конце
                # плавающего batch-окна и "почти гарантированно"
                # позднее dt_candidate. "Почти", т.к. полноценной
                # синхронизации с СУБД без блокировки на запись
                # достичь нельзя. Можно лишь повысить "гарантию",
                # "отсупая" назад в dt_candidate, либо "честно мучаться"
                # со сбором (uuid, modified) либо "поступить логичнее",
                # используя триггеры onUpdate или работая с wal
                extracted_batch = extract_next_batch(
                    extractor,
                    state,
                    et['E'],
                    et['N']
                )
                if len(extracted_batch) > 0:
                    transformed_batch = transformer.transform(
                        extracted_batch,
                        et['T'],
                        et['N']
                    )
                    loader.load_batch(transformed_batch, et['N'])

        sleep(updates_check_interval)
        # если хочется "повысить гарантию", тут можно сделать отступ назад, но
        # очевидно не более чем на updates_check_interval + минимальная дельта
        # но это tradeoff время индексации/гарантированность индексации
        initiate_updates_check(state, dt=dt_candidate)


if __name__ == '__main__':
    main()
