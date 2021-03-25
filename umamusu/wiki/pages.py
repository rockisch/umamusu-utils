from pathlib import Path
import re
from typing import Any, List
from utils import AssetSaver, data_to_dict
from utils.paths import WIKI_UPDATE_ROOT

from wiki.templates import Templates


RE_PAGE = r'^(?P<before>^.*){{%s\n(?P<data>.*)\n}}(?P<after>.*)$'


def translate_references(text: str, references: dict):
    if 'NAME' in references:
        references['ASSET_NAME'] = '_'.join(references['NAME'].split(' '))

    for key, value in references.items():
        text = text.replace(f'${key}', value)

    return text


def dump_page_file(data: Any, name: str, kind: Templates, id: str, assets: List[AssetSaver]=None):
    data = data_to_dict(data)
    source = encode_page_source(data, kind)

    page_folder = Path(WIKI_UPDATE_ROOT, kind.value, str(id))
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


def parse_page_source(source: str, kind: Templates):
    match = re.match(RE_PAGE % kind.value, source, re.DOTALL)
    if not match:
        raise Exception()

    source_data = match['data']
    lines = source_data.split('\n')
    data = {}
    for line in lines:
        key, value = line.split('=', 1)
        # Remove the '|' character
        key = key[1:]
        data[key] = value

    return data, match['before'], match['after']


def encode_page_source(data: dict, kind: Templates, before: str='', after: str=''):
    if not before and kind.before:
        before = kind.before

    source_data = '\n'.join([
        f'|{k}={str(data[k]) if data.get(k) is not None else ""}' for k in kind.fields
    ])
    texts = filter(None, [before, '{{%s' % kind.value, source_data, '}}', after])
    return '\n'.join(texts)
