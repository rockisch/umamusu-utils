import aiohttp
import asyncio
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from typing import List
from consts import root_file, root_folder

LIMIT = 200
SKIP_EXISTING = True
ASYNC_DOWNLOAD = False

DATA_ROOT = root_folder('data')
HOSTNAME = 'https://prd-storage-umamusume.akamaized.net/dl/resources/'
ASSETS_ENDPOINT = HOSTNAME + '/Android/assetbundles/{0:.2}/{0}'
GENERIC_ENDPOINT = HOSTNAME + '/Generic/{0:.2}/{0}'
MANIFEST_ENDPOINT = HOSTNAME + '/Manifest/{0:.2}/{0}'
FILE_TABLE = 'a'
FILE_TABLE_NAME = 'n'
FILE_TABLE_HASH = 'h'
FILE_TABLE_KIND = 'm'


@dataclass
class FileRow:
    name: str
    hash: str
    kind: str

    def __str__(self):
        return f'{self.name}/{self.hash}'


async def save_file_row(session, file_row: FileRow):
    force = False
    if file_row.kind in ('sound', 'movie', 'font', 'master'):
        url = GENERIC_ENDPOINT.format(file_row.hash)
        if file_row.kind == 'master':
            force = True

    elif file_row.kind.startswith('manifest'):
        url = MANIFEST_ENDPOINT.format(file_row.hash)
    else:
        url = ASSETS_ENDPOINT.format(file_row.hash)

    path = Path(DATA_ROOT, file_row.name)
    if not force and SKIP_EXISTING and path.exists():
        return

    async with session.get(url) as resp:
        if resp.status == 403:
            print(f'UNABLE TO DOWNLOAD "{file_row}"')
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            while True:
                chunk = await resp.content.read(1024 * 4)
                if not chunk:
                    break
                f.write(chunk)


async def main(file_rows: List[FileRow]):
    async with aiohttp.ClientSession() as session:
        if ASYNC_DOWNLOAD:
            await asyncio.gather(*[save_file_row(session, file_row) for file_row in file_rows], return_exceptions=True)
        else:
            for file_row in file_rows:
                await save_file_row(session, file_row)


loop = asyncio.get_event_loop()
meta_conn = sqlite3.connect(root_file('meta').absolute())
offset = 0
total_files = meta_conn.execute(f'SELECT COUNT(*) FROM "{FILE_TABLE}"').fetchone()[0]
while True:
    file_rows = []
    for row in meta_conn.execute(f'SELECT "{FILE_TABLE_NAME}", "{FILE_TABLE_HASH}", "{FILE_TABLE_KIND}" FROM "{FILE_TABLE}" LIMIT {LIMIT} OFFSET {offset}'):
        file_row = FileRow(*row)
        if file_row.name.startswith('//'):
            file_row.name = f'manifests/{file_row.name[2:]}'

        file_rows.append(file_row)

    if not file_rows:
        break

    offset += len(file_rows)
    print(f'DOWNLOADING {offset}/{total_files}')
    loop.run_until_complete(main(file_rows))
