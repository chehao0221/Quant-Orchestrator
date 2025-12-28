import os
import json
import requests
from datetime import datetime


class DiscordNotifier:
    """
    Guardian / Stock-Genius 共用 Discord 通知器
    - 支援等級顏色
    - 支援多頻道
    - 支援心跳通知
    - 繁體中文
    """

    COLORS = {
        "L3": 0xF1C40F,        # 黃色
        "L4": 0xE74C3C,        # 紅色
        "BLACK_SWAN": 0x9B59B6,  # 紫色
        "INFO": 0x3498DB,      # 藍色
    }

    def __init__(self, debug: bool = False):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
        }
        self.debug = debug

        if self.debug:
            self._debug_webhooks()

    # --------------------------------------------------
    # Debug

    def _debug_webhooks(self):
        print("[DEBUG] Discord Webhook 狀態檢查：")
        for k, v in self.webhooks.items():
            status = "✅ 已設定" if v else "❌ 未設定"
            print(f" - {k}: {status}")

    # --------------------------------------------------
    # Core sender

    def send(
        self,
        title: str,
        description: str,
        level: str = "INFO",
        channel: str = "general",
        footer: str | None = None,
    ):
        url = self.webhooks.get(channel)
        if not url:
            print(f"[WARN] Discord Webhook 未設定（{channel}）")
            return

        embed = {
            "title": title,
            "description": description,
            "color": self.COLORS.get(level, self.COLORS["INFO"]),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": footer or "Quant-Orchestrator Guardian System"
            },
        }

        payload = {"embeds": [embed]}

        try:
            r = requests.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if r.status_code >= 300:
                print(f"[WARN] Discord 發送失敗：{r.status_code} {r.text}")
        except Exception as e:
            print(f"[WARN] Discord 發送例外：{e}")

    # --------------------------------------------------
    # 💓 Heartbeat（你現在缺的就是這個）

    def heartbeat(self, mode: str = "監控中"):
        """
        Guardian 每日 / 手動 心跳通知
        """
        title = "💓 Guardian 系統心跳回報"
        desc = (
            f"🟢 **系統狀態：正常監控中**\n\n"
            f"⏱ 檢查時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"⚙️ 模式：{mode}\n\n"
            f"📌 備註：系統已完成例行檢查，未偵測到異常。"
        )

        self.send(
            title=title,
            description=desc,
            level="INFO",
            channel="general",
        )

    # --------------------------------------------------
    # 🚨 Guardian 專用封裝（朋友也看得懂）

    def guardian_summary(self, result: dict):
        """
        result example:
        {
          "level": "L3",
          "action": "REDUCE",
          "reason": "VIX 偏高 + 新聞事件"
        }
        """
        level = result.get("level", "L3")
        reason = result.get("reason", "系統綜合評估")

        if level == "L3":
            self.send(
                title="⚠️ 今日市場風險偏高（提醒）",
                description=(
                    f"📊 **風控等級：L3（中度風險）**\n\n"
                    f"🔎 原因：{reason}\n\n"
                    f"📌 建議：降低曝險、謹慎觀察"
                ),
                level="L3",
                channel="general",
            )

        elif level == "L4":
            self.send(
                title="🛑 高風險警告｜今日建議停盤",
                description=(
                    f"🚨 **風控等級：L4（高風險）**\n\n"
                    f"🔎 原因：{reason}\n\n"
                    f"⛔ 建議：暫停交易 / Explorer / 新進策略"
                ),
                level="L4",
                channel="general",
            )

        elif level == "BLACK_SWAN":
            self.send(
                title="🦢 黑天鵝事件警告",
                description=(
                    f"🟪 **等級：黑天鵝事件**\n\n"
                    f"🔎 事件：{reason}\n\n"
                    f"⛔ 建議：全面風險防禦"
                ),
                level="BLACK_SWAN",
                channel="black_swan",
            )
