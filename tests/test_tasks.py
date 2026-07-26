def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "New task",
        "description": "A task description",
        "status": "ToDo",
        "priority": "High",
        "assignee": "alice",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["status"] == payload["status"]
    assert body["priority"] == payload["priority"]
    assert body["assignee"] == payload["assignee"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"description": "missing title"})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "unknown": "value"})

    assert response.status_code == 422


def test_create_task_with_valid_due_date_returns_201(client):
    payload = {
        "title": "Task with deadline",
        "due_date": "2026-08-15",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == "2026-08-15"


def test_create_task_without_due_date_returns_201(client):
    payload = {
        "title": "Task without deadline",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] is None


def test_create_task_invalid_due_date_returns_422(client):
    payload = {
        "title": "Bad deadline",
        "due_date": "not-a-date",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_create_task_with_tags_returns_201(client):
    payload = {
        "title": "Tagged task",
        "tags": ["frontend", "bug"],
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == ["frontend", "bug"]


def test_create_task_without_tags_returns_empty_list(client):
    payload = {
        "title": "Task without tags",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == []


def test_create_task_tags_trimmed_and_empty_removed(client):
    payload = {
        "title": "Clean tags",
        "tags": ["  frontend ", "", "   ", "  bug  "],
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == ["frontend", "bug"]


def test_create_task_tags_duplicates_removed(client):
    payload = {
        "title": "Duplicate tags",
        "tags": ["bug", "frontend", "bug"],
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == ["bug", "frontend"]


def test_create_task_tags_case_sensitive(client):
    payload = {
        "title": "Case-sensitive tags",
        "tags": ["frontend", "Frontend"],
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == ["frontend", "Frontend"]


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "Task 1", "status": "ToDo"})
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Task 1", "priority": "High"})
    client.post("/tasks", json={"title": "Task 2", "priority": "Low"})

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/nonexistent")

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    original_title = created_task["title"]
    original_priority = created_task["priority"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == original_title
    assert body["priority"] == original_priority
    assert body["status"] == "InProgress"


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/nonexistent", json={"status": "InProgress"})

    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 422


def test_patch_invalid_status_value_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Backlog"})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_patch_same_status_returns_200_unchanged(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert response.status_code == 200
    assert response.json()["status"] == "ToDo"


def test_patch_set_due_date_returns_200(client):
    create_resp = client.post("/tasks", json={"title": "Needs deadline"})
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"due_date": "2026-09-01"})

    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-09-01"


def test_patch_remove_due_date_returns_200(client):
    create_resp = client.post(
        "/tasks", json={"title": "Deadline to remove", "due_date": "2026-09-01"}
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"due_date": None})

    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_patch_due_date_preserves_other_fields(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Keep deadline", "priority": "Medium", "due_date": "2026-09-01"},
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"priority": "Low"})

    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "Low"
    assert body["due_date"] == "2026-09-01"


def test_patch_replace_tags_returns_200(client):
    create_resp = client.post(
        "/tasks", json={"title": "Replace tags", "tags": ["frontend", "bug"]}
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"tags": ["docs"]})

    assert response.status_code == 200
    assert response.json()["tags"] == ["docs"]


def test_patch_clear_tags_returns_200(client):
    create_resp = client.post(
        "/tasks", json={"title": "Clear tags", "tags": ["frontend", "bug"]}
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"tags": []})

    assert response.status_code == 200
    assert response.json()["tags"] == []


def test_patch_tags_cleanup_trim_and_dedup(client):
    create_resp = client.post(
        "/tasks", json={"title": "Clean patched tags", "tags": ["old"]}
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"tags": [" docs ", "", "   ", "bug", "docs"]},
    )

    assert response.status_code == 200
    assert response.json()["tags"] == ["docs", "bug"]


def test_patch_tags_preserves_other_fields(client):
    create_resp = client.post(
        "/tasks",
        json={
            "title": "Preserve fields",
            "priority": "Medium",
            "due_date": "2026-09-01",
            "tags": ["old"],
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"tags": ["changed"]})

    assert response.status_code == 200
    body = response.json()
    assert body["tags"] == ["changed"]
    assert body["priority"] == "Medium"
    assert body["due_date"] == "2026-09-01"
    assert body["title"] == "Preserve fields"


def test_patch_tags_null_rejected_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"tags": None})

    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/nonexistent")

    assert response.status_code == 404
