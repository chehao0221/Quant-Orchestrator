import json
from pathlib import Path
from vault.schema import VaultState

VAULT_FILE = Path("vault/state.json")

def load_ranked(market: str, importance: str | None = None, limit: int = 10):
    if not VAULT_FILE.exists():
        return []

    state: VaultState = json.loads(VAULT_FILE.read_text())
    stocks = [
        s for s in state["stocks"]
        if s["market"] == market and (importance is None or s["importance"] == importance)
    ]

    return sorted(
        stocks,
        key=lambda x: (x["decay_weight"], x["avg_pred_ret"]),
        reverse=True
    )[:limit]
