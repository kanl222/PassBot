import aiohttp
import asyncio
import logging
from aiohttp import ClientSession, BasicAuth
from bs4 import BeautifulSoup
from app.tools.json_local import import_json_is_crypto
from ..parsers.urls import link_to_activity, link_to_personal

logging.basicConfig(level=logging.INFO)


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

    async def is_authenticated(self) -> bool:
        """Check if the session is still valid by accessing a protected endpoint."""
        try:
            async with self.session.get(link_to_personal) as response:
                document = BeautifulSoup(await response.text(), features='lxml')
                error_spans = document.find_all('span', class_='error')
                if error_spans and 'неверное сочетание логина и пароля' in error_spans[0].text:
                    logging.warning("Session expired or invalid credentials.")
                    return False
                return True
        except Exception as e:
            logging.error(f"Error during session validation: {e}")
            return False

    async def login(self) -> bool:
        """Authenticate the session by logging in to the server."""
        try:
            async with self.session.post(self.login_url, data=self.payload) as response:
                if response.status == 200 and await self.is_authenticated():
                    logging.info("Login successful.")
                    return True
                else:
                    logging.error(f"Login failed with status {response.status}: {await response.text()}")
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
        if not await self.ensure_authenticated():
            logging.error("Unable to authenticate session. Request aborted.")
            return None

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


async def check_parsing_availability(session_manager: SessionManager) -> bool:
    """
    Check if parsing is available by testing data retrieval from a protected page.

    :return: bool - True if parsing is available, False otherwise.
    """
    logging.info("Checking parsing availability...")
    test_url = "https://www.osu.ru/iss/lks/?page=progress"
    response = await session_manager.get(test_url)

    if response and response.status == 200:
        logging.info("Parsing check successful. Parsing is available.")
        return True

    logging.error("Parsing check failed: Unable to retrieve test data.")
    return False


async def main():
    """Main entry point for session management and parsing availability check."""
    async with SessionManager() as session_manager:
        parsing_available = await check_parsing_availability(session_manager)
        if parsing_available:
            logging.info("Parsing is ready to proceed.")
        else:
            logging.error("Parsing is not available. Please check your configuration.")


if __name__ == "__main__":
    asyncio.run(main())
