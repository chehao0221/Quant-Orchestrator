def should_keep(meta):
    """
    meta:
      - hit_rate
      - usage_count
      - last_used_days
    """

    if meta["hit_rate"] >= 55:
        return True

    if meta["usage_count"] >= 10:
        return True

    if meta["last_used_days"] < 30:
        return True

    return False
