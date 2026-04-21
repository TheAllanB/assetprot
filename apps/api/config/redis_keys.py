def task_key(task_id: str) -> str:
    return f"guardian:task:{task_id}"


def url_cache_key(url_hash: str) -> str:
    return f"guardian:cache:url:{url_hash}"


def rate_limit_key(org_id: str, endpoint: str) -> str:
    return f"guardian:rl:{org_id}:{endpoint}"


def session_key(session_id: str) -> str:
    return f"guardian:session:{session_id}"
