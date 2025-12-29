from pathlib import Path

def safe_delete(path: Path):
    if not path.exists():
        return

    if path.is_file():
        path.unlink()
