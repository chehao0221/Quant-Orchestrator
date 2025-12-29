from pathlib import Path
import json
from datetime import datetime
from vault.schema import REQUIRED_FIELDS

def write_snapshot(
    market_root: Path,
    records: list[dict]
):
    date_str = datetime.now().strftime("%Y-%m-%d")
    history_dir = market_root / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    out_file = history_dir / f"{date_str}.json"

    cleaned = []
    for r in records:
        if not all(k in r for k in REQUIRED_FIELDS):
            continue
        cleaned.append(r)

    if not cleaned:
        return

    out_file.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
