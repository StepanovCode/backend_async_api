import os

ELASTICSEARCH_BASE_URL = os.environ.get(
    "ELASTICSEARCH_BASE_URL", "http://127.0.0.1:9200/"
)
SCANNING_SLEEP_TIME_SEC = int(os.environ.get("SCANNING_SLEEP_TIME_SEC", 10))
