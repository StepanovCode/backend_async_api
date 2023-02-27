from logging import config as logging_config
from pathlib import Path

from core.logger import LOGGING
from pydantic import BaseSettings

logging_config.dictConfig(LOGGING)

ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = 'movies'
    PROJECT_DESCRIPTION: str = 'Сервис для получения данных о фильмах, персонах, жанрах'
    PROJECT_VERSION: str = 'v1.0.0'

    OPENAPI_GET_FILM_DESCRIPTION: str = "Получение фильма по его uuid"
    OPENAPI_GET_FILMS_DESCRIPTION: str = "Получение всех фильмов с пагинацией и отсортированных по полю"
    OPENAPI_SEARCH_FILMS_DESCRIPTION: str = "Полнотекстный поиск фильмов с пагинацией и отсортированных по полю"

    OPENAPI_GET_PERSON_DESCRIPTION: str = "Получение персоны по его uuid"
    OPENAPI_GET_PERSONS_DESCRIPTION: str = "Получение всех персон с пагинацией и отсортированных по полю"
    OPENAPI_SEARCH_PERSONS_DESCRIPTION: str = "Полнотекстный поиск персон с пагинацией и отсортированных по полю"

    OPENAPI_GET_GENRE_DESCRIPTION: str = "Получение жанра по его uuid"
    OPENAPI_GET_GENRES_DESCRIPTION: str = "Получение всех жанров с пагинацией и отсортированных по полю"
    OPENAPI_SEARCH_GENRES_DESCRIPTION: str = "Полнотекстный поиск жанров с пагинацией и отсортированных по полю"

    OPENAPI_SIZE_PARAMETER: str = "Количество получаемых значений на одной странице"
    OPENAPI_NUMBER_PARAMETER: str = "Номер страницы результата пагинации"
    OPENAPI_SORT_PARAMETER: str = "Сортировка по полю"
    OPENAPI_SEARCH_PARAMETER: str = "Значение по которому производится полнотекстовый поиск"
    OPENAPI_ID_PARAMETER: str = "UUID для поиска"
    OPENAPI_FILTER_PARAMETER: str = "Значение для фильтрации"

    # Настройка пагинации

    PAGINATION_MAX_SIZE: int = 50
    PAGINATION_MIN_SIZE: int = 1

    # Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Настройки Elasticsearch
    ELASTIC_HOST: str
    ELASTIC_PORT: str

    # Корень проекта
    ROOT_DIR = ROOT_DIR

    # class Config:
    #     env_file = ROOT_DIR / 'envs/test.local.env'
    #     env_file_encoding = 'utf-8'


settings = Settings()
