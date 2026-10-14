from datetime import datetime


def select_views(events):
    return [event for event in events if (
        event.get("method") == "GET"
        and event.get("path") == "/"
        and event.get("status_code") == 200
        and event.get("kind") == "post_list"
    )]


def parse_time(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def find_following_errors(events, views):
    if not views:
        return []
    last = max(parse_time(row["occurred_at"]) for row in views)
    return [row for row in events if row.get("status_code") == 404
            and 0 < (parse_time(row["occurred_at"]) - last).total_seconds() <= 30]
