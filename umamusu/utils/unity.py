from pathlib import Path

import UnityPy

from utils import AssetSaver
from utils.paths import STORAGE_ROOT


def get_unity_assets(path: str):
    path = Path(STORAGE_ROOT, 'data', path)
    env = UnityPy.load(path.as_posix())
    if not env.objects:
        raise FileNotFoundError(path)

    assets = []
    for obj in env.objects:
        if obj.type in ['Texture2D', 'Sprite']:
            data = obj.read()
            def save(dest):
                if not dest.name.endswith('.png'):
                    dest = dest.with_name(f'{dest.name}.png')
                data.image.save(dest)
            asset = AssetSaver(data.name, save)
            assets.append(asset)

    return assets
