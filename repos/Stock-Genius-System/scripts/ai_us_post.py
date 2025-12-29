# 與 ai_tw_post.py **完全相同**
# 差異僅在：
# - 市場代碼
# - Explorer pool
# - Webhook
# - 股票 symbol 不加 .TW

# 為避免你再被 GPT 亂改
# 我直接給你「對稱版本」

import os
import sys
import json
import warnings
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
ROOT_DIR = BASE_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT_DIR))

from safe_yfinance import safe_download
from vault.core_watch_manager import update_core_watch

DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "us_history.csv"
EXPLORER_POOL_FILE = DATA_DIR / "explorer_pool_us.json"
CORE_STATE_FILE = DATA_DIR / "core_watch_us.json"

GUARDIAN_STATE = ROOT_DIR / "shared" / "guardian_state.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_US", "").strip()

HORIZON = 5

def guardian_freeze():
    if not GUARDIAN_STATE.exists():
        return False
    state = json.loads(GUARDIAN_STATE.read_text())
    return state.get("freeze", False) and state.get("level", 0) >= 4

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def confidence_emoji(conf):
    return "🟢" if conf >= 0.6 else "🟡" if conf >= 0.4 else "🔴"

def run():
    if guardian_freeze():
        return

    explorer_pool = json.loads(EXPLORER_POOL_FILE.read_text()).get("symbols", [])[:500]
    data = safe_download(explorer_pool)

    feats = ["mom20", "bias", "vol_ratio"]
    today_results = []

    for sym in explorer_pool:
        if sym not in data:
            continue
        df = data[sym].dropna()
        if len(df) < 120:
            continue

        df["mom20"] = df["Close"].pct_change(20)
        df["bias"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
        df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
        df["target"] = df["Close"].shift(-HORIZON) / df["Close"] - 1

        train = df.iloc[:-HORIZON].dropna()
        model = XGBRegressor(n_estimators=120, max_depth=3, learning_rate=0.05)
        model.fit(train[feats], train["target"])

        pred = float(model.predict(df[feats].iloc[-1:])[0])
        sup, res = calc_pivot(df)
        conf = min(0.9, max(0.1, abs(pred) * 8))

        today_results.append({
            "symbol": sym,
            "pred": pred,
            "price": round(df["Close"].iloc[-1], 2),
            "sup": sup,
            "res": res,
            "conf": conf,
            "core_score": 1.0,
            "days_since_active": 0,
        })

    top5 = sorted(today_results, key=lambda x: x["pred"], reverse=True)[:5]

    core_prev = []
    if CORE_STATE_FILE.exists():
        core_prev = json.loads(CORE_STATE_FILE.read_text())

    core_updated = update_core_watch(core_prev, top5)
    CORE_STATE_FILE.write_text(json.dumps(core_updated, indent=2))

    msg = f"📊 美股 AI 進階預測報告（{datetime.now().date()}）\n\n"

    msg += "🔍 AI 海選 Top 5（盤後）\n\n"
    for s in top5:
        msg += (
            f"{confidence_emoji(s['conf'])} {s['symbol']}｜預估 {s['pred']:+.2%} ｜信心度 {int(s['conf']*100)}%\n"
            f"└ 現價 {s['price']}（支撐 {s['sup']} / 壓力 {s['res']}）\n\n"
        )

    msg += "👁 核心監控清單（長期｜可汰舊換新）\n\n"
    for s in core_updated:
        msg += f"{confidence_emoji(s.get('conf', 0.5))} {s['symbol']}\n"

    if HISTORY_FILE.exists():
        hist = pd.read_csv(HISTORY_FILE).tail(5)
        win = hist[hist["pred_ret"] > 0]
        msg += (
            "📊 美股｜近 5 日回測結算（歷史觀測）\n\n"
            f"交易筆數：{len(hist)}\n"
            f"命中率：{len(win)/len(hist)*100:.1f}%\n"
            f"平均報酬：{hist['pred_ret'].mean():+.2%}\n"
            f"最大回撤：{hist['pred_ret'].min():+.2%}\n\n"
        )

    msg += "💡 僅供研究參考，非投資建議。"

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
