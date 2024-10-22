import logging
import os
from secrets import choice
from string import ascii_letters, digits
from typing import Optional
from pathlib import Path

from jose import JWTError, jwt
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsCrypto(BaseSettings):
	SECRET_KEY: str = ''
	ALGORITHM: str = 'SHA256'

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

	def load_env_file(self, env_file: str) -> None:
		"""
		Load environment variables from the specified file.

		:param env_file: Path to the environment file.
		"""
		try:
			self.model_config = SettingsConfigDict(env_file=env_file)
			logging.info(f"Environment file loaded from: {env_file}")
		except ValueError as e:
			logging.error(f"Error loading env file '{env_file}': {e}")
			raise


try:
	settings_crypto = SettingsCrypto()
	SECRET_KEY = settings_crypto.SECRET_KEY
	ALGORITHM = settings_crypto.ALGORITHM

	config_file_path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".config_crypto"

	if config_file_path.exists():
		settings_crypto.load_env_file(str(config_file_path))
	else:
		logging.warning(f"Config file not found at: {config_file_path}")

	if not SECRET_KEY:
		settings_crypto.update_secret_key()
		logging.info("A new secret key was generated and set.")
	else:
		logging.info("Using the existing secret key.")
except Exception as e:
	logging.error(f"Error loading crypto settings: {e}", exc_info=True)
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
