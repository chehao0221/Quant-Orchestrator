import sys, os
from datetime import datetime
import requests
from scripts.safe_yfinance import safe_download
from vault.vault_backtest_writer import write_prediction
from vault.vault_backtest_reader import read_last_n_days

HORIZON = 5
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW")

CORE = ["2330.TW","2317.TW","2454.TW","2412.TW","2308.TW"]

def run():
    data = safe_download(CORE)
    results = {}

    for s in CORE:
        df = data[s].dropna()
        ret = df["Close"].pct_change(5).iloc[-1]
        results[s] = {
            "price": round(df["Close"].iloc[-1],2),
            "pred": float(ret)
        }

    write_prediction("TW", HORIZON, results)
    stats = read_last_n_days("TW")

    msg = f"📊 台股 AI 進階預測報告（{datetime.now():%Y-%m-%d}）\n\n"
    msg += "👁 核心監控（固定顯示）\n"

    for s,r in results.items():
        emoji = "🟢" if r["pred"]>0 else "🔴"
        msg += f"{emoji} {s.replace('.TW','')}｜預估 {r['pred']*100:+.2f}%\n"

    if stats:
        msg += (
            f"\n📊 台股｜近 5 日回測結算\n"
            f"交易筆數：{stats['trades']}\n"
            f"命中率：{stats['hit_rate']}%\n"
            f"平均報酬：{stats['avg_ret']}%\n"
            f"最大回撤：{stats['max_dd']}%\n"
        )

    requests.post(WEBHOOK, json={"content": msg[:1900]})

if __name__ == "__main__":
    run()
