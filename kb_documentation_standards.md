# Documentation Standards — Task Manager API

## Overview

Good documentation is treated as a first-class deliverable. Undocumented code
that passes tests is considered incomplete. These standards apply to all PRs.

---

## Endpoint Documentation Requirements

Every new endpoint must have a docstring covering all five elements:

```python
@router.post("/tasks/", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new task for the authenticated user.

    Params:
        task_in: Task fields — title (required), description, status, priority, due_date
        db: Database session (injected)
        current_user: Authenticated user from token (injected)

    Returns:
        TaskResponse: The created task with id, timestamps, and all fields.

    Raises:
        401: If the X-Token header is missing or invalid.
        422: If required fields (title) are missing or field values are invalid.

    Example request:
        POST /tasks/
        X-Token: user_id:1
        {
            "title": "Write unit tests",
            "priority": "high",
            "due_date": "2024-12-31"
        }

    Example response (201):
        {
            "id": 42,
            "title": "Write unit tests",
            "description": null,
            "status": "todo",
            "priority": "high",
            "created_at": "2024-01-15T10:30:00",
            "due_date": "2024-12-31",
            "user_id": 1
        }
    """
```

---

## README Requirements

The README must always contain these sections, in this order:

1. **Project description** — one paragraph, explains what it is and who it's for
2. **Quickstart** — working in 5 commands or fewer:
   ```bash
   git clone https://github.com/org/repo
   cd repo
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   # API at http://localhost:8000, docs at http://localhost:8000/docs
   ```
3. **Endpoint table** — method, path, description, auth required (Y/N)
4. **Environment variables table** — variable name, description, default/required
5. **Known limitations** — honest list of current gaps (links to issues)
6. **Contributing** — link to CONTRIBUTING.md

The README must be updated in the same PR as any change that:
- Adds or removes an endpoint
- Changes authentication method
- Changes environment variable requirements
- Adds a new required dependency

---

## ARCHITECTURE.md Requirements

ARCHITECTURE.md must be updated when:
- A new SQLAlchemy model is added
- A new router/module is added
- The authentication approach changes
- A major dependency is added or removed
- A new external service integration is added

The ARCHITECTURE.md must always contain:
- System overview with technology choices explained
- Data model diagram (ASCII or Mermaid)
- Auth approach (current and planned)
- Known technical debt with explanations

---

## Changelog Requirements

Every merged PR must add an entry to `CHANGELOG.md` (create if missing):

```markdown
## [Unreleased]

### Added
- Pagination support for GET /tasks (page, limit query params) (#12)

### Fixed
- GET /tasks/{id} now returns 404 instead of 500 for missing tasks (#15)

### Security
- Passwords now hashed with bcrypt (#18)
```

Use [Keep a Changelog](https://keepachangelog.com) format.
Categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

---

## OpenAPI / Swagger Expectations

FastAPI auto-generates OpenAPI docs at `/docs`. Ensure quality by:

### Endpoint Metadata
```python
@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description="Returns a single task. Returns 404 if not found or if the task belongs to another user.",
    responses={
        200: {"description": "Task found"},
        401: {"description": "Missing or invalid authentication token"},
        404: {"description": "Task not found"},
    }
)
```

### All Response Models Must Be Documented
- Every endpoint specifies `response_model`
- Error responses include 400, 401, 403, 404, 422, 500 where applicable
- No endpoint should have an undocumented return type

### Schema Field Descriptions
```python
class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    priority: TaskPriority = Field(TaskPriority.medium, description="Task priority: low, medium, or high")
    due_date: Optional[str] = Field(None, description="Due date in ISO 8601 format (YYYY-MM-DD)")
```

---

## Example: Fully Documented Endpoint

This is the gold standard for endpoint documentation in this project:

```python
@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="List all tasks",
    description=(
        "Returns all tasks belonging to the authenticated user. "
        "Results are ordered by created_at descending (newest first). "
        "TODO: pagination will be added in a future release."
    ),
    responses={
        200: {"description": "List of tasks (may be empty)"},
        401: {"description": "Missing or invalid X-Token header"},
    }
)
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks for the current user.

    Returns an array of TaskResponse objects. Returns an empty array
    if the user has no tasks. Does not return tasks belonging to other users.

    Note: Currently returns ALL tasks without pagination. This is a known
    limitation — see GitHub issue #12.

    Params:
        db: Database session (injected via Depends)
        current_user: Authenticated user from X-Token header (injected)

    Returns:
        List[TaskResponse]: Array of task objects, possibly empty.

    Raises:
        401: If the X-Token header is absent or does not correspond to a valid user.
    """
    return db.query(Task).filter(Task.user_id == current_user.id).all()
```
