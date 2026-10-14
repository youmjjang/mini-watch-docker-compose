from db import connect_db


def create_event(event):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO http_events (method, path, status_code, event_type)
               VALUES (%s, %s, %s, %s)""",
            (event["method"], event["path"], event["status_code"], event["event_type"]),
        )


def serialize(rows):
    return [{**row, "occurred_at": row["occurred_at"].isoformat()} for row in rows]


def list_events(event_type=None):
    with connect_db() as conn:
        if event_type is None:
            rows = conn.execute("SELECT * FROM http_events ORDER BY id DESC LIMIT 50").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM http_events WHERE event_type = %s ORDER BY id DESC LIMIT 50",
                (event_type,),
            ).fetchall()
    return serialize(rows)


def last_id():
    with connect_db() as conn:
        row = conn.execute("SELECT COALESCE(MAX(id), 0) AS id FROM http_events").fetchone()
    return row["id"]


def after_id(after, reference_time=None):
    with connect_db() as conn:
        if reference_time is None:
            rows = conn.execute(
                "SELECT * FROM http_events WHERE id > %s ORDER BY id ASC",
                (after,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM http_events WHERE id > %s
                   AND occurred_at > %s::timestamptz - INTERVAL '60 seconds'
                   AND occurred_at <= %s::timestamptz
                   ORDER BY id ASC""",
                (after, reference_time, reference_time),
            ).fetchall()
    return serialize(rows)
