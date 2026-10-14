from datetime import datetime
from flask import Blueprint, request
from auth_helpers import api_access_error
from learning.report import build_report
from learning.support import start_observation, observation_rows, now_iso

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.before_request
def require_auth():
    return api_access_error()


@analysis_bp.post("/api/analysis/start")
def start():
    return start_observation()


@analysis_bp.get("/api/analysis")
def analyze():
    try:
        after = int(request.args.get("after_id", ""))
        threshold = int(request.args.get("threshold", "10"))
        if not (0 <= after <= 2147483647 and 1 <= threshold <= 1000000):
            raise ValueError
        ref = request.args.get("reference_time")
        if ref:
            reference = datetime.fromisoformat(ref.replace("Z", "+00:00"))
            if reference.tzinfo is None:
                raise ValueError
            reference_time = reference.isoformat()
        else:
            reference_time = now_iso()
    except (ValueError, OverflowError, TypeError):
        return {"error": "관찰 ID, 기준 또는 기준시각이 잘못되었습니다."}, 400
    result = build_report(observation_rows(after, reference_time), threshold)
    return {"after_id": after, "reference_time": reference_time, "card": result}
