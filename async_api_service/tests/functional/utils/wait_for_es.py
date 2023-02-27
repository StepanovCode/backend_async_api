import time

from elasticsearch import Elasticsearch

from functional.settings import test_settings
from functional.utils.decorators import backoff


@backoff()
def wait_for():
    es_client = Elasticsearch(hosts=[f'{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}'])
    if not es_client.ping():
        raise Exception("Ping return wrong value")


if __name__ == '__main__':
    wait_for()
