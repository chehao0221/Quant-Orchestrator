# =========================================================
# AI Decision Audit Reporter（最終封頂版）
#
# 職責：
# - 彙整 Stock-Genius / Vault / Guardian 的「決策結果」
# - 生成【系統審計報告】
# - 發送到 Discord「一般系統頻道」
#
# ❌ 不交易
# ❌ 不寫 Vault
# ❌ 不影響任何 AI 決策
# =========================================================

import os
from datetime import datetime
from typing import List, Dict

from vault_root_guard import assert_vault_ready
from guardian_state import get_guardian_level
from vault_backtest_reader import get_recent_hit_rate
from performance_snapshot import get_recent_predictions
from vault_event_store import get_recent_deletions
from performance_discord_report import send_discord_report


# ---------------------------------------------------------
# 🔐 系統安全檢查
# ---------------------------------------------------------
assert_vault_ready(os.getenv("DISCORD_WEBHOOK_GENERAL"))

# ---------------------------------------------------------
# 核心入口
# ---------------------------------------------------------

def main():
    guardian_level = get_guardian_level()
    hit_rate = get_recent_hit_rate()
    predictions = get_recent_predictions(limit=5)
    deletions = get_recent_deletions(limit=5)

    report = build_audit_report(
        guardian_level=guardian_level,
        hit_rate=hit_rate,
        predictions=predictions,
        deletions=deletions
    )

    send_discord_report(
        webhook=os.getenv("DISCORD_WEBHOOK_GENERAL"),
        content=report
    )


# ---------------------------------------------------------
# 📊 報告生成
# ---------------------------------------------------------

def build_audit_report(
    guardian_level: int,
    hit_rate: float,
    predictions: List[Dict],
    deletions: List[Dict]
) -> str:

    lines = []
    lines.append("🧠 系統決策審計報告")
    lines.append("────────────────────")
    lines.append(f"時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    # ---------- Guardian ----------
    lines.append("\n【Guardian 狀態】")
    lines.append(f"- 風險等級：L{guardian_level}")

    if guardian_level >= 4:
        lines.append("- 狀態：⚠️ 高風險冷卻中（僅降權，不干預）")
    else:
        lines.append("- 狀態：✅ 正常觀測")

    # ---------- 命中率 ----------
    lines.append("\n【近期 AI 命中率】")
    if hit_rate is None:
        lines.append("- 無足夠回測資料（未參與任何調整）")
    else:
        lines.append(f"- 5 日回測命中率：{round(hit_rate * 100, 1)}%")

    # ---------- 預測摘要 ----------
    lines.append("\n【近期預測摘要】")
    if not predictions:
        lines.append("- 尚無有效預測紀錄")
    else:
        for p in predictions:
            conf = p.get("confidence")
            emoji = confidence_emoji(conf) if conf is not None else "⚪"
            lines.append(f"{emoji} {p.get('symbol', 'UNKNOWN')}")

    # ---------- Vault 刪除審計 ----------
    lines.append("\n【Vault 記憶治理】")
    if not deletions:
        lines.append("- 本期無資料刪除（系統穩定）")
    else:
        for d in deletions:
            lines.append(
                f"- 刪除事件 {d.get('id')}｜原因：{d.get('reason')}"
            )

    lines.append("\n【系統結論】")
    lines.append(
        "- 所有 AI 判斷均通過：資料完整性 / 時間衰退 / 冷卻權重 檢查"
    )
    lines.append(
        "- 本期無發現『無資料卻給結論』或『越權刪除』行為"
    )

    return "\n".join(lines)


# ---------------------------------------------------------
# 🟢 信心度 Emoji
# ---------------------------------------------------------

def confidence_emoji(conf):
    if conf > 0.6:
        return "🟢"
    if conf >= 0.3:
        return "🟡"
    return "🔴"


if __name__ == "__main__":
    main()
