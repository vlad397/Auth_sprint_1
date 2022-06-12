"""Реализация backoff для внешних вызовов с ошибками."""
from functools import wraps
from time import sleep


def backoff(logger, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """Повторное выполнение функции через некоторое время, при ошибке.

    Использует наивный экспоненциальный рост времени повтора
    (factor) до граничного времени ожидания (border_sleep_time)
    Формула
    t = start_sleep_time * 2^(n) if t < border_sleep_time
    t = border_sleep_time if t >= border_sleep_time

    Args:
        logger (Logger): экземпляр logger'а
        start_sleep_time (float): начальное время повтора
        factor (int): во сколько раз нужно увеличить время ожидания
        border_sleep_time (float): граничное время ожидания

    Returns:
         результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time = start_sleep_time
            counter = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if time < border_sleep_time:
                        time = start_sleep_time * factor ** counter
                    else:
                        time = border_sleep_time
                    logger.log(
                        '[{0}]: connection failed ({1}), sleeping {2}'.format(
                            counter,
                            ex,
                            time,
                        ),
                    )
                sleep(time)
                counter += 1
        return inner
    return func_wrapper
