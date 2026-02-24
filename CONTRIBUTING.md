# Contributing to Task Manager API

Thank you for contributing. Please follow these guidelines to keep the project consistent.

---

## Branch Naming

| Type | Format | Example |
|------|--------|---------|
| New feature | `feature/short-description` | `feature/add-pagination` |
| Bug fix | `bugfix/short-description` | `bugfix/task-404-handling` |
| Improvement | `improvement/short-description` | `improvement/hash-passwords` |
| Documentation | `docs/short-description` | `docs/update-architecture` |
| Tech debt | `tech-debt/short-description` | `tech-debt/migrate-to-postgresql` |

Always branch from `main` unless told otherwise.

---

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

[optional body]

[optional footer]
```

| Type | When to use |
|------|-------------|
| `feat:` | A new feature or endpoint |
| `fix:` | A bug fix |
| `docs:` | Documentation changes only |
| `refactor:` | Code change that doesn't add a feature or fix a bug |
| `test:` | Adding or updating tests |
| `chore:` | Dependency updates, CI changes, tooling |

**Examples:**
```
feat: add pagination to GET /tasks endpoint

Adds page and limit query params. Default: page=1, limit=20, max limit=100.
Returns total_count and has_next in response.

Closes #12
```

```
fix: return 404 instead of 500 for missing tasks

GET /tasks/{id} previously raised AttributeError when task was not found.
Now raises HTTPException(status_code=404).

Closes #15
```

---

## Pull Request Requirements

Before opening a PR:
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] New endpoints have tests (happy path + at least one error case)
- [ ] New endpoints have docstrings
- [ ] README is updated if endpoint list changed
- [ ] ARCHITECTURE.md is updated if models or auth changed
- [ ] A changelog entry is added to `CHANGELOG.md`

### PR Description Template

```markdown
## What does this PR do?
[1-2 sentences describing the change]

## Why?
[Link to the issue this closes: Closes #N]

## How was it tested?
[Describe what you tested manually, or point to new test cases]

## Checklist
- [ ] Tests pass
- [ ] Docstrings added
- [ ] README updated (if needed)
- [ ] ARCHITECTURE.md updated (if needed)
- [ ] Changelog entry added
```

---

## Issue Requirements

Before opening an issue, use the correct template and fill all fields:

- **Title format:** `[Type] Short description`
  - `[Feature] Add JWT authentication`
  - `[Bug] GET /tasks/{id} returns 500 for missing tasks`
  - `[Improvement] Add pagination to task list`
  - `[Tech Debt] Hash passwords with bcrypt`

- **Required sections:**
  - User story (As a... I want... so that...)
  - Acceptance criteria (Given/When/Then format)
  - Priority label: `priority:low`, `priority:medium`, `priority:high`, `priority:critical`
  - Type label: `type:feature`, `type:bug`, `type:improvement`, `type:tech-debt`

See [kb_requirements_standards.md](kb_requirements_standards.md) for the full guide
with examples of good vs. bad issues.

---

## Code Style

- **Formatter:** [black](https://black.readthedocs.io/) — run `black .` before committing
- **Linter:** [ruff](https://docs.astral.sh/ruff/) — run `ruff check .` before committing
- **Type hints:** Preferred but not enforced yet
- **Line length:** 100 characters (configured in pyproject.toml)

```bash
pip install black ruff
black .
ruff check .
```

---

## Security Rules (Non-Negotiable)

- Never commit credentials, tokens, or API keys
- Never store passwords in plain text (use bcrypt)
- Never use raw string interpolation in SQL queries
- If you find a security issue, open a private issue or email the maintainer directly
