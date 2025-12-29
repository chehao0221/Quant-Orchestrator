# Quant-Orchestrator/tools/vault_policy.py
from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")
STOCK_DB = VAULT_ROOT / "STOCK_DB"

# 嚴格保護（幾乎不刪）
PROTECTED_DIRS = [
    "shortlist",
    "core_watch",
]

# 可刪（冷資料）
COLD_DIRS = [
    "universe",
    "history",
    "cache",
]

def classify_stock_path(path: Path):
    """
    回傳:
    - protected
    - cold
    - ignore
    """
    parts = path.parts
    for p in PROTECTED_DIRS:
        if p in parts:
            return "protected"
    for c in COLD_DIRS:
        if c in parts:
            return "cold"
    return "ignore"
