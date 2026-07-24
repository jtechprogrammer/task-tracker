# Mini Architecture Decision Record

## ADR 1: Due Dates and Overdue Filter

### Status

Accepted for implementation.

### Context

The Task Tracker currently allows users to create, view, update, and delete tasks, but it does not support deadlines.

The selected feature must allow users to:

- Assign an optional due date when creating a task.
- Update or remove a due date through the existing `PATCH` endpoint.
- Display the due date on the task card.
- Identify overdue tasks visually.
- Filter the task list to show overdue tasks only.
- Reject invalid date values with status `422`.
- Preserve all existing task behavior and existing tests.

### Decision

Add an optional `due_date` field to the task data model.

The field will use a date value in ISO format:

```text
YYYY-MM-DD
```

The implementation will follow these rules:

- `due_date` is optional when a task is created.
- A missing or `null` due date is valid.
- Invalid date formats are rejected by Backend validation with status `422`.
- The existing `POST /tasks` endpoint will support the field.
- The existing `PATCH /tasks/{id}` endpoint will support adding, changing, or removing the field.
- Updating `due_date` must not change unrelated task fields.
- The Frontend modal will use a date input.
- The task card will display the due date when one exists.

A task will be considered overdue when all these conditions are true:

1. The task has a due date.
2. The due date is earlier than the current date.
3. The task status is not `Done`.

The overdue state and overdue filter will be calculated in the Frontend using the tasks already returned by the existing API. No new Backend endpoint will be added.

### Scope

Included:

- Task model changes.
- Storage support for `due_date`.
- `POST` and `PATCH` support.
- Backend validation.
- Backend tests.
- Frontend create and edit modal support.
- Due-date display on task cards.
- Visible overdue indicator.
- Overdue-only filter.
- Browser and DevTools verification.

Not included:

- Time-of-day deadlines.
- Time zones.
- Email or push reminders.
- Recurring due dates.
- Sorting tasks by due date.
- A separate calendar page.
- A dedicated `GET /tasks/overdue` endpoint.

### Alternatives Considered

#### Alternative 1: Store the due date as an unrestricted string

This option was rejected because invalid values could be saved. Using a validated date field gives consistent formatting and allows FastAPI and Pydantic to return `422` for invalid input.

#### Alternative 2: Add a separate Backend endpoint for overdue tasks

Example:

```text
GET /tasks/overdue
```

This option was rejected because the Frontend already receives the task list and can apply the overdue rule locally. A new endpoint would add unnecessary complexity to this learning project.

#### Alternative 3: Store an `is_overdue` field

This option was rejected because overdue status changes as time passes. Saving it would risk stale or incorrect data. It should be calculated from `due_date`, the current date, and task status.

#### Alternative 4: Include completed tasks in overdue results

This option was rejected because the User Stories explicitly state that tasks with status `Done` must not be marked or filtered as overdue.

### AI Assistance and Human Review

AI may be used to:

- Identify the files affected by the new field.
- Suggest focused Backend and Frontend changes.
- Suggest test scenarios and edge cases.
- Review code diffs for unrelated changes.

Human review remains responsible for:

- Confirming that suggestions match the User Stories and Acceptance Criteria.
- Rejecting changes that expand the scope.
- Verifying that existing API behavior remains unchanged.
- Checking the generated code before accepting it.
- Running the tests and manually checking the Browser behavior.

This section must be updated during implementation with the actual AI suggestions that were accepted, modified, or rejected.

### Consequences

#### Positive

- Users can track task deadlines.
- Invalid date formats are handled consistently by Backend validation.
- Existing endpoints remain unchanged.
- Existing tasks can remain without a due date.
- Overdue status is always calculated from current data instead of being stored.
- The implementation stays small and appropriate for the project scope.

#### Trade-offs

- The overdue calculation depends on the user's current local date in the Browser.
- Filtering occurs only after tasks are loaded.
- The feature does not support deadline times or time zones.
- Large datasets could eventually benefit from Backend filtering, but that is outside the current scope.

### Verification Impact

The implementation should include tests and manual checks for at least these behaviors:

- Creating a task with a valid due date.
- Creating a task without a due date.
- Rejecting an invalid due date with `422`.
- Updating an existing due date.
- Removing an existing due date.
- Confirming unrelated fields remain unchanged after a `PATCH`.
- Marking a past, incomplete task as overdue.
- Not marking a `Done` task as overdue.
- Not marking a task without a due date as overdue.
- Enabling and clearing the overdue filter.
- Confirming all existing tests still pass.

