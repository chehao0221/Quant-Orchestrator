# Performance Judge AI（只負責公平判斷）

def judge(result: dict) -> dict:
    if result["hit"]:
        return {"score": 1.0, "label": "HIT"}
    return {"score": 0.0, "label": "MISS"}
