from http import HTTPStatus

import pytest

from functional.testdata.data import es_data_movies
from functional.testsupport.elastic import create_index, drop_index

films_uri = '/api/v1/films/'
films_search_uri = '/api/v1/films/search/'


@pytest.mark.parametrize(
    'data, expected_answer',
    [
        (
                {
                    'params': {
                        'search': 'The Star',
                        'page[size]': 'some string',
                        'page[number]': 1,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_search_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.BAD_REQUEST, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'The Star',
                        'page[size]': 50,
                        'page[number]': 1,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_search_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'search': 'Mashed potato',
                        'page[size]': 50,
                        'page[number]': 1,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_search_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'The Star',
                        'page[size]': -10,
                        'page[number]': -10,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_search_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 1}
        ),
        (
                {
                    'params': {
                        'search': 'The Star',
                        'page[size]': 100000,
                        'page[number]': -10,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_search_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'page[size]': 40,
                        'page[number]': 1,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 40}
        ),
        (
                {
                    'params': {},
                    'es_data': es_data_movies,
                    'endpoint': films_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {
                    'params': {
                        'page[size]': -10,
                        'page[number]': -10,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 1}
        ),
        (
                {
                    'params': {
                        'page[size]': 100000,
                        'page[number]': -10,
                    },
                    'es_data': es_data_movies,
                    'endpoint': films_uri,
                    'index': 'movies',
                },
                {'status': HTTPStatus.OK, 'length': 50}
        ),
    ]
)
@pytest.mark.asyncio
async def test_films(
        es_client,
        es_write_data,
        delete_redis_keys, make_get_request,
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
