import os
import sys
import json
import warnings
import requests
from datetime import datetime
from pathlib import Path
from xgboost import XGBRegressor

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from scripts.guard_check import check_guardian
from vault.vault_backtest_reader import load_history, summarize_backtest

warnings.filterwarnings("ignore")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_US", "").strip()
HORIZON = 5

VAULT_ROOT = Path("E:/Quant-Vault")
VAULT_US = VAULT_ROOT / "STOCK_DB" / "US"
HISTORY_DIR = VAULT_US / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def run():
    check_guardian(task_type="MARKET")

    core_watch = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
    data = safe_download(core_watch)
    if data is None:
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = []

    for s in core_watch:
        try:
            df = data[s].dropna()
            if len(df) < 120:
                continue

            df["mom20"] = df["Close"].pct_change(20)
            df["bias"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
            df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
            df["target"] = df["Close"].shift(-HORIZON) / df["Close"] - 1

            train = df.iloc[:-HORIZON].dropna()
            model = XGBRegressor(
                n_estimators=120,
                max_depth=3,
                learning_rate=0.05,
                random_state=42
            )
            model.fit(train[feats], train["target"])

            pred = float(model.predict(df[feats].iloc[-1:])[0])
            sup, res = calc_pivot(df)

            results.append({
                "symbol": s,
                "pred": round(pred, 4),
                "price": round(df["Close"].iloc[-1], 2),
                "support": sup,
                "resistance": res
            })
        except Exception:
            continue

    if not results:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    vault_file = HISTORY_DIR / f"{today}.json"
    vault_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    msg = f"📊 美股 AI 進階預測報告（{today}）\n\n"

    top5 = sorted(results, key=lambda x: x["pred"], reverse=True)[:5]
    msg += "🔍 AI 海選 Top 5\n"
    for r in top5:
        emoji = "🟢" if r["pred"] > 0.01 else "🟡" if r["pred"] > 0 else "🔴"
        msg += (
            f"{emoji} {r['symbol']}｜預估 {r['pred']:+.2%}\n"
            f"└ 現價 {r['price']}（支撐 {r['support']} / 壓力 {r['resistance']}）\n"
        )

    msg += "\n👁 核心監控清單（固定顯示）\n"
    for r in results:
        emoji = "🟢" if r["pred"] > 0.01 else "🟡" if r["pred"] > 0 else "🔴"
        msg += (
            f"{emoji} {r['symbol']}｜預估 {r['pred']:+.2%}\n"
            f"└ 現價 {r['price']}（支撐 {r['support']} / 壓力 {r['resistance']}）\n"
        )

    records = load_history(VAULT_US, days=5)
    summary = summarize_backtest(records)

    if summary:
        msg += (
            "\n📊 美股｜近 5 日回測結算（Vault）\n\n"
            f"樣本數：{summary['count']}\n"
            f"正報酬比例：{summary['win_rate']}%\n"
            f"平均預期：{summary['avg_pred']:+.2%}\n"
            f"最差預期：{summary['max_drawdown']:+.2%}\n"
        )

    msg += "\n💡 僅供研究參考，非投資建議。"

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
