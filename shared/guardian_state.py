import json
import os
from datetime import datetime, timedelta

GUARDIAN_STATE_FILE = os.path.join(
    os.path.dirname(__file__),
    "guardian_state.json"
)

# Guardian 狀態有效時間（防止讀到過期狀態）
MAX_STATE_AGE = timedelta(minutes=120)

class GuardianStateError(Exception):
    pass

def load_guardian_state():
    """
    唯一合法讀取 Guardian 狀態的入口
    """
    if not os.path.exists(GUARDIAN_STATE_FILE):
        raise GuardianStateError("Guardian 狀態檔不存在")

    try:
        with open(GUARDIAN_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        raise GuardianStateError(f"Guardian 狀態讀取失敗：{e}")

    # 必要欄位檢查
    for key in ("level", "updated_at"):
        if key not in state:
            raise GuardianStateError(f"Guardian 狀態缺少欄位：{key}")

    # 時間戳檢查
    try:
        updated_at = datetime.fromisoformat(state["updated_at"])
    except Exception:
        raise GuardianStateError("Guardian updated_at 格式錯誤")

    if datetime.utcnow() - updated_at > MAX_STATE_AGE:
        raise GuardianStateError("Guardian 狀態已過期")

    return state

def get_guardian_level():
    """
    給 Stock-Genius 使用的安全入口
    """
    state = load_guardian_state()
    return state["level"]
