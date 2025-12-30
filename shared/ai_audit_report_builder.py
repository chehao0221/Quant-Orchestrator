# AI 系統審計報告產生器（人類可讀）

def build_audit_report(weights: dict, perf: dict, guardian: dict) -> str:
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("🧠 AI 系統自我審計報告（非投資建議）")
    lines.append("━━━━━━━━━━━━━━━━━━━━\n")

    lines.append("【學習狀態】")
    lines.append(f"• 技術面權重：{weights['technical']:.2f}")
    lines.append(f"• 新聞面權重：{weights['news']:.2f}")
    lines.append(f"• 風控影響力：{weights['guardian_bias']:.2f}\n")

    lines.append("【近期表現】")
    lines.append(f"• 命中率：{perf['hit_rate']:.0%}")
    lines.append(f"• 平均誤差：{perf['avg_error']:.2f}%")
    lines.append(f"• 連續失誤：{perf['consecutive_miss']}\n")

    lines.append("【Guardian 影響】")
    lines.append(f"• 當前等級：{guardian['level']}")
    lines.append(f"• 系統模式：{guardian['mode']}")
    lines.append(f"• AI 信心調整：{guardian['bias']}\n")

    lines.append("【系統結論】")
    lines.append(perf["verdict"])
    lines.append("\n（此報告為系統自省用途，非市場建議）")

    return "\n".join(lines)
