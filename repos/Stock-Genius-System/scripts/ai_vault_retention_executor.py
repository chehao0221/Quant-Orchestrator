import os
from datetime import datetime

from vault_cold_file_scanner import scan
from retention_judge_ai import judge
from vault_safe_deleter import safe_delete
from ai_confidence_guard import is_ai_trusted
from ai_performance_summary import summarize
from vault_event_store import load_recent_backtests

VAULT_PATH = r"E:\Quant-Vault"
LOG_PATH = r"E:\Quant-Vault\LOG\vault_deletion_audit.log"

def log(msg: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def main():
    backtests = load_recent_backtests(limit=50)
    perf = summarize(backtests)

    if not is_ai_trusted({"hit_rate": perf["hit_rate"], "samples": len(backtests)}):
        log("[ABORT] AI confidence too low, skip deletion.")
        return

    cold_files = scan(VAULT_PATH)

    for f in cold_files:
        decision = judge(f)
        if not decision["recommend_delete"]:
            continue

        result = safe_delete(f["path"])
        ts = datetime.utcnow().isoformat()

        if result["ok"]:
            log(f"[{ts}] DELETED: {result['deleted']} -> {result['archived_to']}")
        else:
            log(f"[{ts}] SKIP: {f['path']} ({result['reason']})")

if __name__ == "__main__":
    main()
