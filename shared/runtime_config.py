# shared/runtime_config.py
# 系統唯一動態設定來源（最終封頂版）
# ❌ 無硬編碼路徑
# ❌ 無市場邏輯
# ✅ 僅負責提供設定與路徑

import os
import json


# =========================
# Vault Root（唯一來源）
# =========================
def get_vault_root() -> str:
    root = os.environ.get("QUANT_VAULT_ROOT")
    if not root:
        raise RuntimeError("缺少環境變數 QUANT_VAULT_ROOT")
    return root


# =========================
# Learning State 路徑
# =========================
def get_learning_state_path() -> str:
    return os.path.join(
        get_vault_root(),
        "LOCKED_DECISION",
        "horizon",
        "learning_state.json",
    )


# =========================
# Learning Policy（治理參數）
# =========================
def get_learning_policy() -> dict:
    """
    學習治理鐵律（集中管理）
    可由外部 JSON 覆蓋，否則使用預設封頂值
    """

    policy_path = os.environ.get("AI_LEARNING_POLICY_PATH")

    # —— 外部覆蓋（推薦）——
    if policy_path and os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # —— 封頂預設（不可再優化）——
    return {
        "min_sample_size": 30,        # 樣本不足不學
        "cooldown_days": 5,           # 防止頻繁學歪
        "guardian_block_level": 4,    # Guardian >= L4 禁止學習
        "max_confidence_allow": 0.75, # 信心過高門檻
        "min_hitrate_allow": 0.45,    # 命中率下限
    }
