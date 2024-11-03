import logging
import os
from pathlib import Path
from secrets import choice
from string import ascii_letters, digits
from typing import Optional

from jose import jwt, JWTError


class SettingsCrypto:
    ENV_FILE_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".env"

    def __init__(self):
        self.SECRET_KEY  = os.getenv('SECRET_KEY')
        self.ALGORITHM = os.getenv('ALGORITHM')

    def generate_new_secret_key(self) -> str:
        """
        Generate a new 64-character secret key composed of letters and digits.

        :return: A newly generated secret key.
        """
        secret_key_chars = ascii_letters + digits
        return ''.join(choice(secret_key_chars) for _ in range(64))


    def update_secret_key(self) -> None:
        """
        Update the secret key in the current settings, save it to .env, and log the event.
        """
        self.SECRET_KEY = self.generate_new_secret_key()
        self.save_secret_key_to_env()
        logging.info("Secret key updated successfully.")

    def save_secret_key_to_env(self) -> None:
        """
        Write the updated SECRET_KEY to the .env file.
        """
        try:
            # Read lines if the file already exists, else create it
            lines = []
            if self.ENV_FILE_PATH.exists():
                with open(self.ENV_FILE_PATH, "r") as env_file:
                    lines = env_file.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.startswith("SECRET_KEY="):
                    lines[i] = f"SECRET_KEY={self.SECRET_KEY}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"SECRET_KEY={self.SECRET_KEY}\n")

            with open(self.ENV_FILE_PATH, "w") as env_file:
                env_file.writelines(lines)

            logging.info(f"New secret key saved to .env file at: {self.ENV_FILE_PATH}")
        except Exception as e:
            logging.error(f"Failed to update .env with new SECRET_KEY: {e}", exc_info=True)
            raise


try:
    settings_crypto = SettingsCrypto()
    SECRET_KEY = settings_crypto.SECRET_KEY
    ALGORITHM = settings_crypto.ALGORITHM
    print(SECRET_KEY, 1)
except Exception as e:
    logging.error(f"Error initializing SettingsCrypto: {e}", exc_info=True)
    raise


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
