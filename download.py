import aiohttp
import asyncio
import sqlite3
from dataclasses import dataclass
from pathlib import Path

LIMIT = 200
SKIP_EXISTING = False

ROOT = Path(__file__).with_name('data')
ROOT.mkdir(parents=True, exist_ok=True)
ASSETS_ENDPOINT = 'https://prd-storage-umamusume.akamaized.net/dl/resources/Android/assetbundles/{0:.2}/{0}'
FILE_TABLE = 'a'
FILE_TABLE_NAME = 'n'
FILE_TABLE_HASH = 'h'


@dataclass
class FileRow:
    name: str
    hash: str


async def save_file_row(session, file_row: FileRow):
    url = ASSETS_ENDPOINT.format(file_row.hash)
    path = Path(ROOT, file_row.name)
    if SKIP_EXISTING and path.exists():
        return

    async with session.get(url) as resp:
        if resp.status == 403:
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            while True:
                chunk = await resp.content.read(1024 * 4)
                if not chunk:
                    break
                f.write(chunk)


async def main(file_rows: list[FileRow]):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[save_file_row(session, file_row) for file_row in file_rows], return_exceptions=True)


loop = asyncio.get_event_loop()
meta_conn = sqlite3.connect('meta')
offset = 0
total = meta_conn.execute(f'SELECT COUNT(*) FROM "{FILE_TABLE}"')
while True:
    file_rows = []
    for row in meta_conn.execute(f'SELECT "{FILE_TABLE_NAME}", "{FILE_TABLE_HASH}" FROM "{FILE_TABLE}" LIMIT {LIMIT} OFFSET {offset}'):
        file_row = FileRow(*row)
        if file_row.name.startswith('//'):
            file_row.name = f'manifests/{file_row.name[2:]}'

        file_rows.append(file_row)

    if not file_rows:
        break

    loop.run_until_complete(main(file_rows))
    offset += len(file_rows)
    if offset % 1000:
        print('DOWLOAD PROGRESS:', offset)
