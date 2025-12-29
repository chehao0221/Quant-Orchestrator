import os, json, sys
from datetime import datetime
import requests
from pathlib import Path
from vault.vault_backtest_writer import write_backtest
from vault.vault_backtest_reader import read_last_n
from vault.vault_backtest_validator import summarize
from vault.schema import VaultBacktestRecord

VAULT_ROOT = Path("E:/Quant-Vault")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "")
MARKET = "TW"

def run():
    symbols = json.loads((DATA_DIR / "explorer_pool_tw.json").read_text())["symbols"][:500]
    news = json.loads((DATA_DIR / "news_cache.json").read_text())

    results = []
    for sym in symbols:
        score = 0.0
        for n in news.get(sym, []):
            days = (datetime.now() - datetime.fromisoformat(n["date"])).days
            score += n["impact"] * news_decay(days)
        results.append((sym, score))

    top5 = sorted(results, key=lambda x: x[1], reverse=True)[:5]

    msg = f"📊 台股 AI 進階預測報告（{datetime.now().date()}）\n\n"
    msg += "🔍 AI 海選 Top 5（盤後）\n"

    for sym, score in top5:
        rec = VaultBacktestRecord(
            symbol=sym,
            market=MARKET,
            date=str(datetime.now().date()),
            pred_ret=score / 100,
            confidence=min(abs(score), 100),
            source="AI_TW",
            used_by=["DISCORD"]
        )
        write_backtest(rec)
        msg += f"🟢 {sym}｜信心度 {rec.confidence:.0f}%\n"

    msg += "\n📊 近 5 日回測\n"
    for sym, _ in top5:
        s = summarize(read_last_n(sym, MARKET))
        if s:
            msg += f"{sym}：命中率 {s['hit_rate']*100:.1f}%\n"

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=10)

if __name__ == "__main__":
    run()
