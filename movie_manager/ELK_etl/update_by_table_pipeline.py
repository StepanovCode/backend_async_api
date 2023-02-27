from datetime import datetime
from typing import Callable

from django.db.models import QuerySet

from services.elasticsearch import ElasticSearchService
from utils.elastic_prepared_json import genre_index, person_index, index_settings_json
import logging
from services.orm import BasicQueries, GenreService
from services.orm import PersonService
from redis import Redis
import os
from utils.storage import RedisStorage, State
from core.variables import SCANNING_SLEEP_TIME_SEC
import time

logger = logging.getLogger(__name__)

redis_client = Redis(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT")),
    password=os.environ.get("REDIS_PASSWORD"),
)
redis_storage = RedisStorage(redis_adapter=redis_client)
state = State(redis_storage)


def exists_or_create_elastic_index(elastic_connection: ElasticSearchService, index_schema: dict):
    response = elastic_connection.get_index()
    logger.debug(f"Get index info {response.status_code=}")
    if response.status_code != 200:
        elastic_connection.create_index(index_schema)
        elastic_connection.update_index_settings(index_settings_json)


def elasticsearch_bulks(data: list, connection: ElasticSearchService):
    if not data:
        logger.debug("Elastic data is empty")
        return
    logger.debug("Elastic Doc Update")
    resp = connection.bulk_update(data)

    doc_to_add = []
    logger.debug(resp)
    if resp["errors"]:
        for item in resp["items"]:
            update_field = item["update"]
            if update_field["status"] == 404:
                item_to_add = next(
                    (_i for _i in data if _i["id"] == update_field["_id"]), None
                )
                if item_to_add:
                    doc_to_add.append(item_to_add)

    if doc_to_add:
        logger.debug("Elastic Doc Add")
        connection.bulk_add(doc_to_add)


def create_select_query(table_name: str) -> QuerySet:
    if table_name == "genres":
        return BasicQueries.get_genres()
    if table_name == "persons":
        return BasicQueries.get_persons()
    raise Exception("Not implemented")


def pydantic_converting(table_name: str) -> Callable:
    if table_name == "genres":
        return GenreService.prepare_pydantic
    if table_name == "persons":
        return PersonService.prepare_pydantic
    raise Exception("Not implemented")


def processing(index_name: str, index_schema: dict):
    logger.debug("Create connection for table %s" % index_name)
    elastic_search_connection = ElasticSearchService(index=index_name, index_schema=index_schema)
    logger.debug("Check for exists of create new index %s " % index_name)
    exists_or_create_elastic_index(elastic_search_connection, elastic_search_connection.index_schema)

    operation_start_time_str: str = datetime.utcnow().isoformat()
    query = create_select_query(index_name)

    updated_at = state.get_state(f"{index_name}_by_table_last_updated_at")
    if updated_at:
        _start_date = datetime.fromisoformat(updated_at.decode())
        query = query.filter(updated_at__gte=_start_date)

    model_to_json_convertor: Callable = pydantic_converting(index_name)
    data_to_load = []
    for elem in query.all():
        result = model_to_json_convertor(elem)
        data_to_load.append(result.dict())
    logger.info(data_to_load)
    elasticsearch_bulks(data_to_load, elastic_search_connection)

    state.set_state(f"{index_name}_by_table_last_updated_at", operation_start_time_str)


if __name__ == "__main__":
    while True:
        processing("genres", genre_index)
        processing("persons", person_index)
        logger.debug(f"Sleep for {SCANNING_SLEEP_TIME_SEC=}")
        time.sleep(SCANNING_SLEEP_TIME_SEC)
