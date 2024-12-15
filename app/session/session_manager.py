from typing import Self
import aiohttp
import asyncio
import logging
from aiohttp import ClientSession, BasicAuth
from bs4 import BeautifulSoup, NavigableString, Tag
from ..parsers.urls import link_teacher_supervision, link_to_activity, link_to_personal, link_to_login,BASE_PREPOD_URL

logging.basicConfig(level=logging.INFO)


class SessionManager:
    def __init__(self, login: str, password: str) -> None:
        """
        Manages a session for a user.

        :param login: User login.
        :param password: User password.
        """
        self.login_url = link_to_login
        self.session: ClientSession = None
        self.auth = BasicAuth(login, password)
        self.status = False
        self.payload: dict[str, str] = {"login": login, "pwd": password}

    async def __aenter__(self) -> Self:
        """Async context manager entry for session management."""
        self.session = ClientSession(auth=self.auth)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Async context manager exit to close the session."""
        if self.session:
            await self.session.close()

    async def is_authenticated(self) -> bool:
        """Check if the session is still valid by accessing a protected endpoint."""
        try:
            async with self.session.post(self.login_url, data=self.payload) as response:
                document = BeautifulSoup(await response.text(), features='lxml')
                error_div: Tag | NavigableString | None = document.find(id="error_msg")
                if error_div and "Неверный логин-пароль" in error_div.get_text():
                    logging.warning("Session expired or invalid credentials.")
                    return False
                return True
        except Exception as e:
            logging.error(f"Error during session validation: {e}")
            return False

    async def login(self) -> bool:
        """Authenticate the session by logging in to the server."""
        try:
                if await self.is_authenticated():
                    logging.info("Login successful.")
                    self.status = True
                    return True
                else:
                    logging.error(f"Login failed with status")
                    return False
        except aiohttp.ClientError as e:
            logging.error(f"Login failed due to client error: {e}")
            return False

    async def ensure_authenticated(self) -> bool:
        """Ensure the session is authenticated; log in again if necessary."""
        if not await self.is_authenticated():
            logging.info("Re-authenticating...")
            return await self.login()
        return True

    async def request_with_relogin(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Ensure the session is valid before making a request."""
        # if not await self.ensure_authenticated():
        #     logging.error("Unable to authenticate session. Request aborted.")
        #     return None

        try:
            async with self.session.request(method.upper(), url, **kwargs) as response:
                response.raise_for_status()
                logging.info(f"{method.upper()} request to {url} successful.")
                return response
        except aiohttp.ClientError as e:
            logging.error(f"{method.upper()} request to {url} failed: {e}")
            return None

    async def get(self, url: str) -> aiohttp.ClientResponse:
        """Make a GET request."""
        return await self.request_with_relogin("get", url)

    async def post(self, url: str, data: dict) -> aiohttp.ClientResponse:
        """Make a POST request."""
        return await self.request_with_relogin("post", url, data=data)


async def get_user_session(login: str, password: str) -> SessionManager:
    """
    Returns the session for the user if authentication was successful.

    :param login: User login.
    :param password: User password.
    :return: SessionManager instance to work with the session, or None if authentication failed.
    """
    session_manager = SessionManager(login, password)
    async with session_manager as sm:
        if await sm.login():
            logging.info(f"Session created successfully for user: {login}")
            return sm
        else:
            logging.error(f"Failed to create session for user: {login}")
            return sm



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

            error_span: Tag | NavigableString | None = soup.find('span', class_='')
            if 'Введите' == error_span.text.split()[0] and error_span:
                return False
            logging.info("The user is a teacher.")
            return True

    except Exception as e:
        logging.error(f"Teacher verification error: {e}")
        return False


async def main() -> None:
    """Example of using the function to get a session."""
    user_login = "example_login"
    user_password = "example_password"

    session_manager: SessionManager = await get_user_session(user_login, user_password)

    if session_manager:
        test_url = "https://www.osu.ru/iss/lks/?page=progress"
        response: aiohttp.ClientResponse = await session_manager.get(test_url)
        if response:
            logging.info("Data fetched successfully.")
            text: str = await response.text()
            print(text)
        else:
            logging.error("Failed to fetch data.")
    else:
        logging.error("Failed to authenticate user.")


if __name__ == "__main__":
    asyncio.run(main())