from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")

NEVER_DELETE = {
    "LOCKED_RAW",
    "LOCKED_DECISION",
    "LOG",
}

def is_never_delete(path: Path) -> bool:
    return any(p in path.parts for p in NEVER_DELETE)
