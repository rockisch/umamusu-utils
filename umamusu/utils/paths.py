import shutil
from pathlib import Path


ROOT = Path(__file__, '../../..')
LOG_ROOT = Path(ROOT, 'logs')
STORAGE_ROOT = Path(ROOT, 'storage')

DATA_ROOT = Path(STORAGE_ROOT, 'data')
WIKI_CREATE_FILE = Path(STORAGE_ROOT, 'wiki/create.txt')
WIKI_UPDATE_ROOT = Path(STORAGE_ROOT, 'wiki/update')


def clean_storage():
    WIKI_CREATE_FILE.unlink(missing_ok=True)
    shutil.rmtree(WIKI_UPDATE_ROOT)
    WIKI_UPDATE_ROOT.mkdir(parents=True)
