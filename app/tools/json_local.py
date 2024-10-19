import json
import os
from dataclasses import field
from ..core.security import encode_data, decode_data


def import_json_is_crypto(file: str) -> dict:
    with open(file, 'r', encoding='utf-8') as file_:
        cash = json.load(file_)['cash']
        return decode_data(cash)


def create_to_json_is_crypto(namefile: str, data: dict) -> None:
    path = 'temp/{}'.format(namefile)
    with open(path,'r+',encoding='utf-8') as file_:
        data_new = {
            'cash': encode_data(data)
        }
        file_.write(json.dump(data_new,ensure_ascii=False,indent=4))

