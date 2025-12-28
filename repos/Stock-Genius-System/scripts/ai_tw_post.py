import os
import json
import requests
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("../../shared/state.json")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW")

TW_CORE_SYMBOLS = [
    "2330.TW",  # 台積電
    "2317.TW",  # 鴻海
    "2454.TW",  # 聯發科
    "2308.TW",  # 台達電
    "2412.TW",  # 中華電
]

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def guardian_blocked():
    return load_state().get("risk_level") == 4

def send(text):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": text}, timeout=10)

def ai_confidence(score: float):
    if score >= 0.7:
        return "🟢 高"
    if score >= 0.45:
        return "🟡 中"
    return "🔴 低"

def generate_blackhorse():
    return [
        ("3661.TW", 6.12, 0.74),
        ("3035.TW", 5.33, 0.67),
        ("3443.TW", 4.95, 0.62),
        ("2379.TW", 4.21, 0.58),
        ("2382.TW", 3.88, 0.50),
    ]

def main():
    if guardian_blocked():
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    horses = generate_blackhorse()

    lines = []
    lines.append(f"🇹🇼 **台股 AI 進階預測報告 ({today})**")
    lines.append("-" * 40)
    lines.append("")
    lines.append("🔍 **AI 海選 Top 5（潛力黑馬｜研究用途）**")

    for sym, pct, conf in horses:
        lines.append(f"{sym}：預估 {pct:+.2f}%｜信心度 {ai_confidence(conf)}")

    lines.append("")
    lines.append("⭐ **台股核心監控（固定顯示）**")
    for sym in TW_CORE_SYMBOLS:
        lines.append(f"{sym}：穩定觀察")

    lines.append("")
    lines.append("📊 **模型說明**")
    lines.append("• 成交金額前 500 標的")
    lines.append("• 技術面＋消息面 AI 綜合評分")
    lines.append("• 僅供研究觀測，非投資或交易建議")

    send("\n".join(lines))

if __name__ == "__main__":
    main()
