from .extract_items import extract_items
from .extract_character import extract_character
from .upload import upload


def extract_data():
    # extract_items()
    extract_character()


__all__ = ['upload', 'extract_data']
