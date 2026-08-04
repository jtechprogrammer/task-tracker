# Comments Feature Plan

## 1. Data Model

Existing task models live in `app/models/task.py`, and `app/models/__init__.py` re-exports the public model classes. Comments should follow that pattern.

Add comment schemas in a new model module, likely `app/models/comment.py`, then export them from `app/models/__init__.py`.

Recommended model split:

| Model | Purpose |
|---|---|
| `CommentCreate` | Request body for creating a comment. Contains `author` and `body` only. |
| `CommentResponse` | API response and persisted representation. Contains `id`, `task_id`, `author`, `body`, and `created_at`. |

Validation should match existing Pydantic conventions from `app/models/task.py`:

| Field | Rule |
|---|---|
| `author` | Required string, trimmed, 1-100 characters after trimming. |
| `body` | Required string, trimmed, 1-2000 characters after trimming. |
| unknown fields | Rejected, consistent with `ConfigDict(extra="forbid")` on task create/update models. |
| `id` | Server-generated UUID string. |
| `task_id` | Comes from the route path, not the request body. |
| `created_at` | Server-generated UTC datetime. |

The current task IDs are generated with `uuid4().hex` in `app/repositories/task_repository.py`. The team should decide whether comment IDs should also use hex UUID strings for consistency or dashed UUID strings because the requirement says "string UUID."

Comments should not be embedded into `TaskResponse` by default. The current task response shape is focused on task fields only, and adding embedded comments to every `GET /tasks` response would change list payload size and frontend behavior. Prefer separate comment endpoints first.

## 2. API Routes

Task routes currently live directly in `app/main.py`, while only health uses a router in `app/api/routes/health.py`. For the smallest consistent change, comment routes could be added near the existing task routes in `app/main.py`. For better organization, the team could move task/comment routes into `app/api/routes/`, but that would be a broader route-structure cleanup.

Routes should continue the observed layering from `AGENTS.md`: route -> service -> repository -> JSON file. Route handlers should not read JSON files directly.

| Method | Path | Request Body | Response |
|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | `author`, `body` | `201 Created` with `CommentResponse` |
| `GET` | `/tasks/{task_id}/comments` | none | `200 OK` with list of `CommentResponse` |
| `DELETE` | `/tasks/{task_id}/comments/{comment_id}` | none | `204 No Content` |

Recommended error cases:

| Case | Status |
|---|---|
| `task_id` does not match an existing task on create/list/delete | `404`, detail like "Task not found" |
| `comment_id` does not exist for that task on delete | `404`, detail like "Comment not found" |
| `author` missing, blank, not a string, or over 100 characters | `422` |
| `body` missing, blank, not a string, or over 2000 characters | `422` |
| unknown request fields such as `created_at` or `task_id` in create body | `422` |

A direct `GET /comments/{comment_id}` endpoint is not necessary for a task-centered feature unless the frontend or future API clients need comment lookup independent of task context.

## 3. Tests

Existing tests use `fastapi.testclient.TestClient`, live endpoint calls, and an autouse fixture in `tests/conftest.py` that resets the task repository. Comment tests should follow `tests/test_tasks.py` naming and assertion style.

Happy path:

| Test name | Purpose |
|---|---|
| `test_create_comment_valid_returns_201_with_full_body` | Creates a task, posts a comment, verifies generated `id`, path `task_id`, `author`, `body`, and `created_at`. |
| `test_list_comments_for_task_returns_200_with_comments` | Creates multiple comments for one task and verifies they are returned. |
| `test_list_comments_empty_returns_200_and_empty_list` | Existing task with no comments returns `[]`. |
| `test_delete_existing_comment_returns_204_no_body` | Deletes an existing comment and verifies empty response body. |

Validation:

| Test name | Purpose |
|---|---|
| `test_create_comment_missing_author_returns_422` | Reject missing author. |
| `test_create_comment_blank_author_returns_422` | Reject whitespace-only author. |
| `test_create_comment_author_over_100_returns_422` | Enforce author length. |
| `test_create_comment_missing_body_returns_422` | Reject missing body. |
| `test_create_comment_blank_body_returns_422` | Reject whitespace-only body. |
| `test_create_comment_body_over_2000_returns_422` | Enforce body length. |
| `test_create_comment_unknown_field_returns_422` | Match task model `extra="forbid"` behavior. |
| `test_create_comment_client_supplied_id_returns_422` | Confirm server-managed fields are not accepted. |
| `test_create_comment_client_supplied_created_at_returns_422` | Confirm timestamp is server-managed. |

Edge cases:

