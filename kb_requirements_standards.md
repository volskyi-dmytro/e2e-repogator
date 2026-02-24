# Requirements Standards — Task Manager API

## Issue Writing Standards

### Required Fields

Every issue must include all of the following before it can be picked up:

| Field | Requirement |
|-------|-------------|
| **Title** | Clear, action-oriented. Format: `[Type] Short description` (e.g., `[Feature] Add pagination to GET /tasks`) |
| **User story** | `As a <role>, I want <capability>, so that <benefit>` |
| **Acceptance criteria** | Given/When/Then format, minimum 2 criteria |
| **Priority label** | One of: `priority:low`, `priority:medium`, `priority:high`, `priority:critical` |
| **Type label** | One of: `type:feature`, `type:bug`, `type:improvement`, `type:tech-debt` |

### Acceptance Criteria Format

All acceptance criteria must use Given/When/Then:

```
Given [initial context or precondition]
When [an action is performed]
Then [expected outcome]
```

**Multiple criteria example:**
```
Given a user is authenticated
When they call GET /tasks with ?page=2&limit=10
Then they receive tasks 11-20 and a total_count field in the response

Given a user is authenticated
When they call GET /tasks with an invalid limit value (e.g. limit=-1)
Then they receive a 422 Unprocessable Entity response with a descriptive error
```

### Definition of "Ready"

An issue is ready to be picked up when:
- [ ] All required fields are filled in
- [ ] No open questions remain in the comments
- [ ] Acceptance criteria are specific enough to write tests from
- [ ] Any dependent issues are linked
- [ ] Complexity estimate has been assigned

---

## Complexity Estimation Guide

Use these estimates for this codebase (FastAPI + SQLite + SQLAlchemy):

| Size | Description | Examples | Time |
|------|-------------|---------|------|
| **XS** | Single endpoint change, no model changes | Fix typo in error message, add missing field to response, change default value | < 2h |
| **S** | New endpoint using existing models | Add `GET /tasks/{id}` if missing, add filter query param, add input validation | 2–4h |
| **M** | New model + endpoints + tests | Add `Tag` model, CRUD endpoints, update Task to have tags | 4–8h |
| **L** | Cross-cutting concern, auth changes, migrations | Replace plain-text passwords with bcrypt, add JWT auth, database migration | 1–2 days |
| **XL** | Architectural change, new subsystem | Switch from SQLite to PostgreSQL, add background job queue, add WebSocket support | 2+ days |

---

## Good Issue vs. Bad Issue

### BAD Issue ❌

**Title:** `pagination`

**Body:**
> the tasks endpoint is slow, we need pagination

**Problems:**
- No user story
- No acceptance criteria
- No priority or type label
- "slow" is not a measurable problem
- Cannot be picked up without asking questions

---

### GOOD Issue ✅

**Title:** `[Improvement] Add pagination to GET /tasks endpoint`

**Labels:** `priority:medium`, `type:improvement`

**Body:**
```
## User Story
As an API consumer, I want to paginate the task list,
so that I can efficiently retrieve large numbers of tasks
without loading everything at once.

## Problem
Currently GET /tasks returns all tasks for the user with no limit.
A user with 1,000 tasks will receive all 1,000 in a single response,
causing slow responses and high memory usage.

## Acceptance Criteria

Given a user has 50 tasks and calls GET /tasks?page=1&limit=10
When the request is processed
Then exactly 10 tasks are returned along with total_count=50 and has_next=true

Given a user calls GET /tasks with no pagination params
When the request is processed
Then a default of page=1, limit=20 is applied

Given a user calls GET /tasks?limit=500
When the request is processed
Then a 422 error is returned (max limit is 100)

## Complexity
S — no model changes, endpoint update + tests

## Notes
- Do not break the existing response schema; add fields alongside
```

---

## REST API Edge Cases Checklist

When writing requirements for any endpoint, verify these edge cases are addressed:

### Invalid IDs
- What happens when `GET /tasks/99999` and that task doesn't exist?
- Expected: 404 Not Found, not 500 Internal Server Error
- Required: explicit `HTTPException(status_code=404)` in the handler

### Empty / Malformed Request Bodies
- What happens when `POST /tasks` receives `{}`?
- Expected: 422 Unprocessable Entity (FastAPI validates required fields)
- What happens when `PUT /tasks/1` receives invalid JSON?
- Expected: 422 with descriptive field errors

### Auth Boundary Conditions
- What happens when no token is provided?
- Expected: 401 Unauthorized
- What happens when a user tries to access another user's task?
- Expected: 404 (not 403 — don't reveal existence of the resource)
- What happens when the token is malformed?
- Expected: 401 with "Invalid token" message

### Pagination Defaults and Limits
- Default page: 1
- Default limit: 20
- Maximum limit: 100 (reject higher values with 422)
- What happens when `page` exceeds total pages?
- Expected: 200 with empty list, not 404
