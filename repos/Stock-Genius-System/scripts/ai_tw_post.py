import os
import sys
import json
import time
import requests
import warnings
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# ===============================
# Path Fix
# ===============================
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from vault.vault_backtest_reader import read_backtest
from vault.vault_backtest_writer import write_backtest
from vault.schema import decay_weight

# ===============================
# Config
# ===============================
MARKET = "TW"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()

DATA_DIR = BASE_DIR / "data"
VAULT_DIR = BASE_DIR.parents[1] / "vault"

GUARDIAN_STATE = BASE_DIR.parents[1] / "shared" / "guardian_state.json"

EXPLORER_POOL = DATA_DIR / "explorer_pool_tw.json"
FAIL_MARK = DATA_DIR / "tw_data_failed.flag"

HORIZON = 5
MAX_FIXED = 7
RETRY_HOURS = 2

CORE_WATCH = [
    "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2412.TW"
]

# ===============================
def guardian_freeze():
    if not GUARDIAN_STATE.exists():
        return False
    s = json.loads(GUARDIAN_STATE.read_text())
    return s.get("freeze", False) and s.get("level", 0) >= 4

# ===============================
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

# ===============================
def load_explorer():
    if not EXPLORER_POOL.exists():
        return []
    return json.loads(EXPLORER_POOL.read_text()).get("symbols", [])

# ===============================
def data_ready(symbols):
    data = safe_download(symbols)
    if data is None:
        return None
    for s in symbols:
        if s not in data or len(data[s]) < 120:
            return None
    return data

# ===============================
def run():
    if guardian_freeze():
        return

    start_time = datetime.utcnow()
    data = None

    for i in range(RETRY_HOURS + 1):
        data = data_ready(list(set(CORE_WATCH + load_explorer())))
        if data:
            break
        time.sleep(3600)

    if not data:
        FAIL_MARK.touch()
        return

    results = {}
    feats = ["mom20", "bias", "vol_ratio"]

    for sym, df in data.items():
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

        results[sym] = {
            "pred": pred,
            "price": round(df["Close"].iloc[-1], 2),
            "sup": sup,
            "res": res,
        }

        write_backtest(MARKET, sym, pred)

    # ===============================
    # Ranking with decay
    # ===============================
    scored = []
    for s, r in results.items():
        hist = read_backtest(MARKET, s, days=30)
        weight = decay_weight(hist)
        scored.append((s, r, r["pred"] * weight))

    top5 = sorted(scored, key=lambda x: x[2], reverse=True)[:5]

    fixed = CORE_WATCH.copy()
    for s, _, _ in top5:
        if s not in fixed and len(fixed) < MAX_FIXED:
            fixed.append(s)

    # ===============================
    # Discord
    # ===============================
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 預測報告 ({date_str})\n\n"

    msg += "🔍 AI 海選 Top 5\n"
    for s, r, _ in top5:
        e = "📈" if r["pred"] > 0 else "📉"
        sym = s.replace(".TW", "")
        msg += f"{e} {sym}：{r['pred']:+.2%}\n└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n"

    msg += "\n👁 固定監控（含自動補位）\n"
    for s in fixed:
        r = results[s]
        e = "📈" if r["pred"] > 0 else "📉"
        sym = s.replace(".TW", "")
        msg += f"{e} {sym}：{r['pred']:+.2%}\n└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n"

    hist = read_backtest(MARKET, days=5, aggregate=True)
    if hist:
        msg += "\n📊 近 5 日歷史觀測\n"
        msg += f"筆數：{hist['count']} / 命中率：{hist['win_rate']:.1f}% / 平均：{hist['avg']:+.2%}\n"

    msg += "\n💡 僅為研究觀測，非投資建議"

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
