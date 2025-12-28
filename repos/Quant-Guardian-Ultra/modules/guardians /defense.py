class DefenseManager:
    def __init__(self):
        self.level = "NORMAL"

    def evaluate(self, vix_value=None):
        """
        vix_value: float | None
        """
        if vix_value is None:
            return {"level": self.level, "action": "NO_DATA"}

        if vix_value >= 40:
            self.level = "L4"
            return {"level": "L4", "action": "FULL_STOP"}

        if vix_value >= 30:
            self.level = "L3"
            return {"level": "L3", "action": "REDUCE"}

        if vix_value >= 20:
            self.level = "L2"
            return {"level": "L2", "action": "CAUTION"}

        self.level = "L1"
        return {"level": "L1", "action": "NORMAL"}
