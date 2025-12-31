# Quant-Orchestrator/shared/ai_consensus_bridge.py
# 三方 AI 共識橋樑（封頂最終版｜可直接完整覆蓋）
# 職責：
# - 彙整 Stock-Genius / Guardian / Orchestrator 子 AI 回饋
# - 形成「共識狀態」而非單點決策
# - 提供互相約制、反思、學習的唯一中介層
#
# ❌ 不交易 ❌ 不寫 Vault ❌ 不發 Discord
# ❌ 不直接下結論
# ✅ 只輸出「共識結果」供上層使用

from typing import List, Dict, Any


def build_consensus(bridge_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    bridge_messages 範例：
    [
        {
            "ai": "StockGenius_TW",
            "payload": {
                "score": 0.12,
                "confidence": 0.68,
                "reason": "RSI + volume breakout"
            }
        },
        {
            "ai": "Guardian",
            "payload": {
                "veto": False,
                "level": 2,
                "reason": "volatility acceptable"
            }
        }
    ]
    """

    consensus = {
        "confidence": 0.5,
        "veto": False,
        "guardian_level": None,
        "signals": [],
        "reasons": [],
        "participants": [],
    }

    for msg in bridge_messages:
        ai_name = msg.get("ai")
        payload = msg.get("payload", {})

        consensus["participants"].append(ai_name)

        # Guardian 專屬欄位
        if ai_name and ai_name.lower().startswith("guardian"):
            if "level" in payload:
                consensus["guardian_level"] = payload["level"]
            if payload.get("veto"):
                consensus["veto"] = True
                consensus["reasons"].append(f"{ai_name}:VETO({payload.get('reason')})")
            continue

        # 一般 AI 訊號
        score = payload.get("score")
        penalty = payload.get("penalty")
        reason = payload.get("reason")
        conf = payload.get("confidence")

        if isinstance(score, (int, float)):
            consensus["confidence"] += score

        if isinstance(penalty, (int, float)):
            consensus["confidence"] += penalty

        if reason:
            consensus["signals"].append(reason)
            consensus["reasons"].append(f"{ai_name}:{reason}")

        if isinstance(conf, (int, float)):
            consensus["confidence"] = (consensus["confidence"] + conf) / 2

    # 邊界約束（鐵律）
    consensus["confidence"] = max(0.0, min(1.0, round(consensus["confidence"], 4)))

    return consensus
