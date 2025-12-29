from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")

LOCKED_PATHS = [
    VAULT_ROOT / "LOCKED_RAW",
    VAULT_ROOT / "LOCKED_DECISION",
    VAULT_ROOT / "LOG",
]

TEMP_PATH = VAULT_ROOT / "TEMP_CACHE"

def is_path_deletable(path: Path) -> bool:
    path = path.resolve()

    for locked in LOCKED_PATHS:
        if locked in path.parents or path == locked:
            return False

    return TEMP_PATH in path.parents
