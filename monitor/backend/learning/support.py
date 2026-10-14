from datetime import datetime, timezone
from repositories.events import last_id, after_id


def start_observation():
    return {"after_id": last_id()}


def observation_rows(after, reference_time):
    return after_id(after, reference_time)


def now_iso():
    return datetime.now(timezone.utc).isoformat()
