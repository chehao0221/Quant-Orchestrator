# core/guardian_v2.py
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Literal, Tuple

from core.vault_access_guard import VaultAccessGuard

Market = Literal["TW", "US", "JP", "CRYPTO"]
GuardianState = Literal["PASS", "FREEZE", "REJECT"]


@dataclass(frozen=True)
class GuardianConfig:
    # 硬規則（不可破）
    min_eval_score: float = 0.35          # 評估分數太低 → REJECT
    freeze_eval_score: float = 0.45       # 分數偏低 → FREEZE（不允許學習）
    max_consecutive_freeze: int = 7       # 連續 freeze 次數過多 → REJECT（避免永凍/壞死）

    # 軟規則（策略互評制衡；若你還沒接 council，也不會報錯）
    min_soft_score_to_learn: float = 0.0  # soft score < 0 → FREEZE（不允許學習）

    # state persistence
    guardian_state_path: str = "LOCKED_DECISION/guardian/guardian_state.json"


class GuardianV2:
    """
    Guardian V2（終極封頂）
    ----------------------
    目標：
    1) 硬規則先判：確保不會亂學
    2) 軟規則再判：若策略互評偏負面，暫停學習
    3) 全部結果落盤（透過 VaultAccessGuard）可回溯、可稽核
    """

    def __init__(self, vault_root: str, cfg: GuardianConfig | None = None):
        self.vault_root = vault_root
        self.cfg = cfg or GuardianConfig()
        self.guard = VaultAccessGuard(vault_root)

    # ---------- public ----------

    def run(
        self,
        date_key: str,
        eval_scores: Dict[str, float],
        eval_evidence: Dict | None = None,
        soft_votes: Dict[str, float] | None = None,
    ) -> Dict:
        """
        eval_scores: 例如 {"TW":0.62,"US":0.55,"JP":0.50,"CRYPTO":0.41}
        soft_votes: council 互評分數（可選）例如 {"TW":0.1,"US":0.0,...}
        """

        eval_evidence = eval_evidence or {}
        soft_votes = soft_votes or {}

        prev_state = self._read_prev_state()

        freeze_map: Dict[Market, bool] = {m: False for m in ["TW", "US", "JP", "CRYPTO"]}
        reasons: Dict[str, str] = {}
        hard_flags: Dict[str, str] = {}

        # 1) 硬規則（先判）
        state: GuardianState = "PASS"
        for m in freeze_map.keys():
            s = float(eval_scores.get(m, 0.0))
            if s < self.cfg.min_eval_score:
                freeze_map[m] = True
                hard_flags[m] = f"REJECT: eval_score<{self.cfg.min_eval_score}"
                state = "REJECT"
                reasons[m] = f"{m} 評估分數過低（{s:.3f}）→ 拒絕學習"
            elif s < self.cfg.freeze_eval_score:
                freeze_map[m] = True
                hard_flags[m] = f"FREEZE: eval_score<{self.cfg.freeze_eval_score}"
                if state != "REJECT":
                    state = "FREEZE"
                reasons[m] = f"{m} 評估分數偏低（{s:.3f}）→ 冷凍學習"

        # 2) 軟規則（再判）：只有在硬規則沒有 REJECT 時才考慮
        # soft_votes 不存在就跳過（不會影響）
        if state != "REJECT" and soft_votes:
            soft_total = 0.0
            for m, v in soft_votes.items():
                try:
                    soft_total += float(v)
                except Exception:
                    continue

            if soft_total < self.cfg.min_soft_score_to_learn:
                # 不改 freeze_map（freeze_map 表示硬風控）；但整體 state 轉 FREEZE
                state = "FREEZE"
                reasons["SOFT"] = f"互評總分 {soft_total:.3f} < {self.cfg.min_soft_score_to_learn:.3f} → 暫停學習"

        # 3) 連續 freeze 過多 → REJECT（避免系統卡死）
        freeze_count = int(prev_state.get("meta", {}).get("consecutive_freeze", 0))
        if state == "FREEZE":
            freeze_count += 1
        else:
            freeze_count = 0

        if freeze_count >= self.cfg.max_consecutive_freeze and state != "REJECT":
            state = "REJECT"
            reasons["SYSTEM"] = f"連續 FREEZE 達 {freeze_count} 次 → 系統拒絕進一步學習（避免永凍）"

        out = {
            "date": date_key,
            "state": state,
            "freeze": freeze_map,
            "reasons": reasons,
            "hard_flags": hard_flags,
            "soft_votes": soft_votes,
            "eval_scores": eval_scores,
            "evidence": eval_evidence,
            "meta": {
                "consecutive_freeze": freeze_count,
                "timestamp": int(time.time()),
                "version": "guardian_v2_final_120",
            },
        }

        # 4) 寫入 LOCKED_DECISION（唯一合法入口：VaultAccessGuard）
        self.guard.write_json(
            role="guardian",
            relative_path=self.cfg.guardian_state_path,
            payload=out,
            reason=f"guardian_v2::{state}",
        )
        return out

    # ---------- internal ----------

    def _read_prev_state(self) -> Dict:
        """
        讀取上次 guardian_state（若不存在，回空）
        注意：讀取不需要 guard；guard 只管寫入
        """
        p = Path(self.vault_root) / self.cfg.guardian_state_path
        try:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}
