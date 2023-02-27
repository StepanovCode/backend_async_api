from abc import ABC, abstractmethod
from typing import Type, TypeVar, Union

from db.search_engine import BaseSearchEngine
from elasticsearch import ElasticsearchException, NotFoundError
from models.film import Film
from models.genre import Genre
from models.person import Person
from utils.decorators import backoff

ModelType = TypeVar("ModelType", bound=Union[Person, Film, Genre])


class BaseSearchEngineService(ABC):
    def __init__(self, search_engine: BaseSearchEngine, model: Type[ModelType]):
        self.search_engine = search_engine
        self.model = model

    @abstractmethod
    async def get_element_from_elastic(self, index: str, element_id: str) -> ModelType | None:
        pass

    @abstractmethod
    async def get_elements_from_elastic(
            self,
            index: str,
            from_doc: int,
            size: int,
            sort: str = None,
            search: str = None,
            filter_: str = None) -> list[ModelType] | None:
        pass


class ElasticSearchEngineService(BaseSearchEngineService):
    @backoff()
    async def get_element_from_elastic(self, index: str, element_id: str) -> ModelType | None:
        try:
            doc = await self.search_engine.get(index, element_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    @backoff()
    async def get_elements_from_elastic(
            self,
            index: str,
            from_doc: int,
            size: int,
            sort: str = None,
            search: str = None,
            filter_: str = None) -> list[ModelType] | None:

        elements: list = []
        query: dict = {}
        sort_type = 'asc'
        if not filter_ and not search:
            query = {"match_all": {}}
        if filter_:
            query["bool"] = {"filter": {"term": {'genre': filter_}}}

        if search:
            query["bool"] = {"must": {"multi_match": {'query': search, 'fields': ['*']}}}

        if search and filter_:
            query["bool"] = {
                "filter": {"term": {
                    'genre': filter_,
                }},
                "must": {"multi_match": {'query': search, 'fields': ['*']}}
            }

        if sort:
            if not sort.startswith('-'):
                sort = f'{sort}:{sort_type}'
            if sort.startswith('-'):
                sort_field = sort[1:]
                sort_type = 'desc'
                sort = f'{sort_field}:{sort_type}'

        try:
            docs = await self.search_engine.search(
                index=index,
                from_=from_doc,
                size=size,
                sort=sort,
                body={
                    "query": query,
                },
            )
            for doc in docs['hits']['hits']:
                source = doc.get('_source')
                elements.append(self.model(**source))
        except ElasticsearchException:
            return None
        return elements
