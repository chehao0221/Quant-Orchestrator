import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import warnings
from xgboost import XGBRegressor

# ===============================
# Path bootstrap
# ===============================
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from scripts.safe_yfinance import safe_download
from scripts.guard_check import check_guardian
from vault.vault_snapshot_writer import write_snapshot
from vault.vault_pool_writer import write_pool

warnings.filterwarnings("ignore")

# ===============================
# Vault Paths
# ===============================
VAULT_ROOT = Path("E:/Quant-Vault/STOCK_DB/TW")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()
HORIZON = 5

# ===============================
def calc_pivot(df):
    r = df.iloc[-20:]
    h, l, c = r["High"].max(), r["Low"].min(), r["Close"].iloc[-1]
    p = (h + l + c) / 3
    return round(2*p - h, 2), round(2*p - l, 2)

# ===============================
def run():
    # Guardian 檢查（Freeze 則直接結束）
    check_guardian("MARKET")

    # 核心監控（可汰舊換新，來源未來可換 Vault）
    core_watch = [
        "2330.TW",
        "2317.TW",
        "2454.TW",
        "2308.TW",
        "2412.TW",
    ]

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

            results.append({
                "symbol": s.replace(".TW", ""),
                "pred": round(pred, 4),
                "price": round(df["Close"].iloc[-1], 2),
                "support": sup,
                "resistance": res,
            })
        except Exception:
            continue

    if not results:
        return

    # ===============================
    # Vault 寫入（歷史事實）
    # ===============================
    write_snapshot(VAULT_ROOT, results)

    # shortlist / core_watch（狀態，不是歷史）
    top5 = sorted(results, key=lambda x: x["pred"], reverse=True)[:5]
    write_pool(VAULT_ROOT, "shortlist", [r["symbol"] for r in top5])
    write_pool(VAULT_ROOT, "core_watch", [r["symbol"] for r in results])

    # ===============================
    # Discord 顯示
    # ===============================
    if not WEBHOOK:
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 進階預測報告（{date_str}）\n\n"
    msg += "🔍 AI 海選 Top 5（今日盤後｜成交量前 500）\n\n"

    for r in top5:
        conf = int(min(max(abs(r["pred"]) * 100, 5), 95))
        emoji = "🟢" if conf >= 60 else "🟡" if conf >= 40 else "🔴"
        msg += (
            f"{emoji} {r['symbol']}｜預估 {r['pred']:+.2%} ｜信心度 {conf}%\n"
            f"└ 現價 {r['price']}（支撐 {r['support']} / 壓力 {r['resistance']}）\n\n"
        )

    msg += "💡 模型為機率推估，僅供研究參考，非投資建議。"

    requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=15)

if __name__ == "__main__":
    run()
