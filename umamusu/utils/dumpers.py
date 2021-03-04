import json
import UnityPy
from dataclasses import dataclass
from typing import Any, Callable
from pathlib import Path

from utils import STORAGE_ROOT


@dataclass
class UnityAssetWrapper:
    name: str
    dest: Path
    save: Callable


class BaseDumper:
    @classmethod
    def _to_dict(cls, data):
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {'data': data}
        return vars(data)

    @classmethod
    def get_unity_assets(cls, path: str):
        path = Path(STORAGE_ROOT, 'data', path)
        env = UnityPy.load(path.as_posix())
        if not env.objects:
            raise FileNotFoundError(path)

        assets = []
        for obj in env.objects:
            if obj.type in ['Texture2D', 'Sprite']:
                data = obj.read()
                dest = Path(cls.ROOT, 'assets')
                def save(name):
                    path = Path(dest, name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    data.image.save(path)
                    return path

                asset = UnityAssetWrapper(path.name, dest, save)
                assets.append(asset)

        return assets


class WikiDumper(BaseDumper):
    ROOT = Path(STORAGE_ROOT, 'wiki')

    @classmethod
    def _to_dict(cls, data):
        data = super()._to_dict(data)
        for key, value in data.items():
            if isinstance(value, Path) and value.is_relative_to(Path(cls.ROOT, 'assets')):
                value = f'[[File:{value.name}]]'
                data[key] = value

        return data

    @classmethod
    def dump(cls, path: str, data: Any):
        data = cls._to_dict(data)
        dest = Path(cls.ROOT, 'pages', path + '.txt')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'w', encoding='utf8') as f:
            for key, value in data.items():
                f.write('{}={}\n'.format(str(key), str(value)))


class JsonDumper(BaseDumper):
    ROOT = Path(STORAGE_ROOT, 'extract')

    @classmethod
    def dump(cls, path: str, data: Any):
        data = cls._to_dict(data)
        with open(Path(cls.ROOT, path), 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False)
