# 路徑：Quant-Orchestrator/vault/vault_backtest_reader.py

import os
import json
from datetime import datetime, timedelta

VAULT_PATH = r"E:\Quant-Vault\LOCKED_RAW\backtest"


def load_backtest_results(market: str, days: int = 30):
    results = []
    cutoff = datetime.now() - timedelta(days=days)

    market_path = os.path.join(VAULT_PATH, market)
    if not os.path.exists(market_path):
        return []

    for f in os.listdir(market_path):
        if not f.endswith(".json"):
            continue

        path = os.path.join(market_path, f)
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        ts = datetime.fromisoformat(data["date"])
        if ts < cutoff:
            continue

        if "hit" not in data:
            continue  # 尚未完成 Day5

        results.append(data)

    return results
