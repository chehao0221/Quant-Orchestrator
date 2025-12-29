from pathlib import Path

VAULT_ROOT = Path(r"E:\Quant-Vault")

NEVER_DELETE = [
    "LOCKED_RAW",
    "LOCKED_DECISION",
    "LOG",
]

HOT_ZONES = [
    "STOCK_DB/TW/shortlist",
    "STOCK_DB/TW/core_watch",
    "STOCK_DB/US/shortlist",
    "STOCK_DB/US/core_watch",
]

COLD_ZONES = [
    "STOCK_DB/TW/universe",
    "STOCK_DB/TW/history",
    "STOCK_DB/TW/cache",
    "STOCK_DB/US/universe",
    "STOCK_DB/US/history",
    "STOCK_DB/US/cache",
]
