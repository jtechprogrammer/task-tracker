# Feature 1: Due Dates and Overdue Filter

## User Story 1: Assign a Due Date

As a user, I want to assign an optional due date to a task so that I know when it should be completed.

### Acceptance Criteria

- The user can enter an optional due date when creating a task.
- The due date must use a valid date format.
- A valid due date is saved with the task.
- An invalid due date is rejected with status 422.
- A task without a due date is still accepted.
- The due date appears on the task card.

## User Story 2: Edit a Due Date

As a user, I want to update or remove a task's due date so that I can keep its deadline accurate.

### Acceptance Criteria

- The user can update the due date from the edit modal.
- The updated due date is saved through the PATCH request.
- The user can remove an existing due date.
- Updating the due date does not change unrelated task fields.

## User Story 3: Identify Overdue Tasks

As a user, I want overdue tasks to be visually identified so that I can prioritize delayed work.

### Acceptance Criteria

- A task is overdue when its due date is before today.
- A task with status Done is not marked as overdue.
- A task without a due date is not marked as overdue.
- Overdue tasks display a visible indicator on their task cards.

## User Story 4: Filter Overdue Tasks

As a user, I want to filter overdue tasks so that I can focus only on delayed work.

### Acceptance Criteria

- The user can enable the overdue filter.
- Only overdue tasks appear while the filter is active.
- Tasks with status Done are excluded from the overdue results.
- Disabling the filter restores the full task list.


# Feature 2: Tags / Labels

## User Story 1: Add Tags

As a user, I want to add optional tags to a task so that I can categorize it.

### Acceptance Criteria

- The user can add one or more tags when creating a task.
- A task can be created without tags.
- Tags are saved with the task.
- Tags appear on the task card.

## User Story 2: Edit Tags

As a user, I want to update or remove a task's tags so that its categories remain accurate.

### Acceptance Criteria

- The user can update tags from the edit modal.
- Updated tags are saved through the PATCH request.
- The user can remove all tags.
- Updating tags does not change unrelated task fields.

## User Story 3: Validate Tags

As a user, I want invalid tags to be cleaned or rejected so that tasks do not contain meaningless labels.

### Acceptance Criteria

- Leading and trailing spaces are removed.
- Empty or whitespace-only tags are not saved.
- Duplicate tags are not saved more than once.