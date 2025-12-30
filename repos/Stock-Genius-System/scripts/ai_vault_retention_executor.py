# Vault 冷資料 AI 自動治理執行器（F+ 最終封頂版）
# 功能：時間衰退判斷 → AI 信任檢查 → 備份 → 刪除 → 審計
# ❌ 不碰 LOCKED_* ❌ 不可逆刪除 ❌ 無審計不動刀

import os
from datetime import datetime

from vault_cold_file_scanner import scan
from retention_judge_ai import judge
from vault_safe_deleter import safe_delete
from ai_confidence_guard import is_ai_trusted
from ai_performance_summary import summarize
from vault_event_store import load_recent_backtests

# ===== 基本設定 =====
VAULT_PATH = r"E:\Quant-Vault"
AUDIT_LOG = r"E:\Quant-Vault\LOG\vault_deletion_audit.log"

# ===== 工具 =====
def log(msg: str):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ===== 主流程 =====
def main():
    # 1️⃣ 檢查 AI 是否有資格動刀
    backtests = load_recent_backtests(limit=50)

    if not backtests:
        log("[ABORT] No backtest data. Skip retention.")
        return

    perf = summarize(backtests)

    if not is_ai_trusted({
        "hit_rate": perf["hit_rate"],
        "samples": len(backtests)
    }):
        log("[ABORT] AI confidence insufficient. Skip deletion.")
        return

    # 2️⃣ 掃描冷資料
    cold_files = scan(VAULT_PATH)

    if not cold_files:
        log("[INFO] No cold files detected.")
        return

    # 3️⃣ 逐一判斷（時間衰退 + 多重鐵律）
    for f in cold_files:
        path = f["path"]
        age_days = f["age_days"]

        # 絕對防線
        if "LOCKED_" in path:
            continue

        # 僅允許特定路徑
        if not (
            r"\STOCK_DB\" in path or
            r"\TEMP_CACHE\" in path
        ):
            continue

        # 時間衰退 AI 判斷
        decision = judge(f)

        # 未達刪除建議 → 跳過
        if not decision["recommend_delete"]:
            continue

        # 再一道硬保險：2 年以下不動刀
        if age_days < 730:
            continue

        # 4️⃣ 執行安全刪除（含備份）
        result = safe_delete(path)
        ts = datetime.utcnow().isoformat()

        if result.get("ok"):
            log(
                f"[{ts}] DELETED | {path} "
                f"| archived={result['archived_to']} "
                f"| retain_score={decision['retain_score']} "
                f"| decay={decision['time_decay']}"
            )
        else:
            log(
                f"[{ts}] SKIP | {path} "
                f"| reason={result.get('reason')}"
            )

# ===== 入口 =====
if __name__ == "__main__":
    main()
