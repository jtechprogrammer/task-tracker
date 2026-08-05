# Release Evidence

## Baseline

- Branch: final-project
- Date: 2026-08-04
- Local app run command: `python -m uvicorn app.main:app --reload`
- `/health` result: {"status":"ok","timestamp":"2026-08-04T20:33:43.301760Z"}
- Frontend check: `GET /` → HTTP 200, `content-type: text/html; charset=utf-8`, serves `frontend/index.html` (verified 2026-08-05; response starts with the Kanban board's `<!doctype html>` / `<title>Task Tracker — Kanban</title>`).
- Test command: `python -m pytest tests -v`
- Test result: 34 passed

## CI Evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest successful run: https://github.com/jtechprogrammer/task-tracker/actions/runs/30948034958
- Test command used by CI: `python -m pytest tests -v`
- Shortcut check:
  - No `continue-on-error`
  - No `|| true`
  - Pytest is not skipped
  - Dependencies are installed

## Docker Evidence

- Build command: `docker build -t task-tracker-final .`
- Run command: `docker run --rm -p 8000:8000 task-tracker-final`
- `/health` check: {"status":"ok","timestamp":"2026-08-04T20:45:33.282876Z"} (re-verified 2026-08-05: {"status":"ok","timestamp":"2026-08-05T06:34:23.275129Z"})
- Non-root check: `docker exec task-tracker-final whoami` → `app`; `docker exec task-tracker-final id` → `uid=999(app) gid=999(app) groups=999(app)`. Matches the `USER app` directive set after `groupadd --system app && useradd --system ...` in the runtime stage of the `Dockerfile`.
- No-baked-secrets check: `docker history --no-trunc task-tracker-final` shows only `COPY /opt/venv`, `COPY app/`, and `COPY frontend/` layers — no `.env` or credential files are copied in. Confirmed inside the running container with `find / -iname '*.env*'`, which returned no matches; only `app/` and `frontend/` are present under `/home/app`, consistent with `.dockerignore` excluding everything except `requirements.txt`, `app/`, and `frontend/`.
- Runtime command: `docker inspect --format='{{json .Config.Cmd}}' task-tracker-final` → `["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]`, matching the `CMD` in the `Dockerfile` exactly.

## Documentation Claim-vs-Reality Log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README local run command works | Ran the documented command | Pass — `python -m uvicorn app.main:app --reload` started the API on `127.0.0.1:8000` with no errors | None |
| `/health` returns the documented response | Manual HTTP request | Pass — shape matches (`{"status":"ok","timestamp":...}`); the `timestamp` value itself is generated per-request, so it will never match a previously recorded example byte-for-byte | Noted that README/docs should show the response shape, not a literal timestamp, to avoid implying a fixed value — no doc currently claims a fixed timestamp, so no edit was needed |
| Docker command starts the API | Built and ran the image | Pass — `docker build` succeeded, `docker run -p 8000:8000` served `/health` with HTTP 200. Docker Desktop's engine was not running when this check started and had to be started manually first | None to the app; confirms the README's Docker section should assume Docker Desktop is already running, since the CLI gives a low-level pipe error otherwise |