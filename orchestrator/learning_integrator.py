# Quant-Orchestrator/orchestrator/learning_integrator.py
# Orchestrator 吸收 Vault 學習事件並調整權重（封頂最終版）

from typing import Dict


class LearningIntegrator:
    """
    將 Vault 的學習事件轉成權重調整建議
    """

    def apply(self, learning_event: Dict) -> Dict:
        if not learning_event:
            return {}

        strength = learning_event.get("strength", 0)
        signal = learning_event.get("signal")

        if signal not in {"positive", "negative"}:
            return {}

        # 權重調整建議（不是直接修改）
        delta = strength * 0.1
        if signal == "negative":
            delta = -delta

        return {
            "market": learning_event.get("market"),
            "confidence_weight_delta": round(delta, 3),
            "guardian_sensitivity_delta": round(delta * 0.5, 3),
        }
