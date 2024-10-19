from secrets import choice
from string import ascii_letters, digits
from typing import Optional

from jose import JWTError, jwt

from .settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def encode_data(data: dict) -> str:
	"""
    Encode a dictionary into a JWT token.

    Args:
        data (dict): The data to encode into the JWT.

    Returns:
        str: Encoded JWT string.
    """
	new_data: dict = data.copy()
	return jwt.encode(new_data, key=SECRET_KEY, algorithm=ALGORITHM)


def decode_data(token: str) -> Optional[dict]:
	"""
    Decode a JWT token back into a dictionary.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[dict]: The decoded data if successful, None if an error occurs.
    """
	try:
		return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
	except JWTError as e:
		print(f"JWT decoding error: {e}")
		return None


def generate_new_secret_key() -> str:
	"""
    Generate a new 64-character secret key.

    Returns:
        str: A new secret key composed of letters, digits, and special characters.
    """
	secret_key = ascii_letters + digits + '-+)(*?><{}!@#$%^'
	return ''.join([choice(secret_key) for _ in range(64)])



def change_secret_key() -> None:
	"""
    Generate a new secret key and update the application's settings.
    """
	new_secret_key = generate_new_secret_key()
	settings.model_config.update('SECRET_KEY', new_secret_key)
