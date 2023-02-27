import json
import logging

import requests
from utils.decorators import backoff
from core.variables import ELASTICSEARCH_BASE_URL

logger = logging.getLogger("ELASTICSEARCH")


class ElasticSearchService:
    def __init__(
        self, *, base_url: str = ELASTICSEARCH_BASE_URL, index: str = "movies", index_schema: dict
    ):
        logger.debug(f"Init ElasticSearchService {base_url}{index}")
        self.base_url = base_url
        self.index = index
        self.index_schema = index_schema

    @backoff()
    def create_index(self, data: dict):
        logger.debug("Create Index")
        response = requests.put(f"{self.base_url}{self.index}", json=data)
        logger.debug(response.json())
        return response

    @backoff()
    def update_index_settings(self, data: dict):
        logger.debug("Update Index Settings")
        response = requests.put(f"{self.base_url}_all/_settings?pretty", json=data)
        logger.debug(response.json())
        return response

    @backoff()
    def get_index(self) -> requests.Response:
        logger.debug(f"Get index info {self.index}")
        response = requests.get(f"{self.base_url}{self.index}")
        logger.debug(response.json())
        return response

    @backoff()
    def add_record_to_index(self, data: dict):
        logger.debug(f"URL: {self.base_url}{self.index}/_create/")
        logger.debug(f"Data: {data}")
        response = requests.post(
            f"{self.base_url}{self.index}/_create/{data['id']}", json=data
        )
        logger.debug(response.json())
        return response

    @backoff()
    def bulk_add(self, data: list[dict]):
        if not data:
            return
        headers = {"Content-Type": "application/x-ndjson"}
        logger.debug(f"URL: {self.base_url}{self.index}/_bulk")
        logger.debug(f"Data: {data}")

        new_data = "".join(
            '{"index": {"_index": "%s", "_id": "%s"}}\n%s\n'
            % (self.index, elem["id"], json.dumps(elem))
            for elem in data
        )
        response = requests.post(
            f"{self.base_url}{self.index}/_bulk", data=new_data, headers=headers
        )
        r = response.json()
        return r

    @backoff()
    def bulk_update(self, data: list[dict]):
        logger.debug(f"URL: {self.base_url}{self.index}/_bulk")
        logger.debug(f"Data: {data}")

        headers = {"Content-Type": "application/x-ndjson"}

        new_data = "".join(
            '{"update": {"_index": "%s", "_id": "%s"}}\n%s\n'
            % (self.index, elem["id"], json.dumps({"doc": elem}))
            for elem in data
        )
        response = requests.post(
            f"{self.base_url}{self.index}/_bulk", data=new_data, headers=headers
        )
        logger.debug(response.json())
        r = response.json()
        return r
