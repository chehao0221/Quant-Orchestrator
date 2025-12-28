import random


class VixScanner:
    def scan(self):
        """
        模擬 VIX 指數（真實情況可接 API）
        """
        return round(random.uniform(15, 45), 2)
