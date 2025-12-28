# repos/Quant-Guardian-Ultra/core/notifier.py
import requests
from datetime import datetime


class DiscordNotifier:
    def __init__(self, general=None, black_swan=None, us=None, tw=None):
        self.webhooks = {
            "general": general,
            "black_swan": black_swan,
            "us": us,
            "tw": tw,
        }

    # === 基礎送訊 ===
    def _send(self, webhook, content):
        if not webhook:
            print("[WARN] Discord Webhook 未設定（general）")
            return
        try:
            requests.post(webhook, json={"content": content}, timeout=10)
        except Exception as e:
            print(f"[WARN] Discord 發送失敗：{e}")

    # === 心跳（綠）===
    def heartbeat(self, mode=""):
        msg = (
            "🟢 **Guardian 系統心跳回報**\n\n"
            f"狀態：正常運行\n"
            f"模式：{mode}\n"
            f"時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        )
        self._send(self.webhooks["general"], msg)

    # === L3（黃）===
    def risk_alert(self, level, title, message):
        msg = (
            f"🟡 **{title}**\n\n"
            f"風險等級：{level}\n"
            f"{message}\n\n"
            f"時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        )
        self._send(self.webhooks["general"], msg)

    # === L4+（紅）===
    def trading_halt(self, level, title, message):
        msg = (
            f"🔴 **{title}**\n\n"
            f"風險等級：{level}\n"
            f"{message}\n\n"
            f"時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        )
        self._send(self.webhooks["black_swan"], msg)
