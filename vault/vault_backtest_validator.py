from typing import List
from .schema import BacktestRecord

def validate(records: List[BacktestRecord]) -> List[BacktestRecord]:
    """
    回傳：可被 Vault / AI 採信的回測
    """

    valid = []

    for r in records:
        # ❶ 預測與實際不能為 0 垃圾
        if abs(r.pred_return) < 0.0001:
            continue

        # ❷ 信心度太低 → 不影響任何權重
        if r.confidence < 0.3:
            continue

        # ❸ 超短 horizon 不可信
        if r.horizon < 3:
            continue

        valid.append(r)

    return valid
