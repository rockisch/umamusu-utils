import aiohttp
import asyncio
import lz4.frame
from dataclasses import dataclass
from pathlib import Path
from typing import List

from utils import STORAGE_ROOT, get_meta_conn, get_storage_folder, get_logger

logger = get_logger(__name__)

LIMIT = 200
SKIP_EXISTING = True
ASYNC_DOWNLOAD = False

DATA_ROOT = get_storage_folder('data')
HOSTNAME = 'https://prd-storage-game-umamusume.akamaized.net/dl/resources/'
ASSETS_ENDPOINT = HOSTNAME + '/Android/assetbundles/{0:.2}/{0}'
GENERIC_ENDPOINT = HOSTNAME + '/Generic/{0:.2}/{0}'
MANIFEST_ENDPOINT = HOSTNAME + '/Manifest/{0:.2}/{0}'
BLOB_TABLE = 'a'
BLOB_TABLE_PATH = 'n'
BLOB_TABLE_HASH = 'h'
BLOB_TABLE_KIND = 'm'

@dataclass
class BlobRow:
    path: str
    hash: str
    kind: str

    def __str__(self):
        return self.path

def data_download():
    meta_conn = get_meta_conn()
    loop = asyncio.new_event_loop()
    total_blobs = next(meta_conn.execute(f'SELECT COUNT(*) FROM "{BLOB_TABLE}"'))['COUNT(*)']
    offset = 0
    while offset != total_blobs:
        blob_rows = []
        for row in meta_conn.execute(f'SELECT "{BLOB_TABLE_PATH}" as n, "{BLOB_TABLE_HASH}" as h, "{BLOB_TABLE_KIND}" as m FROM "{BLOB_TABLE}" LIMIT {LIMIT} OFFSET {offset}'):
            blob_row = BlobRow(path=row['n'], hash=row['h'], kind=row['m'])
            if blob_row.path.startswith('//'):
                blob_row.path = f'{blob_row.kind}/{blob_row.path[2:]}'
            blob_rows.append(blob_row)
        offset += len(blob_rows)
        logger.debug(f'downloading files: {offset}/{total_blobs}')
        loop.run_until_complete(save_blob_rows(blob_rows))

    meta_conn.close()
    master_path = Path(DATA_ROOT, 'master.mdb')
    if master_path.exists():
        master_path.rename(Path(STORAGE_ROOT, 'master.mdb'))

async def save_blob_rows(blob_rows: List[BlobRow]):
    async with aiohttp.ClientSession() as session:
        if ASYNC_DOWNLOAD:
            await asyncio.gather(*[save_blob_row(session, blob_row) for blob_row in blob_rows], return_exceptions=True)
        else:
            for blob_row in blob_rows:
                await save_blob_row(session, blob_row)

async def save_blob_row(session: aiohttp.ClientSession, blob_row: BlobRow):
    force = not SKIP_EXISTING
    if blob_row.kind == 'master':
        force = True
        endpoint = GENERIC_ENDPOINT
    elif blob_row.kind in ('sound', 'movie', 'font'):
        endpoint = GENERIC_ENDPOINT
    elif blob_row.kind.startswith('manifest'):
        endpoint = MANIFEST_ENDPOINT
    else:
        endpoint = ASSETS_ENDPOINT

    lz4_context = None
    if blob_row.path.endswith('.lz4'):
        lz4_context = lz4.frame.create_decompression_context()
        blob_row.path = blob_row.path[:-4]

    url = endpoint.format(blob_row.hash)
    path = Path(DATA_ROOT, blob_row.path)
    if not force and path.exists():
        return

    async with session.get(url) as resp:
        if resp.status == 403:
            logger.error(f'failed to download: {blob_row}')
            return

        logger.info(f'downloading new file: {blob_row}')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            while True:
                chunk = await resp.content.read(1024 * 4)
                if not chunk:
                    break
                if lz4_context:
                    chunk, b, e = lz4.frame.decompress_chunk(lz4_context, chunk)
                f.write(chunk)

if __name__ == '__main__':
    data_download()
