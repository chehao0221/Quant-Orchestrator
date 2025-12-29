import json
from pathlib import Path
from datetime import date

VAULT_DIR = Path(__file__).resolve().parents[1] / "vault_data"
VAULT_DIR.mkdir(exist_ok=True)


def record_explorer_hit(market: str, symbols: list[str]):
    path = VAULT_DIR / f"explorer_history_{market.lower()}.json"

    data = []
    if path.exists():
        data = json.loads(path.read_text())

    today = date.today().isoformat()
    for s in symbols:
        data.append({
            "date": today,
            "symbol": s
        })

    # Explorer 只保留 60 天
    data = data[-3000:]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
