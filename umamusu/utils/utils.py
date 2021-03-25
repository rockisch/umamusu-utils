import json
import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from utils.paths import ROOT, LOG_ROOT, STORAGE_ROOT


META_DB_PATH = Path(STORAGE_ROOT, 'meta')
MASTER_DB_PATH = Path(STORAGE_ROOT, 'master.mdb')


@dataclass
class AssetSaver:
    name: str
    image: Image
    save: Callable


def merge_dicts(d1, d2, skip=[]):
    d = d1.copy()
    for key, value in d2.items():
        if value and not (key in skip and d.get(key)):
            d[key] = value

    return d


def data_to_dict(data: Any) -> dict:
    if isinstance(data, list):
        data = {'data': data}
    elif not isinstance(data, dict):
        data = vars(data)

    for key, value in data.items():
        if hasattr(value, 'name'):
            value = f'{value.name}'
            data[key] = value

    return data


_girls = None
def get_girls_dict():
    global _girls
    if _girls:
        return _girls

    girls = {}
    with get_master_conn() as master_conn:
        for index, text in master_conn.execute('SELECT "index", "text" FROM "text_data" WHERE "category" = 6'):
            girls[index] = text

    _girls = girls
    return _girls


def get_logger(name: str):
    logger = logging.getLogger(name)
    if name == '__main__':
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s\t%(message)s'))
    else:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=Path(LOG_ROOT, f'{name}.log'), mode='w+', encoding='utf8')

    logger.addHandler(handler)
    return logger


def get_meta_conn():
    return sqlite3.connect(META_DB_PATH)


def get_master_conn():
    return sqlite3.connect(MASTER_DB_PATH)


def get_secret_file():
    with Path(ROOT, 'secret.json').open(encoding='utf8') as s:
        return json.load(s)


def chunk_iter(file, chunk_size=4096):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data
