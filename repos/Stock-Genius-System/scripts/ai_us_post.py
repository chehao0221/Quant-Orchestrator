import os
from datetime import datetime
import requests

from scripts.safe_yfinance import safe_download
from vault.vault_backtest_writer import write_prediction
from vault.vault_backtest_reader import read_last_n_days

# ===============================
# 固定參數（與 TW 對齊）
# ===============================
MARKET = "US"
HORIZON = 5
WEBHOOK = os.getenv("DISCORD_WEBHOOK_US")

# 美股核心監控（可自行擴充，但邏輯不變）
CORE_WATCH = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
]

# ===============================
def run():
    # 1️⃣ 抓市場資料（若失敗 → 直接跳過，不亂發）
    data = safe_download(CORE_WATCH)
    if data is None:
        print("[US AI] Data download failed, skip.")
        return

    results = {}

    # 2️⃣ 產生「當日預測」（只負責預測，不驗證）
    for s in CORE_WATCH:
        try:
            df = data[s].dropna()
            if len(df) < 30:
                continue

            pred_ret = df["Close"].pct_change(HORIZON).iloc[-1]
            results[s] = {
                "price": round(df["Close"].iloc[-1], 2),
                "pred": float(pred_ret),
            }
        except Exception:
            continue

    if not results:
        print("[US AI] No valid prediction results.")
        return

    # 3️⃣ 寫入 Vault（不可覆寫）
    write_prediction(
        market=MARKET,
        horizon=HORIZON,
        records=results,
    )

    # 4️⃣ 讀 Vault 真・近 5 日回測（已驗證資料）
    stats = read_last_n_days(MARKET, days=5)

    # ===============================
    # Discord 顯示（格式完全照你定義）
    # ===============================
    date_str = datetime.now().strftime("%Y-%m-%d")

    msg = (
        f"📊 美股 AI 進階預測報告（{date_str}）\n"
        f"🔍 AI 海選 Top 5（今日盤後｜成交量前 500）\n\n"
    )

    # 🔍 海選 Top 5（依預估報酬排序）
    top5 = sorted(
        results.items(),
        key=lambda x: x[1]["pred"],
        reverse=True
    )[:5]

    for s, r in top5:
        if r["pred"] >= 0.05:
            emoji = "🟢"
        elif r["pred"] >= 0:
            emoji = "🟡"
        else:
            emoji = "🔴"

        msg += (
            f"{emoji} {s}｜預估 {r['pred']*100:+.2f}%\n"
            f"└ 現價 {r['price']}\n\n"
        )

    # 👁 核心監控（固定顯示）
    msg += "👁 核心監控清單（長期觀察｜可汰舊換新）\n\n"

    for s, r in sorted(results.items(), key=lambda x: x[1]["pred"], reverse=True):
        if r["pred"] >= 0.05:
            emoji = "🟢"
        elif r["pred"] >= 0:
            emoji = "🟡"
        else:
            emoji = "🔴"

        msg += (
            f"{emoji} {s}｜預估 {r['pred']*100:+.2f}%\n"
            f"└ 現價 {r['price']}\n\n"
        )

    msg += (
        "核心監控依長期表現動態調整\n"
        "不等同於今日 Top5，亦不因單日預測即時移除\n"
    )

    # 📊 真・近 5 日回測（只顯示 Vault 已驗證）
    if stats:
        msg += (
            f"\n📊 美股｜近 5 日回測結算（歷史觀測）\n\n"
            f"交易筆數：{stats['trades']}\n"
            f"命中率：{stats['hit_rate']}%\n"
            f"平均報酬：{stats['avg_ret']}%\n"
            f"最大回撤：{stats['max_dd']}%\n\n"
            "📌 本結算僅為歷史統計觀測，不影響任何即時預測或系統行為\n"
        )

    msg += "💡 模型為機率推估，僅供研究參考，非投資建議。"

    # 5️⃣ 發 Discord（只負責發文）
    if WEBHOOK:
        requests.post(
            WEBHOOK,
            json={"content": msg[:1900]},
            timeout=15
        )

# ===============================
if __name__ == "__main__":
    run()
