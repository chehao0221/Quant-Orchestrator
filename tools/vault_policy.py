from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")

LOCKED_PATHS = [
    VAULT_ROOT / "LOCKED_RAW",
    VAULT_ROOT / "LOCKED_DECISION",
    VAULT_ROOT / "LOG",
]

STOCK_DB = VAULT_ROOT / "STOCK_DB"

PROTECTED_ZONES = [
    STOCK_DB / "TW/shortlist",
    STOCK_DB / "TW/core_watch",
    STOCK_DB / "US/shortlist",
    STOCK_DB / "US/core_watch",
]

DELETABLE_ZONES = [
    STOCK_DB / "TW/universe",
    STOCK_DB / "TW/history",
    STOCK_DB / "TW/cache",
    STOCK_DB / "US/universe",
    STOCK_DB / "US/history",
    STOCK_DB / "US/cache",
]

def is_deletable_path(path: Path) -> bool:
    path = path.resolve()

    for locked in LOCKED_PATHS:
        if locked in path.parents:
            return False

    for protected in PROTECTED_ZONES:
        if protected in path.parents:
            return False

    return any(zone in path.parents for zone in DELETABLE_ZONES)
