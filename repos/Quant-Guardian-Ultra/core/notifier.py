import os
import json
import requests
from datetime import datetime


class DiscordNotifier:
    """
    Guardian / Stock-Genius / Explorer 共用 Discord 通知器
    規範：
    - 只使用 🟢 / 🟡 / 🔴
    - 只說「結果」，不說技術細節
    """

    def __init__(self):
        self.webhooks = {
            "general": os.getenv("DISCORD_WEBHOOK_GENERAL"),
            "black_swan": os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
            "us": os.getenv("DISCORD_WEBHOOK_US"),
            "tw": os.getenv("DISCORD_WEBHOOK_TW"),
        }

    # =========================
    # 基礎工具
    # =========================
    def _send(self, webhook_url: str, content: str):
        if not webhook_url:
            print("[WARN] Discord Webhook 未設定")
            return

        payload = {
            "content": content
        }

        try:
            r = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if r.status_code >= 400:
                print(f"[WARN] Discord 發送失敗：{r.status_code}")
        except Exception as e:
            print(f"[WARN] Discord 發送例外：{e}")

    def _now(self):
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # =========================
    # 🫀 系統心跳（一般 / 系統）
    # =========================
    def heartbeat(self, mode: str = "風險監控待命"):
        msg = f"""🟢 Guardian 系統心跳回報

系統狀態：正常監控中
檢查時間：{self._now()}
模式：{mode}

備註：
系統已完成本次例行檢查，未偵測到異常風險。
"""
        self._send(self.webhooks["general"], msg)

    # =========================
    # 🟡 L3 風控提醒（一般頻道）
    # =========================
    def risk_warning(self, level: str, summary: str):
        """
        level: 'L3'
        """
        msg = f"""🟡 Guardian 風控提醒｜提高警覺

今日市場狀態：波動偏高
系統判定等級：{level}（中度風險）

建議行動：
- 避免追高
- 降低單日曝險
- 保守看待短線波動

摘要：
{summary}

系統狀態：
- Guardian：✅ 已完成檢查
- Stock Genius：⚠️ 正常運作
- Explorer：✅ 正常
"""
        self._send(self.webhooks["general"], msg)

    # =========================
    # 🔴 停盤 / 黑天鵝（黑天鵝頻道）
    # =========================
    def trading_halt(self, reason: str):
        msg = f"""🔴 Guardian 重大風控警示｜系統防禦模式

今日市場狀態：高風險
系統判定等級：L4（極端波動）

系統已自動執行：
- ⛔ Stock Genius：已暫停
- ⛔ Explorer：已暫停

原因摘要：
{reason}

備註：
系統已進入保護模式，避免非必要決策。
"""
        self._send(self.webhooks["black_swan"], msg)

    # =========================
    # 📊 Stock-Genius 專用（台 / 美）
    # =========================
    def post_us(self, content: str):
        self._send(self.webhooks["us"], content)

    def post_tw(self, content: str):
        self._send(self.webhooks["tw"], content)
