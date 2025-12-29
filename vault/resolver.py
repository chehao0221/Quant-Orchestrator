import os
from .config import MARKETS, SUBDIRS

def ensure_market(market: str):
    root = MARKETS[market]["root"]
    for d in SUBDIRS:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    return root

def path(market: str, category: str, filename: str):
    root = ensure_market(market)
    return os.path.join(root, category, filename)
