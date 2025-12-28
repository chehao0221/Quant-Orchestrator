import os
import requests
from datetime import datetime


class Notifier:
    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
        }

    def send(self, message: str, channel: str = "general"):
        webhook = self.webhooks.get(channel)
        if not webhook:
            print(f"[WARN] Discord Webhook 未設定（{channel}）")
            return

        payload = {"content": message}
        try:
            requests.post(webhook, json=payload, timeout=10)
        except Exception as e:
            print(f"[ERROR] Discord 通知失敗：{e}")

    def heartbeat(self):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        msg = (
            "🛡 Guardian 系統心跳回報\n\n"
            "系統狀態：正常監控中\n"
            f"檢查時間：{now}\n"
            "模式：風險監控待命\n\n"
            "備註：系統已完成本次例行檢查，未偵測到異常風險。"
        )
        self.send(msg, "general")


# 向後相容
DiscordNotifier = Notifier
