import json
import os

from ..core.security import decode_data, encode_data, dict_to_str, str_to_dict


def import_json_is_crypto(file: str) -> dict:
    """
    Read a JSON file and decode the 'cash' field.

    :param file: Path to the JSON file.
    :return: Decoded 'cash' data as a dictionary.
    """
    path = os.path.join('.temp', file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' not found.")

    with open(path, 'r', encoding='utf-8') as file_:
        try:
            cash: bytes = bytes(json.load(file_)['cash'])
            return str_to_dict(decode_data(cash))
        except KeyError:
            raise ValueError(f"'cash' field not found in the file '{path}'.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON file '{path}': {e}")


def create_to_json_is_crypto(namefile: str, data: dict) -> None:
    """
    Create a JSON file with encoded data.

    :param namefile: Name of the file to create (without extension).
    :param data: Data to encode and write to the JSON file.
    """
    path = os.path.join('.temp', f'{namefile}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data_new = {
        'cash': encode_data(dict_to_str(data))
    }

    with open(path, 'w', encoding='utf-8') as file_:
        json.dump(data_new, file_, ensure_ascii=False, indent=4)

    print(f"File '{path}' created successfully.")
