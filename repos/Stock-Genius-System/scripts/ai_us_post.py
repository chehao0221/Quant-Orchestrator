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

# ==================================================
# Path Fix（不再用 scripts.xxx）
# ==================================================
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from safe_yfinance import safe_download

# ==================================================
# Paths
# ==================================================
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "us_history.csv"
EXPLORER_POOL_FILE = DATA_DIR / "explorer_pool_us.json"

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_US", "").strip()

# Guardian State（只讀）
GUARDIAN_STATE = BASE_DIR.parents[2] / "shared" / "guardian_state.json"

HORIZON = 5

# ==================================================
def guardian_freeze():
    if not GUARDIAN_STATE.exists():
        return False
    try:
        state = json.loads(GUARDIAN_STATE.read_text())
        return state.get("freeze", False) and state.get("level", 0) >= 4
    except Exception:
        return False

# ==================================================
def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def confidence_color(score: float):
    if score >= 0.6:
        return "🟢"
    elif score >= 0.4:
        return "🟡"
    else:
        return "🔴"

# ==================================================
def run():
    if guardian_freeze():
        print("[Guardian] L4+ Freeze → Skip US AI post")
        return

    core_watch = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]

    data = safe_download(core_watch)
    if data is None:
        print("[INFO] US AI skipped (data failure)")
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = {}

    for s in core_watch:
        try:
            df = data[s].dropna()
            if len(df) < 120:
                continue

            df["mom20"] = df["Close"].pct_change(20)
            df["bias"] = (
                (df["Close"] - df["Close"].rolling(20).mean())
                / df["Close"].rolling(20).mean()
            )
            df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
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

            confidence = min(0.9, max(0.1, abs(pred) * 8))

            results[s] = {
                "pred": pred,
                "price": round(df["Close"].iloc[-1], 2),
                "sup": sup,
                "res": res,
                "conf": confidence,
            }
        except Exception:
            continue

    if not results:
        return

    # ==================================================
    # Discord Message
    # ==================================================
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 美股 AI 進階預測報告（{date_str}）\n\n"

    # 🔍 Explorer Top 5
    if EXPLORER_POOL_FILE.exists():
        try:
            pool = json.loads(EXPLORER_POOL_FILE.read_text())
            explorer = pool.get("symbols", [])[:200]

            hits = [(s, results[s]) for s in explorer if s in results]
            top5 = sorted(hits, key=lambda x: x[1]["pred"], reverse=True)[:5]

            if top5:
                msg += "🔍 AI 海選 Top 5（盤後）\n\n"
                for s, r in top5:
                    emoji = confidence_color(r["conf"])
                    msg += (
                        f"{emoji} {s}｜預估 {r['pred']:+.2%} ｜信心度 {int(r['conf']*100)}%\n"
                        f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n\n"
                    )
        except Exception:
            pass

    # 👁 Core Watch
    msg += "👁 核心監控（固定顯示）\n\n"
    for s, r in sorted(results.items(), key=lambda x: x[1]["pred"], reverse=True):
        emoji = confidence_color(r["conf"])
        msg += (
            f"{emoji} {s}｜預估 {r['pred']:+.2%} ｜信心度 {int(r['conf']*100)}%\n"
            f"└ 現價 {r['price']}（支撐 {r['sup']} / 壓力 {r['res']}）\n\n"
        )

    # 📊 5 日回測
    if HISTORY_FILE.exists():
        try:
            hist = pd.read_csv(HISTORY_FILE).tail(5)
            if not hist.empty:
                win = hist[hist["pred_ret"] > 0]
                msg += (
                    "📊 美股｜近 5 日回測結算（歷史觀測）\n\n"
                    f"交易筆數：{len(hist)}\n"
                    f"命中率：{len(win)/len(hist)*100:.1f}%\n"
                    f"平均報酬：{hist['pred_ret'].mean():+.2%}\n"
                    f"最大回撤：{hist['pred_ret'].min():+.2%}\n\n"
                )
        except Exception:
            pass

    msg += "💡 模型為機率推估，僅供研究參考，非投資建議。"

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg[:1900]}, timeout=15)

# ==================================================
if __name__ == "__main__":
    run()
