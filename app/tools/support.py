import os
from datetime import datetime
import functools
from random import random
import time
import asyncio
from functools import wraps
from typing import Awaitable, Callable, Any
import logging

from app.core.settings import TEST_MODE,DIR_DATA


def timeit(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        end = time.perf_counter_ns()
        logging.info(f'{func.__name__} took {(end - start) / 1e9:.6f} seconds to complete')
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end = time.perf_counter_ns()
        logging.info(f'{func.__name__} took {(end - start) / 1e9:.6f} seconds to complete')
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper



def log_html(func,log_dir=f'{DIR_DATA}/html', prefix='log'):
    @wraps(func)
    def async_wrapper(*args, **kwargs):
        if TEST_MODE:
            try:
                html_content = args[1]
                if html_content:
                    os.makedirs(f'{log_dir}/{func.__name__}', exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f'{log_dir}/{func.__name__}/{prefix}_{timestamp}.html'
                    with open(filename, 'w', encoding='windows-1251') as f:
                        f.write(html_content)
            except Exception as e:
                print(f"Could not save HTML log: {e}")

        return func(*args, **kwargs)

    return async_wrapper


def import_html_log():
    with open("html_logs\Личный_кабинет_преподавателя_–_Посещение_занятий_студентами_Галимов.html", "r", encoding='windows-1251') as file:
        return file.read()