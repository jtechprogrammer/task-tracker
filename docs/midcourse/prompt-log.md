I am working in the existing Task Tracker repository for the AI-Assisted Coding mid-course project.

Current project:
- Backend: Python and FastAPI.
- Frontend: vanilla HTML, CSS, and JavaScript in frontend/index.html.
- Existing task fields: id, title, description, status, priority, and assignee.
- Status values are exactly: ToDo, InProgress, Done.
- Priority values are exactly: Low, Medium, High.
- Existing Backend and Frontend behavior must continue working.

Selected Feature 1:
Due Dates and Overdue Filter.

Requirements:
- due_date is optional.
- Valid format is YYYY-MM-DD.
- Invalid dates must return HTTP 422.
- POST /tasks must support due_date.
- PATCH /tasks/{task_id} must support adding, updating, and removing due_date.
- The due date must appear on the task card.
- A task is overdue when its due date is before today and its status is not Done.
- Users must be able to filter overdue tasks.
- Tasks without due dates must still work normally.

Workflow rules:
- Work in small steps.
- Do not rewrite whole files.
- Do not add frameworks, authentication, databases, notifications, or unrelated features.
- Treat every answer as a draft that I will inspect, run, test, and refine.

Do not write code yet.
First confirm that you understand the project scope and list any assumptions you are making.
--------------------------------------------------------------------------------------------


Before writing code, give me an incremental implementation plan for Feature 1: Due Dates and Overdue Filter.

Context files:
@app/models/task.py  
@app/business_rules.py  
@app/main.py  
@tests/test_tasks.py  
@frontend/index.html  
@docs/midcourse/user-stories.md  
@docs/midcourse/mini-adr.md  

Output format:
Return a table with these columns:

1. Step
2. File or selection
3. What changes
4. How I verify it

Constraints:
- Do not write code yet.
- Use one small implementation step at a time.
- Preserve all existing routes, validation rules, status-transition rules, and tests.
- Do not add a new overdue endpoint unless the current architecture clearly requires it.
- Do not introduce frameworks, databases, authentication, or unrelated files.
- Include Backend models, storage, API behavior, pytest tests, Frontend modal, task-card display, overdue indicator, filter, and Browser verification.
--------------------------------------------------------------------------------------------------

Before implementing anything, revise the implementation plan based only on the attached files.

Your previous plan has these issues:

1. Step 4 references app/repositories/task_repository.py, but that file was not included in the context.
2. Step 12 is incomplete.
3. The plan does not explicitly include adding due_date to the POST and PATCH payloads submitted by the frontend modal.
4. Confirm whether the existing update/storage logic already supports new TaskUpdate fields through model_dump(exclude_unset=True).

Context files:
@app/models/task.py
@app/business_rules.py
@app/main.py
@tests/test_tasks.py
@frontend/index.html
@app/repositories/task_repository.py

If app/repositories/task_repository.py does not exist, say so and use the actual storage/repository file instead.

Task:
Revise only the affected steps. Do not rewrite the entire plan.

Constraints:
- Do not write code.
- Do not infer files or functions that are not visible.
- Preserve existing routes, validation, transition rules, tests, drag-and-drop, and modal behavior.
- Explicitly include how create and edit submit due_date.
- Keep overdue filtering client-side unless the existing architecture clearly requires backend filtering.

Output:
Return a small table containing only the corrected steps.
--------------------------------------------------------------------------------------------


Now implement only Step 1.

Context file:
@app/models/task.py

Requirements:
- Add due_date only to TaskCreate.
- Use the existing Pydantic version and coding style.
- Preserve extra="forbid", title validation, enums, defaults, and all existing fields.
- Do not modify TaskUpdate or TaskResponse yet.
- Do not modify any other file.

Output:
Provide only the focused diff for app/models/task.py.
-----------------------------------------------------------------------------------------------

Steps 1 and 2 are implemented, and the existing tests pass.

Now implement only Step 3.

Context file:
@app/models/task.py

Task:
Add due_date to TaskUpdate.

