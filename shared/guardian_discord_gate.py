# guardian_discord_gate.py
# Guardian Discord 發送閘門（最終封頂版）
# 規則：
# - L0 / L1 / L2：不顯示（只供系統與 AI 使用）
# - L3：顯示（警示）
# - L4：顯示（高風險）
# - L5：顯示（緊急）

from utils.discord_notifier import send_system_message

# Discord 顯示門檻（鐵律）
DISCORD_MIN_LEVEL = 3  # L3 才顯示


def notify_guardian_state(
    level: int,
    title: str,
    message: str,
    webhook: str = "DISCORD_WEBHOOK_GUARDIAN"
) -> bool:
    """
    Guardian 狀態通知唯一出口
    """

    # L0–L2 完全靜默
    if level < DISCORD_MIN_LEVEL:
        return False

    content = (
        f"🛡️ Guardian 狀態更新\n\n"
        f"{title}\n"
        f"風險等級：L{level}\n\n"
        f"{message}"
    )

    return send_system_message(
        webhook=webhook,
        fingerprint=f"GUARDIAN_L{level}",
        content=content
    )
