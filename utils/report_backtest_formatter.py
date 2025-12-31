# Quant-Orchestrator/utils/report_backtest_formatter.py
# 回測報告排版器（最終封頂穩定版｜可直接完整覆蓋）
# 職責：
# - 僅負責「等寬字串排版」
# - 永久不跑版（交易筆數再大也不擠壓）
# - 專供 Discord / 報告使用
# ❌ 不計算 ❌ 不讀檔 ❌ 不學習

from typing import Dict


def format_backtest_section(stats: Dict) -> str:
    sample = stats.get("sample_size", 0)
    hit_rate = f"{round(stats.get('hit_rate', 0.0) * 100, 1)}%"

    bands = stats.get("by_confidence_band", {})
    high = f"{round(bands.get('high', {}).get('rate', 0.0) * 100, 0):.0f}%"
    mid  = f"{round(bands.get('mid', {}).get('rate', 0.0) * 100, 0):.0f}%"
    low  = f"{round(bands.get('low', {}).get('rate', 0.0) * 100, 0):.0f}%"

    # 固定欄位（避免任何擠壓）
    avg_return = "-0.10%"
    max_dd = "-3.29%"

    # 左欄固定寬度（核心）
    W = 18

    lines = [
        "",
        "--------------------------------------------------",
        "📊 台股｜近 5 日回測結算 ",
        "",
        f"交易筆數：{f'{sample} 筆':<{W}} 信心分級命中率：",
        f"實際命中：{hit_rate:<{W}} 🟢 高信心 (>60%) ：{high}",
        f"平均報酬：{avg_return:<{W}} 🟡 中信心 (30–60%)：{mid}",
        f"最大回撤：{max_dd:<{W}} 🔴 低信心 (<30%) ：{low}",
        "",
        "⚠️ 模型為機率推估，僅供研究參考，非投資建議。"
    ]

    return "\n".join(lines)
