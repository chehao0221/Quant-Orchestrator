from datetime import datetime
from pathlib import Path
from notify.quiet_hours import is_quiet_hours
from notify.dedupe import should_send
from notify.buffer import buffer_general
from notify.discord_client import send_discord

WEBHOOKS = {
    "system": "https://discord.com/api/webhooks/1456288945938628648/qkeG_pBUVfbZdUSz9xLEvfNiltdJLvbfGZRaWV-6ir9sebTZyR-Rre9umb9Ji3cRpoDW",
    "general": "https://discord.com/api/webhooks/1453718156760580106/DAj2RQaAQULSGhgiqY91aKxGZ52stBaCakYst5QKNQ1_obaxYg2p1rXA29VJ-wqU7Jby",
    "TW": "https://discord.com/api/webhooks/1452877459287703664/MA7auObMXj9n6_DCF_iq6fq1n8Be_LrAYYUH-A573UZPwLNlnsOv35ciK7xMzbC3onU5",
    "US": "https://discord.com/api/webhooks/1454126698432823390/3iIo3vKsD1nXoovvnF_sFJGUeHe3N0HPJ4RA7I-xwonXTSkSY_mAXjRAfD53Jh9s4IoE",
    "JP": "https://discord.com/api/webhooks/1455609878948221118/FFqiozKx3aqjq7hMhrFu0lOP7b5_aMQWpX1lotdRl2EC8D3YM9RQBo0ptx31GTCVyGd8",
    "CRYPTO": "https://discord.com/api/webhooks/1455610023848706139/KVBEyoRM6YJ6XD74Y1hdf30gdvK0uk5aYPOYX7KlUf7V4o46Qg8drYoB0llpfKo6CpFg",
    "BLACK_SWAN": "https://discord.com/api/webhooks/1453714965512065106/3oDn_6ni3bQ7drSgUT6hjGju0DoWB-_oF6voQfr86sTr_plNGGmeSnuu2K5y55ixTRa_",
}

def notify(kind: str, title: str, content: str):
    """
    kind: system | general | TW | US | JP | CRYPTO | BLACK_SWAN
    """
    message = f"**{title}**\n{content}"

    # 防重（跨重啟）
    if not should_send(kind, message):
        return

    # 一般消息：夜間暫存
    if kind == "general" and is_quiet_hours():
        buffer_general(title, content)
        return

    send_discord(WEBHOOKS[kind], message)
