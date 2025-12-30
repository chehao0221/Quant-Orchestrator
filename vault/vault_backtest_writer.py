import os
import json
from datetime import date
from writer import safe_write

VAULT_ROOT = r"E:\Quant-Vault"


def write_backtest_prediction(
    market: str,
    symbol: str,
    prediction: dict
) -> bool:
    """
    Day 0：寫入預測，用於 5 日後回測
    """
    today = date.today().isoformat()

    path = os.path.join(
        VAULT_ROOT,
        "LOCKED_RAW",
        "backtest",
        market,
        f"{symbol}_{today}.json"
    )

    return safe_write(path, json.dumps(prediction, ensure_ascii=False, indent=2))
