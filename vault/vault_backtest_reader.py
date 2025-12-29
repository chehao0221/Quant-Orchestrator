import json
from pathlib import Path
from statistics import mean

def load_history(vault_market_path: Path, days: int = 5):
    """
    讀取最近 N 日 Vault history JSON
    """
    history_dir = vault_market_path / "history"
    if not history_dir.exists():
        return []

    files = sorted(history_dir.glob("*.json"), reverse=True)[:days]
    records = []

    for f in files:
        try:
            daily = json.loads(f.read_text(encoding="utf-8"))
            records.extend(daily)
        except Exception:
            continue

    return records


def summarize_backtest(records: list):
    """
    回測摘要（只做統計，不下判斷）
    """
    if not records:
        return None

    preds = [r["pred"] for r in records if "pred" in r]

    if not preds:
        return None

    return {
        "count": len(preds),
        "avg_pred": round(mean(preds), 4),
        "win_rate": round(len([p for p in preds if p > 0]) / len(preds) * 100, 1),
        "max_drawdown": round(min(preds), 4),
    }
