# Commit Message Rules

## Basic Rules
- Format: **`<type>: <summary>`**
- Use **English** and **imperative form**
- Avoid past tense (`Fixed`, `Added`)
- Keep summary short
- Write details in body if needed
- Prefer a single feature per commit. If you must include multiple changes in one commit, separate messages with a semicolon (;) and use a semicolon at the end of all but the last message.
---

## Allowed Types (Prefixes)

| Prefix | Use case | Behavior changes? | Example |
|--------|----------|:----------------:|---------|
| **feat** | Add new feature | ✓ | `feat: generate number plate image` |
| **fix** | Bug fix that changes behavior | ✓ | `fix: correct text color picking` |
| **refactor** | Improve internal code quality without changing behavior | ✗ | `refactor: simplify number plate generator` |
| **add** | Add new file only | ✗ | `add: NumberPlate.py` |
| **remove** | Remove files | ✗ | `remove: unused prototype` |
| **rename** | Rename files or variables | ✗ | `rename: LicensePlate -> NumberPlate` |
| **move** | Move files | ✗ | `move: NumberPlate.py to /src/` |
| **docs** | Update comments, UML, README | ✗ | `docs: add class diagram` |
| **chore** | Maintenance tasks, config changes | ✗ | `chore: update .gitignore` |
| **test** | Add or update tests | ✗ or ✓ | `test: add tests for number plate generator` |
| **perf** | Performance improvement | ✓ | `perf: optimize number plate generator` |

---

## Decision Flow

| Question | Yes → | No → |
|---------|------|-----|
| Actual behavior changed? | **fix** | refactor |
| Is it a new capability? | **feat** | next question |
| Is it code-agnostic work? | docs / chore | add / remove / rename / move |
