from pathlib import Path
import json
from datetime import datetime

VAULT = Path("E:/Quant-Vault/LOCKED_RAW/backtest")

def write_prediction(market: str, horizon: int, records: dict):
    """
    records:
    {
      "2330.TW": {
          "price": 1530.0,
          "pred": 0.0134
      }
    }
    """
    today = datetime.now().strftime("%Y-%m-%d")
    out_dir = VAULT / market
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{today}.json"
    if path.exists():
        return  # ❌ 不可覆寫

    payload = {
        "date": today,
        "market": market,
        "horizon": horizon,
        "symbols": {}
    }

    for sym, r in records.items():
        payload["symbols"][sym] = {
            "pred_date": today,
            "pred_price": r["price"],
            "pred_ret": round(r["pred"], 4),
            "actual_price": None,
            "actual_ret": None,
            "hit": None,
        }

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
