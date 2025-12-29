import os
import json
from datetime import datetime
from pathlib import Path
import requests

from vault.vault_backtest_writer import write_backtest
from vault.vault_backtest_reader import read_last_n
from vault.vault_backtest_validator import summarize
from vault.schema import VaultBacktestRecord

# ==================================================
# 基本設定
# ==================================================
VAULT_ROOT = Path("E:/Quant-Vault")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

WEBHOOK = os.getenv("DISCORD_WEBHOOK_US", "").strip()
MARKET = "US"

MAX_CORE_WATCH = 7

# ==================================================
# 輔助：消息時間衰退
# ==================================================
def news_decay(days_ago: int) -> float:
    if days_ago <= 1:
        return 1.0
    if days_ago <= 3:
        return 0.6
    if days_ago <= 7:
        return 0.3
    return 0.1

# ==================================================
# 主流程
# ==================================================
def run():
    # Explorer pool（成交量前 500）
    pool_path = DATA_DIR / "explorer_pool_us.json"
    if not pool_path.exists():
        return

    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    symbols = pool.get("symbols", [])[:500]

    # News cache
    news_path = DATA_DIR / "news_cache.json"
    news_data = json.loads(news_path.read_text(encoding="utf-8")) if news_path.exists() else {}

    # Core watch（歷史固定標）
    core_watch_path = VAULT_ROOT / "STOCK_DB" / MARKET / "core_watch" / "core_watch.json"
    core_watch = []
    if core_watch_path.exists():
        core_watch = json.loads(core_watch_path.read_text(encoding="utf-8"))

    scores = {}

    # ==================================================
    # 計算分數（技術指標已前處理，這裡聚焦消息）
    # ==================================================
    for sym in symbols:
        score = 0.0
        for n in news_data.get(sym, []):
            days = (datetime.now() - datetime.fromisoformat(n["date"])).days
            score += n.get("impact", 0.0) * news_decay(days)
        scores[sym] = score

    # ==================================================
    # 海選 Top5
    # ==================================================
    top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

    # ==================================================
    # 固定標補位（衰退權重由 Vault 內部管理）
    # ==================================================
    for sym, _ in top5:
        if sym not in core_watch:
            core_watch.append(sym)

    core_watch = core_watch[:MAX_CORE_WATCH]

    # 回寫 core_watch
    core_watch_path.parent.mkdir(parents=True, exist_ok=True)
    core_watch_path.write_text(
        json.dumps(core_watch, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # ==================================================
    # Discord 顯示
    # ==================================================
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 美股 AI 進階預測報告（{date_str}）\n\n"

    msg += "🔍 AI 海選 Top 5（盤後｜成交量前 500）\n"
    for sym, score in top5:
        confidence = min(abs(score) * 10, 100)
        emoji = "🟢" if confidence >= 60 else "🟡" if confidence >= 40 else "🔴"

        record = VaultBacktestRecord(
            symbol=sym,
            market=MARKET,
            date=str(datetime.now().date()),
            pred_ret=score / 100,
            confidence=confidence,
            source="AI_US",
            used_by=["DISCORD"]
        )
        write_backtest(record)

        msg += f"{emoji} {sym}｜信心度 {confidence:.0f}%\n"

    msg += "\n👁 核心監控清單（長期觀察｜可汰舊換新）\n"
    for sym in core_watch:
        msg += f"• {sym}\n"

    msg += "\n📊 近 5 日回測（歷史觀測）\n"
    for sym, _ in top5:
        s = summarize(read_last_n(sym, MARKET, 5))
        if s:
            msg += (
                f"{sym}｜命中率 {s['hit_rate']*100:.1f}% "
                f"｜平均報酬 {s['avg_ret']:+.2%}\n"
            )

    msg += "\n💡 模型為機率推估，僅供研究參考，非投資建議。"

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=10)

# ==================================================
if __name__ == "__main__":
    run()
