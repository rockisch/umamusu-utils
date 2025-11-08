import shutil
from pathlib import Path

from ..shared import Status, state
from . import logger


def extract_supportcard(args, dump_path: Path):
    result: list[tuple[Path, Path]] = []

    supportcard_path = dump_path / "supportcard"
    for folder_path in supportcard_path.iterdir():
        for path_p in folder_path.iterdir():
            if path_p.name.startswith("support_card_s"):
                for path in path_p.iterdir():
                    result.append((path, Path(path.name)))

    return "supportcard", result


def extract_skills(args, dump_path: Path):
    result: list[tuple[Path, Path]] = []

    supportcard_path = dump_path / "outgame/skillicon"
    for folder_path in supportcard_path.iterdir():
        for path in folder_path.iterdir():
            result.append((path, Path(path.name)))

    return "skill", result


HANDLERS = {
    "supportcard": extract_supportcard,
    "skill": extract_skills,
}


def assets_extract(args):
    if not state.storage_path.exists():
        logger.error(f"storage folder does not exist: {state.storage_path}")
        return

    kinds = args.kind
    if not kinds:
        kinds = list(HANDLERS.keys())

    data_dump_path = state.storage_path / "dump"
    if not data_dump_path.exists():
        logger.error(
            "assets folder does not exist, make sure you run 'assets extract' before running 'assets assets'"
        )
        return

    data_path = state.storage_path / "assets"
    data_path.mkdir(exist_ok=True)
    for kind in kinds:
        handler = HANDLERS.get(kind)
        if not handler:
            logger.error(f"invalid kind: {kind}")
            continue

        data_foldername, data_paths = handler(args, data_dump_path)
        data_folder = data_path / data_foldername
        for src, dst_path in data_paths:
            dst = data_folder / dst_path
            dst.parent.mkdir(exist_ok=True)
            shutil.copyfile(src, dst)

        logger.info(f"Extracted '{kind}' assets to '{data_folder}'", status=Status.OK)
