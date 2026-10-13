"""Minimal Sentry setup, without request/user PII."""
import os
import sentry_sdk


def _scrub(event, hint):
    request = event.get("request")
    if isinstance(request, dict):
        for key in ("data", "cookies", "headers", "env"):
            request.pop(key, None)
    event.pop("user", None)
    return event


def init_observability():
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "mini-monitor"),
            release=os.environ.get("APP_VERSION", "day2-deploy"),
            send_default_pii=False,
            before_send=_scrub,
            traces_sample_rate=0.0,
        )
