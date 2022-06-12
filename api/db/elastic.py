from typing import Optional
from elasticsearch import AsyncElasticsearch


es: Optional[AsyncElasticsearch] = None


def get_elastic() -> AsyncElasticsearch:
    return es
