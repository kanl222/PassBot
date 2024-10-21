import logging
import os
import sys
from secrets import choice
from string import ascii_letters, digits
from typing import Optional

from jose import JWTError, jwt
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsCrypto(BaseSettings):
	SECRET_KEY: str = None
	ALGORITHM: str = 'SHA256'

	model_config = SettingsConfigDict(
		env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".config_crypto")
	)

	def generate_new_secret_key(self) -> str:
		"""
		Generate a new 64-character secret key composed of letters, digits, and special characters.

		:return: A newly generated secret key.
		"""
		secret_key = ascii_letters + digits + '-+)(*?><{}!@#$%^'
		return ''.join(choice(secret_key) for _ in range(64))

	def update_secret_key(self) -> None:
		"""
		Update the secret key in the current settings.

		"""
		self.SECRET_KEY = self.generate_new_secret_key()
		logging.info("Secret key updated successfully.")


try:
	settings_crypto = SettingsCrypto()
except Exception as e:
	logging.error(f"Error loading crypto settings: {e}")
	sys.exit(1)

SECRET_KEY = settings_crypto.SECRET_KEY
ALGORITHM = settings_crypto.ALGORITHM

if not SECRET_KEY:
	settings_crypto.update_secret_key()
	logging.info("A new secret key was generated and set.")
else:
	logging.info("Using the existing secret key.")


def encode_data(data: dict) -> Optional[str]:
	"""
	Encode a dictionary into a JWT token.

	:param data: The data to encode into the JWT.
	:return: The encoded JWT string, or None if an error occurs.
	"""
	try:
		return jwt.encode(data, key=SECRET_KEY, algorithm=ALGORITHM)
	except Exception as e:
		logging.error(f"Error encoding data into JWT: {e}")
		return None


def decode_data(token: str) -> Optional[dict]:
	"""
	Decode a JWT token back into a dictionary.

	:param token: The JWT token to decode.
	:return Optional[dict]: The decoded data, or None if an error occurs.
	"""
	try:
		return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
	except JWTError as e:
		logging.error(f"JWT decoding error: {e}")
		return None
