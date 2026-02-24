# Code Review Standards — Task Manager API

## Overview

These standards apply to all pull requests on this Python/FastAPI project.
Reviewers are expected to verify compliance before approving.

---

## Security Checklist

All PRs must pass these security checks before approval:

### Passwords and Credentials
- [ ] **Passwords MUST be hashed** using bcrypt (minimum cost factor 12). Plain text storage is a blocker — do not approve.
  ```python
  # WRONG — never do this
  user.password = plain_password

  # CORRECT
  import bcrypt
  user.password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt(rounds=12)).decode()
  ```
- [ ] No secrets, tokens, or credentials appear in code, comments, or log statements
- [ ] No hardcoded values that should come from environment variables

### SQL and Database
- [ ] All database queries use SQLAlchemy ORM — raw string SQL is not permitted
  ```python
  # WRONG
  db.execute(f"SELECT * FROM tasks WHERE id = {task_id}")

  # CORRECT
  db.query(Task).filter(Task.id == task_id).first()
  ```
- [ ] No N+1 query patterns (loading related objects in a loop without eager loading)

### Input Validation
- [ ] All endpoints validate required fields via Pydantic schemas
- [ ] Date/time inputs are validated as proper ISO 8601 format, not arbitrary strings
- [ ] Integer IDs are validated as positive (Pydantic `gt=0` constraint)
- [ ] String length limits are defined for user-supplied text fields

---

## Performance Checklist

- [ ] **All list endpoints have pagination.** A list endpoint without `page`/`limit` params and a max of 100 items is a blocker.
  ```python
  # REQUIRED pattern for list endpoints
  @router.get("/", response_model=PaginatedResponse[TaskResponse])
  def list_tasks(page: int = 1, limit: int = Query(default=20, le=100), ...):
  ```
- [ ] No database queries inside loops (N+1 problem)
- [ ] `response_model` is always specified to control serialization scope
- [ ] Response models **must not** expose internal fields:
  - `User.password` must never appear in any response
  - Internal IDs of join tables should not be exposed unless required

---

## Code Quality Checklist

### Docstrings
- [ ] All new endpoints have a docstring describing purpose, params, returns, and error cases
  ```python
  @router.get("/{task_id}", response_model=TaskResponse)
  def get_task(task_id: int, ...):
      """
      Retrieve a single task by ID.

      Returns the task if it belongs to the authenticated user.
      Raises 404 if the task does not exist or belongs to another user.
      Raises 401 if no valid token is provided.
      """
  ```

### Error Handling
- [ ] All "not found" cases raise `HTTPException(status_code=404)` — not returning `None` (causes 500)
- [ ] All endpoints use `HTTPException`, not raw Python exceptions
- [ ] Error messages are informative but do not leak internal details (no stack traces in responses)

### Tests
- [ ] All new endpoints have at minimum:
  - Happy path test (correct input, expected response)
  - Error case test (missing resource returns 404, invalid input returns 422)
- [ ] Tests use the test database override, not the production database
- [ ] No `@pytest.mark.skip` without a linked issue explaining when it will be resolved

---

## FastAPI-Specific Patterns

These patterns are required for consistency:

### Dependency Injection
```python
# CORRECT — use Depends() for all shared dependencies
@router.get("/")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ...
```

### Response Models
```python
# ALWAYS specify response_model — controls what fields are serialized
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(...):
    ...
```

### HTTP Status Codes

| Operation | Correct Status Code |
|-----------|-------------------|
| POST (create) | 201 Created |
| GET (read) | 200 OK |
| PUT/PATCH (update) | 200 OK |
| DELETE | 204 No Content |
| Not found | 404 Not Found |
| Validation error | 422 Unprocessable Entity |
| Auth failed | 401 Unauthorized |
| Forbidden | 403 Forbidden |
| Conflict (duplicate) | 409 Conflict |

### HTTPException Usage
```python
# CORRECT
from fastapi import HTTPException

task = db.query(Task).filter(Task.id == task_id).first()
if not task:
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
```

---

## PR Review SLA

- **First response** within 24 hours of PR opening
- **Re-review after changes** within 24 hours of author marking "ready for review"
- PRs open more than 3 days without activity should be escalated

## When to Require Re-review vs. Approve with Comments

**Require re-review when:**
- A security checklist item failed (password hashing, SQL injection, exposed secrets)
- Missing tests for new functionality
- The overall approach is wrong and significant rework is needed
- A blocker-level performance issue (no pagination on list endpoint)

**Approve with comments when:**
- Minor style issues (naming, docstring completeness)
- Non-blocking suggestions for improvement
- Small refactors that are not required for correctness
