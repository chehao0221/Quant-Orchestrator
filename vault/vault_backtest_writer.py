from pathlib import Path
import json
from datetime import datetime

VAULT_ROOT = Path("E:/Quant-Vault/LOCKED_RAW/backtest")

def write_daily_prediction(
    market: str,
    horizon: int,
    predictions: dict,
    prices: dict
):
    """
    predictions: { symbol: pred_ret }
    prices: { symbol: close_price }
    """

    today = datetime.now().strftime("%Y-%m-%d")
    market_dir = VAULT_ROOT / market
    market_dir.mkdir(parents=True, exist_ok=True)

    path = market_dir / f"{today}.json"
    if path.exists():
        return  # ❌ 不可覆寫

    payload = {
        "date": today,
        "market": market,
        "horizon": horizon,
        "symbols": {}
    }

    for sym, pred in predictions.items():
        payload["symbols"][sym] = {
            "pred_date": today,
            "pred_price": prices.get(sym),
            "pred_ret": round(pred, 4),
            "actual_price": None,
            "actual_ret": None,
            "hit": None
        }

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
