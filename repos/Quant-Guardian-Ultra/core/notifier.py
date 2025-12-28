import requests
import os
from datetime import datetime

# ==================================================
# Discord Notifier（Guardian v2 / dict-compatible）
# ==================================================

class Notifier:
    def __init__(self):
        self.webhook_general = os.getenv("DISCORD_WEBHOOK_GENERAL")
        self.webhook_black = os.getenv("DISCORD_WEBHOOK_BLACK_SWAN")

    def notify(self, decision: dict):
        """
        decision 來自 GuardianEngine.run()
        為 dict，不是物件
        """

        # 只在「狀態變化」時通知
        if not decision.get("level_changed", False):
            return

        level = decision["level"]
        color_name = decision["color"]
        description = decision["description"]
        freeze = decision["freeze"]

        # webhook 分流
        webhook = (
            self.webhook_black if level >= 5 else self.webhook_general
        )
        if not webhook:
            return

        # 顏色 & 標題
        if level >= 4:
            color = 15158332  # RED
            emoji = "🔴"
            title = "Guardian 判定：高風險，系統凍結"
        elif level == 3:
            color = 15105570  # YELLOW
            emoji = "🟡"
            title = "Guardian 風控提醒：風險升溫"
        else:
            color = 3066993   # GREEN
            emoji = "🟢"
            title = "Guardian 狀態更新：市場穩定"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        payload = {
            "embeds": [
                {
                    "title": f"{emoji} {title}",
                    "description": (
                        f"**市場狀態**：{description}\n"
                        f"**風險等級**：L{level}\n"
                        f"**系統狀態**：{'凍結中' if freeze else '正常運行'}"
                    ),
                    "color": color,
                    "footer": {
                        "text": f"Quant-Orchestrator • {now}"
                    }
                }
            ]
        }

        try:
            requests.post(webhook, json=payload, timeout=10)
        except Exception as e:
            print(f"[Notifier] Failed to send message: {e}")
