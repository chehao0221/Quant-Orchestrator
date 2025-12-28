class DefenseManager:
    """
    Guardian 防禦決策器
    - 綜合 VIX 與新聞事件
    - 輸出風險等級 L1–L4 與行動
    """

    def evaluate(self, vix: float, news_events: list) -> dict:
        """
        參數：
          vix: VIX 指數
          news_events: 新聞事件列表

        回傳：
          {
            "level": "L1" | "L2" | "L3" | "L4",
            "action": "NONE" | "REDUCE" | "PAUSE"
          }
        """

        level = "L1"
        action = "NONE"

        # -------------------------------
        # VIX 判斷
        # -------------------------------
        if vix is None:
            level = "L1"
        elif vix >= 40:
            level = "L4"
            action = "PAUSE"
        elif vix >= 30:
            level = "L3"
            action = "REDUCE"
        elif vix >= 20:
            level = "L2"
            action = "CAUTION"

        # -------------------------------
        # 新聞事件加權
        # -------------------------------
        if news_events:
            # 有新新聞 → 至少提高一級
            if level == "L1":
                level = "L2"
            elif level == "L2":
                level = "L3"
                action = "REDUCE"

        return {
            "level": level,
            "action": action,
        }
