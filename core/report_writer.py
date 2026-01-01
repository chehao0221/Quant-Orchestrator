# core/report_writer.py
import json
import os
import time
from pathlib import Path
from typing import Dict


class ReportFormatError(Exception):
    """報告格式不合規，直接中止流程"""
    pass


class ReportWriter:
    """
    標準化策略結果輸出器
    --------------------
    - 所有策略結果「唯一合法出口」
    - 作為 evaluation / guardian / learning 的唯一輸入
    """

    REQUIRED_FIELDS = {
        "strategy",
        "market",
        "date",
        "return",
        "drawdown",
        "volatility",
        "win_rate",
        "confidence"
    }

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.snapshot_root = (
            self.vault_root / "TEMP_CACHE" / "snapshot"
        ).resolve()

        self.snapshot_root.mkdir(parents=True, exist_ok=True)

    # ---------- public API ----------

    def write_report(self, report: Dict) -> Path:
        """
        寫入單一策略的標準化結果
        """

        self._validate_report(report)

        date = report["date"]
        strategy = report["strategy"]

        target_dir = self.snapshot_root / date
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / f"{strategy}.json"

        record = {
            "meta": {
                "generated_at": int(time.time()),
                "schema_version": 1
            },
            "report": report
        }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        return target_path

    # ---------- internal ----------

    def _validate_report(self, report: Dict):
        missing = self.REQUIRED_FIELDS - report.keys()
        if missing:
            raise ReportFormatError(
                f"報告缺少必要欄位: {missing}"
            )

        if not (0.0 <= report["confidence"] <= 1.0):
            raise ReportFormatError("confidence 必須介於 0~1")

        if not (-1.0 <= report["return"] <= 1.0):
            raise ReportFormatError("return 必須介於 -1~1")

        if not (-1.0 <= report["drawdown"] <= 0.0):
            raise ReportFormatError("drawdown 必須 ≤ 0")

