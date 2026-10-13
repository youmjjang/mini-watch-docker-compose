# Mini-watch (Day1 Compose + Day2 cloud)

See [Day2 changes](README-day2.md) and [deployment plan](deployment-plan.md). Day1 Compose instructions and gateways remain in the repository; use the two Compose files for local runs and separate Render Docker services for cloud.

## Runtime roles
- general/: user login, posts CRUD, sends sanitized event records to monitor Flask
- monitor/backend/: user login, events classifications/list, notes CRUD and event token verification
- monitor/next-frontend/: monitor UI, same-origin /api forwarding to monitor Flask

Configuration and validation steps are in deployment-plan.md. No credentials or actual environment files should be committed.
