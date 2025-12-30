# 路徑：Quant-Orchestrator/vault/vault_ai_judge.py

import json
import os

WEIGHT_PATH = r"E:\Quant-Vault\LOCKED_DECISION\risk_policy\ai_weights.json"
MAX_SHIFT = 0.1  # 防止一次學歪


def update_ai_weights(market: str, summary: dict):
    os.makedirs(os.path.dirname(WEIGHT_PATH), exist_ok=True)

    if os.path.exists(WEIGHT_PATH):
        with open(WEIGHT_PATH, "r", encoding="utf-8") as f:
            weights = json.load(f)
    else:
        weights = {}

    weights.setdefault(market, {})

    for ind, stat in summary["by_indicator"].items():
        total = stat["hit"] + stat["miss"]
        if total == 0:
            continue

        score = (stat["hit"] - stat["miss"]) / total
        shift = max(min(score * 0.05, MAX_SHIFT), -MAX_SHIFT)

        old = weights[market].get(ind, 1.0)
        weights[market][ind] = round(max(old + shift, 0.1), 3)

    with open(WEIGHT_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)
