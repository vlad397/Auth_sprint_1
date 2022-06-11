"""Загрузка трансформированных данных в ES."""
import logging
import os

import urllib3
from elasticsearch import ConnectionError, ConnectionTimeout, Elasticsearch
from elasticsearch.helpers import bulk

from .backoff import backoff
from .logger import Logger

urllib3.disable_warnings()
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('elastic_transport.transport').setLevel(logging.CRITICAL)
logging.getLogger('elastic_transport.node_pool').setLevel(logging.CRITICAL)


class Loader(Logger):
    """Основной класс, реализующий логику загрузки."""

    def __init__(
        self,
        key: str = 'Loader',
    ):
        """Инициализация.

        Args:
            key (str): наименование для журналирования
        """
        super().__init__(name=key)
        self.key = key
        self.es_address = eval(os.environ.get('ELASTICSEARCH_ADDRESS'))
        self.es = None

    @backoff(
        Logger('Loader/BO'),
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
    )
    def reconnect(self) -> None:
        """Переподключение к ES (игнорируем встроенное).

        Raises:
            ValueError: в случае, если соединение не установлено
        """
        self.es = Elasticsearch(self.es_address)
        if not self.es.ping():
            self.es.close()
            raise ValueError('elasticsearch connection failed')
        self.log('elasticsearch connection opened')

    def load_batch(self, batch: dict, name: str) -> None:
        """Загрузка данных ES с обновлением для повторов.

        Args:
            batch (dict): набор документов для масс-загрузки/обновления
            name (str): имя для логгирования
        Raises:
            AttributeError: в случае, если не все данные получены
        """
        while True:
            try:
                response = bulk(self.es, batch)
                if response[0] != len(batch):
                    self.log('{0}: update {1} rec, {2} errors, retry'.format(
                        name,
                        response[0],
                        len(response[1]),
                    ))
                    raise AttributeError
                self.log('{0} updated {1} records'.format(name, response[0]))
                break
            except (ConnectionError, ConnectionTimeout, AttributeError):
                self.reconnect()
        if self.es is not None:
            self.es.close()
            self.es = None
            self.log('elasticsearch connection closed')
