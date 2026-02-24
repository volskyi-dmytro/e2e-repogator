# Architecture — Task Manager API

## System Overview

A single-process REST API built with FastAPI and SQLite. Designed for personal use
or small teams — one server, one database file, no external dependencies required.

### Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| Framework | FastAPI | Async-capable, auto-generates OpenAPI docs, Pydantic validation |
| Database | SQLite | Zero setup, single file, sufficient for personal/demo use |
| ORM | SQLAlchemy | Type-safe queries, migration support via Alembic (future) |
| Validation | Pydantic v2 | Native FastAPI integration, fast, good error messages |
| Tests | pytest + httpx | Standard Python testing, FastAPI TestClient support |

### Request Flow

```
Client
  │
  ▼
FastAPI App (app/main.py)
  │
  ├── POST /users/register ──► users router (app/routers/users.py)
  ├── POST /users/login    ──► users router
  │
  └── /tasks/* ──► tasks router (app/routers/tasks.py)
                     │
                     ├── get_current_user() — validates X-Token header
                     │
                     └── SQLAlchemy Session (app/database.py)
                               │
                               ▼
                           SQLite DB (taskmanager.db)
```

---

## Data Model

```
┌─────────────────────────────────┐
│              User               │
├─────────────────────────────────┤
│ id          INTEGER  PK         │
│ username    TEXT     UNIQUE     │
│ email       TEXT     UNIQUE     │
│ password    TEXT     (plain!)   │ ← known issue
│ created_at  DATETIME            │
└──────────────┬──────────────────┘
               │ 1
               │
               │ N
┌──────────────▼──────────────────┐
│              Task               │
├─────────────────────────────────┤
│ id          INTEGER  PK         │
│ title       TEXT     NOT NULL   │
│ description TEXT                │
│ status      ENUM  todo/         │
│                   in_progress/  │
│                   done          │
│ priority    ENUM  low/          │
│                   medium/       │
│                   high          │
│ created_at  DATETIME            │
│ due_date    TEXT     (any str!) │ ← known issue
│ user_id     INTEGER  FK → User  │
└─────────────────────────────────┘
```

---

## Authentication Approach

### Current (Simplified — Not Production Safe)

Token format: `user_id:<integer>` (e.g., `user_id:42`)

This token is:
- Trivially forgeable — any client can impersonate user 42 by sending `user_id:42`
- Not expiring — valid forever
- Not signed — no cryptographic verification

It exists only to demonstrate the auth flow structure. It is intentionally simple
so code reviewers can suggest proper JWT implementation.

### Planned: JWT Authentication

```
POST /users/login → returns signed JWT (HS256)
  Payload: { "sub": user_id, "exp": <timestamp> }
  Header: Authorization: Bearer <token>
```

Implementation will require:
- `python-jose[cryptography]` for JWT signing/verification
- `SECRET_KEY` environment variable
- Token expiry (default 24h access, 30d refresh)
- Refresh token endpoint

---

## Known Technical Debt

These are intentional simplifications, not oversights. Each is a realistic issue
that code review and AI analysis should identify.

### 1. Plain Text Passwords
**File:** `app/models.py:22`, `app/routers/users.py:17`
**Issue:** `User.password` stores the raw password string. Anyone with read access
to `taskmanager.db` can read all passwords.
**Fix:** Use `bcrypt.hashpw()` on registration, `bcrypt.checkpw()` on login.
**Complexity:** L (requires migration for existing users)

### 2. No Pagination on GET /tasks
**File:** `app/routers/tasks.py:28`
**Issue:** Returns all tasks with `db.query(Task).all()`. A user with 10,000 tasks
causes a slow response and large JSON payload.
**Fix:** Add `page: int = 1, limit: int = Query(20, le=100)` query params.
**Complexity:** S

### 3. Missing 404 Handling
**File:** `app/routers/tasks.py:34`, `app/routers/tasks.py:40`, `app/routers/tasks.py:47`
**Issue:** When a task is not found, `first()` returns `None`. Subsequent attribute
access raises `AttributeError`, which FastAPI converts to a 500 Internal Server Error.
**Fix:** Check `if not task: raise HTTPException(status_code=404, detail="Task not found")`
**Complexity:** XS

### 4. Forgeable Authentication Token
**File:** `app/routers/users.py:29`, `app/routers/tasks.py:19`
**Issue:** Token is `user_id:<id>` — trivially forgeable. No cryptographic signature.
**Fix:** Implement JWT with `python-jose`.
**Complexity:** L

### 5. No Due Date Validation
**File:** `app/models.py:27`, `app/schemas.py:31`
**Issue:** `due_date` is stored as a plain string. `"not-a-date"` is accepted.
**Fix:** Use `datetime.date` type in schema with ISO 8601 validation.
**Complexity:** XS

---

## Future Roadmap

### Near Term
1. Hash passwords with bcrypt
2. Add pagination to list endpoints
3. Fix 404 handling across all endpoints
4. Validate `due_date` as proper date format

### Medium Term
5. Replace token auth with JWT
6. Add task filtering (by status, priority, due date range)
7. Add task tags/labels
8. Add rate limiting middleware

### Long Term
9. Migrate from SQLite to PostgreSQL (needed for multi-process deployment)
10. Add Alembic migrations for schema changes
11. Add background job for deadline notifications
12. Add multi-user collaboration (shared task lists)
