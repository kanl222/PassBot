import requests
import logging
from requests import Session
from requests.auth import HTTPBasicAuth
from ..tools.json_local import import_json_is_crypto


class SessionManager:
    def __init__(
            self,
            login_url: str = 'https://www.osu.ru/iss/1win/'
                 ):
        self.login_url = login_url
        self.payload = import_json_is_crypto('user.json')
        self.session = Session()
        self.session.auth = HTTPBasicAuth(self.payload['login'], self.payload['pwd'])  # Set up auth

    def initialize_session(self) -> bool:
        """Initialize and verify the session."""
        if not self.login():
            logging.error("Initialization failed: unable to log in.")
            return False
        if not self.is_logged_in():
            logging.error("Initialization failed: session check unsuccessful.")
            return False
        logging.info("Session initialized successfully.")
        return True

    def login(self) -> bool:
        """Authenticate the session by logging in to the server."""
        try:
            response = self.session.post(self.login_url, data=self.payload)
            response.raise_for_status()
            logging.info("Login successful")
            return True
        except requests.exceptions.RequestException as e:
            logging.error("Login failed: %s", e)
            return False

    def is_logged_in(self) -> bool:
        """Check if the session is still active by accessing a test endpoint."""
        try:
            test_response = self.session.get(self.login_url)
            if test_response.status_code == 200:
                logging.info("Session is active")
                return True
            else:
                logging.warning("Session is inactive; re-authentication required.")
                return False
        except requests.exceptions.RequestException:
            logging.warning("Unable to verify session status; re-authentication required.")
            return False

    def request_with_relogin(self, method: str, url: str, **kwargs) -> requests.Response:
        """Wrapper to check and maintain session validity for GET/POST requests."""
        if not self.is_logged_in():
            logging.info("Attempting to re-login...")
            if not self.login():
                logging.error("Re-login attempt failed. Cannot proceed with the request.")
                return None
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            logging.info(f"{method.upper()} request to {url} successful.")
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"{method.upper()} request to {url} failed: {e}")
            return None

    def get(self, url: str) -> requests.Response:
        """Make a GET request, checking session validity."""
        return self.request_with_relogin("get", url)

    def post(self, url: str, data: dict) -> requests.Response:
        """Make a POST request, checking session validity."""
        return self.request_with_relogin("post", url, data=data)

try:
    session_manager = SessionManager()
except  Exception as e:
    logging.error(e)

if __name__ == "__main__":
    if session_manager.initialize_session():
        response = session_manager.get(session_manager.login_url)
        if response:
            print(response.text)
        else:
            logging.error("Failed to retrieve data after session initialization.")
