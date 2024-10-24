import json
import os
import logging
from functools import lru_cache

from ..core.security import decode_data, encode_data


@lru_cache
def import_json_is_crypto(file: str) -> dict:
	"""
	Read a JSON file and decode the 'cash' field.

	:param file: Path to the JSON file.
	:return: Decoded 'cash' data.
	:raises FileNotFoundError: If the specified file does not exist.
	:raises KeyError: If the 'cash' field is missing from the JSON data.
	"""
	try:
		with open(file, 'r', encoding='utf-8') as file_:
			data = json.load(file_)
			if 'cash' not in data:
				raise KeyError(f"'cash' field not found in {file}")
			decoded_data = decode_data(data['cash'])
			logging.info(f"Successfully imported and decoded data from {file}")
			return decoded_data
	except FileNotFoundError as e:
		logging.error(f"File not found: {file}")
		raise e
	except KeyError as e:
		logging.error(f"Key error: {e}")
		raise e
	except Exception as e:
		logging.error(f"Error importing JSON data from {file}: {e}", exc_info=True)
		raise


def create_to_json_is_crypto(namefile: str, data: dict, directory: str = '.temp') -> None:
	"""
	Create a JSON file with encoded 'cash' data.

	:param namefile: Name of the file to create.
	:param data: Data to encode and write to the JSON file.
	:param directory: Directory where the file will be saved.
	:raises OSError: If there is an issue creating directories or writing to the file.
	"""
	path = os.path.join(directory, namefile)
	os.makedirs(os.path.dirname(path), exist_ok=True)

	data_new = {
		'cash': encode_data(data)
	}

	try:
		with open(path, 'w', encoding='utf-8') as file_:
			json.dump(data_new, file_, ensure_ascii=False, indent=4)
			logging.info(f"Successfully created file {namefile} with encoded data at {path}")
	except OSError as e:
		logging.error(f"Error creating or writing to {path}: {e}", exc_info=True)
		raise e