---

## ADR 2: Tags and Labels

### Status

Accepted for implementation.

### Context

The Task Tracker currently allows users to create, view, update, and delete tasks, but users cannot categorize tasks.

The selected feature must allow users to:

- Add optional tags when creating a task.
- Update or remove tags through the existing `PATCH` endpoint.
- Display tags on task cards.
- Preserve existing task behavior and existing tests.
- Prevent empty or duplicate tags from being stored.

### Decision

Add a `tags` field to the task data model as a list of strings.

Example:

```json
{
  "tags": ["frontend", "urgent"]
}
```

The implementation will follow these rules:

- `tags` is optional.
- A task without tags remains valid.
- Tags are stored as a list of strings.
- Leading and trailing whitespace is removed.
- Empty or whitespace-only tags are removed.
- Duplicate tags are removed.
- Tags can be added, replaced, or removed through `PATCH`.
- Updating tags must not change unrelated task fields.
- The Frontend will accept comma-separated tag input.
- The Frontend will convert the input into a list before sending it to the Backend.
- Tags will be displayed on task cards.

Example Frontend input:

```text
frontend, urgent, bug
```

Example request value:

```json
{
  "tags": ["frontend", "urgent", "bug"]
}
```

### Scope

Included:

- Task model changes.
- Storage support for `tags`.
- `POST` and `PATCH` support.
- Tag cleanup and validation.
- Backend tests.
- Frontend create and edit modal support.
- Tag display on task cards.
- Browser and DevTools verification.

Not included:

- A separate Tag model or database table.
- Tag IDs.
- Tag colors.
- Shared tag management.
- Tag suggestions or autocomplete.
- Creating or deleting tags independently from tasks.
- Advanced search by multiple tags.
- A dedicated Backend endpoint for tags.

### Alternatives Considered

#### Alternative 1: Store tags as one comma-separated string

Example:

```json
{
  "tags": "frontend, urgent"
}
```

This option was rejected because filtering, validation, and duplicate removal would be harder. A list of strings gives the API a clearer structure.

#### Alternative 2: Create a separate Tag entity

This option was rejected because it would require extra models, IDs, relationships, and endpoints. That complexity is outside the scope of this small learning project.

#### Alternative 3: Allow duplicate and empty tags

This option was rejected because values such as `"urgent"`, `" urgent "`, and `""` would create inconsistent and meaningless data.

#### Alternative 4: Add tag colors

This option was rejected because colors are not required by the User Stories and would increase the Frontend and data-model scope.

### AI Assistance and Human Review

AI may be used to:

- Identify the files affected by the new `tags` field.
- Suggest focused Backend and Frontend changes.
- Suggest validation and cleanup logic.
- Suggest tests for adding, updating, removing, and cleaning tags.
- Review the code diff for unrelated changes.

Human review remains responsible for:

- Confirming that suggestions match the User Stories and Acceptance Criteria.
- Rejecting changes that add unnecessary models, endpoints, or UI complexity.
- Checking that tag cleanup rules are implemented consistently.
- Verifying that unrelated task fields remain unchanged during `PATCH`.
- Running tests and manually checking Browser behavior.

This section must be updated during implementation with the actual AI suggestions that were accepted, modified, or rejected.

### Consequences

#### Positive

- Users can categorize tasks without changing the existing endpoint structure.
- Tags are easy to save, display, and update.
- Cleaning whitespace and duplicates keeps stored data consistent.
- Existing tasks remain valid because tags are optional.
- The implementation stays small and appropriate for the project scope.

#### Trade-offs

- Tags are not centrally managed.
- Tags do not have IDs or colors.
- Similar values with different capitalization, such as `frontend` and `Frontend`, may be treated as different tags unless case normalization is added.
- Comma-separated input means a tag cannot contain a comma.

### Verification Impact

The implementation should include tests and manual checks for at least these behaviors:

- Creating a task with tags.
- Creating a task without tags.
- Trimming whitespace around tags.
- Removing empty tags.
- Removing duplicate tags.
- Updating existing tags through `PATCH`.
- Removing all tags.
- Confirming unrelated fields remain unchanged after a tag update.
- Displaying tags on the task card.
- Confirming all existing tests still pass.
