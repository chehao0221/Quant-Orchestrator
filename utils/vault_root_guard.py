import os
import sys
from discord_system_notifier import send_system_message

VAULT_ROOT = r"E:\Quant-Vault"

def assert_vault_ready(webhook: str):
    if not os.path.exists(VAULT_ROOT):
        msg = (
            "🛑 系統安全中止\n\n"
            f"找不到 Vault 路徑：{VAULT_ROOT}\n"
            "可能原因：\n"
            "- 外接硬碟未掛載\n"
            "- 路徑錯誤\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )

        send_system_message(
            webhook=webhook,
            fingerprint=f"vault_missing_{VAULT_ROOT}",
            content=msg
        )
        sys.exit(1)
