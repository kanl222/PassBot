import logging
import os
from secrets import choice
from string import ascii_letters, digits
from typing import Optional
from pathlib import Path
from .settings import settings
from jose import JWTError, jwt



class SettingsCrypto(object):
    SECRET_KEY: str = None
    ALGORITHM: str = None

    def __init__(self):
        if settings is not None:
            self.SECRET_KEY = settings.SECRET_KEY
            self.ALGORITHM = settings.ALGORITHM

    def generate_new_secret_key(self) -> str:
        """
        Generate a new 64-character secret key composed of letters, digits, and special characters.

        :return: A newly generated secret key.
        """
        secret_key_chars = ascii_letters + digits + '-+)(*?><{}!@#$%^'
        return ''.join(choice(secret_key_chars) for _ in range(64))

    def update_secret_key(self) -> None:
        """
        Update the secret key in the current settings and log the event.
        """
        self.SECRET_KEY = self.generate_new_secret_key()
        logging.info("Secret key updated successfully.")

    def load_or_generate_secret_key(self) -> None:
        """
        Load the secret key from the environment, or generate a new one if it's missing.
        """
        if not self.SECRET_KEY:
            logging.info("Secret key not found, generating a new one.")
            self.update_secret_key()


try:
    settings_crypto = SettingsCrypto()
    settings_crypto.load_or_generate_secret_key()
    SECRET_KEY = settings_crypto.SECRET_KEY
    ALGORITHM = settings_crypto.ALGORITHM

    logging.info(f"Using secret key: {SECRET_KEY[:5]}... (hidden for security)")
    logging.info(f"Algorithm: {ALGORITHM}")

except Exception as e:
    logging.error(f"Error loading crypto settings: {e}", exc_info=True)
    raise  # Прерываем выполнение, если не удалось загрузить настройки


def encode_data(data: dict) -> Optional[str]:
    """
    Encode a dictionary into a JWT token.

    :param data: The data to encode into the JWT.
    :return: The encoded JWT string, or None if an error occurs.
    """
    try:
        return jwt.encode(data, key=SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        logging.error(f"Error encoding data into JWT: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error during JWT encoding: {e}", exc_info=True)
        return None


def decode_data(token: str) -> Optional[dict]:
    """
    Decode a JWT token back into a dictionary.

    :param token: The JWT token to decode.
    :return: The decoded data, or None if an error occurs.
    """
    try:
        return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logging.error(f"JWT decoding error: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error during JWT decoding: {e}", exc_info=True)
        return None
