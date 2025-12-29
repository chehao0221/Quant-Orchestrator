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

WEBHOOK = os.getenv("DISCORD_WEBHOOK_TW", "").strip()
MARKET = "TW"

MAX_CORE_WATCH = 7

# ==================================================
# 消息時間衰退（台股）
# ==================================================
def news_decay(days_ago: int) -> float:
    if days_ago <= 1:
        return 1.0
    if days_ago <= 3:
        return 0.7
    if days_ago <= 7:
        return 0.4
    return 0.15

# ==================================================
# 主流程
# ==================================================
def run():
    # --------------------------------------------------
    # Explorer Pool（成交量 / 市值前段）
    # --------------------------------------------------
    pool_path = DATA_DIR / "explorer_pool_tw.json"
    if not pool_path.exists():
        print("[TW] explorer_pool 不存在，跳過")
        return

    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    symbols = pool.get("symbols", [])[:500]

    # --------------------------------------------------
    # News Cache（時間衰退）
    # --------------------------------------------------
    news_path = DATA_DIR / "news_cache.json"
    news_data = (
        json.loads(news_path.read_text(encoding="utf-8"))
        if news_path.exists()
        else {}
    )

    # --------------------------------------------------
    # 固定標（Vault）
    # --------------------------------------------------
    core_watch_path = (
        VAULT_ROOT / "STOCK_DB" / MARKET / "core_watch" / "core_watch.json"
    )
    core_watch = []
    if core_watch_path.exists():
        core_watch = json.loads(core_watch_path.read_text(encoding="utf-8"))

    scores = {}

    # --------------------------------------------------
    # 分數計算（技術指標已在前段處理）
    # 這裡專注：消息 × 時間衰退
    # --------------------------------------------------
    for sym in symbols:
        score = 0.0
        for n in news_data.get(sym, []):
            try:
                days = (datetime.now() - datetime.fromisoformat(n["date"])).days
                score += n.get("impact", 0.0) * news_decay(days)
            except Exception:
                continue
        scores[sym] = score

    # --------------------------------------------------
    # 海選 Top5（潛力股）
    # --------------------------------------------------
    top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

    # --------------------------------------------------
    # 固定標補位（真正的汰換在 Vault）
    # --------------------------------------------------
    for sym, _ in top5:
        if sym not in core_watch:
            core_watch.append(sym)

    core_watch = core_watch[:MAX_CORE_WATCH]

    core_watch_path.parent.mkdir(parents=True, exist_ok=True)
    core_watch_path.write_text(
        json.dumps(core_watch, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Discord 顯示內容
    # --------------------------------------------------
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 台股 AI 進階預測報告（{date_str}）\n\n"

    msg += "🔍 AI 海選 Top 5（盤後資料完整條件）\n"
    for sym, score in top5:
        confidence = min(abs(score) * 10, 100)
        emoji = "🟢" if confidence >= 60 else "🟡" if confidence >= 40 else "🔴"

        record = VaultBacktestRecord(
            symbol=sym,
            market=MARKET,
            date=str(datetime.now().date()),
            pred_ret=score / 100,
            confidence=confidence,
            source="AI_TW",
            used_by=["DISCORD"],
        )
        write_backtest(record)

        msg += f"{emoji} {sym}｜信心度 {confidence:.0f}%\n"

    # --------------------------------------------------
    # 固定標顯示（一定顯示）
    # --------------------------------------------------
    msg += "\n👁 核心監控清單（固定標｜最多 7 檔）\n"
    for sym in core_watch:
        msg += f"• {sym}\n"

    # --------------------------------------------------
    # 近 5 日回測（Vault）
    # --------------------------------------------------
    msg += "\n📊 近 5 日回測（歷史觀測）\n"
    for sym, _ in top5:
        summary = summarize(read_last_n(sym, MARKET, 5))
        if not summary:
            continue
        msg += (
            f"{sym}｜命中率 {summary['hit_rate']*100:.1f}% "
            f"｜平均報酬 {summary['avg_ret']:+.2%}\n"
        )

    msg += "\n💡 模型為機率推估，僅供研究參考，非投資建議。"

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg[:1900]}, timeout=10)

# ==================================================
if __name__ == "__main__":
    run()
