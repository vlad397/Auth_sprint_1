import abc
from abc import ABCMeta


class GetByIDService(metaclass=ABCMeta):
    @abc.abstractmethod
    def get(self, uuid: str):
        pass


class SearchService(metaclass=ABCMeta):
    @abc.abstractmethod
    def search(
            self,
            string: str,
            page_number: int = 0,
            page_size: int = 50,
            **kwargs: dict
    ):
        pass


class ListService(metaclass=ABCMeta):
    @abc.abstractmethod
    def list(
            self,
            page_number: int = 0,
            page_size: int = 50,
            **kwargs: dict
    ):
        pass