Requirements:
- due_date must accept a valid date or null.
- It must be optional and default to None.
- Reuse the existing date import.
- Preserve extra="forbid", title validation, enums, fields, and all existing behavior.
- Do not modify TaskCreate.
- Do not modify TaskResponse.
- Do not modify routes, repository/storage, tests, or frontend files.

Important behavior:
- PATCH without due_date must leave the current due date unchanged.
- PATCH with "due_date": null must allow the due date to be removed. The storage implementation will be reviewed separately in the next step.

Output:
Return only a focused diff for app/models/task.py.
-------------------------------------------------------------------

Steps 1, 2, and 3 are implemented, and the existing tests pass.

Now implement only the corrected Step 4 from our plan.

Context files:
@app/models/task.py

Add due_date=payload.due_date to the TaskResponse(...) constructor call.

Task:
Make the task creation/storage logic preserve due_date when constructing the saved TaskResponse.

Requirements:
- Copy payload.due_date into the created TaskResponse.
- Preserve id generation, timestamps, defaults, and all existing fields.
- Do not change TaskCreate, TaskUpdate, or TaskResponse.
- Do not modify API routes, business rules, tests, or frontend code.
- Do not rewrite the update logic if it already uses
  payload.model_dump(exclude_unset=True).
- Keep the diff limited to the actual repository/storage file.

Output:
Return only a focused diff for the repository/storage file.
-----------------------------------------------------------------------------------------------------

Steps 1–4 are implemented, and all existing tests pass.

Now implement only Step 5.

Context files:
@tests/test_tasks.py
@app/main.py
@app/models/task.py

Task:
Add one pytest test for creating a task with a valid due date.

Required behavior:
- Send POST /tasks with:
  - a valid title
  - "due_date": "2026-08-15"
- Assert the response status is due_date": "2026-08-15"
- Assert the response status is 201.
- Assert response JSON contains:
  "due_date": "2026-08-15"

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not add tests for missing, invalid, PATCH, or clearing due_date yet.

Output:
Return only the focused diff for tests/test_tasks.py.
-------------------------------------------------------------------------

Steps 1–5 are implemented, and all tests pass.

Now implement only Step 6.

Context files:
@tests/test_tasks.py
@app/main.py
@app/models/task.py

Task:
Add one pytest test proving that a task can be created without a due date.

Required behavior:
- Send POST /tasks with a valid title but without the due_date field.
- Assert the response status is 201.
- Assert response JSON contains:
  "due_date": null

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test invalid dates, PATCH behavior, or removing due dates yet.

Suggested test name:
test_create_task_without_due_date_returns_201

Output:
Return only the focused diff for tests/test_tasks.py.
----------------------------------------------------------------


Steps 1–6 are implemented, and all tests pass.

Now implement only Step 7.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py

Task:
Add one pytest test proving that an invalid due date is rejected.

Required behavior:
- Send POST /tasks with a valid title.
- Include:
  "due_date": "not-a-date"
- Assert the response status is 422.

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not add PATCH tests yet.
- Do not assert an exact Pydantic error-message string unless the project already has a stable convention for doing so.

Suggested test name:
test_create_task_invalid_due_date_returns_422

Output:
Return only the focused diff for tests/test_tasks.py.
------------------------------------------------------------------

Steps 1–7 are implemented, and all tests pass.

Now implement only Step 8.

Context files:
@tests/test_tasks.py
@app/main.py
@app/models/task.py
@app/business_rules.py
@[actual repository or storage file]

Task:
Add one pytest test proving that PATCH can assign a due date to an existing task.

Required behavior:
1. Create a task without a due date using the existing test client.
2. Read the created task id from the POST response.
3. Send PATCH /tasks/{id} with:
   {
     "due_date": "2026-09-01"
   }
4. Assert the PATCH response status is 200.
5. Assert the response contains:
   "due_date": "2026-09-01"

Constraints:
- Follow the existing test style and fixtures.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test removing the due date yet.
- Do not test preservation of unrelated fields yet.
- Preserve all existing status-transition rules.

