# 冷資料建議報告產生器（給人 / Guardian 看）

def build_report(items: list) -> str:
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("🧊 Vault 冷資料審計建議（不自動刪除）")
    lines.append("━━━━━━━━━━━━━━━━━━━━\n")

    for it in items:
        lines.append(f"• {it['path']}")
        lines.append(f"  └ 使用間隔：{it['age_days']} 天")
        lines.append(f"  └ 建議：{it['reason']}（保留分數 {it['retain_score']:.2f}）\n")

    if not items:
        lines.append("（未偵測到可討論的冷資料）")

    return "\n".join(lines)
