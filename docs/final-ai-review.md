# Final AI Review and Ownership Evidence

## AGENTS.md Guardrails

- Repo-specific stack and commands included: Yes — `AGENTS.md` lists the FastAPI/Uvicorn/Pydantic stack, the `python -m pip install -r requirements.txt` setup command, both server run forms, and the `pytest -v` / `python -m pytest tests/ -v` test commands.
- Docs-first and read-first guardrail included: Yes — the "Module 5 Guardrails" section states "read `README.md`, relevant files in `docs/`, and the source files related to the request before proposing changes" and "Read-only by default: inspect, summarize, and propose before editing."
- Unexpected `app/` and `frontend/` edits rule included: Yes — "Do not change files under `app/` unless the user explicitly approves application-code changes," and edits are meant to stay inside the documented three-layer architecture (routes → `TaskService` → `JsonTaskRepository`).

## AI Code Review Mini-Log

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| "`_read_all()` in `app/repositories/task_repository.py` swallows missing files, empty files, and invalid JSON by returning `{}` instead of raising — this hides corruption from callers." | Useful | The observation is accurate (lines 40-54), and it's an easy thing to miss when reading `TaskService` in isolation since the failure mode is invisible above the repository layer. | Checked this is documented, intended behavior (see `CLAUDE.md` "Repository patterns" and `AGENTS.md` "Persistence Rules") and is exercised by existing tests. Kept as-is; no code change needed. |
| "Consider extracting a shared `_apply_filters` helper in `get_all()` since status and priority filtering could grow into more filter types later." | Noise | This is a premature abstraction for two boolean filters, and the project ADRs explicitly say no new backend filtering (overdue/tags stay client-side), so "could grow" doesn't apply here. | Rejected. Left `get_all()` as two sequential list comprehensions (`app/repositories/task_repository.py:135-138`) — it's shorter and easier to read than a helper for only two filters. |
| "`VALID_TRANSITIONS` in `app/business_rules.py` could be simplified to a `dict[TaskStatus, set[TaskStatus]]` instead of a `frozenset` of tuples." | Useful | A dict-of-sets is arguably more idiomatic for "allowed next states," and the AI was right that the current form requires building the tuple set by hand for each idempotent case. | Reviewed the alternative, but the current frozenset already has full test coverage (`tests/test_tasks.py`) for every transition, including the ToDo→Done rejection. Kept the existing implementation to avoid touching tested logic for a style-only change; noted the idea for a future refactor pass. |

## AI Security Mini-Review

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| CORS policy includes `"null"` in `allow_origins`, which lets a page opened directly from disk (`file://`, origin `null`) make cross-origin requests to the API. | `app/main.py:27-37` | Valid | Confirmed `"null"` is literally in the `allow_origins` list alongside the two local dev ports; this is broader than most CORS configs and was presumably added to support opening `frontend/index.html` directly. | Accepted as a documented local-dev tradeoff — the API has no auth and isn't deployed publicly. Would need to be removed before any real deployment; noted in this review rather than silently left. |
| The repository's `threading.Lock` in `JsonTaskRepository._write_all()` only guards the write, not the full read-modify-write cycle in `add`/`update`/`delete` — two concurrent requests can both call `_read_all()` before either writes, and the second write can silently overwrite the first. | `app/repositories/task_repository.py:37-74, 88-197` | Valid | Traced the lock scope myself: `_read_all()` at lines 112, 168, 192 runs unlocked, and the lock only wraps the `json.dumps`/temp-file/`os.replace` sequence inside `_write_all()`. Under concurrent PATCH/DELETE requests this is a real lost-update race. | Documented as a known limitation rather than fixed — single-process JSON storage is the agreed scope for this project stage per `CLAUDE.md`, and no test currently exercises concurrent writers. Flagged for follow-up if the project ever moves past a single JSON file. |
| "`load_dotenv()` in `app/main.py` loads environment variables from a file, which is a secrets-exposure risk." | `app/main.py:1-14` | False Positive | `load_dotenv()` only reads a local `.env` if one exists; it doesn't create, print, or commit anything. I confirmed `.env` and `.env.*` are in `.gitignore` (only `.env.example` is tracked), so no secret material is exposed by this line. | Rejected the finding. No change made; verified via `.gitignore` and `git status` that no real `.env` file has ever been committed. |

## Manual Security Check

Describe one security check I performed myself:

- What I checked: Whether the repository's write path is actually atomic the way `CLAUDE.md` and `AGENTS.md` claim. I read `_write_all()` in `app/repositories/task_repository.py` line by line instead of trusting the docstring, tracing the `tempfile.mkstemp` → write → `os.replace` sequence and the `except`/cleanup branch.
- What I found: The temp-file-and-replace pattern is correctly implemented for the write itself (a crash mid-write can't corrupt `tasks.json`), but as noted above the lock does not cover the read that happens before the write, so the "atomic write" guarantee is narrower than it sounds — it protects against partial-file corruption, not against lost updates from concurrent requests.
- Why it matters: The docs describe this as "atomic," which could lead someone (including me, later) to assume it's also safe under concurrency. Distinguishing "atomic write to disk" from "safe under concurrent access" mattered enough that I recorded it here instead of just accepting the docstring's framing.

## One AI Output I Rejected or Corrected

- AI suggestion: When I asked for a review of `.dockerignore` and `Dockerfile` during the final-project cleanup, the AI suggested collapsing the multi-stage Docker build (`builder` + `runtime` stages) into a single-stage image "to simplify the file," since the project is small.
- Why I did not accept it as-is: The multi-stage build already keeps the runtime image slim and avoids shipping build tooling, and it pairs with the non-root `app` user created in the runtime stage (`Dockerfile:21`). Collapsing it would have made the image bigger and undone a security-relevant choice (smaller attack surface, no build deps in the final image) for a cosmetic simplification.
- What I did instead: Kept the two-stage `Dockerfile` as-is and only trimmed `.dockerignore` to the narrower allow-list it currently has (`*` excluded, then explicit `!requirements.txt`, `!app/`, `!frontend/`), which was the part of the suggestion that was actually safe to take — it reduces what gets sent to the Docker build context without changing runtime behavior.

## Three AI Usage Rules

1. Never paste: API keys, tokens, the contents of `.env`, or anything from `app/data/tasks.json` if it ever contained real (non-sample) task data.
2. Always verify: Any AI claim about this codebase against the actual file and line — for example, checking the lock scope in `task_repository.py` myself rather than accepting "the writes are atomic" at face value.
3. Record AI contributions by: Logging useful/noise/wrong AI review comments and valid/false-positive security findings in this file (`docs/final-ai-review.md`), and updating `docs/ai-playbook.md` when an interaction changes how I plan to work with AI going forward.

## Ownership Statement

I understand the submitted code because I traced every route in `app/main.py` down through `TaskService` and `JsonTaskRepository` myself, including the parts (the lock scope, the silent-`{}`-on-bad-JSON behavior) that weren't obvious from the docstrings alone. I understand the commands and configuration because I ran the test suite locally (`34 passed`), built and ran the Docker image, and hit `/health` directly rather than trusting the README's claims — the results are logged in `docs/release-evidence.md`. I understand the documentation because I wrote or edited `README.md`, `docs/ai-playbook.md`, and this file against the real behavior I observed, not against what an AI assistant asserted. I understand the AI-assisted decisions in this review because each one required me to grade the AI's output against file evidence and either accept it, reject it, or record it as an open tradeoff — none of the three tables above are copy-pasted AI text; they reflect my own verification of the underlying code.
