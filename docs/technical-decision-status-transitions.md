# Technical Decision: Task Status Transition Rules

**Date:** 2026-07-29
**Context:** Module 4 Task Tracker — AI-Assisted Coding learning project
**Status:** Draft

---

## 1. Context

The Task Tracker is a minimal FastAPI REST API backed by a single JSON file. Tasks move through three workflow statuses — **ToDo**, **InProgress**, and **Done** — and the API must enforce which transitions are allowed. Without rules, a client could skip from ToDo directly to Done, bypassing InProgress, or set arbitrary status strings that have no meaning in the system.

The project uses a three-layer architecture: API routes delegate to a service layer, which delegates to a JSON file repository. Cross-cutting rules like status transitions need a single home so that every path that updates a task's status reaches the same validation.

Three statuses are defined in the `TaskStatus` enum at [app/models/task.py:10-20](../app/models/task.py#L10-L20):

| Enum member | API value |
|---|---|
| `TaskStatus.TODO` | `"ToDo"` |
| `TaskStatus.IN_PROGRESS` | `"InProgress"` |
| `TaskStatus.DONE` | `"Done"` |

New tasks default to `ToDo` ([app/models/task.py:58](../app/models/task.py#L58)).

---

## 2. Decision

**Status transition rules are enforced in a dedicated business-rules module and called by the service layer. The rules are:**

- **Allowed transitions:** ToDo → InProgress, InProgress → Done, Done → InProgress.
- **Same-status transitions are allowed** (ToDo→ToDo, InProgress→InProgress, Done→Done) for idempotent PATCH requests.
- **ToDo → Done is explicitly blocked** — a task must pass through InProgress first.
- **Invalid status strings are rejected at the model layer** by Pydantic enum validation before they reach the service.
- **Invalid transitions raise HTTP 422** with a detail message listing the allowed transitions.

The full set of valid transitions is defined as a `frozenset` in [app/business_rules.py:5-12](../app/business_rules.py#L5-L12):

```python
VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    (TaskStatus.TODO, TaskStatus.TODO),
    (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
    (TaskStatus.DONE, TaskStatus.DONE),
})
```

The `validate_status_transition()` function ([app/business_rules.py:15-35](../app/business_rules.py#L15-L35)) looks up the `(current, new)` pair in this set and raises `HTTPException(422)` if the pair is absent.

The service calls this function during `update_task()` only when the caller explicitly sets a new status ([app/services/task_service.py:100-101](../app/services/task_service.py#L100-L101)) — if `payload.status` is `None` (i.e. the field was not included in the PATCH body), no transition check runs.

**Completed tasks can be reopened.** Moving from Done→InProgress is a valid transition. This is intentional — the Kanban board frontend supports drag-and-drop between columns, and dragging a Done card back to InProgress must succeed.

---

## 3. Alternatives Considered

### A. Allow all transitions (no rules at all)

Any status could change to any other. This is the simplest approach and requires zero validation code. Rejected because it undermines the Kanban workflow — a task going straight from ToDo to Done skips the "in progress" signal, and a task going from Done back to ToDo loses the distinction between "not started" and "reopened."

### B. Enforce the rules inside the PATCH route handler in main.py

The route handler would check the transition before calling the service. Rejected because it violates the three-layer architecture: route handlers must not contain business logic. Putting the check in `main.py` also duplicates it if another route needs to update status later.

### C. Block reopening completed tasks (no Done→InProgress)

Done would be a terminal state — once a task is marked Done, its status cannot change. Rejected because the Kanban board supports drag-and-drop from the Done column back to InProgress, and the project's frontend is designed around this behavior ([CLAUDE.md:84-85](../CLAUDE.md#L84-L85)).

### D. Enforce the rules inside the Pydantic model (model validator)

A `@model_validator` on `TaskUpdate` could check the transition without a separate module. Rejected because the model does not have access to the task's *current* status — that data lives in the repository, not in the request body. The model validates the shape of incoming data; the service validates it against persisted state.

---

## 4. Trade-offs

**DRAFT — REWRITE IN MY OWN WORDS**

| Trade-off | Detail |
|---|---|
| **Single source of truth for rules** | The `VALID_TRANSITIONS` frozenset is the only place transition rules are defined. Adding a new status means updating one data structure. The risk is that a developer adds a status enum value but forgets to update the frozenset — the linter will not catch this. |
| **Business-rules module couples to HTTP** | `validate_status_transition()` raises `HTTPException` directly ([app/business_rules.py:32-35](../app/business_rules.py#L32-L35)). This means the business-rules module cannot be tested without FastAPI, and it cannot be reused in a non-HTTP context (e.g. a CLI or background worker). A pure domain exception caught by the service would decouple these concerns. |
| **Idempotent same-status transitions allowed** | PATCH with `{"status": "ToDo"}` on a task already at ToDo returns 200 rather than 422. This simplifies the frontend (the Kanban board can send the same status on any drag without checking the current value first). The downside is it masks client bugs — a client that accidentally re-sends the same status gets silent success instead of a signal that nothing changed. |
| **Done→InProgress is allowed; Done→ToDo is not** | Reopening a task sends it to InProgress, not ToDo. The team decided that a reopened task was already started, so "not started" is inaccurate. The frontend's Kanban board only has three columns and drag-and-drop targets the InProgress column, so this maps naturally. [VERIFY: whether the frontend actually prevents dropping a Done card onto the ToDo column] |
| **Three statuses is intentionally minimal** | Adding a "Blocked" or "Cancelled" status would require updating the enum, the frozenset, the Kanban board columns, and every test that iterates over statuses. The project ADRs constrain scope intentionally — no new backend endpoints for filtering, no separate models for tags. The same philosophy applies to statuses. |

---

## 5. Consequences

**What the current implementation delivers:**

- Every status change through the API is validated. A client cannot set a task to an arbitrary string (Pydantic enum validation blocks it before the service runs).
- ToDo→Done is blocked. The error response body includes the list of allowed transitions, making the API self-documenting for a developer reading error output.
- Completed tasks can move back to InProgress — the workflow is not a one-way pipeline.
- Same-status PATCH requests are harmless and return 200, so the Kanban board does not need conditional logic before sending a drag event.

**What the current implementation does not cover (and is out of scope for Module 4):**

- There is no audit log of status changes. The `updated_at` timestamp is overwritten on every PATCH regardless of which field changed.
- There is no per-status field validation (e.g. requiring a `completed_at` timestamp when moving to Done, or requiring an assignee before moving to InProgress).
- There is no rate-limiting or concurrent-edit conflict detection — the last write wins.
- The rules are not enforced at the repository layer. If a future feature writes directly to the JSON file or uses a different service, the transition rules must be re-invoked manually.

**Tests that verify the behavior (from [tests/test_tasks.py](../tests/test_tasks.py)):**

| Test | What it verifies |
|---|---|
| `test_patch_valid_transition_todo_to_inprogress_returns_200` (line 208) | ToDo→InProgress is allowed |
| `test_patch_invalid_transition_todo_to_done_returns_422` (line 217) | ToDo→Done is blocked |
| `test_patch_invalid_status_value_returns_422` (line 225) | Bogus status `"Backlog"` is rejected at the model layer |
| `test_patch_same_status_returns_200_unchanged` (line 235) | ToDo→ToDo is idempotent |
| `test_patch_partial_update_keeps_other_fields` (line 187) | Status change preserves other fields and returns 200 |

No automated test currently verifies the Done→InProgress transition or the InProgress→InProgress idempotency case. These are implicit in the `VALID_TRANSITIONS` frozenset but lack explicit regression coverage. [VERIFY: whether a Done→InProgress test exists elsewhere or was deliberately omitted.]

---

## 6. Open Questions

**DRAFT — REWRITE IN MY OWN WORDS**

1. **Should Done→ToDo ever be allowed?** Currently it is not. A task that was marked Done by mistake must go through InProgress before it can return to ToDo (which requires two PATCH requests). Is this friction intentional, or should an "undo" path exist?
2. **Should the transition error response include the current status?** The 422 error currently says "Invalid transition from X to Y. Allowed: […]" It could also echo the current status so the client can reconcile without a separate GET request.
3. **Should the business-rules module raise a domain exception instead of `HTTPException`?** This would decouple the rules from the transport layer and allow reuse in non-HTTP contexts (tests, scripts, future CLI tools).
4. **Is the frozenset approach sustainable as status count grows?** With three statuses, enumerating all six valid pairs is manageable. With five or six statuses, a rule-based approach (e.g. a dict of allowed destinations per source) might be clearer. This is not an issue today but worth noting in case of future expansion.
5. **Should the same-status transition return 200 or 204?** Currently it returns 200 with the full task body. A 204 No Content (or a 200 with a header indicating no change) would let the client distinguish "I changed something" from "nothing happened," at the cost of frontend complexity.

I would do this differently by raising a pure domain exception in the business-rules module and catching it in the service layer to convert to HTTP 422, decoupling the transition rules from FastAPI and making the module directly testable without a TestClient.
