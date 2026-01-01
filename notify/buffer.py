import json
from pathlib import Path
from datetime import datetime

BUFFER_FILE = Path("TEMP_CACHE/general_buffer.json")

def buffer_general(title: str, content: str):
    entry = {
        "time": datetime.now().isoformat(),
        "title": title,
        "content": content,
    }

    if BUFFER_FILE.exists():
        data = json.loads(BUFFER_FILE.read_text(encoding="utf-8"))
    else:
        data = []

    data.append(entry)
    BUFFER_FILE.parent.mkdir(exist_ok=True)
    BUFFER_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
