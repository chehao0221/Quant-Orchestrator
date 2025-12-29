from pathlib import Path

def safe_delete(path: Path):
    try:
        if path.exists():
            path.unlink()
            print(f"[Vault] Deleted {path}")
    except Exception as e:
        print(f"[Vault] Delete failed {path}: {e}")
