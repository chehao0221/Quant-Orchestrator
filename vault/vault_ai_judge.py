from pathlib import Path
import json
from vault_cold_classifier import classify


def judge(path: Path, meta: dict) -> dict:
    """
    AI 判斷是否可刪
    """
    temp = classify(path, meta)

    decision = {
        "path": str(path),
        "temperature": temp,
        "can_delete": temp == "COLD",
        "reason": "",
    }

    if temp == "COLD":
        decision["reason"] = "長期未使用，命中率與貢獻度低"
    elif temp == "WARM":
        decision["reason"] = "近期仍可能被回測或引用"
    else:
        decision["reason"] = "高價值或受保護資料"

    return decision
