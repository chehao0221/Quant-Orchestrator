import os
import requests
from datetime import datetime

# ==================================================
# Discord Notifier（Final）
# ==================================================

class Notifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_GENERAL")

    def notify(self, level: int, decision, changed: bool):
        """
        只有在風險等級變化時才發送通知
        """
        if not changed:
            return

        if not self.webhook_url:
            print("[Notifier] DISCORD_WEBHOOK_GENERAL not set")
            return

        payload = self._build_payload(level, decision)
        self._send(payload)

    # --------------------------------------------------

    def _build_payload(self, level: int, decision) -> dict:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # === 視覺定義 ===
        if level >= 4:
            color = 15158332  # RED
            emoji = "🔴"
            title = "Guardian 判定：高風險，系統凍結"
        elif level == 3:
            color = 15844367  # YELLOW
            emoji = "🟡"
            title = "Guardian 風控提醒：風險升溫"
        else:
            color = 3066993   # GREEN
            emoji = "🟢"
            title = "Guardian 狀態更新：市場穩定"

        description = (
            f"**市場狀態**：{decision.description}\n"
            f"**風險等級**：L{decision.level}\n"
            f"**系統狀態**：{'凍結中' if decision.freeze else '正常運行'}"
        )

        return {
            "embeds": [
                {
                    "title": f"{emoji} {title}",
                    "description": description,
                    "color": color,
                    "footer": {
                        "text": f"Quant-Orchestrator • {now}"
                    }
                }
            ]
        }

    # --------------------------------------------------

    def _send(self, payload: dict):
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"[Notifier] Failed to send message: {e}")
