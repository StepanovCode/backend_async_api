import abc
import logging
from typing import Any

from redis import Redis
from utils.decorators import backoff

logger = logging.getLogger("STORAGE")


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self, key: str) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    @backoff()
    def retrieve_state(self, key: str) -> dict:
        return self.redis_adapter.get(key)

    @backoff()
    def save_state(self, state: dict) -> None:
        self.redis_adapter.set(**state)


class State:
    def __init__(self, storage: BaseStorage):
        logger.debug("Init State")
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        logger.debug(f"Set to Storage {key=}, {value=}")
        self.storage.save_state({"name": key, "value": value})

    def get_state(self, key: str) -> Any:
        value = self.storage.retrieve_state(key)
        logger.debug(f"Get from Storage {key=} {value=}")
        return value
