import json
import os
from ..core.security import decode_data, encode_data


def import_json_is_crypto(file: str) -> dict:
    """
    Read a JSON file and decode the 'cash' field.

    :param file: Path to the JSON file.
    :return: Decoded 'cash' data.
    """
    path = os.path.join('.temp', f'{file}')
    with open(path, 'r', encoding='utf-8') as file_:
        cash = json.load(file_)['cash']
        return decode_data(cash)


def create_to_json_is_crypto(namefile: str, data: dict) -> None:
    """
    Create a JSON file with encoded data.

    :param namefile: Name of the file to create.
    :param data: Data to encode and write to the JSON file.
    """
    path = os.path.join('.temp', f'{namefile}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data_new = {
        'cash': encode_data(data)
    }

    with open(path, 'w', encoding='utf-8') as file_:
        json.dump(data_new, file_, ensure_ascii=False, indent=4)
