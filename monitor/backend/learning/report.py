from .http_rules import select_views, find_following_errors
from .normalize import normalize_events


def build_report(raw_rows, threshold=10):
    events = normalize_events(raw_rows)
    views = select_views(events)
    following = find_following_errors(events, views)
    records = sorted(views + following, key=lambda row: int(row["id"].split("-")[1]))
    count = len(views)
    flagged = count >= threshold
    return {
        "rule_id": "http_post_list",
        "title": "게시판 목록 조회",
        "observed": count,
        "threshold": threshold,
        "candidate": flagged,
        "verdict": "검토 후보" if flagged else "기준 미해당",
        "reason": f"목록 조회 {count}회와 기준 {threshold}회 비교. 뒤따른 404 {len(following)}건은 횟수에 포함하지 않음.",
        "view_ids": [row["id"] for row in views],
        "evidence": [row["id"] for row in records],
        "records": records,
    }
