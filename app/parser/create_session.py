import aiohttp
import asyncio
import logging
from aiohttp import ClientSession, BasicAuth
from bs4 import BeautifulSoup
from ..tools.json_local import import_json_is_crypto

logging.basicConfig(level=logging.INFO)


async def is_logining(response: aiohttp.ClientResponse) -> bool:
    """Check if login is successful based on the HTML response."""
    try:
        text = await response.text()
        document = BeautifulSoup(text, features='lxml')
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


class SessionManager:
    def __init__(self, login_url: str = 'https://www.osu.ru/iss/1win/'):
        self.login_url = login_url
        self.session: ClientSession = None
        self.payload = import_json_is_crypto('user.json')

        if not self.payload:
            logging.error("User data not found in 'user.json'. Initialization failed.")
            raise ValueError("Missing user credentials.")

        self.auth = BasicAuth(self.payload.get('login'), self.payload.get('pwd'))

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
                if response.status == 200 and await is_logining(response):
                    logging.info("Login successful.")
                    return True
                else:
                    logging.error("Login failed with status %s: %s", response.status, await response.text())
                    return False
        except aiohttp.ClientError as e:
            logging.error(f"Login failed due to client error: {e}")
            return False

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


async def main():
    async with SessionManager() as session_manager:
        if await session_manager.initialize_session():
            response = await session_manager.get(session_manager.login_url)
            if response:
                text = await response.text()
                print(text)
            else:
                logging.error("Failed to retrieve data after session initialization.")


if __name__ == "__main__":
    asyncio.run(main())
