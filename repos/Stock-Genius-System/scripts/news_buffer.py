import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

BUFFER_FILE = Path("repos/Stock-Genius-System/data/news_buffer.json")
MAX_DAYS = 7   # 保存天數（可調）

def load_buffer():
    if BUFFER_FILE.exists():
        return json.loads(BUFFER_FILE.read_text())
    return []

def save_buffer(buffer):
    BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
    BUFFER_FILE.write_text(json.dumps(buffer, indent=2, ensure_ascii=False))

def add_news(market, related_symbols, impact_score, sentiment):
    buffer = load_buffer()
    buffer.append({
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "market": market,
        "related_symbols": related_symbols,
        "impact_score": impact_score,
        "sentiment": sentiment,
        "published": False
    })
    save_buffer(buffer)

def clean_buffer():
    buffer = load_buffer()
    now = datetime.utcnow()
    new_buffer = []

    for item in buffer:
        ts = datetime.fromisoformat(item["timestamp"])
        if now - ts > timedelta(days=MAX_DAYS):
            continue
        if item.get("impact_score", 0) < 0.3:
            continue
        new_buffer.append(item)

    save_buffer(new_buffer)
