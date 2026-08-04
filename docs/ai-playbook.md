# Personal AI Coding Playbook

## 1. When I reach for AI first

- When I need to turn a vague assignment or issue into a short checklist before I start coding.
- When I want help reading an unfamiliar part of the repo and tracing where a behavior lives.
- When I have a draft solution and want a second pass on edge cases, tests, or simpler wording.

## 2. When I do not reach for AI

- When the work includes secrets, private data, `.env` values, or anything I am not allowed to share.
- When I have not read the relevant file myself yet and would only be asking AI to guess.
- When the change is small enough that using AI would slow me down more than thinking it through directly.

## 3. My non-negotiables

- I read the actual diff before accepting or submitting any AI-assisted change.
- I keep application changes inside the existing architecture instead of jumping around the service and repository layers.
- I record important AI-assisted decisions in docs when they affect design, security, or governance.

## 4. My review rules

- I check whether the change matches the documented requirements before I focus on style.
- I verify claims against files, tests, or command output instead of trusting a confident explanation.
- I look for validation, error handling, and missing tests whenever behavior changes.

## 5. What I am still figuring out

- How much context to give AI before the prompt becomes too large to be useful.
- When to ask AI for a plan only, and when to let it help with the actual edit.
- How to balance speed with still building my own debugging instincts.

## Decision Card

- For a new feature I reach for: a checklist, affected files, and test ideas.
- For code review I reach for: a risk-focused second pass after my own read.
- For debugging I reach for: a trace of the failing path and possible root causes.
- For infrastructure I reach for: docs, commands, and config checks before changing anything.
- For planning and governance I reach for: a short decision note with assumptions and limits.
- I will never paste secrets, private data, or `.env` contents into an AI tool.
- My one rule is: AI can help me move faster, but I still own the final judgment.
