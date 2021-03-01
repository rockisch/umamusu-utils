from pathlib import Path


ROOT = Path(__file__).parent.parent


def root_folder(path: str):
    folder = Path(ROOT, path)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def root_file(path: str):
    file = Path(ROOT, path)
    if not file.exists():
        raise Exception(f'file "{file}" does not exist at root')

    return file
