import os
import shutil
from pathlib import Path

from utils import get_meta_conn, get_storage_folder, get_logger, _derive_asset_key

logger = get_logger(__name__)
SKIP_EXISTING = True
HPATHS = False

if HPATHS:
    DATA_ROOT = get_storage_folder("dat")
else:
    DATA_ROOT = get_storage_folder("data")

DECRYPTED_DATA_ROOT = get_storage_folder("data_decrypted")
BLOB_TABLE = "a"

# If this is NOT empty, ONLY assets within these folders will be decrypted.
# If this IS empty, ALL assets will be processed (with exclusions).
# Example:
# INCLUDED_FOLDERS = set()
# INCLUDED_FOLDERS = {"sound/v/", "story/data/"}
INCLUDED_FOLDERS = {"story/data/"}

# Any asset from these folders will be explicitly SKIPPED.
# This is useful for ignoring entire categories of files.
# Example:
# EXCLUDED_FOLDERS = {"font/"}
# EXCLUDED_FOLDERS = {"font/", "movie/"}
EXCLUDED_FOLDERS = set()

def decrypt_assets():
    logger.info("Starting asset decryption process...")
    meta_conn = None
    try:
        meta_conn = get_meta_conn()
        query = f'SELECT "n", "h", "e" FROM "{BLOB_TABLE}"'
        all_assets = list(meta_conn.execute(query))
        total_assets = len(all_assets)
        logger.info(f"Found {total_assets} assets from meta.")

        for i, row in enumerate(all_assets):
            db_asset_name = row["n"]
            asset_hash = row["h"]
            asset_key = row["e"]

            if any(db_asset_name.startswith(folder) for folder in EXCLUDED_FOLDERS):
                logger.info(f"Skipping file in excluded folder: {db_asset_name}...")
                continue
            if INCLUDED_FOLDERS and not any(db_asset_name.startswith(folder) for folder in INCLUDED_FOLDERS):
                continue

            if HPATHS:
                source_path = Path(DATA_ROOT, asset_hash[:2].upper(), asset_hash)
                dest_path = Path(DECRYPTED_DATA_ROOT, asset_hash[:2].upper(), asset_hash)
            else:
                source_path = Path(DATA_ROOT, db_asset_name)
                dest_path = Path(DECRYPTED_DATA_ROOT, db_asset_name)

            if not source_path.exists():
                logger.warning(f"Source file not found, skipping: {source_path}...")
                continue
            if SKIP_EXISTING and dest_path.exists() and dest_path.stat().st_size > 0:
                continue
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if asset_key == 0:
                logger.info(f"Skipping unencrypted file: {db_asset_name}...")
                # shutil.copy2(source_path, dest_path)
                continue

            try:
                decryption_key = _derive_asset_key(asset_key)
                with open(source_path, "rb") as f_in:
                    data = bytearray(f_in.read())

                if decryption_key and len(data) > 256:
                    key_len = len(decryption_key)
                    for j in range(256, len(data)):
                        data[j] ^= decryption_key[j % key_len]
                with open(dest_path, "wb") as f_out:
                    f_out.write(data)
                logger.info(f"Successfully decrypted: {db_asset_name}")
            except Exception as e:
                logger.error(f"Failed to process {db_asset_name}: {e}")
    except Exception as e:
        logger.error(f"A fatal error occurred: {e}")
    finally:
        if meta_conn:
            meta_conn.close()
            logger.info("Database connection closed.")
    logger.info("Asset decryption process complete.")

if __name__ == "__main__":
    decrypt_assets()