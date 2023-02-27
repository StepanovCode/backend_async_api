from pathlib import Path

from pydantic import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.parent


class TestSettings(BaseSettings):
    # Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Настройки Elasticsearch
    ELASTIC_HOST: str
    ELASTIC_PORT: str

    ES_INDEX: str
    ES_ID_FIELD: str
    ES_INDEX_MAPPING: dict

    SERVICE_URL: str

    # class Config:
    #     env_file = ROOT_DIR / 'envs/test.local.env'
    #     env_file_encoding = 'utf-8'


test_settings = TestSettings()
