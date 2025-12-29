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

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from scripts.guard_check import check_guardian

from vault.core_watch_manager import update_core_watch
from vault.explorer_weight_tracker import record_explorer_hit
from vault.vault_backtest_writer import write_backtest
from vault.vault_backtest_reader import read_recent_backtest
from vault.vault_backtest_validator import summarize_backtest

MARKET = "US"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_US", "").strip()
HORIZON = 5

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EXPLORER_POOL = DATA_DIR / "explorer_pool_us.json"

def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2 * p - h, 2), round(2 * p - l, 2)

def run():
    check_guardian(task_type="MARKET")

    core_universe = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
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

            results[s] = {
                "pred": pred,
                "price": round(df["Close"].iloc[-1], 2),
                "sup": sup,
                "res": res
            }

            write_backtest(MARKET, s, pred)

        except Exception:
            continue

    if not results:
        return

    explorer_hits = list(sorted(results, key=lambda x: results[x]["pred"], reverse=True)[:5])
    record_explorer_hit(MARKET, explorer_hits)

    core = update_core_watch(
        market=MARKET,
        today_hits=list(results.keys()),
        explorer_hits=explorer_hits
    )

    recent = read_recent_backtest(MARKET, days=5)
    summary = summarize_backtest(recent)

    today = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 美股 AI 進階預測報告（{today}）\n\n"

    msg += "🔍 AI 海選 Top 5\n"
    for s in explorer_hits:
        msg += f"{s}｜預估 {results[s]['pred']:+.2%}\n"

    msg += "\n👁 核心監控清單（Vault）\n"
    for c in core:
        s = c["symbol"]
        if s in results:
            msg += f"{s}｜預估 {results[s]['pred']:+.2%}\n"

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
