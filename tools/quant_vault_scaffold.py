#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quant-Vault Scaffold & Governance Bootstrapper
------------------------------------------------
用途：
1) 一鍵生成你設計的 Quant-Vault 目錄結構（含建議加強項目）
2) 產生治理/風控/學習狀態的初始檔案（JSON）
3) (可選) 在支援 POSIX 權限的系統上，將 LOCKED_* 目錄設為只讀（防誤寫）
4) 內建最小「不可變寫入」入口：ingest_raw()，寫入 LOCKED_RAW 並記錄雜湊鏈台帳
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_json_if_missing(path: Path, data: Dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def safe_chmod(path: Path, mode: int) -> bool:
    try:
        os.chmod(path, mode)
        return True
    except Exception:
        return False


VAULT_DIRS = [
    "LOCKED_RAW/market_raw",
    "LOCKED_RAW/black_swan",
    "LOCKED_RAW/backtest/TW",
    "LOCKED_RAW/backtest/US",
    "LOCKED_RAW/backtest/JP",
    "LOCKED_RAW/backtest/CRYPTO",

    "LOCKED_DECISION/guardian",
    "LOCKED_DECISION/risk_policy",
    "LOCKED_DECISION/horizon",

    "STOCK_DB/TW/universe",
    "STOCK_DB/TW/shortlist",
    "STOCK_DB/TW/core_watch",
    "STOCK_DB/TW/history",
    "STOCK_DB/TW/cache",
    "STOCK_DB/US",
    "STOCK_DB/JP",
    "STOCK_DB/CRYPTO",

    "TEMP_CACHE/cache",
    "TEMP_CACHE/snapshot",
    "TEMP_CACHE/tmp",

    "LOG",

    # 120/100 加強
    "INBOX_STAGING/raw_drop",
    "INBOX_STAGING/quarantine",
    "DERIVED/features",
    "DERIVED/signals",
    "MODELS/checkpoints",
    "MODELS/registry",
    "REPORTS/daily",
    "MANIFESTS",
    "GOVERNANCE/proposals",
    "GOVERNANCE/approvals",
    "KEYS",
]

DEFAULT_FILES = {
    "LOCKED_DECISION/guardian/guardian_state.json": {
        "schema": "guardian_state.v1",
        "updated_at": utc_now_iso(),
        "level": 1,
        "freeze": False,
        "freeze_reason": "",
        "notes": "L1=Normal, L2=Elevated, L3=High Risk, L4=Freeze (no outbound).",
    },
    "LOCKED_DECISION/risk_policy/ai_weights.json": {
        "schema": "ai_weights.v1",
        "updated_at": utc_now_iso(),
        "policy_version": "0.1.0",
        "weights": {
            "trend": 0.25,
            "mean_reversion": 0.20,
            "macro": 0.15,
            "volatility": 0.20,
            "sentiment": 0.20
        },
        "constraints": {
            "sum_to_one": True,
            "max_single_weight": 0.35,
            "min_single_weight": 0.05
        },
        "write_rule": "ONLY via governance proposal + approval (see GOVERNANCE/)."
    },
    "LOCKED_DECISION/horizon/learning_state.json": {
        "schema": "learning_state.v1",
        "updated_at": utc_now_iso(),
        "cooldown_hours": 24,
        "last_learn_at": None,
        "allowed": True,
        "notes": "Mutual constraint: learning is gated by Guardian level + cooldown."
    },
    "TEMP_CACHE/system_audit_state.json": {
        "schema": "system_audit_state.v1",
        "updated_at": utc_now_iso(),
        "discord": {
            "last_post_hash": None,
            "last_post_at": None,
            "dedupe_window_sec": 900
        }
    },
    "MANIFESTS/vault_manifest.json": {
        "schema": "vault_manifest.v1",
        "created_at": utc_now_iso(),
        "vault_name": "Quant-Vault",
        "notes": "Index/meta. Append-only ledger in MANIFESTS/ledger.ndjson"
    },
    "MANIFESTS/ledger.ndjson": "",
    "GOVERNANCE/policy_registry.json": {
        "schema": "policy_registry.v1",
        "updated_at": utc_now_iso(),
        "policies": [
            {
                "id": "risk_policy.ai_weights",
                "path": "LOCKED_DECISION/risk_policy/ai_weights.json",
                "update_flow": "proposal -> approval -> apply",
                "guardrails": ["sum_to_one", "max_single_weight", "min_single_weight"]
            }
        ]
    },
}

@dataclass
class LedgerEntry:
    ts: str
    action: str
    src: Optional[str]
    dst: Optional[str]
    sha256: Optional[str]
    meta: Dict[str, Any]
    prev_hash: str
    entry_hash: str

def ledger_last_hash(ledger_path: Path) -> str:
    if not ledger_path.exists() or ledger_path.stat().st_size == 0:
        return "GENESIS"
    last_line = ""
    with ledger_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if not last_line:
        return "GENESIS"
    try:
        obj = json.loads(last_line)
        return obj.get("entry_hash") or "GENESIS"
    except Exception:
        return "GENESIS"

def append_ledger(ledger_path: Path, action: str, src: Optional[str], dst: Optional[str], sha256: Optional[str], meta: Dict[str, Any]) -> LedgerEntry:
    prev = ledger_last_hash(ledger_path)
    payload = {
        "ts": utc_now_iso(),
        "action": action,
        "src": src,
        "dst": dst,
        "sha256": sha256,
        "meta": meta,
        "prev_hash": prev,
    }
    entry_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    payload["entry_hash"] = entry_hash

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return LedgerEntry(
        ts=payload["ts"],
        action=action,
        src=src,
        dst=dst,
        sha256=sha256,
        meta=meta,
        prev_hash=prev,
        entry_hash=entry_hash,
    )

def create_structure(vault_root: Path) -> None:
    for d in VAULT_DIRS:
        ensure_dir(vault_root / d)

    for rel, content in DEFAULT_FILES.items():
        p = vault_root / rel
        if rel.endswith(".ndjson"):
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("", encoding="utf-8")
        else:
            write_json_if_missing(p, content)

def apply_readonly_locks(vault_root: Path) -> Dict[str, Any]:
    report = {"platform": platform.system(), "attempted": [], "applied": [], "skipped": []}
    locked_paths = [vault_root / "LOCKED_RAW", vault_root / "LOCKED_DECISION"]

    if platform.system().lower().startswith("win"):
        report["skipped"].append("Windows detected: skipping chmod-based locks (use NTFS ACL / BitLocker / VeraCrypt).")
        return report

    for base in locked_paths:
        if not base.exists():
            continue
        for p in [base] + list(base.rglob("*")):
            report["attempted"].append(str(p))
            ok = safe_chmod(p, 0o555 if p.is_dir() else 0o444)
            if ok:
                report["applied"].append(str(p))
    return report

def ingest_raw(vault_root: Path, src_file: Path, category: str, market: Optional[str] = None, note: str = "") -> Path:
    category = category.strip()
    if category not in {"market_raw", "black_swan", "backtest"}:
        raise ValueError("category must be one of: market_raw, black_swan, backtest")
    if not src_file.exists() or not src_file.is_file():
        raise FileNotFoundError(str(src_file))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ext = src_file.suffix
    safe_name = src_file.stem.replace(" ", "_")
    fname = f"{ts}__{safe_name}{ext}"

    if category == "backtest":
        m = (market or "UNKNOWN").upper()
        dst_dir = vault_root / "LOCKED_RAW" / "backtest" / m
    else:
        dst_dir = vault_root / "LOCKED_RAW" / category

    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_path = dst_dir / fname
    if dst_path.exists():
        raise FileExistsError(str(dst_path))

    shutil.copy2(src_file, dst_path)
    digest = sha256_file(dst_path)

    manifest_dir = vault_root / "MANIFESTS" / "raw"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    sidecar = manifest_dir / (fname + ".json")
    sidecar.write_text(json.dumps({
        "schema": "raw_ingest_manifest.v1",
        "ingested_at": utc_now_iso(),
        "src": str(src_file),
        "dst": str(dst_path.relative_to(vault_root)),
        "sha256": digest,
        "category": category,
        "market": (market.upper() if market else None),
        "note": note
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ledger = vault_root / "MANIFESTS" / "ledger.ndjson"
    append_ledger(
        ledger_path=ledger,
        action="INGEST_RAW",
        src=str(src_file),
        dst=str(dst_path.relative_to(vault_root)),
        sha256=digest,
        meta={"category": category, "market": market, "note": note}
    )
    return dst_path

def main():
    ap = argparse.ArgumentParser(description="Quant-Vault scaffold & bootstrap")
    ap.add_argument("--root", type=str, default="Quant-Vault", help="Vault root folder (default: ./Quant-Vault)")
    ap.add_argument("--lock", action="store_true", help="Best-effort set LOCKED_* to read-only (POSIX only)")
    ap.add_argument("--ingest", type=str, default=None, help="(Optional) ingest a file into LOCKED_RAW (path)")
    ap.add_argument("--category", type=str, default="market_raw", help="ingest category: market_raw|black_swan|backtest")
    ap.add_argument("--market", type=str, default=None, help="market for backtest: TW|US|JP|CRYPTO")
    ap.add_argument("--note", type=str, default="", help="note for ingest ledger")
    args = ap.parse_args()

    vault_root = Path(args.root).expanduser().resolve()
    create_structure(vault_root)

    report = None
    if args.lock:
        report = apply_readonly_locks(vault_root)
        ledger = vault_root / "MANIFESTS" / "ledger.ndjson"
        append_ledger(ledger, "APPLY_LOCKS", None, None, None, {"report": report})

    ingested_path = None
    if args.ingest:
        ingested_path = ingest_raw(vault_root, Path(args.ingest).expanduser().resolve(), args.category, args.market, args.note)

    print("✅ Quant-Vault ready:", vault_root)
    if report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if ingested_path:
        print("📥 Ingested to:", ingested_path)

if __name__ == "__main__":
    main()
