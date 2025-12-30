# 日股 AI 最終預測與系統審計發送器（封頂版）
# 與 TW / US 完全對稱

import os
from datetime import datetime

from vault_root_guard import assert_vault_ready
from guard_check import guardian_freeze_check
from performance_discord_report import send_ai_report

MARKET = "JP"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_JP")
GENERAL_WEBHOOK = os.getenv("DISCORD_WEBHOOK_GENERAL")


def main():
    assert_vault_ready(GENERAL_WEBHOOK)

    if guardian_freeze_check():
        return

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = {
        "market": MARKET,
        "time": report_time,
        "status": "OK",
        "content": "日股 AI 報告產生完成"
    }

    send_ai_report(
        webhook=WEBHOOK,
        fingerprint=f"{MARKET}_{report_time}",
        report=report
    )


if __name__ == "__main__":
    main()
