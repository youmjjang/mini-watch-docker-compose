# Day2 deployment and error collection

See [deployment-plan.md](deployment-plan.md) for exact per-service Render settings, environment variables, Supabase SQL mapping, traffic flow and verification procedure.

Starting code: previous Day1 mini-watch Docker Compose project on main (f61a546ca193dff550164f0a9e15a81e305677b6). On day2-deploy, updated both Flask Dockerfiles to Waitress; each db.py adds DB_SSLMODE; cookie security is environment-controlled; added observability.py and safe Sentry initialization; general app gains /health and guarded /api/sentry-test returning JSON (instead of ZeroDivisionError); secured event delivery with EVENT_TOKEN; added a Next server Route Handler forwarding auth cookies and CSRF headers; added separate DB deployment scripts, environment examples, and Render plan.

Error: an intentional division by zero in the class sample would raise ZeroDivisionError. The guarded general/app.py sentry_test function now returns a valid JSON response without division; only authenticated users with ENABLE_SENTRY_TEST=true can call it. Commit identifiers: starting commit f61a546; Day2 changes: refer to current day2-deploy branch HEAD in GitHub. Actual deployment, DB and Sentry receipt are **not yet verified**.
