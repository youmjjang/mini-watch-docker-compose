# Day2 deployment and error collection

See [deployment-plan.md](deployment-plan.md) for exact per-service Render settings, environment variables, Supabase SQL mapping, traffic flow and verification procedure.

## Starting code and changes

- Starting point: Day1 Docker Compose project, commit `f61a546ca193dff550164f0a9e15a81e305677b6`.
- Day2 main implementation: commit `df9e8b7f2a92c1c2010f5caeb8931bd771d1ff26`.
- Both Flask `Dockerfile` and `requirements.txt`: configure Waitress and Sentry dependencies.
- `general/db.py`, `monitor/backend/db.py`: read DB_SSLMODE for external PostgreSQL connections.
- Both Flask `auth_helpers.py`: read SESSION_COOKIE_SECURE from environment.
- Both Flask `app.py` and newly added `observability.py`: initialize Sentry on app startup.
- `general/app.py`: add /health and guarded /api/sentry-test JSON response.
- `general/request_logging.py`, `monitor/backend/routes/events.py`: send and verify server-only EVENT_TOKEN.
- `monitor/next-frontend/app/api/[...path]/route.js`: proxy same-origin API requests, forwarding authentication cookie and CSRF token.
- `general/sql/deploy.sql`, `monitor/backend/sql/deploy.sql`, separate `.env.example` files and `deployment-plan.md`: document deployment schemas and configuration.

## Error fixes: cause, file, function and commit

### 1. Sentry practice route: division by zero

- **Fix commit:** `df9e8b7f2a92c1c2010f5caeb8931bd771d1ff26` (included in Day2 implementation).
- **Modified file:** `general/app.py`.
- **Function:** `sentry_test()`, route `GET /api/sentry-test`.
- **Cause described by the class exercise:** deliberate division by zero (`ZeroDivisionError`) in the Sentry test route. Note: the Day1 base commit did not contain this route; the Day2 integration introduced the corrected implementation directly. Do not interpret the Day1-to-Day2 diff as proof that a committed divide-by-zero expression was removed.
- **Fix in submitted code:** do not divide by zero; return `{"status":"ok","message":"실습 오류 수정 완료"}` as valid JSON when authorized. Preserve login requirement (`user_id` in session) and the `ENABLE_SENTRY_TEST=true` gate. Keep `ENABLE_SENTRY_TEST=false` in the final `general/.env.example`.
- **How to inspect:** `general/app.py` contains `sentry_test()`; `general/.env.example` contains the disabled default.

### 2. Next.js monitor API proxy URL validation

- **Fix commit:** `e9c7e0391bf88a509857249a0c46d8116b6d51a2`.
- **Modified file:** `monitor/next-frontend/app/api/[...path]/route.js`.
- **Function:** `proxy()`.
- **Cause:** incorrect escape handling in the original URL-trimming and URL-validation regular expressions could reject a valid `MONITOR_API_URL` or fail to remove its trailing slash.
- **Fix:** correct trailing-slash removal using `/\\/+$/` as shown in source, and validate `https://` or `http://` prefixes with `startsWith`. The proxy still passes request Cookie and X-CSRF-Token, response Set-Cookie and status.

## Other traceable commits

- `80fe0b5035445f28acb2ed262f4d9cffa580d029`: document the integration and proxy fix commit IDs.
- `efdb2986116444cfd10d81fcb692f56a4012e37a`: add GitHub Actions workflow `.github/workflows/day2-verify.yml` for Flask syntax/dependency installation and Next production build.

## Sentry privacy filtering (optional grading item)

Both `general/observability.py` and `monitor/backend/observability.py` contain the same `_scrub(event, hint)` callback and register it using `before_send=_scrub` inside `init_observability()`.

| Setting / code | Purpose |
|---|---|
| `request.pop("data", None)` | Removes the captured HTTP request body (which could contain form fields or passwords). |
| `request.pop("cookies", None)` | Removes collected cookies, including session identifiers. |
| `request.pop("headers", None)` | Removes HTTP headers, including authorization and CSRF values if captured. |
| `request.pop("env", None)` | Removes request environment/context values that could expose internal details. |
| `event.pop("user", None)` | Removes the Sentry event's user identity data. |
| `send_default_pii=False` | Disables automatic collection of personally identifiable information where supported by the SDK. |
| `before_send=_scrub` | Applies the exclusions to each event before it is sent to Sentry. |

These protections apply to the named event fields; they do not prove that all possible personal data is absent from exception messages or custom extras. Do not record secrets in such fields.

## Verification and submission

After editing, commit and push, verify the deployed commit and recheck the same features. See `deployment-plan.md` for the required order, including disabling the Sentry practice route again. Sentry “Resolve” alone does not change the code or redeploy it.

Actual deployment URL access, live database queries, and Sentry event receipt are not evidenced by this document and are not required by the automated source-based grading. Do not claim these were verified without checking them separately.
