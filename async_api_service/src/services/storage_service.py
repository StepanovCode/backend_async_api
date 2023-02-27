import json
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Union

from db.storage import BaseStorage
from models.film import Film
from models.genre import Genre
from models.person import Person
from utils.decorators import backoff

ModelType = TypeVar("ModelType", bound=Union[Person, Film, Genre])


class BaseStorageService(ABC):
    def __init__(self, storage: BaseStorage, model: Type[ModelType]):
        self.storage = storage
        self.model = model

    @abstractmethod
    async def element_from_cache(self, url: str) -> ModelType | None:
        pass

    @abstractmethod
    async def elements_from_cache(self, url: str) -> list[ModelType] | None:
        pass

    @abstractmethod
    async def put_element_to_cache(self, url: str, element: ModelType, expire: int) -> None:
        pass

    @abstractmethod
    async def put_elements_to_cache(self, url: str, elements: list[ModelType], expire: int) -> None:
        pass


class StorageService(BaseStorageService):
    @backoff()
    async def element_from_cache(self, url: str) -> ModelType | None:
        data = await self.storage.get(url)
        if not data:
            return None

        element = self.model.parse_raw(data)
        return element

    @backoff()
    async def elements_from_cache(self, url: str) -> list[ModelType] | None:
        datas = await self.storage.get(url)
        if not datas:
            return None
        decode_datas = [self.model.parse_raw(data) for data in json.loads(datas)]
        return decode_datas

    @backoff()
    async def put_element_to_cache(self, url: str, element: ModelType, expire: int):
        await self.storage.set(url, element.json(), expire=expire)

    @backoff()
    async def put_elements_to_cache(self, url: str, elements: list[ModelType], expire: int):
        json_elements = [element.json() for element in elements]
        await self.storage.set(url, json.dumps(json_elements), expire=expire)
