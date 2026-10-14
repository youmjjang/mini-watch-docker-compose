import json
from pathlib import Path
from .report import build_report
def main():
    rows = json.loads((Path(__file__).parent / "data" / "observation.json").read_text(encoding="utf-8"))
    card = build_report(rows)
    print("조회", card["observed"], "근거", card["evidence"])
    print("뒤따른 404", [r["id"] for r in card["records"] if r["status_code"] == 404])
if __name__ == "__main__":
    main()
