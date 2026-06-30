import json


def _create_task(client, title="Write tests", description="Cover all endpoints", status=None):
    payload = {"title": title, "description": description}
    if status:
        payload["status"] = status
    response = client.post("/tasks", json=payload)
    return response


class TestCreateTask:
    def test_create_task_success(self, client):
        response = _create_task(client)
        assert response.status_code == 201

        data = response.get_json()
        assert data["title"] == "Write tests"
        assert data["description"] == "Cover all endpoints"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_task_missing_title(self, client):
        response = client.post("/tasks", json={"description": "no title here"})
        assert response.status_code == 400
        assert "title" in response.get_json()["error"]

    def test_create_task_empty_title(self, client):
        response = client.post("/tasks", json={"title": "   "})
        assert response.status_code == 400

    def test_create_task_invalid_status(self, client):
        response = client.post(
            "/tasks", json={"title": "Bad status", "status": "not_a_status"}
        )
        assert response.status_code == 400

    def test_create_task_unknown_field(self, client):
        response = client.post(
            "/tasks", json={"title": "Has extra", "priority": "high"}
        )
        assert response.status_code == 400

    def test_create_task_non_json_body(self, client):
        response = client.post(
            "/tasks", data="not json", content_type="text/plain"
        )
        assert response.status_code == 400


class TestListTasks:
    def test_list_tasks_empty(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_list_tasks_returns_created(self, client):
        _create_task(client, title="Task A")
        _create_task(client, title="Task B")

        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2

    def test_list_tasks_filter_by_status(self, client):
        _create_task(client, title="Pending task")
        _create_task(client, title="Done task", status="completed")

        response = client.get("/tasks?status=completed")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Done task"


class TestGetTask:
    def test_get_task_success(self, client):
        created = _create_task(client).get_json()
        response = client.get(f"/tasks/{created['id']}")
        assert response.status_code == 200
        assert response.get_json()["id"] == created["id"]

    def test_get_task_not_found(self, client):
        response = client.get("/tasks/9999")
        assert response.status_code == 404
        assert "error" in response.get_json()


class TestUpdateTask:
    def test_update_task_success(self, client):
        created = _create_task(client).get_json()
        response = client.put(
            f"/tasks/{created['id']}",
            json={"status": "in_progress"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "in_progress"
        assert data["title"] == created["title"]

    def test_update_task_full_replace(self, client):
        created = _create_task(client).get_json()
        response = client.put(
            f"/tasks/{created['id']}",
            json={"title": "Updated title", "description": "Updated desc", "status": "completed"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated title"
        assert data["status"] == "completed"

    def test_update_task_not_found(self, client):
        response = client.put("/tasks/9999", json={"status": "completed"})
        assert response.status_code == 404

    def test_update_task_invalid_status(self, client):
        created = _create_task(client).get_json()
        response = client.put(
            f"/tasks/{created['id']}", json={"status": "bogus"}
        )
        assert response.status_code == 400

    def test_update_task_empty_body(self, client):
        created = _create_task(client).get_json()
        response = client.put(f"/tasks/{created['id']}", json={})
        assert response.status_code == 400


class TestDeleteTask:
    def test_delete_task_success(self, client):
        created = _create_task(client).get_json()
        response = client.delete(f"/tasks/{created['id']}")
        assert response.status_code == 204

        follow_up = client.get(f"/tasks/{created['id']}")
        assert follow_up.status_code == 404

    def test_delete_task_not_found(self, client):
        response = client.delete("/tasks/9999")
        assert response.status_code == 404
