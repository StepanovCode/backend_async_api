import aiohttp
import pytest_asyncio
from aiohttp import ClientSession

from functional.settings import test_settings


@pytest_asyncio.fixture
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def make_get_request(aiohttp_session: ClientSession):
    async def inner(url: str, query_data: dict):
        async with aiohttp_session.get(test_settings.SERVICE_URL + url, params=query_data) as response:
            body = await response.json()
            response_status = response.status
            return response_status, body
    return inner
