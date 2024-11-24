import json
import logging
import os
from pathlib import Path
from secrets import token_hex
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.padding import PaddingContext

SECRET_KEY = None

class SettingsCrypto:
    ENV_FILE_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".env"

    def __init__(self):
        self.SECRET_KEY: str = os.getenv('SECRET_KEY')

        if not self.SECRET_KEY:
            logging.warning("SECRET_KEY not found in environment. Generating new key.")
            self.update_secret_key()

    def generate_new_secret_key(self) -> str:
        """Generate a new 64-character secret key composed of letters and digits."""
        return token_hex(64)

    def update_secret_key(self) -> None:
        """Update the secret key in the current settings, save it to .env, and log the event."""
        self.SECRET_KEY: str = self.generate_new_secret_key()
        self.save_secret_key_to_env()
        logging.info("Secret key updated successfully.")

    def save_secret_key_to_env(self) -> None:
        """Write the updated SECRET_KEY to the .env file."""
        try:
            lines: list = []
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
            logging.error("Failed to update .env with new SECRET_KEY", exc_info=True)
            raise


def pad_data(data: bytes) -> bytes:
    """Pad data to be a multiple of 16 bytes for AES encryption."""
    padder: PaddingContext = padding.PKCS7(algorithms.AES.block_size).padder()
    return padder.update(data) + padder.finalize()


def unpad_data(data: bytes) -> bytes:
    """Remove padding from data after AES decryption."""
    unpadder: PaddingContext = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(data) + unpadder.finalize()


try:
    settings_crypto = SettingsCrypto()
    SECRET_KEY: str = settings_crypto.SECRET_KEY
    logging.info("SettingsCrypto initialized successfully.")
except Exception as e:
    logging.error("Error initializing SettingsCrypto", exc_info=True)
    raise


def encode_data(data: str) -> Optional[bytes]:
    """Encrypt a string using AES encryption."""
    try:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = pad_data(data.encode('utf-8'))
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data
    except Exception as e:
        logging.error(f"Unexpected error during AES encryption", exc_info=True)
        return None


def decode_data(encrypted_data: bytes) -> Optional[str]:
    """Decrypt an AES-encrypted byte string."""
    try:
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        decrypted_data = unpad_data(decrypted_padded_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logging.error("Unexpected error during AES decryption", exc_info=True)
        return None



def dict_to_str(data: Optional[dict]) -> Optional[str]:
    """Converts a dictionary to a JSON string or returns None."""
    if data is None:
        return None
    return json.dumps(data)

def str_to_dict(data: Optional[str]) -> Optional[dict]:
    """Converts a JSON string back to a dictionary or returns None."""
    if data is None:
        return None
    try:
        return json.loads(data)[0]
    except json.JSONDecodeError:
        raise ValueError("Invalid format: Ensure the string is valid JSON.")

