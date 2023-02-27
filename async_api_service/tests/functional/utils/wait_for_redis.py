import time

from redis import Redis

from functional.settings import test_settings
from functional.utils.decorators import backoff


@backoff()
def wait_for():
    redis_client = Redis(
        host=test_settings.REDIS_HOST,
        port=test_settings.REDIS_PORT,
        password=test_settings.REDIS_PASSWORD
    )

    if not redis_client.ping():
        raise Exception("Ping return wrong value")


if __name__ == '__main__':
    wait_for()
