import os
from vault_root_guard import assert_vault_ready

VAULT_ROOT = r"E:\Quant-Vault"


def safe_write(path: str, content: str) -> bool:
    """
    最底層安全寫入：
    - Vault 必須存在
    - 成功 / 失敗明確回傳
    """
    assert_vault_ready(None)

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False
