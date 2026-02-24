# Task Manager API

A personal task manager REST API built with FastAPI and SQLite.
Create, organize, and track tasks with priorities, statuses, and due dates.

> **Note:** This project is intentionally simple — it uses SQLite and basic token auth
> to keep setup minimal. See [Known Limitations](#known-limitations) for what would
> need to change before a production deployment.

---

## Quickstart

```bash
git clone https://github.com/volskyi-dmytro/e2e-repogator.git
cd e2e-repogator
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`
Interactive docs (Swagger UI) at `http://localhost:8000/docs`

---

## Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/health` | Health check | No |
| POST | `/users/register` | Register a new user | No |
| POST | `/users/login` | Login and receive token | No |
| GET | `/tasks/` | List all tasks for current user | Yes |
| POST | `/tasks/` | Create a new task | Yes |
| GET | `/tasks/{id}` | Get a task by ID | Yes |
| PUT | `/tasks/{id}` | Update a task | Yes |
| DELETE | `/tasks/{id}` | Delete a task | Yes |

### Authentication

After login, include the token in the `X-Token` header:

```bash
# Register
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret"}'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
# Response: {"token": "user_id:1", "user_id": 1}

# Use token
curl http://localhost:8000/tasks/ -H "X-Token: user_id:1"
```

### Task Fields

| Field | Type | Values | Required |
|-------|------|--------|----------|
| `title` | string | any | Yes |
| `description` | string | any | No |
| `status` | enum | `todo`, `in_progress`, `done` | No (default: `todo`) |
| `priority` | enum | `low`, `medium`, `high` | No (default: `medium`) |
| `due_date` | string | any date string | No |

---

## Environment Variables

This project requires no environment variables in its current form — it uses SQLite
with a local file (`taskmanager.db`). Future versions will require:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | (SQLite local file) |
| `SECRET_KEY` | JWT signing key | (planned) |

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

Expected output: 7 tests pass, 2 skipped (pagination and 404 handling — see Known Limitations).

---

## Known Limitations

These are **intentional simplifications** for this demo project. See linked issues for planned fixes.

| Limitation | Impact | Status |
|-----------|--------|--------|
| Passwords stored in plain text | Security risk — anyone with DB access can read all passwords | Issue #1 planned |
| No pagination on `GET /tasks` | Large task lists will be slow | Issue #2 planned |
| `GET /tasks/{id}` returns 500 for missing tasks | Should return 404 | Issue #3 planned |
| Token is trivially forgeable (`user_id:N`) | Anyone can impersonate any user | Issue #4 planned |
| `due_date` accepts any string | No format validation | Issue #5 planned |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, commit format, and PR requirements.
