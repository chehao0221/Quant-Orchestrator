from dataclasses import dataclass
from typing import List

@dataclass
class VaultBacktestRecord:
    symbol: str
    market: str
    date: str
    pred_ret: float
    confidence: float
    source: str            # AI_TW / AI_US
    used_by: List[str]