Suggested test name:
test_patch_set_due_date_returns_200

Output:
Return only the focused diff for tests/test_tasks.py.
----------------------------------------------------------------


Steps 1–9 are implemented, and all tests pass.

Now implement only Step 10.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/task_repository

Task:
Add one pytest test proving that a partial PATCH which does not include due_date preserves the existing due date.

Required behavior:
1. Create a task with:
   - a valid title
   - "priority": "Medium"
   - "due_date": "2026-09-01"
2. Read the created task id.
3. Send PATCH /tasks/{id} with:
   {
     "priority": "Low"
   }
4. Assert the PATCH response status is 200.
5. Assert:
   - "priority" is "Low"
   - "due_date" is still "2026-09-01"

Constraints:
- Follow the existing test style and fixtures.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not send due_date in the PATCH body.
- Preserve all existing status-transition rules.

Suggested test name:
test_patch_due_date_preserves_other_fields

Output:
Return only the focused diff for tests/test_tasks.py.
----------------------------------------------------------------------------

Steps 1–12 are implemented and verified.

Now implement only Step 13.

Context file:
@frontend/index.html

Task:
Display the optional due date on each task card.

Requirements:
- In the existing task-card rendering function, display the due date when task.due_date is present.
- Use a clear label such as:
  Due: 2026-08-15
- Do not display an empty due-date element when due_date is null.
- Keep the date value in YYYY-MM-DD format unless the existing frontend already has a date-formatting convention.
- Preserve HTML escaping and the existing card structure.

Constraints:
- Do not add overdue detection or overdue styling yet.
- Do not add the overdue filter yet.
- Do not change modal submission behavior.
- Do not change backend files.
- Preserve drag-and-drop, sorting, card editing, and all existing UI states.

Output:
Return only a focused diff for frontend/index.html.
----------------------------------------------------------------


Steps 1–13 are implemented and verified.

Now implement only Step 14: overdue detection and visual indication.

Context file:
@frontend/index.html

Task:
Add an overdue indicator to task cards.

A task is overdue only when:
- task.due_date is present
- task.status is not "Done"
- task.due_date is earlier than today's local date

Required changes:
1. Add an isOverdue(task) helper.
2. Compare date-only values safely so the result is not affected by time-of-day.
3. When a task is overdue:
   - add a card-overdue CSS class
   - show a visible "Overdue" badge near the due-date information
4. A completed task must never appear overdue, even when its due date is in the past.
5. A task due today must not appear overdue.

Preservation constraints:
- Preserve the existing task-card due-date display.
- Preserve HTML escaping.
- Preserve create/edit modal behavior.
- Preserve drag-and-drop, rollback behavior, priority sorting, and UI states.
- Do not add the overdue-only filter yet.
- Do not modify backend files.

Output:
Return only a focused diff for frontend/index.html.
----------------------------------------------------------

Steps 1–13 are implemented and verified.

Now implement only Step 14: overdue detection and visual indication.

Context file:
@frontend/index.html

Task:
Add an overdue indicator to task cards.

A task is overdue only when:
- task.due_date is present
- task.status is not "Done"
- task.due_date is earlier than today's local date

Required changes:
1. Add an isOverdue(task) helper.
2. Compare date-only values safely so the result is not affected by time-of-day.
3. When a task is overdue:
   - add a card-overdue CSS class
   - show a visible "Overdue" badge near the due-date information
4. A completed task must never appear overdue, even when its due date is in the past.
5. A task due today must not appear overdue.

Preservation constraints:
- Preserve the existing task-card due-date display.
- Preserve HTML escaping.
- Preserve create/edit modal behavior.
- Preserve drag-and-drop, rollback behavior, priority sorting, and UI states.
- Do not add the overdue-only filter yet.
- Do not modify backend files.

Output:
Return only a focused diff for frontend/index.html.
----------------------------------------------------------------


Steps 1–14 are implemented and verified.

Now implement only Step 15: add an overdue-only filter.

Context file:
@frontend/index.html

Task:
Add a toggle that filters the board to show only overdue tasks.

