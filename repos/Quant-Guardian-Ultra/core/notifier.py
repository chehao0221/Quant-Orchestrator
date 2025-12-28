import os
import json
import requests
from datetime import datetime


class DiscordNotifier:
    """
    Guardian / Stock-Genius 共用 Discord 通知器
    - 三色視覺：綠 / 黃 / 紅
    - 心跳
    - 停盤公告
    - 黑天鵝
    - 繁體中文
    """

    # 🎨 統一三色視覺
    COLORS = {
        "GREEN": 0x2ECC71,   # 🟢 安全 / 正常
        "YELLOW": 0xF1C40F,  # 🟡 提醒 / 風險升高
        "RED": 0xE74C3C,     # 🔴 停盤 / 黑天鵝
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
        color: str = "GREEN",
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
            "color": self.COLORS.get(color, self.COLORS["GREEN"]),
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
    # 💓 心跳（🟢）

    def heartbeat(self, mode: str = "風險監控待命"):
        self.send(
            title="🟢 Guardian 系統狀態正常",
            description=(
                f"💓 **系統心跳回報**\n\n"
                f"⏱ 時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"⚙️ 模式：{mode}\n\n"
                f"📌 狀態：持續監控中"
            ),
            color="GREEN",
            channel="general",
        )

    # --------------------------------------------------
    # 🚨 Guardian 判斷結果

    def guardian_summary(self, result: dict):
        level = result.get("level", "L3")
        reason = result.get("reason", "系統綜合評估")

        # 🟡 L3：提醒
        if level == "L3":
            self.send(
                title="🟡 市場風險提醒",
                description=(
                    f"⚠️ **風控等級：L3（風險升高）**\n\n"
                    f"🔎 原因：{reason}\n\n"
                    f"📌 建議：降低部位、謹慎操作"
                ),
                color="YELLOW",
                channel="general",
            )

        # 🔴 L4：停盤
        elif level == "L4":
            self.trading_halt(reason)

        # 🔴 黑天鵝
        elif level == "BLACK_SWAN":
            self.send(
                title="🔴 黑天鵝事件警告",
                description=(
                    f"🚨 **重大系統風險事件**\n\n"
                    f"🔎 事件：{reason}\n\n"
                    f"⛔ 建議：全面風險防禦"
                ),
                color="RED",
                channel="black_swan",
            )

    # --------------------------------------------------
    # 🛑 停盤公告（🔴）

    def trading_halt(self, reason: str):
        self.send(
            title="🔴 Guardian 判定今日停盤",
            description=(
                f"🛑 **市場風險過高，系統已進入防禦模式**\n\n"
                f"🔎 原因：{reason}\n\n"
                f"⛔ 已暫停：\n"
                f"- Stock-Genius 預測發布\n"
                f"- Explorer 探索任務\n\n"
                f"📌 將於下一次 Guardian 檢查後自動恢復"
            ),
            color="RED",
            channel="general",
        )
