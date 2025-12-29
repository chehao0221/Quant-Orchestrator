import json
from pathlib import Path
from datetime import date
from .schema import BacktestRecord

VAULT_DIR = Path(__file__).resolve().parents[1] / "vault_data"
VAULT_DIR.mkdir(exist_ok=True)


def write_backtest(market: str, records: list[BacktestRecord]):
    path = VAULT_DIR / f"backtest_{market.lower()}.json"

    existing = []
    if path.exists():
        existing = json.loads(path.read_text())

    existing.extend(records)

    # 只保留最近 30 筆（夠你 rolling）
    existing = existing[-30:]

    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
