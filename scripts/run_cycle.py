#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_cycle.py — 開機自動跑的「閉環」入口
1) scaffold Quant-Vault（補齊結構/治理檔）
2) promote INBOX_STAGING/raw_drop → LOCKED_RAW（append-only + ledger）
3) 跑一次 MainOrchestrator 閉環
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.quant_vault_scaffold import create_structure  # type: ignore
from tools import raw_validator_and_promoter as rvp       # type: ignore
from core.main_orchestrator import MainOrchestrator, OrchestratorConfig  # type: ignore


def promote_from_inbox(vault_root: Path) -> None:
    argv_backup = sys.argv[:]
    try:
        sys.argv = [
            "raw_validator_and_promoter.py",
            "--root", str(vault_root),
            "--category", "market_raw",
            "--note", "auto_cycle"
        ]
        rvp.main()
    finally:
        sys.argv = argv_backup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault-root", type=str, default=os.getenv("QUANT_VAULT_ROOT") or "E:/Quant-Vault",
                    help="Quant-Vault 根目錄（預設 QUANT_VAULT_ROOT，否則 E:/Quant-Vault）")
    ap.add_argument("--skip-promote", action="store_true")
    ap.add_argument("--skip-orchestrator", action="store_true")
    args = ap.parse_args()

    vault_root = Path(args.vault_root).expanduser()
    create_structure(vault_root.resolve())

    if not args.skip_promote:
        promote_from_inbox(vault_root)

    result = None
    if not args.skip_orchestrator:
        cfg = OrchestratorConfig(vault_root=str(vault_root))
        result = MainOrchestrator(cfg).run()

    print("✅ run_cycle done.")
    if result is not None:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
