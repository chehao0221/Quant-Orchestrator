# AI 決策審計報告產生器（人類可讀）

import hashlib
import json
from datetime import datetime


def _fingerprint(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_audit_report(market: str, guardian_state: dict, judge_result: dict, bridge_messages: list):
    payload = {
        "market": market,
        "guardian_level": guardian_state.get("level"),
        "judge": judge_result,
        "ais": bridge_messages,
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    }

    fp = _fingerprint(payload)

    report_text = f"""
🧠 系統決策審計報告

━━━━━━━━━━━━━━━━━━
📅 日期：{payload["date"]}
🌐 市場：{market}
🛡 Guardian 狀態：L{payload["guardian_level"]}

🔍 AI 討論摘要：
"""  # ⚠️ 保留格式，不動空行

    for m in bridge_messages:
        report_text += f'- {m["ai"]}：{m["payload"].get("reason","")}\n'

    report_text += f"""
🗳 決策結果：
- 最終信心度：{judge_result["confidence"]:.2f}
- VETO：{"是" if judge_result["veto"] else "否"}
- 是否發送市場報告：{"是" if not judge_result["veto"] else "否"}

━━━━━━━━━━━━━━━━━━
""".strip()

    return {
        "fingerprint": fp,
        "text": report_text.strip()
    }
