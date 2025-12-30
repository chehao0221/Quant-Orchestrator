import os
import sys
from datetime import datetime
from discord_system_notifier import send_system_message

# === Vault 實體根目錄（鐵律）===
VAULT_ROOT = r"E:\Quant-Vault"

# === 系統最小結構需求（只檢查存在）===
REQUIRED_DIRS = [
    "LOCKED_RAW",
    "LOCKED_DECISION",
    "STOCK_DB",
    "TEMP_CACHE",
    "LOG",
]

def _system_halt(webhook: str, fingerprint: str, message: str):
    """
    系統級中止：
    - 一定發 Discord
    - 一定 exit
    """
    send_system_message(
        webhook=webhook,
        fingerprint=fingerprint,
        content=message
    )
    sys.exit(1)

def assert_vault_ready(webhook: str):
    """
    🚨 鐵律入口：
    - 所有 AI / 發文 / 判斷腳本的第一行必須呼叫
    - ❌ 不寫 Vault
    - ❌ 不刪資料
    - ❌ 不給 AI 結論
    """

    # 1️⃣ Vault Root 是否存在（你原本就有，保留）
    if not os.path.exists(VAULT_ROOT):
        msg = (
            "🛑 系統安全中止\n\n"
            f"找不到 Vault 路徑：{VAULT_ROOT}\n\n"
            "可能原因：\n"
            "- 外接硬碟未掛載\n"
            "- 磁碟代號改變\n"
            "- 權限異常\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint=f"vault_missing_{VAULT_ROOT}",
            message=msg
        )

    # 2️⃣ 基本結構檢查（不檢查是否有檔案）
    for d in REQUIRED_DIRS:
        path = os.path.join(VAULT_ROOT, d)
        if not os.path.isdir(path):
            msg = (
                "🛑 系統安全中止\n\n"
                f"Vault 結構不完整，缺失資料夾：\n{path}\n\n"
                "此狀態可能導致：\n"
                "- AI 誤判\n"
                "- 狀態不同步\n"
                "- 回測失真\n\n"
                "系統已停止，未產生任何 AI 結論。"
            )
            _system_halt(
                webhook=webhook,
                fingerprint=f"vault_structure_missing_{d}",
                message=msg
            )

    # 3️⃣ 最低權限檢查（只讀即可）
    if not os.access(VAULT_ROOT, os.R_OK):
        msg = (
            "🛑 系統安全中止\n\n"
            f"Vault 存在但無讀取權限：\n{VAULT_ROOT}\n\n"
            "請檢查磁碟權限或系統政策。\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint="vault_permission_denied",
            message=msg
        )

    # 4️⃣ 通過檢查（什麼都不做，讓主流程繼續）
    return True
