# Vault 冷資料 AI 審計 Discord 報告（不刪檔）

import os
from notifier import send_discord_message
from vault_cold_file_scanner import scan
from retention_judge_ai import judge
from vault_retention_report import build_report

VAULT_PATH = r"E:\Quant-Vault"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_GENERAL")

def main():
    cold_files = scan(VAULT_PATH)

    judged = []
    for f in cold_files:
        decision = judge(f)
        if decision["recommend_delete"]:
            judged.append({**f, **decision})

    report = build_report(judged)
    send_discord_message(DISCORD_WEBHOOK, report)

if __name__ == "__main__":
    main()
