from functools import lru_cache
from typing import Type

from db.search_engine import BaseSearchEngine, ElasticSearchEngine
from db.storage import BaseStorage, RedisStorage
from fastapi import Depends
from models.genre import Genre
from services.base import BaseService
from services.search_engine_service import (BaseSearchEngineService,
                                            ElasticSearchEngineService)
from services.storage_service import BaseStorageService, StorageService


class GenreService(BaseService):
    def __init__(
            self,
            storage_service: BaseStorageService,
            search_engine_service: BaseSearchEngineService,
            index: str,
            model: Type[Genre]):
        super().__init__(storage_service, search_engine_service, index, model)


@lru_cache()
def get_genre_service(
        storage: BaseStorage = Depends(RedisStorage.get_connection),
        search_engine: BaseSearchEngine = Depends(ElasticSearchEngine.get_connection),
) -> GenreService:
    model = Genre
    storage_service = StorageService(storage, model)
    search_engine_service = ElasticSearchEngineService(search_engine, model)
    return GenreService(storage_service, search_engine_service, "genres", model)
