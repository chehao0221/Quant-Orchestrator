import json
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parents[1] / "vault_data"


def read_recent_backtest(market: str, days: int = 5):
    path = VAULT_DIR / f"backtest_{market.lower()}.json"
    if not path.exists():
        return []

    data = json.loads(path.read_text())
    return data[-days:]
