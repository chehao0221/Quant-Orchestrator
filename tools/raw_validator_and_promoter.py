#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raw Validator & Promoter
------------------------
用途：
1) 驗證 INBOX_STAGING/raw_drop 內的原始資料（schema/缺值/時間序/大小）
2) 通過者「不可變」提升(promote)至 LOCKED_RAW（append-only）
3) 失敗者移至 INBOX_STAGING/quarantine（保留證據）
4) 全程寫入 MANIFESTS/ledger.ndjson（雜湊鏈台帳）

設計原則：
- 不直接覆寫任何 LOCKED_* 內容
- Promote = copy + hash + sidecar manifest + ledger
"""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib, json, shutil
from datetime import datetime, timezone

def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def append_ledger(vault: Path, action: str, src: str, dst: Optional[str], digest: Optional[str], meta: Dict[str, Any]):
    ledger = vault / "MANIFESTS" / "ledger.ndjson"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    prev = "GENESIS"
    if ledger.exists() and ledger.stat().st_size > 0:
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        prev = json.loads(line).get("entry_hash", prev)
                    except Exception:
                        pass
    payload = {
        "ts": utc(),
        "action": action,
        "src": src,
        "dst": dst,
        "sha256": digest,
        "meta": meta,
        "prev_hash": prev
    }
    entry_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    payload["entry_hash"] = entry_hash
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def basic_validate(p: Path, max_mb: int = 500) -> Dict[str, Any]:
    """
    最小驗證：存在、大小、非空
    （你之後可以在此加入 CSV/Parquet schema 驗證）
    """
    res = {"ok": True, "errors": []}
    if not p.exists() or not p.is_file():
        res["ok"] = False
        res["errors"].append("not_a_file")
        return res
    if p.stat().st_size == 0:
        res["ok"] = False
        res["errors"].append("empty_file")
    if p.stat().st_size > max_mb * 1024 * 1024:
        res["ok"] = False
        res["errors"].append("file_too_large")
    return res

def promote(vault: Path, src: Path, category: str, market: Optional[str], note: str):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"{ts}__{src.stem}{src.suffix}"
    if category == "backtest":
        dst_dir = vault / "LOCKED_RAW" / "backtest" / (market or "UNKNOWN").upper()
    else:
        dst_dir = vault / "LOCKED_RAW" / category
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / fname
    shutil.copy2(src, dst)
    digest = sha256(dst)

    sidecar = vault / "MANIFESTS" / "raw" / (fname + ".json")
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps({
        "schema": "raw_ingest_manifest.v1",
        "ingested_at": utc(),
        "src": str(src),
        "dst": str(dst.relative_to(vault)),
        "sha256": digest,
        "category": category,
        "market": market,
        "note": note
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    append_ledger(vault, "PROMOTE_RAW", str(src), str(dst.relative_to(vault)), digest, {"category": category, "market": market, "note": note})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Quant-Vault root")
    ap.add_argument("--category", default="market_raw", help="market_raw|black_swan|backtest")
    ap.add_argument("--market", default=None, help="TW|US|JP|CRYPTO (for backtest)")
    ap.add_argument("--note", default="", help="note for ledger")
    args = ap.parse_args()

    vault = Path(args.root).expanduser().resolve()
    inbox = vault / "INBOX_STAGING" / "raw_drop"
    quarantine = vault / "INBOX_STAGING" / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)

    for p in inbox.glob("*"):
        v = basic_validate(p)
        if v["ok"]:
            promote(vault, p, args.category, args.market, args.note)
            p.unlink()  # remove from inbox after successful promote
        else:
            q = quarantine / p.name
            shutil.move(str(p), q)
            append_ledger(vault, "QUARANTINE", str(p), str(q.relative_to(vault)), None, {"errors": v["errors"]})

    print("✅ Validation & promotion done.")

if __name__ == "__main__":
    main()
