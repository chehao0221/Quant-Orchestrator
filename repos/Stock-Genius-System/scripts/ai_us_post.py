import os
import sys
import json
import warnings
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from xgboost import XGBRegressor

# ===== Path Fix =====
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from vault.stock_weight_engine import compute_message_weight
from vault.core_watch_manager import update_core_watch

warnings.filterwarnings("ignore")

DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "us_history.csv"

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_US", "").strip()
HORIZON = 5

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def confidence_color(conf):
    if conf >= 0.6:
        return "🟢"
    if conf >= 0.4:
        return "🟡"
    return "🔴"

def run():
    core_candidates = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA"]

    data = safe_download(core_candidates)
    if data is None:
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = {}

    for s in core_candidates:
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
            conf = min(0.9, max(0.1, abs(pred) * 20))

            results[s] = {
                "pred": pred,
                "price": round(df["Close"].iloc[-1], 2),
                "sup": sup,
                "res": res,
                "conf": conf
            }
        except Exception:
            continue

    if not results:
        return

    message_weight = compute_message_weight()
    ranked = [(s, r["pred"] * message_weight) for s, r in results.items()]
    ranked.sort(key=lambda x: x[1], reverse=True)

    core_watch = update_core_watch(ranked)

    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 美股 AI 進階預測報告（{date_str}）\n\n"

    msg += "🔍 AI 海選 Top 5\n\n"
    for s, _ in ranked[:5]:
        r = results[s]
        emoji = confidence_color(r["conf"])
        msg += (
            f"{emoji} {s}｜預估 {r['pred']:+.2%} ｜信心度 {int(r['conf']*100)}%\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n\n"
        )

    msg += "👁 核心監控清單（長期觀察｜可汰舊換新）\n\n"
    for sym, meta in core_watch.items():
        if sym not in results:
            continue
        r = results[sym]
        emoji = confidence_color(r["conf"])
        msg += (
            f"{emoji} {sym}｜預估 {r['pred']:+.2%} ｜信心度 {int(r['conf']*100)}%\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n\n"
        )

    if HISTORY_FILE.exists():
        hist = pd.read_csv(HISTORY_FILE).tail(50)
        if len(hist) > 0:
            win = hist[hist["pred_ret"] > 0]
            msg += (
                "📊 美股｜近 5 日回測結算（歷史觀測）\n\n"
                f"交易筆數：{len(hist)}\n"
                f"命中率：{len(win)/len(hist)*100:.1f}%\n"
                f"平均報酬：{hist['pred_ret'].mean():+.2%}\n"
                f"最大回撤：{hist['pred_ret'].min():+.2%}\n\n"
            )

    msg += "💡 模型為機率推估，僅供研究參考，非投資建議。"

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
