import os
import sys
from typing import List, Optional
from utils.discord_system_notifier import send_system_message


# ==============================
# Vault Root（由環境變數提供）
# ==============================

def _get_vault_root() -> Optional[str]:
    """
    從環境變數取得 Vault Root
    """
    return os.environ.get("VAULT_ROOT")


def _get_required_dirs() -> List[str]:
    """
    Vault 最小結構需求（只檢查存在）
    """
    return [
        "LOCKED_RAW",
        "LOCKED_DECISION",
        "STOCK_DB",
        "TEMP_CACHE",
        "LOG",
    ]


# ==============================
# 系統級中止（鐵律）
# ==============================

def _system_halt(webhook: str, fingerprint: str, message: str) -> None:
    """
    系統級中止：
    - 一定發 Discord
    - 一定 exit
    """
    send_system_message(
        webhook=webhook,
        fingerprint=fingerprint,
        content=message,
    )
    sys.exit(1)


# ==============================
# 對外唯一入口
# ==============================

def assert_vault_ready(webhook: str) -> bool:
    """
    🚨 鐵律入口：
    - 所有 AI / 發文 / 判斷腳本的第一行必須呼叫
    - ❌ 不寫 Vault
    - ❌ 不刪資料
    - ❌ 不給 AI 結論
    """

    vault_root = _get_vault_root()

    # 1️⃣ Vault Root 是否存在
    if not vault_root or not os.path.exists(vault_root):
        msg = (
            "🛑 系統安全中止\n\n"
            f"找不到 Vault 路徑：{vault_root}\n\n"
            "可能原因：\n"
            "- 外接硬碟未掛載\n"
            "- 環境變數 VAULT_ROOT 未設定\n"
            "- 磁碟代號改變\n"
            "- 權限異常\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint="vault_root_missing",
            message=msg,
        )

    # 2️⃣ 基本結構檢查（只檢查存在）
    for d in _get_required_dirs():
        path = os.path.join(vault_root, d)
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
                message=msg,
            )

    # 3️⃣ 最低權限檢查（只讀即可）
    if not os.access(vault_root, os.R_OK):
        msg = (
            "🛑 系統安全中止\n\n"
            f"Vault 存在但無讀取權限：\n{vault_root}\n\n"
            "請檢查磁碟權限或系統政策。\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint="vault_permission_denied",
            message=msg,
        )

    # 4️⃣ 通過檢查（什麼都不做）
    return True
