# Quant-Orchestrator/orchestrator/orchestrator_ai.py
# 多 AI 溝通橋樑 + 學習閉環（封頂最終版）

from datetime import datetime
from typing import Dict, Any, List
from orchestrator.learning_integrator import LearningIntegrator


class OrchestratorAI:
    def __init__(self):
        self.inputs: List[Dict[str, Any]] = []
        self.learning_events: List[Dict[str, Any]] = []

    # ---------- AI 輸入 ----------

    def ingest(self, source: str, payload: Dict[str, Any]):
        payload["_source"] = source
        self.inputs.append(payload)

    def ingest_learning(self, event: Dict[str, Any]):
        if event:
            self.learning_events.append(event)

    # ---------- 內部檢查 ----------

    def _validate_inputs(self):
        if not self.inputs:
            raise RuntimeError("OrchestratorAI: 無 AI 輸入，禁止結論")

        for item in self.inputs:
            if "confidence" not in item:
                raise RuntimeError(
                    f"OrchestratorAI: {item.get('_source')} 缺少 confidence"
                )

    # ---------- 彙整 ----------

    def _aggregate_confidence(self) -> float:
        weight_map = {"guardian": 0.45, "market": 0.4, "vault": 0.15}
        score, total = 0.0, 0.0

        for item in self.inputs:
            w = weight_map.get(item["_source"], 0)
            score += item["confidence"] * w
            total += w

        return round(score / total, 2) if total else 0.0

    # ---------- 對外 ----------

    def finalize(self) -> Dict[str, Any]:
        self._validate_inputs()
        final_confidence = self._aggregate_confidence()

        # 學習建議整合
        integrator = LearningIntegrator()
        learning_adjustments = [
            integrator.apply(e) for e in self.learning_events if e
        ]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "final_confidence": final_confidence,
            "learning_adjustments": learning_adjustments,
            "sources": [i["_source"] for i in self.inputs],
        }
