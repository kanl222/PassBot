import asyncio
import functools
import json
import logging
import os
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple

from aiohttp import ClientResponse


def cached_url_response(cache_dir: str = "cached_responses"):    # Added cache_dir parameter
    """
    Decorator to cache URL responses for offline use and testing.
    Saves HTML content separately in windows-1251 encoding.
    """

    def decorator(func):
        @functools.wraps(wrapped=func)
        async def wrapper(self, method: str, url: str, **kwargs) -> Optional[ClientResponse]:
            cache_key = f"{method}_{hash(url)}_{kwargs}"
            print(cache_key)
            cache_filepath = f'{cache_dir}/{cache_key}.json'
            html_filepath = f'{cache_dir}/{cache_key}.html'
            print(os.path.exists(cache_filepath),cache_filepath)
            if os.path.exists(cache_filepath) and os.path.exists(html_filepath):
                logging.info(f"Using cached response for {url}")
                with open(cache_filepath, encoding="utf-8") as f, open(html_filepath, encoding="windows-1251") as html_file:
                    cached_data = json.load(f)
                    html_content = html_file.read()

                mock_response = MockClientResponse(method, url, cached_data["status"], html_content)
                self.last_response = mock_response
                return mock_response

            response = await func(self, method, url, **kwargs)

            if response:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_filepath, "w+", encoding="utf-8") as f, open(html_filepath, "w+", encoding="windows-1251") as html_file:
                    response = MockClientResponse(method, url, response.status, content=await response.text())
                    json.dump({"status": response.status}, f, ensure_ascii=False, indent=4)
                    html_file.write(await response.text())

            return mock_response

        return wrapper

    return decorator

class MockClientResponse:
    """Mocks aiohttp.ClientResponse for cached responses."""

    def __init__(self, method: str, url: str, status: int, content: str):
        self._method = method
        self._url = url
        self.status = status
        self._content = content

    async def text(self) -> str:
        """Returns the content of the response."""
        return self._content

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
