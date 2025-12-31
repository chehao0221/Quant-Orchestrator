# Vault 根目錄安全守門（封頂最終版）
# ✅ 不寫死任何實體路徑
# ✅ Vault Root 只來自環境變數
# ✅ 只做「存在 / 結構 / 權限」檢查
# ❌ 不寫 Vault
# ❌ 不刪資料
# ❌ 不產生 AI 判斷
# ❌ 不介入 Guardian / Stock-Genius 邏輯

import os
import sys
from utils.discord_notifier import send_system_message


# ==============================
# 環境設定（鐵律）
# ==============================

VAULT_ROOT_ENV = "QUANT_VAULT_ROOT"  # 例如設為 E:\Quant-Vault

REQUIRED_DIRS = [
    "LOCKED_RAW",
    "LOCKED_DECISION",
    "STOCK_DB",
    "TEMP_CACHE",
    "LOG",
]


# ==============================
# 內部工具
# ==============================

def _system_halt(webhook: str, fingerprint: str, message: str):
    """
    系統級中止：
    - 一定嘗試送 Discord
    - 一定 exit
    """
    send_system_message(
        webhook=webhook,
        fingerprint=fingerprint,
        content=message
    )
    sys.exit(1)


# ==============================
# 對外 API（鐵律入口）
# ==============================

def assert_vault_ready(webhook: str) -> bool:
    """
    🚨 Vault 安全入口（所有 AI / 發文 / Orchestrator 第一行必須呼叫）

    僅檢查：
    - Vault Root 是否存在
    - 必要資料夾是否齊全
    - 是否具備讀取權限

    不做：
    - 寫入
    - 刪除
    - AI 判斷
    """

    vault_root = os.environ.get(VAULT_ROOT_ENV)

    # 1️⃣ 是否設定 Vault Root
    if not vault_root:
        msg = (
            "🛑 系統安全中止\n\n"
            f"未設定環境變數：{VAULT_ROOT_ENV}\n\n"
            "請先在系統或 CI 中設定 Vault 實體路徑。\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint="vault_root_env_missing",
            message=msg
        )

    # 2️⃣ Vault Root 是否存在
    if not os.path.exists(vault_root):
        msg = (
            "🛑 系統安全中止\n\n"
            f"找不到 Vault 路徑：\n{vault_root}\n\n"
            "可能原因：\n"
            "- 外接硬碟未掛載\n"
            "- 路徑錯誤\n"
            "- 權限異常\n\n"
            "系統已停止，未產生任何 AI 結論。"
        )
        _system_halt(
            webhook=webhook,
            fingerprint=f"vault_missing_{vault_root}",
            message=msg
        )

    # 3️⃣ 基本結構檢查（只檢查存在）
    for d in REQUIRED_DIRS:
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
                message=msg
            )

    # 4️⃣ 最低權限檢查（唯讀即可）
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
            message=msg
        )

    # 5️⃣ 全部通過（不回傳任何狀態資訊）
    return True
