from datetime import datetime


class NewsScanner:
    """
    新聞掃描器
    - 透過 DataManager 進行新聞去重
    - scan() 回傳本次「新新聞事件」列表
    """

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def scan(self) -> list:
        """
        回傳：
          [
            {"title": "...", "time": "..."},
            ...
          ]
        """
        # ⚠️ 目前為保守實作（stub）
        # 你之後可以替換為 RSS / API
        fetched_news = self._fetch_news()

        new_events = []

        for news in fetched_news:
            key = f"{news['title']}-{news['time']}"
            if not self.data_manager.is_news_seen(key):
                self.data_manager.mark_news_seen(key)
                new_events.append(news)

        return new_events

    # -------------------------------------------------
    # 內部：新聞來源（目前 stub）
    # -------------------------------------------------

    def _fetch_news(self) -> list:
        """
        模擬新聞來源（不造成 runtime 失敗）
        """
        return [
            {
                "title": "市場觀望聯準會政策動向",
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            }
        ]
