from .items_extract import items_extract
from .upload import upload


def extract_data():
    items_extract()


__all__ = ['upload', 'extract_data']
