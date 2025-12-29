from datetime import datetime
from .schema import VaultEvent

def compute_weight(event: VaultEvent) -> float:
    base = event.weight

    if not event.decay:
        return base

    age_days = (datetime.utcnow() - event.timestamp).days
    decay_factor = max(0.1, 1 - age_days * 0.15)

    return round(base * decay_factor, 3)