Required behavior:
1. Add a button in the existing board header or filter area.
2. Initial button text:
   Show Overdue Only
3. Add a boolean state variable such as:
   filterOverdue = false
4. When the button is clicked:
   - toggle filterOverdue
   - re-render the board
5. When filterOverdue is true:
   - render only tasks for which isOverdue(task) returns true
6. When filterOverdue is false:
   - render all tasks
7. Change the button text while active to:
   Show All Tasks
8. Keep all three Kanban columns visible, even when a column contains no matching overdue tasks.

Preservation constraints:
- Reuse the existing isOverdue(task) helper.
- Do not duplicate overdue-date comparison logic.
- Preserve priority sorting.
- Preserve loading, empty, ready, and error states.
- Preserve drag-and-drop, rollback behavior, modal behavior, task-card display, and overdue styling.
- Do not modify backend files.
- Do not add a new API endpoint.
- Keep the diff focused on the filter button, filter state, and rendering logic.

Output:
Return only a focused diff for frontend/index.html.
--------------------------------------------------------------------------


Before writing code, give me an incremental implementation plan for Feature 2: Tags and Labels.

Context files:
@app/models/task.py
@app/business_rules.py
@app/main.py
@repositories/task_repository
@tests/test_tasks.py
@frontend/index.html
@docs/midcourse/user-stories.md
@docs/midcourse/mini-adr.md

Feature 2 ADR requirements:

- Add tags to tasks as a list of strings.
- Tags are optional.
- A task without tags remains valid.
- POST /tasks can accept tags.
- PATCH /tasks/{id} can add, replace, or remove tags.
- Trim leading and trailing whitespace from every tag.
- Remove empty and whitespace-only tags.
- Remove duplicate tags.
- Preserve the first occurrence order.
- Duplicate comparison should be case-sensitive:
  "frontend" and "Frontend" remain different tags.
- Updating tags must preserve unrelated task fields.
- The frontend modal accepts comma-separated input.
- The frontend converts the input into a string list before sending it.
- Tags are displayed on task cards.

Explicitly out of scope:

- Separate Tag model or database table.
- Tag IDs.
- Tag colors.
- Tag suggestions or autocomplete.
- Independent tag CRUD.
- Dedicated tags endpoint.
- Tag filtering.
- Advanced tag search.
- Case normalization.
- Frameworks, databases, authentication, or unrelated files.

Output format:
Return a table with these columns:

1. Step
2. File or selection
3. What changes
4. How I verify it

The plan must include:

- TaskCreate model support.
- TaskResponse model support.
- TaskUpdate model support.
- Tag cleanup logic.
- Storage or repository creation behavior.
- PATCH behavior.
- Tests for:
  - creating with tags
  - creating without tags
  - trimming whitespace
  - removing empty tags
  - removing duplicate tags
  - updating tags
  - removing all tags
  - preserving unrelated fields
- Full backend regression.
- Frontend modal input.
- POST and PATCH payload conversion.
- Edit modal pre-fill.
- Tag display on task cards.
- Browser and DevTools verification.
- Final pytest regression.

Constraints:

- Do not write code yet.
- Use one small implementation step at a time.
- Preserve all existing routes, validation rules, status-transition rules, due-date behavior, overdue behavior, overdue filtering, drag-and-drop, frontend states, and tests.
- Do not invent files or functions that are not visible.
- Do not add a dedicated tags endpoint.
- Do not add tag filtering.
- Include verification after every step.

Important ambiguity to inspect:
Determine from the existing project style whether a task without tags should return:
- "tags": []
or
- "tags": null

Do not silently decide. State the recommended choice and explain it in the plan before implementation.
---------------------------------------------------------


Before writing code, revise only the affected steps in the Feature 2 plan.

Corrections required:

1. Do not use a mutable default:
   tags: list[str] = []

   Use:
   tags: list[str] = Field(default_factory=list)

2. TaskCreate:
   - tags must always be a list.
   - omitted tags default to [].
   - add cleanup validation for trimming, removing empty values, and removing case-sensitive duplicates while preserving order.

