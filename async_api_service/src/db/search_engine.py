from __future__ import annotations

from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


class BaseSearchEngine(ABC):
    obj = None

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = super().__new__(cls)
        return cls.obj

    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.connection = None

    @abstractmethod
    async def get(self, index: str, key: str) -> dict:
        pass

    @abstractmethod
    async def search(self, *, index: str, from_: int,
                     size: int, sort: str, body: dict) -> dict:
        pass

    @abstractmethod
    async def create_connection(self):
        pass

    @classmethod
    async def get_connection(cls) -> BaseSearchEngine:
        if cls.obj is None:
            raise ValueError("Create instance of this class first")
        if cls.obj.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        return cls.obj

    @abstractmethod
    async def close(self):
        pass


class ElasticSearchEngine(BaseSearchEngine):
    connection: AsyncElasticsearch = None

    async def get(self, index: str, key: str) -> dict:
        if self.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        response = await self.connection.get(index, key)
        return response

    async def search(self, *, index: str, from_: int, size: int, sort: str, body: dict) -> dict:
        if self.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        response = await self.connection.search(
            index=index,
            from_=from_,
            size=size,
            sort=sort,
            body=body,
        )
        return response

    async def create_connection(self):
        if self.connection is None:
            self.connection = AsyncElasticsearch(hosts=[f'{self.host}:{self.port}'])

    async def close(self):
        await self.connection.close()
