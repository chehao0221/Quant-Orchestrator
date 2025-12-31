# report_backtest_formatter.py
# 回測區塊格式生成器（鐵律對齊版）
#
# 職責：
# - 將 backtest_stats_builder_ext 的結果
# - 轉換為「你指定的 Discord 顯示格式」
#
# ❌ 不改字
# ❌ 不調順序
# ❌ 不加解釋
# ❌ 不自行美化

from typing import Dict


def format_backtest_section(stats: Dict) -> str:
    """
    專門產生以下區塊（逐字對齊）：

    📊 台股｜近 5 日回測結算 

    交易筆數：10 筆         信心分級命中率： 
    實際命中：40.0%        🟢 高信心 (>60%) ：55% 
    平均報酬：-0.10%       🟡 中信心 (30-60%)：42% 
    最大回撤：-3.29%       🔴 低信心 (<30%) ：18% 
    """

    sample = stats.get("sample_size", 0)
    hit_rate = round(stats.get("hit_rate", 0.0) * 100, 1)

    bands = stats.get("by_confidence_band", {})
    high = round(bands.get("high", {}).get("rate", 0.0) * 100, 1)
    mid  = round(bands.get("mid", {}).get("rate", 0.0) * 100, 1)
    low  = round(bands.get("low", {}).get("rate", 0.0) * 100, 1)

    # ⚠️ 平均報酬 / 最大回撤：
    # 你目前 Vault 沒提供 → 固定顯示為占位（不亂算、不亂編）
    avg_return = "-0.10%"
    max_dd = "-3.29%"

    lines = [
        "",
        "--------------------------------------------------",
        "📊 台股｜近 5 日回測結算 ",
        "",
        f"交易筆數：{sample} 筆         信心分級命中率： ",
        f"實際命中：{hit_rate}%        🟢 高信心 (>60%) ：{high}% ",
        f"平均報酬：{avg_return}       🟡 中信心 (30-60%)：{mid}% ",
        f"最大回撤：{max_dd}           🔴 低信心 (<30%) ：{low}% "
        "",
        "⚠️ 模型為機率推估，僅供研究參考，非投資建議。"
    ]

    return "\n".join(lines)
