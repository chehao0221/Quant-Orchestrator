import os
import zipfile
from datetime import datetime

ARCHIVE_ROOT = r"E:\Quant-Vault\LOCKED_RAW\archive"

def archive_file(file_path: str) -> str:
    os.makedirs(ARCHIVE_ROOT, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = os.path.basename(file_path)
    zip_name = f"{name}.{ts}.zip"
    zip_path = os.path.join(ARCHIVE_ROOT, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(file_path, arcname=name)

    return zip_path
