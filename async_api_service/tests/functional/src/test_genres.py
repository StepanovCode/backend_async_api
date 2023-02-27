from http import HTTPStatus

import pytest

from functional.testdata.data import es_data_genres
from functional.testsupport.elastic import create_index, drop_index

genres_uri = '/api/v1/genres/'
genres_search_uri = '/api/v1/genres/search/'


@pytest.mark.parametrize(
    'data, expected_answer',
    [
        (
                {
                    'params': {
                        'search': 'Action',
                        'page[size]': 'somestring',
                        'page[number]': 1,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_search_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.BAD_REQUEST, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'Action',
                        'page[size]': 50,
                        'page[number]': 1,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_search_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'search': 'Fantasy',
                        'page[size]': 50,
                        'page[number]': 1,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_search_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'Action',
                        'page[size]': -10,
                        'page[number]': -10,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_search_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'Action',
                        'page[size]': 10000,
                        'page[number]': -10,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_search_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'page[size]': 40,
                        'page[number]': 1,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 40}
        ),
        (
                {
                    'params': {},
                    'es_data': es_data_genres,
                    'endpoint': genres_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'page[size]': -10,
                        'page[number]': -10,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_uri,
                    'index': 'genres',
                },
                {'status': HTTPStatus.OK, 'length': 1}
        ),
        (
                {
                    'params': {
                        'page[size]': 100000,
                        'page[number]': -10,
                    },
                    'es_data': es_data_genres,
                    'endpoint': genres_uri,
                    'index': 'genres',

                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
    ]
)
@pytest.mark.asyncio
async def test_genres(
        es_client,
        es_write_data, delete_redis_keys, make_get_request,
        data, expected_answer
):

    await delete_redis_keys()
    await drop_index(es_client, data.get('index'))
    await create_index(es_client, data.get('index'))
    await es_write_data(
        data.get('es_data'),
        data.get('index'),
    )

    path = data.get('endpoint')
    expected_status, expected_body = await make_get_request(path, data.get('params'))

    assert expected_status == expected_answer.get('status')
    assert len(expected_body) == expected_answer.get('length')

    await drop_index(es_client, data.get('index'))

    status, body = await make_get_request(path, data.get('params'))

    assert status == expected_status
    assert body == expected_body
