import os, json, time
from datetime import datetime, timedelta
from .resolver import ensure_market

N_DAYS = 180
K_TOP5 = 30

def is_cold(file_path):
    last_access = datetime.fromtimestamp(os.path.getatime(file_path))
    return datetime.now() - last_access > timedelta(days=N_DAYS)

def clean_market(market: str, protect_symbols: set):
    root = ensure_market(market)
    for cat in ["history", "cache"]:
        d = os.path.join(root, cat)
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if not is_cold(fp):
                continue
            try:
                data = json.load(open(fp))
                symbols = set(data.get("symbols", []))
                if symbols & protect_symbols:
                    continue
                os.remove(fp)
            except Exception:
                continue
