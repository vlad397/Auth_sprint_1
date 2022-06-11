"""Реализация механики работы с состоянием."""
import abc
import os
from typing import Any

from dotenv import load_dotenv
from redis import Redis

load_dotenv(
    dotenv_path=os.path.dirname(os.path.abspath(__file__)) + '/../../.env',
)


class BaseStorage(abc.ABC):
    """Абстрактный интерфейс хранилища."""

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище.

        Args:
            state (dict): новое состояние
        """

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Получить состояние из постоянного хранилища."""


class RedisStorage(BaseStorage):
    """Реализация хранилища состояния на базе Redis."""

    def __init__(self, redis_adapter: Redis, base_key: str = 'state'):
        """Инициализировать экземпляр хранилища состояния.

        Args:
            redis_adapter (Redis): интерфейс к redis
            base_key (str): базовый ключ для сохранения dict-состояния
        """
        self.redis_adapter = redis_adapter
        self.base_key = base_key

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище.

        Args:
            state (dict): новое состояние
        """
        self.redis_adapter.hset(self.base_key, mapping=state)

    def retrieve_state(self) -> dict:
        """Получить состояние из постоянного хранилища.

        Returns:
            dict: текущее состояние
        """
        return self.redis_adapter.hgetall(self.base_key)


class State(object):
    """Класс для работы с состоянием."""

    KEY_QUIT = 'quit'
    KEY_QUIT_VALUE_QUIT = '1'
    KEY_QUIT_VALUE_RUN = '0'
    KEY_LAST_DATETIME = 'datetime'
    KEY_OFFSET = 'offset'
    KEY_BATCH_SIZE = 'batch'

    def __init__(
        self,
        storage: BaseStorage,
        date: str = '1970-01-01 00:00:00+0000',
        batch_size: int = 100,
        offset: int = 0,
    ):
        """Инициализировать экземпляр хранилища состояния.

        Args:
            storage (BaseStorage): интерфейс к физическому хранилищу
            date (str): дата последнего обновления (начальная)
            batch_size (int): размер батча для выгрузки
            offset (int): текущее смещение (начальное)
        """
        self.storage = storage
        self.set_state(State.KEY_QUIT, State.KEY_QUIT_VALUE_RUN)
        self.set_state(State.KEY_LAST_DATETIME, date)
        self.set_state(State.KEY_OFFSET, offset)
        self.set_state(State.KEY_BATCH_SIZE, batch_size)

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа.

        Args:
            key (str): ключ состояния
            value (Any): значение состояния
        """
        kv = self.storage.retrieve_state()
        if kv is not None:
            kv[key] = value
        else:
            kv = {key: value}
        self.storage.save_state(kv)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу.

        Args:
            key (str): ключ состояния

        Returns:
            Any: значение состояния
        """
        kv = self.storage.retrieve_state()
        if kv is not None:
            return kv[key] if key in kv else None
        return None

    @staticmethod
    def via_redis(
        base_key: str = None,
        initial_date: str = '1970-01-01 00:00:00+0000',
        batch_size: int = 100,
        offset: int = 0,
    ) -> 'State':
        """Получить экземпляр State, работающий через Redis.

        Args:
            base_key (str): базовый ключ для хранения словаря значений
            initial_date (str): дата последнего обновления (начальная)
            batch_size (int): размер батча для выгрузки
            offset (int): текущее смещение (начальное)

        Returns:
            State: Redis-backed состояние
        """
        redis_adapter = Redis(
            host=os.environ['REDIS_HOST'],
            port=os.environ['REDIS_PORT'],
            db=os.environ['REDIS_DB'],
            password=os.environ['REDIS_PASSWORD'],
            charset='utf-8',
            decode_responses=True,
        )
        redis_adapter.ping()  # raise, если нет соединения
        redis = RedisStorage(redis_adapter, base_key)
        return State(
            redis,
            date=initial_date,
            batch_size=batch_size,
            offset=offset,
        )
