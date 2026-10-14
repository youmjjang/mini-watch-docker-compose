def normalize_event(row):
    event = dict(row)
    event["id"] = f"http-{row['id']}"
    event["source"] = "http_live"
    event["kind"] = row["event_type"]
    return event


def normalize_events(rows):
    return [normalize_event(row) for row in rows]
