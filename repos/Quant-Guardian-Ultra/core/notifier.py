import os
import json
import requests
from datetime import datetime


class Notifier:
    """
    Discord 通知器
    支援頻道：
      - general      系統 / 心跳 / 一般回報
      - black_swan   黑天鵝 / 高風險
      - tw           台股分析
      - us           美股分析
    """

    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
        }

    # -------------------------------------------------
    # 公開介面
    # -------------------------------------------------

    def send(self, message: str, channel: str = "general"):
        webhook = self.webhooks.get(channel)

        if not webhook:
            print(f"[WARN] Discord Webhook 未設定（{channel}）")
            return

        payload = self._build_payload(message)

        try:
            resp = requests.post(webhook, json=payload, timeout=10)
            if resp.status_code >= 300:
                print(
                    f"[WARN] Discord 發送失敗（{channel}） "
                    f"HTTP {resp.status_code}: {resp.text}"
                )
        except Exception as e:
            print(f"[WARN] Discord 發送例外（{channel}）：{e}")

    # -------------------------------------------------
    # 內部工具
    # -------------------------------------------------

    def _build_payload(self, message: str) -> dict:
        """
        統一 Discord Payload（純文字，避免 embed 相容問題）
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        content = (
            f"{message}\n\n"
            f"───\n"
            f"🕒 {timestamp}\n"
            f"🛡 Guardian Ultra"
        )

        return {"content": content}
