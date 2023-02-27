import json

import pytest_asyncio
from elasticsearch import AsyncElasticsearch, NotFoundError

from functional.settings import test_settings
from functional.testdata.schemas_elastic import (genre_index, movies_index,
                                                 person_index)

INDEX_BODY_MAP = {
    'movies': movies_index,
    'persons': person_index,
    'genres': genre_index
}


@pytest_asyncio.fixture
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}'])
    yield client
    await client.close()


@pytest_asyncio.fixture
async def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], es_index):
        bulk_query = get_es_bulk_query(data, es_index)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            print(f'RESP: {response}')
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


async def create_index(es_client: AsyncElasticsearch, index):
    response = await es_client.indices.create(index=index, body=INDEX_BODY_MAP[index])
    if not response:
        raise Exception('Ошибка при создании индекса в Elasticsearch')
    return response


async def drop_index(es_client: AsyncElasticsearch, index):
    try:
        await es_client.delete_by_query(index=index, body={"query": {"match_all": {}}})
        await es_client.indices.delete(index=index, ignore_unavailable=True)
    except NotFoundError as e:
        pass
    except Exception as e:
        raise Exception('Ошибка при удалении индекса в Elasticsearch')


def get_es_bulk_query(data: list[dict], es_index: str):
    bulk_query = []
    for row in data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row['id']}}),
            json.dumps(row)
        ])
    return bulk_query
