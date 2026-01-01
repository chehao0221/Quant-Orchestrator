# core/report_writer.py
import os
import json
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, Literal


Market = Literal["TW", "US", "JP", "CRYPTO"]


class ReportWriterError(Exception):
    pass


@dataclass(frozen=True)
class StandardReport:
    """
    標準化報告（固定欄位，不允許隨意加減，避免未來格式混亂）
    """
    date: str                    # YYYY-MM-DD
    market: Market               # TW / US / JP / CRYPTO
    strategy: str                # 策略名稱或版本
    horizon: str                 # e.g. "1D", "1W", "1M"
    return_pct: float            # 報酬率（百分比，例如 1.23 = +1.23%）
    drawdown_pct: float          # 回撤（百分比，通常為負值）
    volatility_pct: float        # 波動（百分比）
    win_rate: float              # 0~1
    confidence: float            # 0~1
    sample_size: int             # 用多少筆樣本/交易/天數（至少要有）
    notes: str = ""              # 可留空


class ReportWriter:
    """
    將策略結果輸出到 Quant-Vault/TEMP_CACHE/snapshot/ 形成後續評估與學習唯一輸入
    """
    SNAPSHOT_DIR = Path("TEMP_CACHE") / "snapshot"

    REQUIRED_FIELDS = {
        "date", "market", "strategy", "horizon",
        "return_pct", "drawdown_pct", "volatility_pct",
        "win_rate", "confidence", "sample_size", "notes"
    }

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.snapshot_root = (self.vault_root / self.SNAPSHOT_DIR).resolve()
        self.snapshot_root.mkdir(parents=True, exist_ok=True)

    # ---------------- public API ----------------

    def write_report(self, report: StandardReport) -> Path:
        """
        寫入單一市場報告（原子寫入）
        產出：
        E:\Quant-Vault\TEMP_CACHE\snapshot\YYYY-MM-DD\{market}.json
        """
        payload = asdict(report)
        self._validate_payload(payload)

        day_dir = (self.snapshot_root / report.date).resolve()
        day_dir.mkdir(parents=True, exist_ok=True)

        target_path = (day_dir / f"{report.market}.json").resolve()
        if not str(target_path).startswith(str(self.snapshot_root)):
            raise ReportWriterError("非法寫入路徑（疑似 path traversal）")

        record = {
            "meta": {
                "timestamp": int(time.time()),
                "schema_version": "1.0",
                "payload_hash": self._hash_payload(payload),
            },
            "data": payload
        }

        self._atomic_write_json(target_path, record)
        return target_path

    def write_bundle(
        self,
        date: str,
        reports: Dict[Market, StandardReport],
        require_all_markets: bool = False
    ) -> Dict[Market, Path]:
        """
        一次寫入多市場報告
        - require_all_markets=True 代表缺任何市場就直接失敗（嚴格模式）
        """
        if require_all_markets:
            missing = [m for m in ["TW", "US", "JP", "CRYPTO"] if m not in reports]
            if missing:
                raise ReportWriterError(f"缺少市場報告（嚴格模式）：{missing}")

        written: Dict[Market, Path] = {}
        for mkt, rep in reports.items():
            if rep.date != date:
                raise ReportWriterError(f"{mkt} 報告 date 不一致：{rep.date} != {date}")
            written[mkt] = self.write_report(rep)
        return written

    # ---------------- validations ----------------

    def _validate_payload(self, payload: Dict[str, Any]) -> None:
        keys = set(payload.keys())
        missing = self.REQUIRED_FIELDS - keys
        extra = keys - self.REQUIRED_FIELDS

        if missing:
            raise ReportWriterError(f"報告缺欄位：{sorted(missing)}")
        if extra:
            # 這裡故意「不允許多欄位」，避免未來亂加造成下游崩壞
            raise ReportWriterError(f"報告出現未定義欄位（禁止）：{sorted(extra)}")

        # 型別與範圍
        if payload["market"] not in ("TW", "US", "JP", "CRYPTO"):
            raise ReportWriterError(f"market 不合法：{payload['market']}")

        for k in ("win_rate", "confidence"):
            v = payload[k]
            if not (0.0 <= float(v) <= 1.0):
                raise ReportWriterError(f"{k} 超出範圍 0~1：{v}")

        if int(payload["sample_size"]) <= 0:
            raise ReportWriterError(f"sample_size 必須 > 0：{payload['sample_size']}")

    # ---------------- utils ----------------

    @staticmethod
    def _hash_payload(payload: Dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _atomic_write_json(path: Path, content: Dict[str, Any]) -> None:
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
