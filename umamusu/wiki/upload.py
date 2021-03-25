from pathlib import Path

from utils import get_logger, merge_dicts
from utils.paths import WIKI_UPDATE_ROOT, WIKI_CREATE_FILE
from wiki import api
from wiki.pages import parse_page_source, encode_page_source, translate_references
from wiki.templates import Templates


logger = get_logger(__name__)


def upload():
    api_session = api.APISession()
    with WIKI_CREATE_FILE.open('w', encoding='utf8') as wiki_create_file:
        for kind_folder in WIKI_UPDATE_ROOT.iterdir():
            kind = Templates(kind_folder.name)
            bulk_page_ids = [int(f.name) for f in kind_folder.iterdir()]
            bulk_page_data = api_session.bulk_get_pages(kind, bulk_page_ids)

            for page_folder in kind_folder.iterdir():
                page_id = int(page_folder.name)
                page_data = bulk_page_data.get(page_id)
                if page_data:
                    # If the page already exists, we'll do some translation and upload it
                    upload_page_folder(api_session, kind, page_data, page_folder)
                else:
                    # Otherwise, dump it into a file
                    page_file, _ = get_page_folder_files(page_folder)
                    wiki_create_file.write(f'{kind.value}|{page_id}|{page_file.name}\n')


def get_page_folder_files(page_folder: Path):
    page_file = None
    page_assets = None
    # Each page folder has a page file with the jpname and a folder with assets
    for file in page_folder.iterdir():
        if file.name == 'assets':
            page_assets = file
        else:
            page_file = file

    return page_file, page_assets


def upload_page_folder(api_session: api.APISession, kind: Templates, page_data: dict, page_folder: Path):
    page_file, page_assets = get_page_folder_files(page_folder)

    remote_source = page_data['source']
    remote_source_data, before, after = parse_page_source(remote_source, kind)
    references = {'NAME': remote_source_data.get(kind.name_field)}

    with page_file.open(encoding='utf8') as f:
        local_source = f.read()

    local_source = translate_references(local_source, references)
    local_source_data, _, _ = parse_page_source(local_source, kind)

    new_source_data = merge_dicts(remote_source_data, local_source_data)
    if new_source_data != remote_source_data:
        new_source = encode_page_source(new_source_data, kind, before, after)
        api_session.update_page(page_data, new_source)

    page_assets = Path(page_folder, 'assets')
    for asset in page_assets.iterdir():
        asset_name = translate_references(asset.name, references)
        api_session.upload_asset(asset, asset_name)
