"""Create actual HTTP requests and retrieve their persisted monitor DB rows."""
import json
import os
import sys
import time
from urllib.request import urlopen
from urllib.error import HTTPError
from repositories.events import last_id, after_id

def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or int(sys.argv[1]) < 1:
        raise SystemExit("Usage: python -m learning.capture_case 4|12")
    count = int(sys.argv[1])
    boundary = last_id()
    base = os.environ.get("GENERAL_CAPTURE_URL", "http://general-api:5000").rstrip("/")
    for path in ["/"] * count + ["/training-missing"]:
        try:
            with urlopen(base + path, timeout=5) as response:
                status = response.status
        except HTTPError as err:
            status = err.code
        expected = 404 if path == "/training-missing" else 200
        if status != expected:
            raise RuntimeError(f"{path} returned {status}, expected {expected}")
    rows = []
    for _ in range(20):
        rows = after_id(boundary)
        if len(rows) >= count + 1:
            break
        time.sleep(0.25)
    if len(rows) != count + 1:
        raise RuntimeError(f"Expected {count + 1} persisted rows, got {len(rows)}. Check EVENT_TOKEN and general/monitor logs.")
    print(json.dumps(rows, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
