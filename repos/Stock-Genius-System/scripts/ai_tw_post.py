import os
import sys
import json
import time
import warnings
import requests
from pathlib import Path
from datetime import datetime

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
    compute_confidence,
)

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

def confidence_emoji(conf):
    if conf >= 0.6:
        return "🟢"
    if conf >= 0.4:
        return "🟡"
    return "🔴"

def trend_emoji(pred):
    return "📈" if pred >= 0 else "📉"

def calc_features(df):
    df["mom20"] = df["Close"].pct_change(20)
    df["bias"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
    df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
    return df

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2*p - h, 2), round(2*p - l, 2)

def load_explorer():
    if not EXPLORER_POOL.exists():
        return []
    return json.loads(EXPLORER_POOL.read_text()).get("symbols", [])

# ==================================================
def run():
    if guardian_freeze():
        return

    symbols = list(set(load_explorer()))
    data = None

    for _ in range(RETRY_HOURS + 1):
        data = safe_download(symbols)
        if data:
            break
        time.sleep(3600)

    if not data:
        FAIL_FLAG.touch()
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = {}

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
        conf = compute_confidence(df, pred)
        sup, res = calc_pivot(df)

        write_backtest(MARKET, s, pred)

        results[s] = {
            "pred": pred,
            "conf": conf,
            "price": round(df["Close"].iloc[-1], 2),
            "sup": sup,
            "res": res,
        }

    if not results:
        return

    # ===============================
    ranked = sorted(results.items(), key=lambda x: x[1]["pred"], reverse=True)
    top5 = ranked[:5]

    fixed_scores = []
    for s, r in results.items():
        hist = read_symbol_history(MARKET, s, days=90)
        decay = compute_decay_weight(hist)
        score = compute_fixed_score(r["pred"], decay, hist)
        fixed_scores.append((s, score))

    fixed = [s for s, _ in sorted(fixed_scores, key=lambda x: x[1], reverse=True)[:MAX_FIXED]]

    # ===============================
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 進階預測報告（{date_str}）\n\n"

    msg += "🔍 AI 海選 Top 5\n"
    for s, r in top5:
        msg += (
            f"{confidence_emoji(r['conf'])} {s.replace('.TW','')}｜"
            f"預估 {r['pred']:+.2%} ｜信心度 {int(r['conf']*100)}%\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n"
        )

    msg += "\n👁 核心監控清單
