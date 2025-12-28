import os
import json
import datetime
import requests


class DiscordNotifier:
    """
    Guardian Discord 通知器
    支援：
    - general（系統 / 心跳 / 停盤）
    - black_swan（黑天鵝）
    - us / tw（預留）
    """

    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
        }

    def _send(self, channel: str, content: str):
        url = self.webhooks.get(channel)
        if not url:
            print(f"[WARN] Discord Webhook 未設定（{channel}）")
            return

        payload = {
            "content": content
        }

        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code >= 300:
                print(f"[WARN] Discord 發送失敗（{channel}）：{r.status_code}")
        except Exception as e:
            print(f"[WARN] Discord 發送例外（{channel}）：{e}")

    # ==========================
    # 🫀 每日心跳
    # ==========================
    def heartbeat(self, mode: str = "風險監控待命"):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        msg = (
            "🫀 **Guardian 系統心跳回報**\n\n"
            f"系統狀態：正常監控中\n"
            f"模式：{mode}\n"
            f"檢查時間：{now:%Y-%m-%d %H:%M}（台灣）\n"
        )
        self._send("general", msg)

    # ==========================
    # 🛑 今日停盤公告（只送一次）
    # ==========================
    def trading_halt(self, level: str, reason: str):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        msg = (
            "🛑 **今日停盤公告（Guardian）**\n\n"
            f"風險等級：{level}\n"
            f"原因：{reason}\n\n"
            "📌 今日所有交易與 Explorer 已暫停\n\n"
            f"時間：{now:%Y-%m-%d %H:%M}（台灣）"
        )
        self._send("general", msg)

    # ==========================
    # 🦢 黑天鵝
    # ==========================
    def black_swan(self, description: str):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        msg = (
            "🦢 **黑天鵝事件警告**\n\n"
            f"{description}\n\n"
            f"時間：{now:%Y-%m-%d %H:%M}（台灣）"
        )
        self._send("black_swan", msg)
