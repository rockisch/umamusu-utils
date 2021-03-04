import json
import logging
import aiohttp
from pathlib import Path

from utils.utils import get_storage_folder, chunk_iter, get_logger


logger = get_logger(__file__)


ENDPOINT = ''
USERNAME = ''
PASSWORD = ''
try:
    with open('secret.json') as f:
        secret = json.load(f)
    ENDPOINT = secret['endpoint']
    USERNAME = secret['username']
    PASSWORD = secret['password']
except:
    pass

API_ENDPOINT = ENDPOINT + '/api.php'
REST_ENDPOINT = ENDPOINT + '/rest.php'

PAGES_ROOT = get_storage_folder('wiki/pages')
ASSETS_ROOT = get_storage_folder('wiki/assets')


async def session_auth(session: aiohttp.ClientSession):
    # Get Token
    async with session.get(API_ENDPOINT, params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json',
    }) as resp:
        data = await resp.json()

    login_token = data['query']['tokens']['logintoken']

    # Session Auth
    async with session.post(API_ENDPOINT, data={
        'action': 'login',
        'lgname': USERNAME,
        'lgpassword': PASSWORD,
        'lgtoken': login_token,
        'format': 'json',
    }) as resp:
        data = await resp.json()

    if data['login']['result'] == 'Failed':
        raise Exception(data['login']['reason'])


async def get_csrf_token(session: aiohttp.ClientSession):
    async with session.get(API_ENDPOINT, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json',
    }) as resp:
        data = await resp.json()

    csrf_token = data['query']['tokens']['csrftoken']
    return csrf_token


async def upload_files():
    async with aiohttp.ClientSession() as session:
        await session_auth(session)
        for child in assets_iter(ASSETS_ROOT):
            print(child)
            await upload_asset_file(child, session)
            break


def assets_iter(folder):
    for child in folder.iterdir():
        if child.is_dir():
            logger.warning('directory in assets, something is wrong')
        else:
            yield child


async def upload_asset_file(file: Path, session: aiohttp.ClientSession):
    csrf_token = await get_csrf_token(session)
    params = {
        'action': 'upload',
        'filename': file.name,
        'token': csrf_token,
        'format': 'json',
    }
    filesize = file.stat().st_size
    # For bigger files, we can do a chunked upload
    if filesize < 1_024_000:
        params['file'] = file.open('rb')
        async with session.post(API_ENDPOINT, data=params) as resp:
            data = await resp.json()

        print('UPLOAD', data)
    else:
        chunks = chunk_iter(file)
        chunk = next(chunks)
        chunk_data = {'chunk': ('0' + file.suffix, chunk, 'multipart/form-data')}
        async with session.post(API_ENDPOINT, params={
            **params,
            'stash': 1,
            'filesize': filesize,
            'offset': 0,
        }, data=chunk_data) as resp:
            data = await resp.json()

        for i, chunk in enumerate(chunks):
            filekey = data['upload']['filekey']
            offset = data['upload']['offset']
            chunk_data = {'chunk': (i + file.suffix, chunk, 'multipart/form-data')}
            async with session.post(API_ENDPOINT, params={
                **params,
                'stash': 1,
                'filesize': filesize,
                'filekey': filekey,
                'offset': offset,
            }, data=chunk_data) as resp:
                data = await resp.json()

        async with session.post(API_ENDPOINT, params={
            **params,
            'filekey': filekey,
        }) as resp:
            data = await resp.json()
