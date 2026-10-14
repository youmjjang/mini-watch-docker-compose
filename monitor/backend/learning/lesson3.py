import json
from pathlib import Path
from .normalize import normalize_events
from .http_rules import select_views
def main():
    rows = json.loads((Path(__file__).parent / "data" / "observation.json").read_text(encoding="utf-8"))
    views = select_views(normalize_events(rows))
    print("조회", len(views), "근거 ID", [row["id"] for row in views])
if __name__ == "__main__":
    main()
