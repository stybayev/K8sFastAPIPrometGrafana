import logging
import time
from functools import wraps


def backoff(
    exceptions: tuple = Exception,
    start_sleep_time: float = 0.1,
    factor: float = 2,
    border_sleep_time: float = 10,
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param exceptions: кортеж обрабатываемых ошибок
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 1

            def t():
                return start_sleep_time * (factor**n)

            while t() < border_sleep_time:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.error(f"Connection lost! Exception: {e}")
                    logging.error(f"Next reconnect try in {t()} seconds")
                    time.sleep(t())
                    n += 1

        return inner

    return func_wrapper
