# Security Review

Date: 2026-08-03

This review summarizes the Module 5 security audit findings for the Task Tracker learning project. The findings are valid either as real issues in the current repository or as course-scope limitations that would matter before using the app outside a local learning context.

## Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/models/task.py:64`, `app/models/task.py:120` | Non-string `title` values can produce HTTP 500 instead of validation 422. | The title validators raise `TypeError` for non-string values. A TestClient probe with `{"title": 123}` returned `500 Internal Server Error` under Pydantic `2.13.4`. | Raise `ValueError` or a Pydantic validation error type instead, and add create/update tests for non-string titles. | High |
| SEC-02 | Medium | `app/main.py:65`, `docs/midcourse/prompt-log.md:28` | Task CRUD has no authentication or authorization. This appears intentional for course scope, but it is unsafe if deployed beyond local learning use. | The `/tasks` create/list/get/patch/delete routes have no auth dependencies. The prompt log explicitly says not to add authentication. | Document "local/course only" clearly, or add auth before any shared/deployed environment. | High |
| SEC-03 | Medium | `app/models/task.py:56`, `app/repositories/task_repository.py:37` | Free-text fields and tag lists are mostly unbounded, while storage reads/writes the entire JSON file. | Only `title` has a 200-character limit; `description`, `assignee`, tag value length, and tag count have no limits. The repository reads the full file and writes the full collection. | Add max lengths/counts, request-size limits, and eventually pagination or database-backed storage. | High |
| SEC-04 | Medium | `app/repositories/task_repository.py:60`, `app/repositories/task_repository.py:112` | Concurrent writes can lose updates. | The lock only wraps `_write_all`; `add`, `update`, and `delete` perform read-modify-write with reads outside the lock. | Lock the whole read-modify-write operation, or move to a storage backend with transactional writes. | High |
| SEC-05 | Low | `app/repositories/task_repository.py:40` | Storage errors or invalid JSON are treated as an empty task list, which can mask corruption and lead to overwrite on the next write. | Missing, unreadable, empty, invalid, or non-list JSON all return `{}`. | Fail closed for unreadable/corrupt storage, log clearly, and consider backup/quarantine behavior. | High |
| SEC-06 | Low | `app/main.py:27`, `frontend/index.html:208` | CORS and frontend assumptions are local-development oriented. | CORS allows localhost origins plus `"null"` and wildcard methods/headers; the frontend hardcodes `http://localhost:8000`. | Remove `"null"` unless needed, make origins/API base environment-specific, and restrict methods/headers for production. | High |
| SEC-07 | Medium | `requirements.txt:1`, `.github/workflows/ci.yml:17`, `Dockerfile:13` | Dependency installs are not reproducible. | Runtime dependencies are unpinned; CI and Docker install from `requirements.txt`; `requirements.lock.txt` contains unrelated GUI packages, not the FastAPI stack. | Pin runtime dependencies, regenerate a real lock file, and add dependency vulnerability scanning. | High |
| SEC-08 | Low | `Dockerfile:33`, `app/data/tasks.json:1` | Docker images can include local task data. | Docker copies all of `app/`, including `app/data/tasks.json`; the current file is empty (`[]`), but future local data would be baked into the image. | Exclude seeded/local data from images, create an empty runtime file, or mount persistent storage separately. | Medium |

## Review Classification

| Finding ID | Proposed grade | Reason |
|---|---|---|
| SEC-01 | Valid | Malformed input can trigger a server error instead of a validation response. |
| SEC-02 | Valid | No authentication is intentional for course scope, but it is still a production risk. |
| SEC-03 | Valid | Unbounded fields plus whole-file storage create a resource-exhaustion and scaling risk. |
| SEC-04 | Valid | The current locking does not protect the full read-modify-write sequence. |
| SEC-05 | Valid | Silent fallback to empty storage can hide corruption and enable accidental data loss. |
| SEC-06 | Valid | Local-development CORS/API assumptions should be hardened before deployment. |
| SEC-07 | Valid | Unpinned runtime dependencies make builds non-reproducible. |
| SEC-08 | Valid, borderline | No current task data is exposed, but the Dockerfile would include future local persisted task data. |

## Files Inspected

- `AGENTS.md`
- `README.md`
- `app/main.py`
- `app/models/task.py`
- `app/models/health.py`
- `app/models_legacy.py`
- `app/business_rules.py`
- `app/services/task_service.py`
- `app/repositories/task_repository.py`
- `app/api/routes/health.py`
- `frontend/index.html`
- `tests/test_tasks.py`
- `tests/conftest.py`
- `tests/verify_a.py`
- `requirements.txt`
- `requirements.lock.txt`
- `Dockerfile`
- `.dockerignore`
- `.gitignore`
- `.env.example`
- `.github/workflows/ci.yml`
- relevant files under `docs/`

## Categories With No Issue Found

- Enum handling for `status` and `priority`
- Unknown-field rejection on task create/update models
- Blank and over-200-character title validation
- Due-date type validation
- Tag trimming and duplicate removal behavior
- Frontend rendering of task-controlled fields via `textContent`
- `.env` ignore rules
- Docker runtime user, which is non-root

## Assumptions And Limits

- This was a read-only audit except for creating this documentation file.
- `.env` was not inspected, following the project guardrail in `AGENTS.md`.
- Full tests were not run during the audit because the test fixture writes to `app/data/tasks.json`.
- No live dependency vulnerability lookup or dynamic security scan was performed.
- Git status was blocked by local dubious-ownership protection during the audit, so findings are based on direct file inspection.
