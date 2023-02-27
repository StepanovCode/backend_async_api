import datetime
import json
import logging  # Root Logger from Django
import os
import time
from typing import Tuple

from django.core.paginator import Paginator
from django.db.models import QuerySet
from redis import Redis
from services.elasticsearch import ElasticSearchService
from services.orm import BasicQueries, FilmworkService
from utils.elastic_prepared_json import create_index_json, index_settings_json
from utils.storage import RedisStorage, State
from core.variables import SCANNING_SLEEP_TIME_SEC

logger = logging.getLogger("ELK-ETL")

logger.debug("Create Redis Client")
redis_client = Redis(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT")),
    password=os.environ.get("REDIS_PASSWORD"),
)
redis_storage = RedisStorage(redis_adapter=redis_client)
state = State(redis_storage)

logger.debug("Create ElasticSearch Client")
elastic_search = ElasticSearchService(index="movies", index_schema=create_index_json)

response = elastic_search.get_index()
logger.debug(f"Get index info {response.status_code=}")
if response.status_code != 200:
    elastic_search.create_index(create_index_json)
    elastic_search.update_index_settings(index_settings_json)


def elasticsearch_bulks(data: list):
    logger.debug("Elastic Doc Update")
    resp = elastic_search.bulk_update(data)

    doc_to_add = []
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
        elastic_search.bulk_add(doc_to_add)


def prepare_query_and_page_num_by_table_name(
    table_name: str, q: QuerySet
) -> Tuple[QuerySet, int]:
    updated_at = state.get_state(f"{table_name}_updated_at")
    page_number = state.get_state(f"{table_name}_page_number")

    if updated_at:
        _start_date = datetime.datetime.fromisoformat(updated_at.decode())
        q = q.filter(updated_at__gte=_start_date)

    page_start = int(page_number.decode()) - 1 if page_number else 0

    return q, page_start


def processing(q: QuerySet, table_name: str, page_start: int):
    start_time: datetime = datetime.datetime.utcnow()
    pages = Paginator(q, 30)
    logger.debug(f"Total page count {pages.count}")

    for page_ind in pages.page_range[page_start:]:
        obj_list = pages.get_page(page_ind).object_list
        if len(obj_list) == 0:
            break

        logger.debug(f"PAGE NUMBER :{page_ind}")
        data_to_load = []
        logger.debug("Prepare data to ElasticSearch")

        for ind, filmwork in enumerate(obj_list):
            if ind == 0 and table_name == "filmworks":
                state.set_state("filmworks_updated_at", str(filmwork.updated_at))
            logger.debug(
                f"Processing query:{filmwork.id} {filmwork.created_at} Filmwork"
            )
            result = FilmworkService.prepare_pydantic_filmwork(filmwork=filmwork)
            data_to_load.append(result.dict())

        state.set_state(f"{table_name}_page_number", page_ind)

        logger.debug("Save prepared data")
        state.set_state("data_to_load", json.dumps(data_to_load))

        elasticsearch_bulks(data_to_load)

        logger.debug("Clear prepared data")
        state.set_state("data_to_load", "[]")

    state.set_state(f"{table_name}_updated_at", start_time.isoformat())
    state.set_state(f"{table_name}_page_number", 1)


def main():
    logger.debug("Get ELK Data Upload Query from STATE")
    temp_data_to_load = state.get_state("data_to_load")
    if temp_data_to_load:
        temp_data_to_load = json.loads(temp_data_to_load)
        if temp_data_to_load:
            elasticsearch_bulks(temp_data_to_load)

    logger.debug("Get checking_on field name from STATE")
    checking_on = state.get_state("checking_on")
    if not checking_on:
        logger.debug("There are not checking_on field name in STATE, initial setup")
        time_str: str = datetime.datetime.utcnow().isoformat()
        checking_on = "filmworks"
        state.set_state("checking_on", checking_on)
        state.set_state("genres_updated_at", time_str)
        state.set_state("persons_updated_at", time_str)
    else:
        checking_on = checking_on.decode()

    completed = False
    while True:
        for table_name in ["filmworks", "genres", "persons"]:

            if completed:
                state.set_state("checking_on", table_name)
                checking_on = table_name

            if checking_on != table_name:
                continue

            logger.debug(f"Prepare queryset for filmworks depended on {checking_on}")
            filmworks_query = (
                BasicQueries.get_filmwork_with_prefetch_related().order_by("updated_at")
            )
            page_start = 0

            if checking_on == "filmworks":
                filmworks_query, page_start = prepare_query_and_page_num_by_table_name(
                    checking_on, filmworks_query
                )

            if checking_on == "genres":
                genres_query = BasicQueries.get_genres().order_by("updated_at")
                genres_query, page_start = prepare_query_and_page_num_by_table_name(
                    checking_on, genres_query
                )
                filmworks_query = filmworks_query.filter(genres__in=genres_query)

            if checking_on == "persons":
                persons_query = BasicQueries.get_persons().order_by("updated_at")
                persons_query, page_start = prepare_query_and_page_num_by_table_name(
                    checking_on, persons_query
                )
                filmworks_query = filmworks_query.filter(persons__in=persons_query)

            processing(filmworks_query, checking_on, page_start)
            completed = True

            logger.debug(f"Sleep for {SCANNING_SLEEP_TIME_SEC=}")
            time.sleep(SCANNING_SLEEP_TIME_SEC)


if __name__ == "__main__":
    main()