3. TaskResponse:
   - tags must always be a list.
   - use Field(default_factory=list) so existing tasks and existing constructors remain valid.

4. TaskUpdate:
   - tags must always be a list when supplied.
   - use Field(default_factory=list), not Optional[list[str]] = None.
   - rely on model_dump(exclude_unset=True):
     - omitted tags means unchanged
     - [] means clear all tags
     - null must be rejected with HTTP 422
   - apply the same cleanup validation as TaskCreate.

5. Add a test proving PATCH cleanup:
   PATCH tags such as:
   [" docs ", "", "bug", "docs"]
   Expected:
   ["docs", "bug"]

6. Revise the unrelated-fields preservation test:
   - create a task with tags, priority, and due_date
   - PATCH only tags
   - assert tags changed
   - assert priority and due_date remained unchanged

7. Add a test proving PATCH with:
   {"tags": null}
   returns HTTP 422 because tags must always be a list.

8. Recalculate the expected final test count using the actual number of added tests. Do not assume a count unless the arithmetic matches.

Constraints:
- Do not write code yet.
- Revise only the affected plan rows.
- Preserve Feature 1 behavior and all existing tests.
- Do not add tag filtering, colors, models, or endpoints.

Output:
Return only the corrected rows in the same table format.
-------------------------------------------------------------


Before implementation, revise only these affected parts of the Feature 2 plan:

1. In TaskCreate and TaskUpdate, use a normal field_validator("tags")
   after Pydantic validates list[str], rather than mode="before".
   The validator should trim values, remove empty strings, and remove
   case-sensitive duplicates while preserving order.
   null and non-list values should be rejected by Pydantic.

2. Restore the missing repository step:
   app/repositories/task_repository.py — add()
   Add tags=payload.tags when constructing TaskResponse.
   Do not change update() if model_dump(exclude_unset=True) already handles it.

3. Add a Browser and DevTools verification step covering:
   - create with tags
   - create without tags
   - edit/replace tags
   - clear tags
   - tag badges
   - drag-and-drop
   - overdue filter
   - POST/PATCH payload inspection
   - no console errors

4. Move final pytest regression to the step after browser verification.

Do not write code yet.
Return only the corrected rows.
-------------------------------------------------------

Step 1 is implemented, and all existing tests pass.

Now implement only Step 2.

Context file:
@app/models/task.py

Task:
Add tags support to TaskResponse.

Requirements:
- Add:
  tags: list[str] = Field(default_factory=list)
- Reuse the existing Field import.
- Place the field consistently with TaskCreate, after due_date.
- Existing TaskResponse constructors that do not pass tags must continue to work and default to [].
- Preserve all existing fields, model_config, enums, due-date behavior, and validation.
- Do not modify TaskCreate.
- Do not modify TaskUpdate.
- Do not modify repository, routes, tests, or frontend files.

Output:
Return only a focused diff for app/models/task.py.
-------------------------------------------------------------

Steps 1 and 2 are implemented, and all existing tests pass.

Now implement only Step 3.

Context file:
@app/models/task.py

Task:
Add tags support to TaskUpdate.

Requirements:
- Add:
  tags: list[str] = Field(default_factory=list)
- Place the field consistently after due_date.
- Add the same tag-cleanup behavior used by TaskCreate:
  - trim leading and trailing whitespace
  - remove empty or whitespace-only tags
  - remove case-sensitive duplicates
  - preserve first-occurrence order
- Use a normal @field_validator("tags"), not mode="before".
- Preserve these PATCH behaviors:
  - omitted tags → existing tags remain unchanged through model_dump(exclude_unset=True)
  - "tags": [] → clear all tags
  - "tags": null → rejected with HTTP 422
- Preserve all existing TaskUpdate fields, title validation, model_config, due-date behavior, and status behavior.
- Do not modify TaskCreate or TaskResponse.
- Do not modify repository, routes, tests, or frontend files.
- Avoid unrelated refactoring.

