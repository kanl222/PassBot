from functools import wraps
from typing import Any, Awaitable, Callable, LiteralString, Optional, Self, Union
import aiohttp
import asyncio
import logging
from aiohttp import ClientError, ClientResponse, ClientSession, BasicAuth
from bs4 import BeautifulSoup, NavigableString, Tag
from ..parsers.urls import (
    LOGOUT_URL,
    link_teacher_supervision,
    link_to_activity,
    link_to_personal,
    link_to_login,
    BASE_PREPOD_URL,
)
from app.tools.local_response_url import cached_url_response

logging.basicConfig(level=logging.INFO)


def handle_session_errors(
    func: Callable[..., Awaitable[Any]]
) -> Callable[..., Awaitable[Any]]:
    """Decorator to handle common session-related errors and logging."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientError as e:
            logging.error(f"Client error in {func.__name__}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            return None

    return wrapper


class SessionManager:
    def __init__(self, login: str, password: str) -> None:
        """
        Manages a session for a user.

        :param login: User login.
        :param password: User password.
        """
        self.login_url = link_to_login
        self.logout_url: LiteralString = LOGOUT_URL
        self.session: Optional[ClientSession] = None
        self.auth = BasicAuth(login=login, password=password)
        self.status = False
        self.payload: dict[str, str] = {"login": login, "pwd": password}
        self.last_response: Optional[ClientResponse] = None

    async def __aenter__(self) -> "SessionManager":
        """Async context manager entry for session management."""
        self.session = ClientSession(auth=self.auth)
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Async context manager exit to close the session and log out if necessary."""
        try:
            if self.session and self.status:
                await self.logout()
        finally:
            if self.session:
                await self.session.close()

    @handle_session_errors
    async def is_authenticated(self) -> bool:
        """Check if the current session is authenticated."""
        if not self.session:
            logging.warning("Session not initialized.")
            return False

        async with self.session.post(self.login_url, data=self.payload) as response:
            document = BeautifulSoup(await response.text(), features="lxml")
            error_div: Tag | NavigableString | None = document.find(id="error_msg")
            return not (error_div and "Неверный логин-пароль" in error_div.get_text())

    async def login(self) -> bool:
        """
        Authenticates the session by logging in to the server.

        :return: True if login is successful, otherwise False.
        """
        try:
            if await self.is_authenticated():
                logging.info(msg="Login successful.")
                self.status = True
                return True
            else:
                logging.error(msg="Login failed: Invalid credentials.")
                return False
        except ClientError as e:
            logging.error(msg=f"Login failed due to client error: {e}")
            return False

    async def ensure_authenticated(self) -> bool:
        """
        Ensures the session is authenticated; logs in again if necessary.

        :return: True if authentication is successful, otherwise False.
        """
        if not await self.is_authenticated():
            logging.info(msg="Re-authenticating...")
            return await self.login()
        return True

    async def request(
        self, method: str, url: str, **kwargs
    ) -> Optional[ClientResponse]:
        """Generic method to handle different HTTP request types with authentication."""
        try:

            response = self.session.request(method.upper(), url, **kwargs)
            logging.info(f"{method.upper()} request to {url} successful.")
            self.last_response = response
            return response
        except ClientError as e:
            logging.error(f"Client error during request: {e}")
            return None
        except aiohttp.ClientResponseError as e:
            logging.error(
                f"Request to {url} failed with status {e.status}: {e.message}"
            )
            return None

    async def get(self, url: str, **kwargs) -> Optional[ClientResponse]:
        """Simplified GET request method."""
        return await self.request("get", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Optional[ClientResponse]:
        """Simplified POST request method."""
        return await self.request("post", url, **kwargs)

    @handle_session_errors
    async def logout(self) -> bool:
        """Log out of the current session."""
        if not self.session:
            logging.warning("Session not initialized.")
            return False

        async with self.session.get(self.logout_url) as response:
            self.status: bool = False
            logging.info("Logout " + ("failed" if self.status else "successful"))
            return not self.status


async def is_teacher(session: ClientSession) -> bool:
    """
    Checks if the user is a teacher.

    :param session: Asynchronous aiohttp session authorized for the user.
    :return: True if the user is a teacher, otherwise False.
    """
    try:
        async with await session.get(link_teacher_supervision) as response:
            if response.status != 200:
                return False

            soup = BeautifulSoup(await response.text(), "lxml")
            error_span: Tag | NavigableString | None = soup.find("span", class_="error")

            return not (
                error_span
                and error_span.text.strip()
                == "Нет доступа к Личному кабинету преподавателя!"
            )

    except Exception as e:
        logging.error(msg=f"Teacher verification error: {e}")
        return False
