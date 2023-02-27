from typing import Type, TypeVar, Union

from core.config import settings
from models.film import Film
from models.genre import Genre
from models.person import Person
from services.search_engine_service import BaseSearchEngineService
from services.storage_service import BaseStorageService

CACHE_EXPIRE_IN_SECONDS = 60 * 5

ModelType = TypeVar("ModelType", bound=Union[Person, Film, Genre])


class BaseService:
    def __init__(self, storage_service: BaseStorageService,
                 search_engine_service: BaseSearchEngineService,
                 index: str, model: Type[ModelType]):
        self.storage_service = storage_service
        self.search_engine_service = search_engine_service
        self.model = model
        self.index = index

    async def get_by_id(self, url: str, element_id: str) -> ModelType | None:
        element = await self.storage_service.element_from_cache(url)
        if not element:
            element = await self.search_engine_service.get_element_from_elastic(self.index, element_id)
            if not element:
                return None
            await self.storage_service.put_element_to_cache(url, element, CACHE_EXPIRE_IN_SECONDS)
        return element

    async def get_all(self, url: str, number: int, size, sort: str,
                      search: str = None, filter_: str = None) -> list[ModelType] | None:
        limit = min(size, settings.PAGINATION_MAX_SIZE)
        limit = max(limit, settings.PAGINATION_MIN_SIZE)
        number = 1 if number < 0 else number
        start = (number - 1) * limit
        end = start + limit
        elements = await self.storage_service.elements_from_cache(url)
        if not elements:
            elements = await self.search_engine_service.get_elements_from_elastic(
                self.index, start, end,
                sort, search, filter_
            )
            if not elements:
                return None
            await self.storage_service.put_elements_to_cache(url, elements, CACHE_EXPIRE_IN_SECONDS)
        return elements