Output:
Return only a focused diff for app/models/task.py.
-------------------------------------------------------


Steps 1–3 are implemented, and all existing tests pass.

Now implement only Step 4.

Context files:
@app/models/task.py
@app/repositories/task_repository.py

Task:
Preserve tags when creating and storing a new task.

Required change:
- In the repository add() method, pass:
  tags=payload.tags
  when constructing TaskResponse.

Requirements:
- Preserve id generation, timestamps, due_date, defaults, and all existing task fields.
- Do not modify the update() method if it already uses:
  payload.model_dump(exclude_unset=True)
  and model_copy(update=updates).
- Do not modify models, routes, business rules, tests, or frontend files.
- Do not perform unrelated refactoring.

Output:
Return only a focused diff for app/repositories/task_repository.py.
-----------------------------------------------------


Steps 1–4 are implemented, and all existing tests pass.

Now implement only Step 5.

Context files:
@tests/test_tasks.py
@app/main.py
@app/models/task.py

Task:
Add one pytest test proving that a task can be created with tags.

Required behavior:
1. Send POST /tasks with:
   {
     "title": "Tagged task",
     "tags": ["frontend", "bug"]
   }
2. Assert the response status is 201.
3. Assert:
   response.json()["tags"] == ["frontend", "bug"]

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test trimming, duplicates, empty tags, or PATCH behavior yet.
- Preserve all existing due-date and status-transition tests.

Suggested test name:
test_create_task_with_tags_returns_201

Output:
Return only a focused diff for tests/test_tasks.py.
---------------------------------------------------------

Steps 1–5 are implemented, and all tests pass.

Now implement only Step 6.

Context files:
@tests/test_tasks.py
@app/main.py
@app/models/task.py

Task:
Add one pytest test proving that a task can be created without providing tags.

Required behavior:
1. Send POST /tasks with:
   {
     "title": "Task without tags"
   }
2. Do not include the tags field in the request.
3. Assert the response status is 201.
4. Assert:
   response.json()["tags"] == []

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test trimming, duplicates, null values, or PATCH behavior yet.
- Preserve all existing due-date and status-transition tests.

Suggested test name:
test_create_task_without_tags_returns_empty_list

Output:
Return only a focused diff for tests/test_tasks.py.
---------------------------------------------------


Steps 1–6 are implemented, and all tests pass.

Now implement only Step 7.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py

Task:
Add one pytest test proving that tag whitespace is trimmed and empty tags are removed when creating a task.

Required behavior:
1. Send POST /tasks with:
   {
     "title": "Clean tags",
     "tags": [" frontend ", "", "   ", " bug "]
   }
2. Assert the response status is 201.
3. Assert:
   response.json()["tags"] == ["frontend", "bug"]

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test duplicate removal or PATCH behavior yet.
- Preserve all existing due-date, overdue, and status-transition tests.

Suggested test name:
test_create_task_tags_trimmed_and_empty_removed

Output:
Return only a focused diff for tests/test_tasks.py.
-----------------------------------------------------------


Steps 1–7 are implemented, and all tests pass.

Now implement only Step 8.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py

Task:
Add one pytest test proving that duplicate tags are removed when creating a task while preserving first-occurrence order.

Required behavior:
1. Send POST /tasks with:
   {
     "title": "Duplicate tags",
     "tags": ["bug", "frontend", "bug"]
   }
2. Assert the response status is 201.
3. Assert:
   response.json()["tags"] == ["bug", "frontend"]

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test case-sensitive behavior or PATCH behavior yet.
- Preserve all existing due-date, overdue, and status-transition tests.

Suggested test name:
test_create_task_tags_duplicates_removed

Output:
Return only a focused diff for tests/test_tasks.py.
------------------------------------------------------------------


Steps 1–8 are implemented, and all tests pass.

Now implement only Step 9.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py

Task:
Add one pytest test proving that tag duplicate comparison is case-sensitive.

Required behavior:
1. Send POST /tasks with:
   {
     "title": "Case-sensitive tags",
     "tags": ["frontend", "Frontend"]
   }
