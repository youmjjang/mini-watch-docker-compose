import os
from flask import Flask
from observability import init_observability
from routes.posts import posts_bp
from routes.auth import auth_bp
from auth_helpers import configure_session, no_cache, template_auth
from error_handlers import register_error_handlers
from request_logging import record_request

init_observability()
app = Flask(__name__)
app.json.ensure_ascii = False
configure_session(app, "general_session")
app.register_blueprint(posts_bp)
app.register_blueprint(auth_bp)
app.context_processor(template_auth)
register_error_handlers(app)
app.after_request(no_cache)
app.after_request(record_request)


@app.get("/health")
def health():
    return {"service": "general", "status": "ok"}


@app.get("/api/sentry-test")
def sentry_test():
    from flask import session, jsonify
    if "user_id" not in session:
        return {"error": "로그인이 필요합니다."}, 401
    if os.environ.get("ENABLE_SENTRY_TEST", "false").lower() != "true":
        return {"error": "실습 오류 경로가 비활성화되어 있습니다."}, 404
    return jsonify({"status": "ok", "message": "실습 오류 수정 완료"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