| Test name | Purpose |
|---|---|
| `test_create_comment_for_missing_task_returns_404` | Comments cannot be created for nonexistent tasks. |
| `test_list_comments_for_missing_task_returns_404` | Decide and verify missing parent task behavior. |
| `test_delete_comment_for_missing_task_returns_404` | Missing task wins over comment lookup. |
| `test_delete_missing_comment_returns_404` | Existing task, missing comment. |
| `test_list_comments_filters_by_task_id` | Comments for task A do not appear under task B. |
| `test_delete_task_comment_cleanup_behavior` | Verify whatever delete-task behavior the team chooses for related comments. |
| `test_comment_created_at_is_utc_datetime` | Confirms UTC server timestamp behavior, matching task timestamp intent. |

The existing autouse fixture only resets `repo` from `app/main.py`. If comments use a separate repository or file, tests need to reset comment storage too.

## 4. Frontend Changes

The frontend is a single-file Kanban app in `frontend/index.html`. It currently renders task cards, an add/edit task modal, drag-and-drop status changes, tags, due dates, and overdue filtering.

Recommended user experience:

| Area | Change |
|---|---|
| Task cards | Add a small comment count or "Comments" action on each card. |
| Task detail/comment panel | Add an expandable comments area or modal tied to a selected task. |
| Comment list | Show author, body, and created time for each comment. |
| Comment form | Add author and body inputs with client-side length checks matching backend limits. |
| Error handling | Reuse existing board/modal error patterns for validation and network failures. |
| Refresh behavior | After creating or deleting a comment, refresh only that task's comments if possible. |

Since task cards are rebuilt in JavaScript by `createCardElement()`, comment UI would likely be added there. Fetching comments for every task during `fetchTasks()` could create extra requests, so the first implementation should probably lazy-load comments when a user opens a task's comments.

No framework or build setup is visible; changes should stay in `frontend/index.html` unless the team decides to restructure the frontend.

## 5. Migration Notes

Current persisted tasks are stored as a JSON list at `app/data/tasks.json`, and that file currently contains an empty list.

Recommended storage shape: create a separate comments JSON file, likely `app/data/comments.json`, storing a flat list of comment objects. This avoids changing existing task records and keeps comments queryable by `task_id`.

Migration impact:

| Area | Note |
|---|---|
| Existing task data | No task record migration needed if comments are stored separately. |
| New storage file | The repository should tolerate missing, empty, invalid, or non-list comment storage consistently with `JsonTaskRepository`, unless the team decides to harden that behavior. |
| Task deletion | The current task repository deletes only the task. The team must decide whether deleting a task also deletes its comments. |
| Tests | Test reset logic must clear both task and comment storage. |
| Docker/local data | Security docs note that `app/data/tasks.json` can be copied into Docker images; the same consideration would apply to `comments.json`. |
| Concurrency | Existing repository reads/writes full JSON files and locks only writes. Comments would inherit similar lost-update risks unless the repository pattern is improved. |

## 6. Open Questions

1. Should comment IDs use `uuid4().hex` like existing task IDs, or standard dashed UUID strings?
2. Should deleting a task cascade-delete its comments, leave orphaned comments in storage, or reject task deletion while comments exist?
3. Should comments be immutable after creation, or should the API include an edit endpoint such as `PATCH /tasks/{task_id}/comments/{comment_id}`?
4. Should `GET /tasks` include comment counts, or should the frontend fetch comment counts/details only when a task is opened?
5. Should list comments return oldest-first or newest-first? The repo has no visible ordering convention beyond task list insertion order and frontend sorting by priority/id.
6. Should `author` be free text, or should it eventually connect to authentication? The current app has no auth, as noted in `docs/security-review.md`.
7. Should blank trimming apply to both `author` and `body`? Existing task title validation trims before checking blank/length, but the requirement only says required 1-100 and 1-2000.

## Files read

- `AGENTS.md`
- `README.md`
- `app/main.py`
- `app/models/task.py`
- `app/models/__init__.py`
- `app/models/health.py`
- `app/models_legacy.py`
- `app/services/task_service.py`
- `app/repositories/task_repository.py`
- `app/business_rules.py`
- `app/api/routes/health.py`
- `app/data/tasks.json`
- `tests/conftest.py`
- `tests/test_tasks.py`
- `tests/verify_a.py`
- `frontend/index.html`
- `docs/technical-decision-status-transitions.md`
- `docs/security-review.md`
- `docs/governance-worksheet.md`
- `docs/ai-usage.md`

## Assumptions to verify

- No existing comment model, route, service, repository, or frontend comment UI was visible in the files read.
- No `app/storage.py` file was visible; task persistence is currently handled by `app/repositories/task_repository.py`.
- The README appears stale because it says task CRUD is not implemented, while `app/main.py` and `tests/test_tasks.py` show task CRUD exists.
- Tests were not run because this was a documentation-only planning task.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** TODO
**Plan I would hand to a teammate:** TODO
**Where the generic plan was still useful:** TODO
**Where repo grounding mattered most:** TODO
