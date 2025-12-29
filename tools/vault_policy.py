from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")

NEVER_DELETE = [
    VAULT_ROOT / "LOCKED_RAW",
    VAULT_ROOT / "LOCKED_DECISION",
    VAULT_ROOT / "LOG",
]

def is_under(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False

def is_never_delete(path: Path) -> bool:
    return any(is_under(path, p) for p in NEVER_DELETE)
