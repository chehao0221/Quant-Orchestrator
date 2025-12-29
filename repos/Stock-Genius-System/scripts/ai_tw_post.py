import os
import sys
import json
import time
import requests
import warnings
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# ==================================================
# Path
# ==================================================
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from vault.vault_backtest_reader import (
    read_symbol_history,
    read_market_aggregate,
)
from vault.vault_backtest_writer import write_backtest
from vault.schema import (
    compute_decay_weight,
    compute_fixed_score,
)

# ==================================================
# Config
# ==================================================
MARKET = "TW"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()

DATA_DIR = BASE_DIR / "data"
EXPLORER_POOL = DATA_DIR / "explorer_pool_tw.json"
FAIL_FLAG = DATA_DIR / "tw_data_failed.flag"

GUARDIAN_STATE = BASE_DIR.parents[1] / "shared" / "guardian_state.json"

HORIZON = 5
MAX_FIXED = 7
RETRY_HOURS = 2

# ==================================================
def guardian_freeze():
    if not GUARDIAN_STATE.exists():
        return False
    s = json.loads(GUARDIAN_STATE.read_text())
    return s.get("freeze", False) and s.get("level", 0) >= 4

# ==================================================
def calc_features(df):
    df["mom20"] = df["Close"].pct_change(20)
    df["bias"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
    df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
    return df

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

# ==================================================
def load_explorer():
    if not EXPLORER_POOL.exists():
        return []
    return json.loads(EXPLORER_POOL.read_text()).get("symbols", [])

# ==================================================
def data_ready(symbols):
    data = safe_download(symbols)
    if data is None:
        return None
    for s in symbols:
        if s not in data or len(data[s]) < 120:
            return None
    return data

# ==================================================
def run():
    if guardian_freeze():
        return

    symbols = list(set(load_explorer()))
    data = None

    for _ in range(RETRY_HOURS + 1):
        data = data_ready(symbols)
        if data:
            break
        time.sleep(3600)

    if not data:
        FAIL_FLAG.touch()
        return

    feats = ["mom20", "bias", "vol_ratio"]
    preds = {}

    # ===============================
    # Prediction
    # ===============================
    for s, df in data.items():
        df = calc_features(df.dropna())
        if len(df) < 120:
            continue

        df["target"] = df["Close"].shift(-HORIZON) / df["Close"] - 1
        train = df.iloc[:-HORIZON].dropna()

        model = XGBRegressor(
            n_estimators=120,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
        )
        model.fit(train[feats], train["target"])

        pred = float(model.predict(df[feats].iloc[-1:])[0])
        sup, res = calc_pivot(df)

        preds[s] = {
            "pred": pred,
            "price": round(df["Close"].iloc[-1], 2),
            "sup": sup,
            "res": res,
        }

        write_backtest(MARKET, s, pred)

    if not preds:
        return

    # ===============================
    # Top 5
    # ===============================
    ranked = sorted(preds.items(), key=lambda x: x[1]["pred"], reverse=True)
    top5 = ranked[:5]

    # ===============================
    # Fixed Watch (Dynamic)
    # ===============================
    fixed_scores = []

    for s, r in preds.items():
        hist = read_symbol_history(MARKET, s, days=90)
        decay = compute_decay_weight(hist)
        score = compute_fixed_score(
            pred=r["pred"],
            decay=decay,
            history=hist,
        )
        fixed_scores.append((s, score))

    fixed = [s for s, _ in sorted(fixed_scores, key=lambda x: x[1], reverse=True)[:MAX_FIXED]]

    # ===============================
    # Discord
    # ===============================
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 預測報告 ({date_str})\n\n"

    msg += "🔍 AI 海選 Top 5\n"
    for s, r in top5:
        e = "📈" if r["pred"] > 0 else "📉"
        sym = s.replace(".TW", "")
        msg += (
            f"{e} {sym}：{r['pred']:+.2%}\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n"
        )

    msg += "\n👁 固定監控（AI 動態席位）\n"
    for s in fixed:
        r = preds[s]
        e = "📈" if r["pred"] > 0 else "📉"
        sym = s.replace(".TW", "")
        msg += (
            f"{e} {sym}：{r['pred']:+.2%}\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n"
        )

    agg = read_market_aggregate(MARKET, days=5)
    if agg:
        msg += (
            "\n📊 近 5 日歷史觀測\n"
            f"筆數：{agg['count']} / 命中率：{agg['win_rate']:.1f}% / 平均：{agg['avg']:+.2%}\n"
        )

    msg += "\n💡 僅為研究觀測，非投資建議"

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
