# AI Council 溝通橋樑（唯一合法通道）

from datetime import datetime

class AICouncilBridge:
    def __init__(self):
        self._opinions = []

    def submit(self, ai_name: str, payload: dict):
        self._opinions.append({
            "ai": ai_name,
            "payload": payload,
            "ts": datetime.utcnow().isoformat()
        })

    def collect(self):
        return list(self._opinions)

    def summary(self):
        return {
            "count": len(self._opinions),
            "sources": [o["ai"] for o in self._opinions]
        }

    def clear(self):
        self._opinions.clear()
