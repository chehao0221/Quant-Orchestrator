import os
import sys
from typing import List

from utils.discord_notifier import send_system_message

# --------------------------------------------------
# Vault Root 由環境變數提供（鐵律）
# --------------------------------------------------

VAULT_ROOT = os.environ.get("VAULT_ROOT")

REQUIRED_DIRS: List[str] = [
    "LOCKED_RAW",
    "LOCKED_DECISION",
    "STOCK_DB",
    "TEMP_CACHE",
    "LOG",
]


# --------------------------------------------------

def _halt(webhook: str, fingerprint: str, message: str) -> None:
    """
    系統級中止：
    - 一定嘗試發 Discord
    - 一定 exit
    """
    try:
        send_system_message(
            webhook=webhook,
            fingerprint=fingerprint,
            content=message
        )
    finally:
        sys.exit(1)


def assert_vault_ready(webhook: str) -> bool:
    """
    🚨 鐵律入口
    - 所有 AI / 發文 / 決策腳本第一行必須呼叫
    - ❌ 不寫 Vault
    - ❌ 不刪資料
    - ❌ 不產生任何 AI 結論
    """

    # 0️⃣ VAULT_ROOT 是否設定
    if not VAULT_ROOT:
        _halt(
            webhook,
            "vault_root_env_missing",
            "🛑 系統安全中止\n\n"
            "未設定 VAULT_ROOT 環境變數。\n"
            "系統已停止，未產生任何 AI 結論。"
        )

    # 1️⃣ Root 是否存在
    if not os.path.exists(VAULT_ROOT):
        _halt(
            webhook,
            f"vault_missing_{VAULT_ROOT}",
            "🛑 系統安全中止\n\n"
            f"找不到 Vault 路徑：\n{VAULT_ROOT}\n\n"
            "可能原因：\n"
            "- 外接硬碟未掛載\n"
            "- 磁碟代號改變\n"
            "- 權限異常\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )

    # 2️⃣ 基本結構是否齊全（只檢查存在）
    for d in REQUIRED_DIRS:
        path = os.path.join(VAULT_ROOT, d)
        if not os.path.isdir(path):
            _halt(
                webhook,
                f"vault_structure_missing_{d}",
                "🛑 系統安全中止\n\n"
                f"Vault 結構缺失資料夾：\n{path}\n\n"
                "此狀態可能導致：\n"
                "- AI 誤判\n"
                "- 狀態不同步\n"
                "- 回測失真\n\n"
                "系統已停止，未產生任何 AI 結論。"
            )

    # 3️⃣ 最低讀取權限
    if not os.access(VAULT_ROOT, os.R_OK):
        _halt(
            webhook,
            "vault_permission_denied",
            "🛑 系統安全中止\n\n"
            f"Vault 存在但無讀取權限：\n{VAULT_ROOT}\n\n"
            "請檢查磁碟權限或系統政策。\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )

    return True
