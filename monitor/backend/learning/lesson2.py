import json
from pathlib import Path
from .normalize import normalize_events
DATA = Path(__file__).parent / "data" / "observation.json"
def main():
    events = normalize_events(json.loads(DATA.read_text(encoding="utf-8")))
    print(f"정규화 원본 {len(events)}행")
    for e in events:
        print(e["id"], e["kind"], e["method"], e["path"], e["status_code"], e["occurred_at"])
if __name__ == "__main__":
    main()
