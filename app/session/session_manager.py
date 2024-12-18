from typing import Optional, Self, Union
import aiohttp
import asyncio
import logging
from aiohttp import ClientError, ClientResponse, ClientSession, BasicAuth
from bs4 import BeautifulSoup, NavigableString, Tag
from ..parsers.urls import LOGOUT_URL, link_teacher_supervision, link_to_activity, link_to_personal, link_to_login,BASE_PREPOD_URL

logging.basicConfig(level=logging.INFO)


class SessionManager:
    def __init__(self, login: str, password: str) -> None:
        """
        Manages a session for a user.

        :param login: User login.
        :param password: User password.
        """
        self.login_url = link_to_login
        self.logout_url = LOGOUT_URL
        self.session: Optional[ClientSession] = None
        self.auth = BasicAuth(login, password)
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

    async def is_authenticated(self) -> bool:
        """
        Checks if the session is still valid by posting login credentials and analyzing the response.

        :return: True if authentication is successful, otherwise False.
        """
        if not self.session:
            logging.warning("Session not initialized. Authentication cannot proceed.")
            return False

        try:
            async with self.session.post(self.login_url, data=self.payload) as response:
                document = BeautifulSoup(await response.text(), features="lxml")
                error_div: Union[Tag, NavigableString, None] = document.find(id="error_msg")
                if error_div and "Неверный логин-пароль" in error_div.get_text():
                    logging.warning("Session expired or invalid credentials.")
                    return False
                return True
        except Exception as e:
            logging.error(f"Error during session validation: {e}")
            return False

    async def login(self) -> bool:
        """
        Authenticates the session by logging in to the server.

        :return: True if login is successful, otherwise False.
        """
        try:
            if await self.is_authenticated():
                logging.info("Login successful.")
                self.status = True
                return True
            else:
                logging.error("Login failed: Invalid credentials.")
                return False
        except ClientError as e:
            logging.error(f"Login failed due to client error: {e}")
            return False

    async def ensure_authenticated(self) -> bool:
        """
        Ensures the session is authenticated; logs in again if necessary.

        :return: True if authentication is successful, otherwise False.
        """
        if not await self.is_authenticated():
            logging.info("Re-authenticating...")
            return await self.login()
        return True

    async def request_with_relogin(
        self, method: str, url: str, **kwargs
    ) -> Optional[ClientResponse]:
        """
        Ensures the session is valid before making a request.

        :param method: HTTP method (GET, POST, etc.).
        :param url: The target URL for the request.
        :param kwargs: Additional parameters for the request.
        :return: The HTTP response object if the request is successful, otherwise None.
        """
        try:
            if not await self.ensure_authenticated():
                logging.error("Unable to authenticate session. Request aborted.")
                return None

            async with self.session.request(method.upper(), url, **kwargs) as response:
                response.raise_for_status()
                logging.info(f"{method.upper()} request to {url} successful.")
                self.last_response = response
                return response
        except ClientError as e:
            logging.error(f"{method.upper()} request to {url} failed: {e}")
            return None

    async def get(self, url: str) -> Optional[ClientResponse]:
        """
        Makes a GET request.

        :param url: The target URL for the GET request.
        :return: The HTTP response object if successful, otherwise None.
        """
        return await self.request_with_relogin("get", url)

    async def post(self, url: str, data: dict) -> Optional[ClientResponse]:
        """
        Makes a POST request.

        :param url: The target URL for the POST request.
        :param data: The data to send in the POST request.
        :return: The HTTP response object if successful, otherwise None.
        """
        return await self.request_with_relogin("post", url, data=data)

    async def logout(self) -> bool:
        """
        Logs out of the session by making a request to the LOGOUT_URL.

        :return: True if logout is successful, otherwise False.
        """
        if not self.session:
            logging.warning("Session not initialized. Logout cannot proceed.")
            return False

        try:
            async with self.session.get(self.logout_url) as response:
                if response.status == 200:
                    logging.info("Logout successful.")
                    self.status = False
                    return True
                else:
                    logging.error(f"Logout failed with status code {response.status}.")
                    return False
        except ClientError as e:
            logging.error(f"Logout failed due to client error: {e}")
            return False



async def is_teacher(session: ClientSession) -> bool:
    """
    Checks if the user is a teacher.

    :param session: Asynchronous aiohttp session authorized for the user.
    :return: True if the user is a teacher, otherwise False.
    """
    try:
        async with (await session.get(link_teacher_supervision)) as response:
            if response.status != 200:
                logging.error(f"Error accessing {link_teacher_supervision}: {response.status}")
                return False
            soup = BeautifulSoup(await response.text(), 'lxml')
            error_span: Tag | NavigableString | None = soup.find('span', class_='error')
            if error_span and error_span.text.strip() == 'Нет доступа к Личному кабинету преподавателя!':
                return False
            logging.info("The user is a teacher.")
            return True

    except Exception as e:
        logging.error(f"Teacher verification error: {e}")
        return False

