from functools import lru_cache
from typing import Type

from db.search_engine import BaseSearchEngine, ElasticSearchEngine
from db.storage import BaseStorage, RedisStorage
from fastapi import Depends
from models.film import Film
from services.base import BaseService
from services.search_engine_service import (BaseSearchEngineService,
                                            ElasticSearchEngineService)
from services.storage_service import BaseStorageService, StorageService


class FilmService(BaseService):
    def __init__(
            self,
            storage_service: BaseStorageService,
            search_engine_service: BaseSearchEngineService,
            index: str,
            model: Type[Film]):
        super().__init__(storage_service, search_engine_service, index, model)


@lru_cache()
def get_film_service(
        storage: BaseStorage = Depends(RedisStorage.get_connection),
        search_engine: BaseSearchEngine = Depends(ElasticSearchEngine.get_connection),
) -> FilmService:
    model = Film
    storage_service = StorageService(storage, model)
    search_engine_service = ElasticSearchEngineService(search_engine, model)
    return FilmService(storage_service, search_engine_service, 'movies', model)
