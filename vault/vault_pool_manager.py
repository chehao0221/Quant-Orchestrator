from pathlib import Path
import json
from collections import Counter

def update_core_watch(
    market_root: Path,
    history_days: int = 30,
    top_n: int = 5,
):
    history_dir = market_root / "history"
    if not history_dir.exists():
        return

    files = sorted(history_dir.glob("*.json"))[-history_days:]
    counter = Counter()

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for r in data:
                counter[r["symbol"]] += 1
        except Exception:
            continue

    # 長期前 N 名
    core = [s for s, _ in counter.most_common(top_n)]

    core_dir = market_root / "core_watch"
    core_dir.mkdir(parents=True, exist_ok=True)
    (core_dir / "latest.json").write_text(
        json.dumps({"symbols": core}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
