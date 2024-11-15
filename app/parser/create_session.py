import aiohttp
import asyncio
import logging
from aiohttp import ClientSession, BasicAuth
from ..tools.json_local import import_json_is_crypto

class SessionManager:
    def __init__(
            self,
            login_url: str = 'https://www.osu.ru/iss/1win/'
    ):
        self.login_url = login_url
        self.session = None

        self.payload = import_json_is_crypto('user.json')
        if self.payload:
            self.auth = BasicAuth(self.payload['login'], self.payload['pwd'])
        else:
            logging.error('Not data user')
            raise

    async def initialize_session(self) -> bool:
        """Initialize and verify the session."""
        async with ClientSession(auth=self.auth) as session:
            self.session = session
            if not await self.login():
                logging.error("Initialization failed: unable to log in.")
                return False
            logging.info("Session initialized successfully.")
            return True

    async def login(self) -> bool:
        """Authenticate the session by logging in to the server."""
        try:
            async with self.session.post(self.login_url, data=self.payload) as response:
                if response.status == 200:
                    logging.info("Login successful")
                    return True
                else:
                    response_text = await response.text()
                    logging.error("Login failed: %s, %s", response.status, response_text)
                    return False
        except aiohttp.ClientError as e:
            logging.error("Login failed: %s", e)
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
        """Make a GET request, checking session validity."""
        return await self.request_with_relogin("get", url)

    async def post(self, url: str, data: dict) -> aiohttp.ClientResponse:
        """Make a POST request, checking session validity."""
        return await self.request_with_relogin("post", url, data=data)

session_manager = SessionManager()

async def main():
    if await session_manager.initialize_session():
        response = await session_manager.get(session_manager.login_url)
        if response:
            text = await response.text()
            print(text)
        else:
            logging.error("Failed to retrieve data after session initialization.")

if __name__ == "__main__":
    asyncio.run(main())
