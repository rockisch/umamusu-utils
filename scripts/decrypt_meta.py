import os
import shutil
import apsw
from utils import DB_KEY, DB_BASE_KEY, STORAGE_ROOT, _derive_decryption_key, get_logger
from pathlib import Path

def decrypt_meta():
    logger = get_logger(__name__)
    encrypted_path = Path(STORAGE_ROOT, "meta")
    decrypted_path = Path(STORAGE_ROOT, "meta_decrypted")

    if not encrypted_path.exists():
        raise FileNotFoundError(f"Encrypted meta not found at {encrypted_path}")

    logger.info("Encrypted meta found. Decrypting...")
    temp_decryption_path = Path(STORAGE_ROOT, "meta_temp_decryption")
    shutil.copy2(encrypted_path, temp_decryption_path)

    conn = None
    try:
        conn = apsw.Connection(str(temp_decryption_path))
        final_key = _derive_decryption_key(DB_KEY, DB_BASE_KEY)
        conn.pragma("cipher", "chacha20")
        conn.pragma("hexkey", final_key.hex())
        next(conn.cursor().execute("PRAGMA quick_check"))
        conn.pragma("rekey", "")
    except Exception as e:
        if temp_decryption_path.exists():
            os.remove(temp_decryption_path)
        raise RuntimeError(f"Failed to create decrypted meta: {e}")
    finally:
        if conn:
            conn.close()
    temp_decryption_path.rename(decrypted_path)
    print("Successfully created permanent decrypted meta.")

if __name__ == '__main__':
    decrypt_meta()
