from pathlib import Path
import shutil
from datetime import datetime


def execute_delete(path: Path, meta: dict):
    """
    真正執行刪除（實際為安全搬移）
    """
    backup_dir = path.parent / "_deleted_backup"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.stem}_{timestamp}{path.suffix}"

    shutil.move(str(path), str(backup_path))
