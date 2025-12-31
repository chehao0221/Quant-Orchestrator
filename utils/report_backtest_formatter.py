# schedule_backtest_reports.py
# 全市場回測報告自動排程器（終極封頂版）
# 職責：
# - 定時觸發 5 日回測準確率報告
# - 統一調度 post_all_backtest_reports
# - 可被 cron / systemd / 任意 orchestrator 呼叫
# ❌ 不計算 ❌ 不排版 ❌ 不學習

import time
from datetime import datetime
from typing import Optional

from post_all_backtest_reports import post_all_backtest_reports


# -------------------------------------------------
# 排程鐵律設定（集中管理）
# -------------------------------------------------

# 每日執行時間（24h 制，UTC）
RUN_HOUR_UTC = 1    # 01:00 UTC（美股收盤後、亞洲盤前）
RUN_MINUTE = 0

# 回測天數（全市場一致）
BACKTEST_DAYS = 5

# 失敗重試等待（秒）
RETRY_SLEEP = 60


# -------------------------------------------------
# 內部工具
# -------------------------------------------------

def _seconds_until_next_run(
    hour: int,
    minute: int,
    now: Optional[datetime] = None
) -> int:
    now = now or datetime.utcnow()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target <= now:
        # 已過當日時間，排到明天
        target = target.replace(day=now.day + 1)

    return int((target - now).total_seconds())


# -------------------------------------------------
# 主排程循環
# -------------------------------------------------

def run_scheduler() -> None:
    """
    常駐型排程（給 container / VM / systemd 使用）
    """
    while True:
        try:
            sleep_sec = _seconds_until_next_run(
                RUN_HOUR_UTC,
                RUN_MINUTE
            )
            time.sleep(sleep_sec)

            post_all_backtest_reports(days=BACKTEST_DAYS)

        except Exception as e:
            # ⚠️ 排程不中斷，避免單次錯誤卡死
            time.sleep(RETRY_SLEEP)


# -------------------------------------------------
# CLI 入口
# -------------------------------------------------

if __name__ == "__main__":
    run_scheduler()
