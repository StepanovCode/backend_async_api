from __future__ import annotations

from abc import ABC, abstractmethod

from aioredis import Redis, create_redis_pool


class BaseStorage(ABC):
    obj = None

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = super().__new__(cls)
        return cls.obj

    def __init__(self, host: str, port: str, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.connection = None

    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value, expire: int) -> bool:
        pass

    @abstractmethod
    async def create_connection(self):
        pass

    @classmethod
    async def get_connection(cls) -> BaseStorage:
        if cls.obj is None:
            raise ValueError("Create instance of this class first")
        if cls.obj.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        return cls.obj

    @abstractmethod
    async def close(self):
        pass


class RedisStorage(BaseStorage):
    connection: Redis = None

    async def get(self, key: str) -> str | None:
        if self.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        response = await self.connection.get(key)
        return response

    async def set(self, key: str, value, expire: int) -> bool:
        if self.connection is None:
            raise ValueError("Create connection first: self.create_connection")
        response = await self.connection.set(key, value, expire=expire)
        return response

    async def create_connection(self):
        if self.connection is None:
            self.connection = await create_redis_pool(
                (self.host, self.port),
                password=self.password, minsize=10, maxsize=20)

    async def close(self):
        self.connection.close()
        await self.connection.wait_closed()
