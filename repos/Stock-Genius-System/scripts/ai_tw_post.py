import os
import sys
import json
import math
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ==================================================
# Path Fix（保證 GitHub Actions / 本地都不迷路）
# ==================================================
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

# ==================================================
# External Guards
# ==================================================
from scripts.guard_check import check_guardian
from vault.vault_backtest_reader import read_recent_backtest
from vault.schema import StockScoreSchema

# ==================================================
# Env
# ==================================================
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()

# ==================================================
# Config
# ==================================================
MARKET = "TW"
MAX_CORE = 7
TOP_K = 5
LOOKBACK_DAYS = 5

# ==================================================
# Helpers
# ==================================================
def confidence_color(score: float):
    if score >= 0.65:
        return "🟢"
    if score >= 0.45:
        return "🟡"
    return "🔴"

def decay(days: int):
    return math.exp(-days / 7)

# ==================================================
# Main
# ==================================================
def run():
    # ----------------------------------------------
    # Guardian 檢查（MARKET）
    # ----------------------------------------------
    check_guardian(task_type="MARKET")

    # ----------------------------------------------
    # 讀 Vault Backtest（JSON）
    # ----------------------------------------------
    records = read_recent_backtest(
        market=MARKET,
        days=LOOKBACK_DAYS
    )

    if not records:
        print("[AI_TW] No backtest data.")
        return

    scores = []
    for r in records:
        s = StockScoreSchema.from_dict(r)
        scores.append(s)

    # ----------------------------------------------
    # 海選 Top 5（綜合分數）
    # ----------------------------------------------
    top5 = sorted(scores, key=lambda x: x.final_score, reverse=True)[:TOP_K]

    # ----------------------------------------------
    # 固定標（含衰退權重）
    # ----------------------------------------------
    core_sorted = sorted(
        scores,
        key=lambda x: (x.long_term_weight * decay(x.days_since_hot)),
        reverse=True
    )
    core_watch = core_sorted[:MAX_CORE]

    # ----------------------------------------------
    # Discord 組裝
    # ----------------------------------------------
    today = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 進階預測報告（{today}）\n\n"

    # ---- Top 5 ----
    msg += "🔍 AI 海選 Top 5（今日盤後）\n\n"
    for s in top5:
        color = confidence_color(s.confidence)
        msg += (
            f"{color} {s.symbol}｜預估 {s.pred_ret:+.2%} ｜信心度 {int(s.confidence*100)}%\n"
            f"└ 現價 {s.price}（支撐 {s.support} / 壓力 {s.resistance}）\n\n"
        )

    # ---- Core ----
    msg += "👁 核心監控清單（長期｜可汰舊換新）\n\n"
    for s in core_watch:
        color = confidence_color(s.confidence)
        msg += (
            f"{color} {s.symbol}｜預估 {s.pred_ret:+.2%} ｜信心度 {int(s.confidence*100)}%\n"
            f"└ 現價 {s.price}（支撐 {s.support} / 壓力 {s.resistance}）\n\n"
        )

    # ---- 回測 ----
    wins = [s for s in scores if s.real_ret > 0]
    avg = sum(s.real_ret for s in scores) / len(scores)

    msg += (
        "📊 台股｜近 5 日回測結算（歷史觀測）\n\n"
        f"交易筆數：{len(scores)}\n"
        f"命中率：{len(wins)/len(scores)*100:.1f}%\n"
        f"平均報酬：{avg:+.2%}\n"
        f"最大回撤：{min(s.real_ret for s in scores):+.2%}\n\n"
        "📌 本結算僅為歷史統計觀測，不影響任何即時預測或系統行為\n"
        "💡 模型為機率推估，僅供研究參考，非投資建議。"
    )

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=15)

# ==================================================
if __name__ == "__main__":
    run()
