# 匯總近期 AI 表現（給人看的）

def summarize(results: list) -> dict:
    total = len(results)
    hits = sum(1 for r in results if r["hit"])
    avg_error = sum(r["error"] for r in results) / max(total, 1)

    consecutive_miss = 0
    for r in reversed(results):
        if r["hit"]:
            break
        consecutive_miss += 1

    verdict = "AI 判斷穩定，未偵測到過度自信或失控行為。"
    if consecutive_miss >= 3:
        verdict = "AI 偵測到連續失誤，已自動進入保守調整模式。"

    return {
        "hit_rate": hits / max(total, 1),
        "avg_error": avg_error,
        "consecutive_miss": consecutive_miss,
        "verdict": verdict
    }
