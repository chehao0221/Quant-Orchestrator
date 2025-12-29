from datetime import datetime, timedelta
from pathlib import Path
import json

VAULT_EVENT_DIR = Path("E:/Quant-Vault/LOCKED_RAW/black_swan")

def load_active_events(max_days: int = 7):
    events = []
    if not VAULT_EVENT_DIR.exists():
        return events

    for f in VAULT_EVENT_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ts = datetime.fromisoformat(data["timestamp"])
            if datetime.utcnow() - ts <= timedelta(days=max_days):
                events.append(data)
        except Exception:
            continue
    return events


def compute_message_weight():
    """
    回傳一個整體 message 權重
    黑天鵝 > 重大消息 > 一般消息
    """
    events = load_active_events()

    weight = 1.0
    for e in events:
        if e["event_type"] == "BLACK_SWAN":
            return 0.3    # 🔴 直接壓制股票排序（最高等級）
        elif e["event_type"] == "MAJOR_NEWS":
            weight *= 0.8
        elif e["event_type"] == "NORMAL_NEWS":
            weight *= 0.9

    return round(weight, 3)
