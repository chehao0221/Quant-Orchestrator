import json
from pathlib import Path
from datetime import datetime
from vault.schema import VaultBacktestRecord

VAULT_ROOT = Path("E:/Quant-Vault/STOCK_DB")

def write_backtest(record: VaultBacktestRecord):
    path = (
        VAULT_ROOT
        / record.market
        / "history"
        / f"{record.symbol}.json"
    )

    path.parent.mkdir(parents=True, exist_ok=True)

    data = []
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))

    data.append(record.__dict__)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
