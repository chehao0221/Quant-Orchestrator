from pathlib import Path
import json
from notify.discord_client import send_discord
from notify.router import WEBHOOKS

BUFFER_FILE = Path("TEMP_CACHE/general_buffer.json")

def main():
    if not BUFFER_FILE.exists():
        return

    data = json.loads(BUFFER_FILE.read_text(encoding="utf-8"))
    if not data:
        return

    lines = []
    for i, item in enumerate(data, 1):
        lines.append(f"{i}. **{item['title']}**\n{item['content']}")

    message = "🌅 **早安摘要（一般消息）**\n\n" + "\n\n".join(lines)
    send_discord(WEBHOOKS["general"], message)

    BUFFER_FILE.unlink()

if __name__ == "__main__":
    main()
