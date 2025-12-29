from pathlib import Path
from tools.vault_ai_judge import ai_should_delete
from tools.vault_executor import safe_delete

VAULT = Path(r"E:\Quant-Vault\STOCK_DB")

def scan_market(market: str):
    base = VAULT / market

    universe = base / "universe"
    shortlist = base / "shortlist"
    core = base / "core_watch"
    history = base / "history"
    cache = base / "cache"

    for folder in [universe, history, cache]:
        if not folder.exists():
            continue

        for f in folder.glob("*.json"):
            # ⚠️ 這裡的資訊你之後可以接真實 metadata
            delete = ai_should_delete(
                f,
                last_read_days=999,
                in_universe=f.parent == universe,
                in_recent_top5=False,
                in_core_watch=False,
                has_newer_version=True
            )

            if delete:
                safe_delete(f)
