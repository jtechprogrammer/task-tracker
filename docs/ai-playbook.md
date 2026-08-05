# My AI Playbook

## When I Reach for AI First

I use AI first when I need help breaking a bounded task into steps,
understanding an error, reviewing a small diff, or identifying tests I may
have missed.

## When I Do Not Reach for AI First

I do not use AI first when the task contains secrets, customer data, unclear
business rules, or when I need to learn the concept myself before accepting code.

## My Non-Negotiables

- I never paste API keys, tokens, passwords, `.env` values, or real customer data.
- I do not accept code I cannot explain.
- I review every changed file.
- I run the relevant tests myself.
- I verify security findings against real repository files.

## My Review Rules

- Read the proposed diff line by line.
- Reject edits outside the approved scope.
- Run the application and tests after changes.
- Grade AI findings instead of automatically trusting them.
- Record important AI contributions and corrections.

## What I Am Still Figuring Out

I am still learning when AI context is sufficient and when I should provide
more repository files or ask a teammate for business context.

## Decision Card

- New feature: Ask AI for a plan first; do not implement immediately.
- Code review: Require file evidence and verify each important claim.
- Debugging: Reproduce the problem before accepting a fix.
- Infrastructure: Test CI and Docker commands in reality.
- Never paste: Secrets or real personal/customer data.
- One rule: If I cannot explain it, I do not submit it.