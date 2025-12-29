import os
import sys
import json
import warnings
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.safe_yfinance import safe_download
from scripts.guard_check import check_guardian

warnings.filterwarnings("ignore")

check_guardian("MARKET")

DATA_DIR = os.path.join(BASE_DIR, "data")
EXPLORER_POOL_FILE = os.path.join(DATA_DIR, "explorer_pool_us.json")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_US", "").strip()

VAULT_ROOT = Path(os.getenv("QUANT_VAULT", r"E:\Quant-Vault"))
VAULT_US = VAULT_ROOT / "STOCK_DB" / "US"

for d in ["universe", "shortlist", "core_watch", "history", "cache"]:
    (VAULT_US / d).mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
HORIZON = 5

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def run():
    core_watch = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
    data = safe_download(core_watch)
    if data is None:
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = {}

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
            model = XGBRegressor(n_estimators=120, max_depth=3, learning_rate=0.05, random_state=42)
            model.fit(train[feats], train["target"])

            pred = float(model.predict(df[feats].iloc[-1:])[0])
            sup, res = calc_pivot(df)

            results[s] = {
                "symbol": s,
                "pred": round(pred, 4),
                "price": round(df["Close"].iloc[-1], 2),
                "support": sup,
                "resistance": res,
            }
        except Exception:
            continue

    if not results:
        return

    top5 = sorted(results.values(), key=lambda x: x["pred"], reverse=True)[:5]

    (VAULT_US / "shortlist" / f"{TODAY}.json").write_text(
        json.dumps(top5, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (VAULT_US / "history" / f"{TODAY}.json").write_text(
        json.dumps(list(results.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    msg = f"📊 美股 AI 進階預測報告（{TODAY}）\n\n"
    msg += "🔍 AI 海選 Top 5（盤後）\n\n"

    for r in top5:
        emoji = "🟢" if r["pred"] > 0.02 else "🟡" if r["pred"] > 0 else "🔴"
        msg += (
            f"{emoji} {r['symbol']}｜預估 {r['pred']:+.2%}\n"
            f"└ 現價 {r['price']}（支撐 {r['support']} / 壓力 {r['resistance']}）\n\n"
        )

    msg += "💡 模型為機率推估，僅供研究參考，非投資建議。"

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
