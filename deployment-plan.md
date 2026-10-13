# Day2 cloud deployment plan

Repository: https://github.com/youmjjang/mini-watch-docker-compose
Deployment branch: day2-deploy (keep main and Day1 Compose intact)

| Render Docker Web Service | Root Directory | Dockerfile Path | Health Check Path | Status |
|---|---|---|---|---|
| Monitor API (Flask) | monitor/backend | ./Dockerfile | /health | Not deployed |
| General (Flask) | general | ./Dockerfile | /health | Not deployed |
| Monitor UI (Next.js) | monitor/next-frontend | ./Dockerfile | / | Not deployed |

Use Render Hobby/Free; Docker Build Context '.' relative to each Root Directory, leave Docker Command blank; Auto Deploy = On Commit. Flask Dockerfiles use Waitress with 0.0.0.0 and PORT, whereas local `python app.py` still works. Next uses npm ci, npm run build and npm run start; never request APIs/DB at build time. Keep compose-general.yaml, compose-monitor.yaml and gateways for local Docker runs; these are distinct from three Render services.

## Databases
Use two **different Supabase projects**. General uses `general/sql/deploy.sql` (users, posts), monitor uses `monitor/backend/sql/deploy.sql` (users, http_events, notes). No DROP/TRUNCATE or seed overwrite. Each project provides its own Session pooler host and user with DB_PORT=5432, DB_NAME=postgres and DB_SSLMODE=require; both use the same database *name* but are separate projects. Set DB_HOST, DB_USER, DB_PASSWORD separately for each Flask service. Turn off Data API for class-only projects if following course setup; database access happens server-side through psycopg. Run `python create_user.py` separately from each Flask folder in its respective local virtual environment after setting credentials. Never commit credentials.

## Request connections and secrets
General Flask MONITOR_URL = monitor Flask HTTPS base + `/api/events`; its EVENT_TOKEN must equal monitor Flask EVENT_TOKEN. Monitor Next server MONITOR_API_URL = monitor Flask HTTPS base (no /api). Browser calls same-origin `/api/...`, Next Route Handler forwards Cookie and X-CSRF-Token and returns Set-Cookie plus status. General sends only method/path/status; monitor checks a server-only X-Event-Token before recording login_failure/401, login_success/200 and other events. Never put secrets in NEXT_PUBLIC_* or browser JavaScript. General Flask and monitor Flask need distinct SECRET_KEY values (32+ characters), local HTTP SESSION_COOKIE_SECURE=false, Render HTTPS true. Configure SENTRY_DSN separately; SENTRY_ENVIRONMENT=mini-general or mini-monitor, APP_VERSION=day2-deploy. ENABLE_SENTRY_TEST remains false at rest. No paid services required.

## Verification order
1. Check monitor Flask /health and general Flask /health: this checks process/routing, **not database credentials**.
2. Confirm independent DB connections and query tables, then create one user in each project.
3. Log into monitor UI. Generate a wrong login (401) and right login (200) in general app, reload monitor events, confirm classified records in monitor DB.
4. Create/update/delete general posts and monitor notes, refresh and query the corresponding Supabase tables.
5. With general login, temporarily set ENABLE_SENTRY_TEST=true to test /api/sentry-test; ensure it returns normal JSON, then set false. Sentry Resolve merely closes an issue; it does not fix code or redeploy.
6. Commit/push, confirm Render deployed the commit, recheck health, login, existing posts and notes after redeploy. If Render/Supabase/Sentry connections are not configured, mark them not verified rather than claiming success.

## Troubleshooting
A /health success but 500 in listing posts/notes suggests a DB hostname, password, SSL or missing table issue. A 502 from Next /api indicates MONITOR_API_URL or monitor Flask connectivity; a 503 means MONITOR_API_URL missing. 400 is usually invalid input, 401 a missing session/bad credentials, 403 a failed CSRF check or invalid event token. Check the service's Render logs; do not expose headers, passwords or tokens. UI error text comes from api/client.js; retry with the existing reload button after fixing connectivity.
