from curses import wrapper

import aiohttp
import asyncio
import logging
from aiohttp import ClientSession, BasicAuth
from bs4 import BeautifulSoup
from app.tools.json_local import import_json_is_crypto
from ..parsers.urls import link_to_activity, link_to_personal
from ..parsers.urls import *
logging.basicConfig(level=logging.INFO)
from functools import wraps

session_manager = None


async def is_authenticated(response: aiohttp.ClientResponse) -> bool:
    """Check if login is successful based on the HTML response."""
    try:
        document = BeautifulSoup(await response.text(), features='lxml')
        error_spans = document.find_all('span', class_='error')
        if error_spans and 'неверное сочетание логина и пароля' in error_spans[0].text:
            return False
        forms = document.find_all('form')
        if forms and forms[0].get('action') == "https://www.osu.ru/iss/prepod/lk.php":
            return False
        return True
    except Exception as e:
        logging.error(f"Error during login check: {e}")
        return False


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = args[0]
        with session.request("GET", link_to_personal) as response:
            if not is_authenticated(response):
                session.login()
        return await func(*args, **kwargs)
    return wrapper


class SessionManager:
    def __init__(self, login_url: str = 'https://www.osu.ru/iss/1win/'):
        self.login_url = login_url
        self.session: ClientSession = None
        self.payload = import_json_is_crypto('user.json')

        if not self.payload:
            logging.error("User data not found in 'user.json'. Initialization failed.")
            raise ValueError("Missing user credentials.")

        login = self.payload.get('login')
        pwd = self.payload.get('pwd')
        if not login or not pwd:
            logging.error("Login or password missing in user data.")
            raise ValueError("Both 'login' and 'pwd' must be present in 'user.json'.")

        self.auth = BasicAuth(login, pwd)

    async def __aenter__(self):
        """Async context manager entry for session management."""
        self.session = ClientSession(auth=self.auth)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit to close the session."""
        if self.session:
            await self.session.close()

    async def initialize_session(self) -> bool:
        """Initialize and verify the session."""
        if not await self.login():
            logging.error("Initialization failed: unable to log in.")
            return False
        logging.info("Session initialized successfully.")
        return True

    async def login(self) -> bool:
        """Authenticate the session by logging in to the server."""
        try:
            async with self.session.post(self.login_url, data=self.payload) as response:
                if response.status == 200 and await is_authenticated(response):
                    logging.info("Login successful.")
                    return True
                else:
                    logging.error("Login failed with status %s: %s", response.status, await response.text())
                    return False
        except KeyError as e:
            logging.error(f"Missing key in payload: {e}")
            return False
        except aiohttp.ClientError as e:
            logging.error(f"Login failed due to client error: {e}")
            return False

    @auth_required
    async def request_with_relogin(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Wrapper to check and maintain session validity for GET/POST requests."""
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


async def check_parsing_availability() -> bool:
    """
    Check if parsing is available by initializing a session and testing data retrieval.

    :return: bool - True if parsing is available, False otherwise.
    """
    logging.info("Checking parsing availability...")
    if not await session_manager.initialize_session():
        logging.error("Parsing check failed: Unable to establish a session.")
        return False

    test_url = "https://www.osu.ru/iss/lks/?page=progress"
    response = await session_manager.get(test_url)

    if is_authenticated(response) and response and response.status == 200:
        logging.info("Parsing check successful. Parsing is available.")
        return True
    else:
        logging.error("Parsing check failed: Unable to retrieve test data.")
        return False


def main_session_manager():
    global session_manager
    session_manager = SessionManager()

    with session_manager:
        parsing_available = check_parsing_availability()
        if parsing_available:
            logging.info("Parsing is ready to proceed.")
        else:
            logging.error("Parsing is not available. Please check your configuration.")


if __name__ == "__main__":
    main_session_manager()
