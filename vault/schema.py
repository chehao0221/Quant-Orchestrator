from dataclasses import dataclass
from datetime import datetime
from typing import Literal

EventType = Literal["BLACK_SWAN", "MAJOR_NEWS", "NORMAL_NEWS"]

@dataclass
class VaultEvent:
    id: str
    event_type: EventType
    title: str
    source: str
    timestamp: datetime
    weight: float
    decay: bool
