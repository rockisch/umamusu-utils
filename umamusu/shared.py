import enum
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


@dataclass
class State:
    version: str
    meta_path: Path
    master_path: Path
    appdata_path: Path
    storage_path: Path
    log_path: Path | None


state = State(*[None] * 6)

# DB-related
_master_conn: sqlite3.Connection = None
_meta_conn: sqlite3.Connection = None


@contextmanager
def _db_cursor(conn: sqlite3.Connection):
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def master_cursor():
    global _master_conn

    if _master_conn is None:
        _master_path = state.master_path
        if not _master_path.exists():
            _master_path = state.appdata_path / "master/master.mdb"
        if not _master_path.exists():
            raise Exception("master DB path does not exist: {}", _master_path)

        _master_conn = sqlite3.connect(_master_path)

    return _db_cursor(_master_conn)


def meta_cursor():
    global _meta_conn
    if _meta_conn is None:
        _meta_path = state.meta_path
        if not _meta_path.exists():
            _meta_path = state.appdata_path / "meta"
        if not _meta_path.exists():
            raise Exception("meta DB path does not exist: {}", _meta_path)

        _meta_conn = sqlite3.connect(_meta_path)

    return _db_cursor(_meta_conn)


# Logging
class Status(enum.Enum):
    OK = enum.auto()
    ERR = enum.auto()


class CustomAdapter(logging.LoggerAdapter):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def process(self, msg, kwargs):
        if status := kwargs.pop("status", None):
            if status == Status.OK:
                return f"{self.OKGREEN}{msg}{self.ENDC}", kwargs
            elif status == Status.ERR:
                return f"{self.FAIL}{msg}{self.ENDC}", kwargs

        return msg, kwargs


def get_logger(name: str):
    logger = logging.getLogger(name)
    if state.log_path is None:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
    else:
        logger.setLevel(logging.INFO)
        state.log_path.mkdir(exist_ok=True)
        handler = logging.FileHandler(
            filename=Path(state.log_path, f"{name}.log"), mode="w+", encoding="utf8"
        )

    logger.addHandler(handler)
    logger = CustomAdapter(logger, {})
    return logger


class AppDataException(Exception):
    def __init__(self):
        super().__init__("Unable to find AppData folder")
