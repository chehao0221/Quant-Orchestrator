import json
import pandas as pd
from pathlib import Path
from typing import List
from .schema import BacktestRecord
from datetime import datetime

def read_csv(path: Path, market: str) -> List[BacktestRecord]:
    if not path.exists():
        return []

    df = pd.read_csv(path)
    records = []

    for _, r in df.iterrows():
        records.append(
            BacktestRecord(
                symbol=r["symbol"],
                market=market,
                date=r["date"],
                horizon=int(r.get("horizon", 5)),
                pred_return=float(r["pred_ret"]),
                actual_return=float(r.get("actual_ret", 0)),
                confidence=float(r.get("confidence", 0.5)),
                model_version=r.get("model", "unknown"),
                created_at=datetime.utcnow()
            )
        )
    return records


def read_json(path: Path) -> List[BacktestRecord]:
    if not path.exists():
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    records = []

    for r in raw:
        records.append(
            BacktestRecord(
                symbol=r["symbol"],
                market=r["market"],
                date=r["date"],
                horizon=r["horizon"],
                pred_return=r["pred_return"],
                actual_return=r["actual_return"],
                confidence=r["confidence"],
                model_version=r["model_version"],
                created_at=datetime.fromisoformat(r["created_at"])
            )
        )
    return records