2. Assert the response status is 201.
3. Assert:
   response.json()["tags"] == ["frontend", "Frontend"]

Reason:
The ADR does not require case normalization, so tags with different capitalization remain separate.

Constraints:
- Follow the existing test style and fixtures in tests/test_tasks.py.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not add PATCH tests yet.
- Preserve all existing due-date, overdue, drag-and-drop, and status-transition behavior.

Suggested test name:
test_create_task_tags_case_sensitive

Output:
Return only a focused diff for tests/test_tasks.py.
-------------------------------------------------------


Steps 1–9 are implemented, and all tests pass.

Now implement only Step 10.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/repositories/task_repository.py

Task:
Add one pytest test proving that PATCH can replace all existing tags.

Required behavior:
1. Create a task with:
   {
     "title": "Replace tags",
     "tags": ["frontend", "bug"]
   }
2. Read the created task id.
3. Send PATCH /tasks/{id} with:
   {
     "tags": ["docs"]
   }
4. Assert the PATCH response status is 200.
5. Assert:
   response.json()["tags"] == ["docs"]

Constraints:
- Follow the existing test style and fixtures.
- Add exactly one test.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test clearing, cleanup, null rejection, or unrelated-field preservation yet.
- Preserve all due-date, overdue, and status-transition behavior.

Suggested test name:
test_patch_replace_tags_returns_200

Output:
Return only a focused diff for tests/test_tasks.py.
-------------------------------------------------------

Steps 1–10 are implemented, and all tests pass.

Now implement only Step 11.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/repositories/task_repository.py

Task:
Add one pytest test proving that PATCH can remove all tags from an existing task.

Required behavior:
1. Create a task with:
   {
     "title": "Clear tags",
     "tags": ["frontend", "bug"]
   }
2. Read the created task id.
3. Send PATCH /tasks/{id} with:
   {
     "tags": []
   }
4. Assert the PATCH response status is 200.
5. Assert:
   response.json()["tags"] == []

Constraints:
- Add exactly one test.
- Follow the existing test style and fixtures.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test cleanup, null rejection, or unrelated-field preservation yet.
- Preserve due-date, overdue, and status-transition behavior.

Suggested test name:
test_patch_clear_tags_returns_200

Output:
Return only a focused diff for tests/test_tasks.py.
---------------------------------------------------------


Steps 1–11 are implemented, and all tests pass.

Now implement only Step 12.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/repositories/task_repository.py

Task:
Add one pytest test proving that PATCH cleans tag values by trimming whitespace, removing empty tags, and removing duplicate tags while preserving first-occurrence order.

Required behavior:
1. Create a task with:
   {
     "title": "Clean patched tags",
     "tags": ["old"]
   }
2. Read the created task id.
3. Send PATCH /tasks/{id} with:
   {
     "tags": [" docs ", "", "   ", "bug", "docs"]
   }
4. Assert the PATCH response status is 200.
5. Assert:
   response.json()["tags"] == ["docs", "bug"]

Constraints:
- Add exactly one test.
- Follow the existing test style and fixtures.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not test null rejection or unrelated-field preservation yet.
- Preserve all due-date and status-transition behavior.

Suggested test name:
test_patch_tags_cleanup_trim_and_dedup

Output:
Return only a focused diff for tests/test_tasks.py.
-----------------------------------------------------


Steps 1–12 are implemented, and all tests pass.

Now implement only Step 13.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/repositories/task_repository.py

Task:
Add one pytest test proving that updating tags through PATCH does not change unrelated task fields.

Required behavior:
1. Create a task with:
   {
     "title": "Preserve fields",
     "priority": "Medium",
     "due_date": "2026-09-01",
     "tags": ["old"]
   }

2. Read the created task id.

3. Send PATCH /tasks/{id} with only:
   {
     "tags": ["changed"]
   }

4. Assert the PATCH response status is 200.

5. Assert:
   - response.json()["tags"] == ["changed"]
   - response.json()["priority"] == "Medium"
   - response.json()["due_date"] == "2026-09-01"
   - response.json()["title"] == "Preserve fields"

