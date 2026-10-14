import json
from pathlib import Path
from .report import build_report
def main():
    rows = json.loads((Path(__file__).parent / "data" / "observation.json").read_text(encoding="utf-8"))
    for threshold in (10, 20):
        card = build_report(rows, threshold)
        print("기준", threshold, "조회", card["observed"], "판정", card["verdict"], "근거", len(card["records"]))
if __name__ == "__main__":
    main()
