from pathlib import Path
from datetime import datetime

def build_meta(path: Path) -> dict:
    stat = path.stat()

    return {
        "path": str(path),
        "last_access_days": (datetime.now().timestamp() - stat.st_atime) / 86400,
        "last_modify_days": (datetime.now().timestamp() - stat.st_mtime) / 86400,
        "size": stat.st_size,
    }
