import os
import requests
import json
from datetime import datetime


class Notifier:
    """
    Legacy Notifier（供 core.engine / core.__init__ 使用）
    """
    def __init__(self):
        self.webhook = os.getenv("DISCORD_WEBHOOK_URL")
        if not self.webhook:
            raise ValueError("DISCORD_WEBHOOK_URL 未設定")

    def send(self, message: str):
        payload = {
            "content": message
        }
        response = requests.post(
            self.webhook,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()


class DiscordNotifier(Notifier):
    """
    擴充型 Discord Notifier（含心跳）
    """

    # =========================
    # 🫀 Guardian 每日心跳（繁體中文）
    # =========================
    def send_heartbeat(self, status="正常監控中", note=""):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        message = (
            "🫀 **Guardian 系統心跳回報**\n\n"
            f"🟢 系統狀態：**{status}**\n"
            f"🕒 檢查時間：{now}\n"
            "🛡 模式：風險監控待命\n"
        )

        if note:
            message += f"\n📌 備註：{note}"

        self.send(message)
