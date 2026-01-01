class AICouncil:
    """
    AI 互相監督 / 評分 / 學習建議
    """

    def evaluate(self, reports: dict) -> dict:
        """
        回傳：
        {
          "trend": +0.05,
          "macro": -0.02,
          ...
        }
        """
        votes = {}
        for k, r in reports.items():
            votes[k] = r.get("score", 0) * 0.1
        return votes

    def supervise(self, state: dict) -> bool:
        """
        回傳 False = 阻止學習 / Freeze
        """
        if state.get("risk_level", 1) >= 4:
            return False
        return True
