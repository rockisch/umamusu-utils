import logging
import apsw
from pathlib import Path
import struct

def dict_factory(cursor, row):
    description = [d[0] for d in cursor.get_description()]
    return {key: value for key, value in zip(description, row)}

DB_BASE_KEY = b'\xF1\x70\xCE\xA4\xDF\xCE\xA3\xE1\xA5\xD8\xC7\x0B\xD1\x00\x00\x00'
DB_KEY = b'\x6D\x5B\x65\x33\x63\x36\x63\x25\x54\x71\x2D\x73\x50\x53\x63\x38\x6D\x34\x37\x7B\x35\x63\x70\x23\x37\x34\x53\x29\x73\x43\x36\x33'
AB_KEY = b'\x53\x2B\x46\x31\xE4\xA7\xB9\x47\x3E\x7C\xFB'

def _derive_decryption_key(key, base_key):
    key = bytearray(key)
    if len(base_key) < 13:
        raise ValueError("Invalid Base Key length.")
    for i in range(len(key)):
        key[i] ^= base_key[i % 13]
    return bytes(key)

def _derive_asset_key(key_long):
    if key_long == 0:
        return None
    key_bytes = struct.pack('<q', key_long)
    base_key = AB_KEY
    base_len = len(base_key)
    final_key = bytearray(base_len * 8)

    for i in range(base_len):
        b = base_key[i]
        base_offset = i * 8
        for j in range(8):
            final_key[base_offset + j] = b ^ key_bytes[j]
    return bytes(final_key)

ROOT = Path(__file__).resolve().parent.parent
LOG_ROOT = Path(ROOT, 'logs')
STORAGE_ROOT = Path(ROOT, 'storage')

_girls = None
def get_girls_dict():
    global _girls
    if _girls:
        return _girls

    girls = {}
    master_conn = get_master_conn()
    try:
        for row in master_conn.execute('SELECT "index", "text" FROM "text_data" WHERE "category" = 6'):
            girls[row['index']] = row['text']
    finally:
        master_conn.close()

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

def get_storage_folder(folder: str):
    path = Path(STORAGE_ROOT, folder)
    path.mkdir(exist_ok=True)
    return path

def get_meta_conn():
    conn = apsw.Connection(str(Path(STORAGE_ROOT, 'meta')))
    conn.row_trace = dict_factory

    final_key = _derive_decryption_key(DB_KEY, DB_BASE_KEY)

    conn.pragma("cipher", "chacha20")
    conn.pragma("hexkey", final_key.hex())
    return conn

def get_master_conn():
    conn = apsw.Connection(str(Path(STORAGE_ROOT, 'master.mdb')))
    conn.row_trace = dict_factory
    return conn
