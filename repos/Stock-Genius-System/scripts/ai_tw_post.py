import os
import sys
import json
import requests
import warnings
import pandas as pd
from datetime import datetime
from pathlib import Path
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# ===============================
# Path Fix
# ===============================
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from scripts.guard_check import check_guardian

from vault.core_watch_manager import update_core_watch
from vault.explorer_weight_tracker import record_explorer_hit
from vault.vault_backtest_writer import write_backtest
from vault.vault_backtest_reader import read_recent_backtest
from vault.vault_backtest_validator import summarize_backtest

# ===============================
# Config
# ===============================
MARKET = "TW"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()
HORIZON = 5

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

HISTORY_CSV = DATA_DIR / "tw_history.csv"
EXPLORER_POOL = DATA_DIR / "explorer_pool_tw.json"

# ===============================
def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

# ===============================
def run():
    # Guardian Freeze Check
    check_guardian(task_type="MARKET")

    core_universe = [
        "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2412.TW"
    ]

    data = safe_download(core_universe)
    if data is None:
        return

    feats = ["mom20", "bias", "vol_ratio"]
    results = {}

    for s in core_universe:
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

            results[s.replace(".TW", "")] = {
                "pred": pred,
                "price": round(df["Close"].iloc[-1], 2),
                "sup": sup,
                "res": res
            }

            write_backtest(
                market=MARKET,
                symbol=s.replace(".TW", ""),
                pred=pred
            )

        except Exception:
            continue

    if not results:
        return

    # ===============================
    # Explorer Top5
    # ===============================
    explorer_hits = []
    if EXPLORER_POOL.exists():
        pool = json.loads(EXPLORER_POOL.read_text())
        syms = pool.get("symbols", [])[:100]
        hits = [(s.replace(".TW", ""), results[s.replace(".TW", "")])
                for s in syms if s.replace(".TW", "") in results]
        explorer_hits = [s for s, _ in sorted(hits, key=lambda x: x[1]["pred"], reverse=True)[:5]]
        record_explorer_hit(MARKET, explorer_hits)

    # ===============================
    # Core Watch (Vault)
    # ===============================
    core = update_core_watch(
        market=MARKET,
        today_hits=list(results.keys()),
        explorer_hits=explorer_hits
    )

    # ===============================
    # Backtest Summary
    # ===============================
    recent = read_recent_backtest(MARKET, days=5)
    summary = summarize_backtest(recent)

    # ===============================
    # Discord Message
    # ===============================
    today = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 進階預測報告（{today}）\n\n"

    msg += "🔍 AI 海選 Top 5\n"
    for s in explorer_hits:
        r = results[s]
        msg += f"{s}｜預估 {r['pred']:+.2%}\n"

    msg += "\n👁 核心監控清單（Vault）\n"
    for c in core:
        s = c["symbol"]
        r = results.get(s)
        if not r:
            continue
        msg += f"{s}｜預估 {r['pred']:+.2%}\n"

    msg += (
        "\n📊 近 5 日回測結算\n"
        f"交易筆數：{summary['count']}\n"
        f"命中率：{summary['win_rate']:.1f}%\n"
        f"平均報酬：{summary['avg_ret']:+.2%}\n"
        f"最大回撤：{summary['max_dd']:+.2%}\n"
    )

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
