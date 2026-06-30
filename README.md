# Task Manager API

A REST API for managing tasks, built with Flask, SQLAlchemy, and SQLite. Supports full CRUD operations, input validation, structured error handling, logging, and a pytest test suite.

## Features

- Full CRUD: create, read, update, delete tasks
- SQLite persistence via SQLAlchemy ORM
- Input validation with explicit 400 error responses
- Global error handling (404s, validation errors, unexpected exceptions)
- Structured logging throughout the request lifecycle
- Application factory pattern for clean testing/config separation
- Pytest test suite covering every endpoint and edge case

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- SQLite
- pytest

## Project Structure

```
task-manager-api/
├── app/
│   ├── __init__.py      # App factory, db setup, logging config
│   ├── models.py        # Task model
│   ├── routes.py        # CRUD route handlers (Blueprint)
│   ├── errors.py        # Global error handlers
│   └── validation.py    # Request payload validation
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   └── test_tasks.py     # Endpoint tests
├── app.py                # Entrypoint
├── config.py              # Environment-based configuration
├── .env.example            # Template for required env vars
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repo and move into it:
   ```bash
   git clone <your-repo-url>
   cd task-manager-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy the env template and adjust as needed:
   ```bash
   cp .env.example .env
   ```

4. Run the app:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## Running Tests

```bash
pytest -v
```

## Task Model

| Field         | Type     | Notes                                          |
|---------------|----------|-------------------------------------------------|
| `id`          | integer  | Auto-generated primary key                     |
| `title`       | string   | Required, max 120 chars                         |
| `description` | string   | Optional                                        |
| `status`      | string   | One of `pending`, `in_progress`, `completed`    |
| `created_at`  | datetime | Auto-generated, ISO 8601 format                 |

## API Endpoints

### Create a Task
`POST /tasks`

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

Response `201 Created`:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-06-30T10:15:00+00:00"
}
```

### List Tasks
`GET /tasks`

```bash
curl http://localhost:5000/tasks
```

Optionally filter by status:
```bash
curl "http://localhost:5000/tasks?status=completed"
```

Response `200 OK`:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "created_at": "2026-06-30T10:15:00+00:00"
  }
]
```

### Get a Single Task
`GET /tasks/<id>`

```bash
curl http://localhost:5000/tasks/1
```

Response `200 OK` (or `404` if not found):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-06-30T10:15:00+00:00"
}
```

### Update a Task
`PUT /tasks/<id>`

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

Response `200 OK`:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "in_progress",
  "created_at": "2026-06-30T10:15:00+00:00"
}
```

### Delete a Task
`DELETE /tasks/<id>`

```bash
curl -X DELETE http://localhost:5000/tasks/1
```

Response: `204 No Content`

## Error Responses

All errors return JSON in the form `{"error": "message"}`.

| Status | Cause                                      |
|--------|---------------------------------------------|
| 400    | Invalid/missing fields, malformed JSON      |
| 404    | Task or route not found                     |
| 405    | HTTP method not allowed on the route        |
| 500    | Unexpected server error                     |

Example validation error:
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```
```json
{
  "error": "'title' is required."
}
```

## Notes

- The `status` field only accepts `pending`, `in_progress`, or `completed`.
- `PUT` requests support partial updates — only the fields you include are changed.
- Unknown fields in the request body are rejected with a `400` to keep the API contract explicit.
