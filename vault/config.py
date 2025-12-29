import os

VAULT_ROOT = os.getenv("QUANT_VAULT", r"E:\Quant-Vault")

STOCK_DB = os.path.join(VAULT_ROOT, "STOCK_DB")

MARKETS = {
    "TW": {
        "root": os.path.join(STOCK_DB, "TW"),
    },
    "US": {
        "root": os.path.join(STOCK_DB, "US"),
    },
}

SUBDIRS = [
    "universe",
    "shortlist",
    "core_watch",
    "history",
    "cache",
]
