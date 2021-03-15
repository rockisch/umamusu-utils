import json
import UnityPy
from dataclasses import dataclass
from typing import Any, Callable, List
from pathlib import Path

from utils import AssetSaver
from utils.paths import STORAGE_ROOT, WIKI_UPDATE_ROOT
from wiki.templates import Templates
from wiki.pages import encode_page_source


class BaseDumper:
    @classmethod
    def _to_dict(cls, data):
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {'data': data}
        return vars(data)


class WikiDumper(BaseDumper):
    ROOT = WIKI_UPDATE_ROOT

    @classmethod
    def _to_dict(cls, data):
        data = super()._to_dict(data)
        for key, value in data.items():
            if hasattr(value, 'name'):
                value = f'{value.name}'
                data[key] = value

        return data

    @classmethod
    def dump_unnamed_page(cls, kind: Templates, id: str, name: str, data: Any, assets: List[AssetSaver]=[]):
        data = cls._to_dict(data)
        source = encode_page_source(data, kind)
        page_folder = Path(cls.ROOT, kind.value, id)
        page_folder.mkdir(parents=True, exist_ok=True)
        page_dest = Path(page_folder, name)
        with open(page_dest, 'w', encoding='utf8') as f:
            f.write(source)

        if assets:
            assets_folder = Path(page_folder, 'assets')
            assets_folder.mkdir(parents=True, exist_ok=True)
            for asset in assets:
                asset_dest = Path(assets_folder, asset.name)
                asset.save(asset_dest)