Constraints:
- Add exactly one test.
- Follow the existing test style and fixtures.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not include priority, due_date, or title in the PATCH body.
- Do not test null rejection yet.
- Preserve all existing status-transition behavior.

Suggested test name:
test_patch_tags_preserves_other_fields

Output:
Return only a focused diff for tests/test_tasks.py.
-------------------------------------------------------------


Steps 1–13 are implemented, and all tests pass.

Now implement only Step 14.

Context files:
@tests/test_tasks.py
@app/models/task.py
@app/main.py
@app/repositories/task_repository.py

Task:
Add one pytest test proving that PATCH rejects null for tags because tags must always be a list of strings.

Required behavior:
1. Create a valid task.
2. Read the created task id.
3. Send PATCH /tasks/{id} with:
   {
     "tags": null
   }
4. Assert the response status is 422.
5. Confirm the existing task remains unchanged after the rejected request, if the current test style makes that easy to verify.

Constraints:
- Add exactly one test.
- Follow the existing test style and fixtures.
- Do not modify production code.
- Do not rewrite existing tests.
- Do not assert the complete Pydantic error message because its exact wording may vary.
- Preserve all existing routes, due-date behavior, tag cleanup, and status-transition rules.

Suggested test name:
test_patch_tags_null_rejected_422

Output:
Return only a focused diff for tests/test_tasks.py.
-----------------------------------------------------


Steps 1–15 are implemented, and the complete backend test suite passes.

Now implement only Step 16: add tags support to the existing create/edit modal.

Context file:
@frontend/index.html

Required changes:

1. Add a Tags field to the existing modal:
   <input
     type="text"
     id="task-form-tags"
     placeholder="e.g. frontend, bug, urgent"
   >

2. Add the corresponding DOM reference using the existing naming style.

3. When opening the New Task modal:
   - reset the tags input to an empty string.

4. When opening the Edit modal:
   - populate the input using:
     (task.tags || []).join(", ")

5. When submitting the create form:
   - convert the comma-separated input into a list.
   - trim each value.
   - remove empty values.
   - send [] when the input is empty.
   - include tags in the POST /tasks payload.

6. When submitting the edit form:
   - perform the same conversion.
   - include tags in the PATCH /tasks/{id} payload.
   - clearing the input must send tags: [].

Preservation constraints:
- Preserve all existing modal fields and styling.
- Preserve title validation and server 422 error handling.
- Preserve due-date create, edit, and clearing behavior.
- Preserve status, priority, description, and assignee behavior.
- Preserve drag-and-drop, overdue logic, overdue filter, sorting, and UI states.
- Do not display tags on cards yet.
- Do not modify backend files.
- Do not add tag filtering, colors, suggestions, or endpoints.
- Keep the diff focused on the modal and request payload logic.

Output:
Return only a focused diff for frontend/index.html.
---------------------------------------------------------


Steps 1–16 are implemented and verified.

Now implement only Step 17: display tags on task cards.

Context file:
@frontend/index.html

Task:
Display each task's tags on its existing task card.

Required behavior:
1. In the existing card-rendering function, check whether task.tags contains any values.
2. When tags exist, render each tag as a separate small badge.
3. When tags is empty, render no tags container or empty badge.
4. Preserve the original tag order returned by the backend.
5. Render tag text safely using DOM textContent or the existing escaping approach.

Styling:
- Add minimal CSS for the tag container and tag badges.
- Use the existing frontend visual style.
- Do not introduce tag colors based on tag values.
- All tags may use the same neutral badge style.

Preservation constraints:
- Preserve task title, description, priority, assignee, due-date display, and overdue indicator.
- Preserve drag-and-drop and rollback behavior.
- Preserve create/edit modal behavior.
- Preserve priority sorting, overdue filtering, and all UI states.
- Do not add tag filtering.
- Do not modify backend files.
- Avoid unrelated HTML, CSS, or JavaScript changes.

Output:
Return only a focused diff for frontend/index.html.
