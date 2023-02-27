import logging
import time
from functools import wraps

from django.db.utils import OperationalError as django_OperationError
from psycopg2 import OperationalError
from redis.exceptions import ConnectionError as redis_ConnectionError
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError


class MaxRetryConnectionError(Exception):
    """Conneciton Error"""


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный
    экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """
    logger = logging.getLogger('backoff')

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            while True:
                logger.debug(f"Try-{n} ")
                t = locals().get("t")

                if t:
                    if t >= border_sleep_time:
                        t = border_sleep_time
                    else:
                        new_t = start_sleep_time * factor ** n
                        t = border_sleep_time if new_t >= border_sleep_time else new_t
                else:
                    new_t = start_sleep_time * factor ** n
                    t = border_sleep_time if new_t >= border_sleep_time else new_t

                logger.debug(f"Sleep time {t} sec")
                time.sleep(t)
                try:
                    result = func(*args, **kwargs)
                    break
                except (
                        ConnectionError,
                        ConnectionRefusedError,
                        NewConnectionError,
                        OperationalError,
                        django_OperationError,
                        redis_ConnectionError,
                        Exception
                ) as e:
                    logger.error(e)
                    n += 1

            return result

        return inner

    return func_wrapper
