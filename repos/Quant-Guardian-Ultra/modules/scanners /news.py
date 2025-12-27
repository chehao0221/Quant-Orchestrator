import feedparser
import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_FILE = os.path.join(BASE_DIR, "data", "system", "state.json")

class NewsScanner:
    def scan(self):
        feed = feedparser.parse(
            "https://news.google.com/rss/search?q=股市+崩盤+戰爭+黑天鵝&hl=zh-TW&gl=TW"
        )

        # === Load state.json（若不存在就初始化）===
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        else:
            state = {}

        news_seen = state.get("news_seen", [])
        if not isinstance(news_seen, list):
            news_seen = []

        level = 1
        news_titles = []

        keywords = ["崩盤", "戰爭", "暴跌", "黑天鵝", "斷頭", "大跌"]

        for entry in feed.entries[:8]:
            if not any(kw in entry.title for kw in keywords):
                continue

            news_hash = hashlib.md5(entry.title.encode("utf-8")).hexdigest()

            if news_hash in news_seen:
                continue

            level = 4
            news_titles.append(entry.title)
            news_seen.append(news_hash)

        # cache 上限
        news_seen = news_seen[-50:]

        # 回寫 state（向下相容）
        state["news_seen"] = news_seen
        if news_seen:
            state["last_news_hash"] = news_seen[-1]

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        return level, news_titles
