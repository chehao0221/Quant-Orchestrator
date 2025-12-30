import os
from datetime import datetime
from writer import safe_write

VAULT_ROOT = r"E:\Quant-Vault"


def write_snapshot(market: str, snapshot_text: str) -> bool:
    """
    系統快照寫入（可供 AI / 人類回溯）
    """
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(
        VAULT_ROOT,
        "TEMP_CACHE",
        "snapshot",
        f"{market}_{ts}.txt"
    )
    return safe_write(path, snapshot_text)
