# Quant-Orchestrator/orchestrator/orchestrator_ai.py
# 封頂最終版：多 AI 溝通橋樑（Orchestrator AI）

from datetime import datetime
from typing import Dict, Any, List


class OrchestratorAI:
    """
    唯一具有「最終結論權限」的 AI
    - 不產生原始分析
    - 只整合、檢查、加權、裁決
    """

    def __init__(self):
        self.inputs: List[Dict[str, Any]] = []
        self.decision_log: List[str] = []

    # ---------- AI 輸入區 ----------

    def ingest(self, source: str, payload: Dict[str, Any]):
        """
        接收其他 AI 的結論輸入
        source: guardian / market / vault
        payload: 已完成判斷的結果
        """
        payload["_source"] = source
        self.inputs.append(payload)

    # ---------- 核心裁決邏輯 ----------

    def _validate_inputs(self):
        if not self.inputs:
            raise RuntimeError("OrchestratorAI: 無任何 AI 輸入，禁止產生結論")

        for item in self.inputs:
            if "confidence" not in item:
                raise RuntimeError(
                    f"OrchestratorAI: 來源 {item.get('_source')} 缺少 confidence"
                )

    def _check_conflict(self) -> bool:
        """
        若 Guardian 與 Market 結論方向完全相反，視為衝突
        """
        guardian = [i for i in self.inputs if i["_source"] == "guardian"]
        market = [i for i in self.inputs if i["_source"] == "market"]

        if guardian and market:
            g = guardian[0].get("risk_level")
            m = market[0].get("market_bias")
            if g in ("L4", "L5") and m == "bullish":
                return True
        return False

    def _aggregate_confidence(self) -> float:
        """
        加權信心度（Guardian > Market > Vault）
        """
        weight_map = {
            "guardian": 0.45,
            "market": 0.40,
            "vault": 0.15,
        }

        score = 0.0
        total_weight = 0.0

        for item in self.inputs:
            w = weight_map.get(item["_source"], 0.0)
            score += item["confidence"] * w
            total_weight += w

        return round(score / total_weight, 2) if total_weight > 0 else 0.0

    # ---------- 對外輸出 ----------

    def finalize(self) -> Dict[str, Any]:
        """
        產生最終 AI 結論（唯一出口）
        """
        self._validate_inputs()

        conflict = self._check_conflict()
        final_confidence = self._aggregate_confidence()

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "final_confidence": final_confidence,
            "conflict_detected": conflict,
            "sources": [i["_source"] for i in self.inputs],
            "detail": self.inputs,
        }

        if conflict:
            result["note"] = (
                "⚠ Guardian 與 Market 判斷衝突，已降低整體信心度"
            )
            result["final_confidence"] = round(final_confidence * 0.7, 2)

        return result
