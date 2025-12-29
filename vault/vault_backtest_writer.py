import json
from datetime import datetime, timedelta
from pathlib import Path
from vault.schema import VaultState, StockHistory

VAULT_FILE = Path("vault/state.json")

DECAY_DAYS = 30

def _decay_factor(last_seen: str) -> float:
    dt = datetime.fromisoformat(last_seen)
    days = (datetime.utcnow() - dt).days
    return max(0.2, 1.0 - days / DECAY_DAYS)

def write_backtest(symbol: str, market: str, pred_ret: float, hit: bool, importance: str):
    now = datetime.utcnow().isoformat()

    if VAULT_FILE.exists():
        state: VaultState = json.loads(VAULT_FILE.read_text())
    else:
        state = {
            "version": 1,
            "updated_at": now,
            "stocks": []
        }

    for s in state["stocks"]:
        if s["symbol"] == symbol and s["market"] == market:
            s["appear_count"] += 1
            if hit:
                s["hit_count"] += 1
                s["last_hit"] = now

            s["avg_pred_ret"] = (
                (s["avg_pred_ret"] * (s["appear_count"] - 1) + pred_ret)
                / s["appear_count"]
            )

            s["last_seen"] = now
            s["decay_weight"] = s["base_weight"] * _decay_factor(s["last_seen"])
            break
    else:
        state["stocks"].append({
            "symbol": symbol,
            "market": market,
            "appear_count": 1,
            "hit_count": 1 if hit else 0,
            "avg_pred_ret": pred_ret,
            "first_seen": now,
            "last_seen": now,
            "last_hit": now if hit else None,
            "base_weight": 1.0,
            "decay_weight": 1.0,
            "importance": importance
        })

    state["updated_at"] = now
    VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    VAULT_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
