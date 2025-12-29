import json
from datetime import datetime
from .resolver import path

def write_universe(market: str, symbols: list):
    p = path(market, "universe", f"{datetime.now():%Y-%m-%d}.json")
    json.dump({"symbols": symbols}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def write_shortlist(market: str, top5: list):
    p = path(market, "shortlist", f"{datetime.now():%Y-%m-%d}.json")
    json.dump({"top5": top5}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def write_history(market: str, records: list):
    p = path(market, "history", f"{datetime.now():%Y-%m-%d}.json")
    json.dump(records, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
