# AI Council 通訊匯流排（唯一合法溝通層）

class AICouncilBus:
    def __init__(self):
        self.messages = {}

    def publish(self, sender: str, payload: dict):
        self.messages[sender] = payload

    def collect(self):
        return self.messages.copy()

    def clear(self):
        self.messages.clear()
