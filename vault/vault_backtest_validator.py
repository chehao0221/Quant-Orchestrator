from pathlib import Path
import json
from datetime import datetime, timedelta
import yfinance as yf

VAULT = Path("E:/Quant-Vault/LOCKED_RAW/backtest")
HORIZON = 5

def validate_market(market: str):
    target_date = (datetime.now() - timedelta(days=HORIZON)).strftime("%Y-%m-%d")
    path = VAULT / market / f"{target_date}.json"
    if not path.exists():
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for sym, r in data["symbols"].items():
        if r["hit"] is not None:
            continue

        ticker = yf.Ticker(sym)
        hist = ticker.history(period="1d")
        if hist.empty:
            continue

        close = float(hist["Close"].iloc[-1])
        actual_ret = close / r["pred_price"] - 1
        hit = (actual_ret > 0) == (r["pred_ret"] > 0)

        r["actual_price"] = round(close, 2)
        r["actual_ret"] = round(actual_ret, 4)
        r["hit"] = hit
        changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
