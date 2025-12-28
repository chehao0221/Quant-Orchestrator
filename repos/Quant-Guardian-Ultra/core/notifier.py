import os
import json
import requests
from datetime import datetime


class DiscordNotifier:
    """
    Discord 通知器
    顏色規範：
    🟢 綠：正常
    🟡 黃：警戒
    🔴 紅：停盤 / 黑天鵝
    """

    COLOR_MAP = {
        "GREEN": 0x2ECC71,   # 綠
        "YELLOW": 0xF1C40F,  # 黃
        "RED": 0xE74C3C      # 紅
    }

    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
        }

    # =========================
    # 基礎工具
    # =========================
    def _send(self, channel: str, title: str, description: str, color: str):
        webhook = self.webhooks.get(channel)
        if not webhook:
            print(f"[WARN] Discord Webhook 未設定（{channel}）")
            return

        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": self.COLOR_MAP[color],
                    "footer": {
                        "text": "Quant Guardian Ultra"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }

        try:
            requests.post(webhook, json=payload, timeout=10)
        except Exception as e:
            print(f"[WARN] Discord 發送失敗：{e}")

    # =========================
    # 心跳
    # =========================
    def heartbeat(self, mode: str):
        self._send(
            channel="general",
            title="🟢 Guardian 系統心跳回報",
            description=(
                f"**系統狀態**：正常監控中\n"
                f"**模式**：{mode}\n"
                f"**時間**：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            ),
            color="GREEN"
        )

    # =========================
    # 一般風險通知（L3）
    # =========================
    def risk_alert(self, level: str, action: str, summary: str):
        self._send(
            channel="general",
            title="🟡 市場風險警示",
            description=(
                f"**風險等級**：{level}\n"
                f"**建議行動**：{action}\n\n"
                f"{summary}"
            ),
            color="YELLOW"
        )

    # =========================
    # 停盤 / 黑天鵝（L4+）
    # =========================
    def trading_halt(self, level: str, action: str, reason: str):
        description = (
            f"🛑 **Guardian 判定今日停盤**\n\n"
            f"**風險等級**：{level}\n"
            f"**系統動作**：{action}\n\n"
            f"**原因說明**：\n{reason}\n\n"
            f"Stock-Genius / Explorer 已暫停"
        )

        # 一般頻道（摘要）
        self._send(
            channel="general",
            title="🔴 今日停盤通知",
            description=description,
            color="RED"
        )

        # 黑天鵝頻道（完整）
        self._send(
            channel="black_swan",
            title="🔴 黑天鵝 / 極端風險事件",
            description=description,
            color="RED"
        )
