from functools import wraps

import aioredis
import pytest_asyncio
from aioredis import Redis

from functional.settings import test_settings


@pytest_asyncio.fixture
async def redis_client():
    client = await aioredis.create_redis_pool(
        (test_settings.REDIS_HOST, test_settings.REDIS_PORT),
        password=test_settings.REDIS_PASSWORD,
        minsize=10, maxsize=20
    )
    yield client
    client.close()
    await client.wait_closed()


@pytest_asyncio.fixture
async def delete_redis_keys(redis_client: Redis):
    async def inner():
        response = await redis_client.flushdb()
        if not response:
            raise Exception('Ошибка при удалении ключей из Redis')
    return inner
