# repos/Quant-Guardian-Ultra/core/notifier.py
import os
import requests
from datetime import datetime


class DiscordNotifier:
    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
        }

    def _send(self, webhook_url: str, content: str):
        if not webhook_url:
            raise RuntimeError("Discord Webhook 未設定")

        response = requests.post(
            webhook_url,
            json={"content": content},
            timeout=10,
        )
        response.raise_for_status()

    # ===== 公開 API =====

    def send_general(self, message: str):
        self._send(self.webhooks["general"], message)

    def send_black_swan(self, message: str):
        self._send(self.webhooks["black_swan"], message)

    def send_us(self, message: str):
        self._send(self.webhooks["us"], message)

    def send_tw(self, message: str):
        self._send(self.webhooks["tw"], message)

    # ===== 系統心跳（只走 general）=====

    def send_heartbeat(self, status: str = "正常監控中"):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        message = (
            "🛡 **Guardian 系統心跳回報**\n\n"
            f"系統狀態：{status}\n"
            f"檢查時間：{now}\n"
            "模式：風險監控待命\n\n"
            "備註：系統已完成本次例行檢查，未偵測到異常風險。"
        )
        self.send_general(message)
