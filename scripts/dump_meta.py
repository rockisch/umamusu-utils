import json
from pathlib import Path
from utils import STORAGE_ROOT, get_meta_conn, get_logger

def dump_meta():
    logger = get_logger(__name__)
    meta_conn = None
    output = Path(STORAGE_ROOT, "meta_dump.json")

    try:
        meta_conn = get_meta_conn()
        query = "SELECT n, m, h, e FROM a"
        cursor = meta_conn.cursor()
        rows = list(cursor.execute(query))
        with open(output, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully dumped {len(rows)} rows to '{output}'.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if meta_conn:
            meta_conn.close()

if __name__ == "__main__":
    dump_meta()
