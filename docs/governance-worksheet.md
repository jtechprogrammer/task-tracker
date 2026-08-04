# Governance Retrospective for AI-Assisted Coding

## What I Shared With AI

| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker code | 2-5 | Medium | I shared application structure, API routes, models, repository code, tests, and documentation. This is course project code rather than proprietary production code, but it still reveals architecture, validation behavior, and implementation weaknesses. |
| Test output and stack traces | 2-4 | Low | The shared output helped debug validation and behavior. It did not include secrets, but stack traces can reveal local paths, package versions, and internal code structure. |
| Frontend code | 3 | Low | The frontend is a single-file vanilla Kanban board for the course project. The main risk is exposing local API assumptions and UI behavior, not private user data. |
| Dockerfile and CI YAML | 4 | Medium | Build and CI files reveal runtime versions, dependency installation choices, and deployment assumptions. This is useful for review but can also expose supply-chain and deployment weaknesses. |
| Any real external data I used by mistake | 2-5 | Low | I did not identify real external customer, company, or personal data in the repository. The persistent task data file currently contains an empty list, so this remains low unless real data is added later. |

## What I Received From AI

| Generated Thing | Module | Do I Understand It Line by Line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | Mostly | Review validators carefully, especially the `TypeError` behavior for non-string titles, and add tests before accepting behavior changes. |
| Frontend board and drag-and-drop logic | 3 | Partially | Keep manual browser testing in the workflow because drag-and-drop, overdue filtering, and modal behavior are easier to break than simple API calls. |
| CI workflow | 4 | Mostly | Keep CI simple for the course, but verify that it installs the intended dependencies and runs the documented test command. |
| Dockerfile | 4 | Mostly | Check runtime assumptions before using the image outside local learning, including dependency pinning, copied data files, and writable storage. |
| Security findings and plans | 5 | Mostly | Treat AI findings as draft review notes. Confirm each finding against code and scope before grading it or turning it into implementation work. |
