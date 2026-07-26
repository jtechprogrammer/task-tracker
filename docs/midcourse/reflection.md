# Feature 1 Reflection — Due Dates and Overdue Filter

## Feature Completed

I implemented optional due dates across the backend and frontend of the Task Tracker.

Tasks can now:

- Be created with or without a due date.
- Have their due date added, changed, or removed through the existing `PATCH /tasks/{id}` endpoint.
- Display the due date on task cards.
- Show an overdue indicator when the due date is before today and the task is not completed.
- Be filtered so that only overdue tasks are displayed.

The implementation preserved the existing routes, validation rules, status-transition rules, drag-and-drop behavior, frontend states, and previous tests.

## AI Assistance and Human Review

Claude helped create an incremental implementation plan that separated the work into backend models, repository behavior, pytest tests, frontend modal support, task-card display, overdue logic, filtering, and browser verification.

I corrected the original plan before implementing it. One step referred to repository behavior without being fully grounded in the attached project files, and the modal step was incomplete because it did not clearly explain how `due_date` should be included in both POST and PATCH payloads.

I also constrained Claude to implement only one small step at a time. After every change, I inspected the diff and ran the relevant test before continuing.

## Backend Changes

I added the optional `due_date` field to:

- `TaskCreate`
- `TaskResponse`
- `TaskUpdate`

I updated the repository creation logic so that a supplied due date is copied into the saved task.

The existing partial-update behavior was preserved:

- Omitting `due_date` from PATCH leaves the existing value unchanged.
- Sending `"due_date": null` removes the due date.
- Sending a valid date replaces the existing due date.

## Backend Verification

The backend tests verified:

- Creating a task with a valid due date.
- Creating a task without a due date.
- Rejecting an invalid due date with HTTP 422.
- Assigning a due date through PATCH.
- Removing a due date by sending `null`.
- Preserving the existing due date when PATCH updates another field.
- Preserving all previous API behavior.

Final pytest result:

`24 passed`

## Frontend Changes

I added a Due Date field to the existing create/edit modal.

The frontend now:

- Starts with an empty due-date input when creating a task.
- Pre-fills the current due date when editing a task.
- Sends the selected date in `YYYY-MM-DD` format.
- Sends `null` when the due date is cleared.
- Displays the due date on task cards.
- Shows an overdue badge and styling for overdue tasks.
- Provides a toggle to show overdue tasks only or restore all tasks.

## Overdue Rules

A task is considered overdue only when:

- It has a due date.
- Its due date is earlier than today.
- Its status is not `Done`.

The following behaviors were verified:

- Past `ToDo` tasks are overdue.
- Past `InProgress` tasks are overdue.
- Past `Done` tasks are not overdue.
- Tasks due today are not overdue.
- Future tasks are not overdue.
- Tasks without a due date are not overdue.

## Browser and DevTools Verification

- Creating a task without a due date: Pass
- Creating a task with a future due date: Pass
- Creating a past-due task: Pass
- Editing an existing due date: Pass
- Clearing a due date: Pass
- Due-date display on task cards: Pass
- Overdue badge and styling: Pass
- Done tasks excluded from overdue status: Pass
- Tasks due today excluded from overdue status: Pass
- Overdue-only filter: Pass
- Show All Tasks toggle: Pass
- All Kanban columns remain visible while filtered: Pass
- Drag-and-drop still works: Pass
- Due-date behavior remains correct after re-rendering: Pass
- POST payload contains the correct `due_date`: Pass
- PATCH payload contains the correct `due_date` or `null`: Pass
- Browser console errors: None

## Debugging Log

1. What failed or what I intentionally broke: I temporarily removed `due_date=payload.due_date` from the repository task-creation logic to verify that the due-date test could detect a storage mapping error.

2. Failing test and failure summary: `test_create_task_with_valid_due_date_returns_201` failed because the POST request accepted the due date, but the response returned `due_date` as `null` instead of `"2026-08-15"`.

3. AI diagnosis: Claude identified that the request model correctly accepted the field, but the repository did not copy `payload.due_date` into the constructed `TaskResponse`. The value was therefore lost while creating the stored task.

4. Decision about the proposed fix: I accepted the focused fix of restoring `due_date=payload.due_date` in the repository. The fix corrected the mapping problem without changing the route, validation rules, PATCH logic, or unrelated fields.

## Final Reflection

Claude helped me divide the due-date and overdue-filter feature into small backend, testing, and frontend changes instead of rewriting the project all at once. I had to review and correct the initial plan because some repository and modal details were incomplete or based on assumptions. Running pytest after each backend change helped catch regressions early, while Browser DevTools confirmed that POST and PATCH requests sent the correct due-date values. Manual browser checks also proved that overdue detection worked correctly for past, current, future, and completed tasks. I will reuse the habit of implementing one focused change, inspecting the result, and verifying it before continuing.

# Feature 2 Reflection — Tags and Labels

## Feature completed

I added optional tags to tasks as a list of strings. Tags can be created, replaced, or cleared through the existing POST and PATCH endpoints. The backend trims whitespace, removes empty and duplicate tags, and preserves unrelated fields during partial updates. The frontend accepts comma-separated tags and displays them as badges on task cards.

## Backend verification

- Creating tasks with tags: Pass
- Creating tasks without tags: Pass
- Tag cleanup: Pass
- Duplicate removal: Pass
- PATCH replace and clear tags: Pass
- Unrelated fields preserved: Pass
- Null tags rejected: Pass
- Final pytest result: 34 passed

## Feature 2 Browser Verification

- Create task without tags: Pass
- Create task with tags: Pass
- Tag cleanup and duplicate removal: Pass
- Edit and replace tags: Pass
- Clear all tags: Pass
- Tag badges displayed correctly: Pass
- Due-date and overdue behavior preserved: Pass
- Overdue filter preserved: Pass
- Drag-and-drop preserved: Pass
- Network payloads correct: Pass
- Console errors: None

## Debugging Log

1. What failed or what I intentionally broke: I temporarily removed the tags cleanup validator from `TaskUpdate` to confirm that the PATCH tests could detect incorrect tag handling.

2. Failing test and failure summary: `test_patch_tags_cleanup_trim_and_dedup` failed because PATCH stored whitespace, empty values, and duplicate tags instead of returning `["docs", "bug"]`.

3. AI diagnosis: The cleanup validator existed for `TaskCreate`, but PATCH requests use `TaskUpdate`, so tag trimming, empty-value removal, and duplicate removal were not being applied during updates.

4. Decision about the proposed fix: I accepted the focused fix of applying the same tags validator to `TaskUpdate` because it preserved the existing repository and endpoint behavior while making POST and PATCH follow the same cleanup rules.

## Final Reflection

The AI assistant helped me divide the tags feature into small backend, testing, and frontend changes that I could verify individually. I had to constrain the assistant to use the existing task model and endpoints and to avoid adding tag filtering, tag colors, or a separate Tag entity. Inspecting each diff and running pytest helped confirm that partial PATCH updates did not change unrelated fields. Browser and DevTools checks confirmed that the frontend sent the correct tag lists and displayed the saved tags correctly. I will reuse the habit of implementing one focused change and verifying it before moving to the next step.