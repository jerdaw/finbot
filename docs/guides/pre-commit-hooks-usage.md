# Pre-commit Hooks Usage Guide

**Created:** 2026-02-10
**Status:** Active

---

## Overview

This project uses pre-commit hooks to automatically check code quality before commits. Hooks are organized into two categories:

1. **Automatic hooks** - Run on every commit (fast, must pass)
2. **Manual hooks** - Run on demand (slower, informational)

---

## Automatic Hooks (Run on Every Commit)

These hooks run automatically when you commit and will block the commit if they fail:

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| `trailing-whitespace` | Remove trailing whitespace | ✅ Yes |
| `end-of-file-fixer` | Ensure files end with newline | ✅ Yes |
| `check-yaml` | Validate YAML syntax | ❌ No |
| `check-added-large-files` | Block files >50MB | ❌ No |
| `debug-statements` | Catch Python debugger statements | ❌ No |
| `check-case-conflict` | Prevent case-sensitive filename conflicts | ❌ No |
| `check-merge-conflict` | Catch unresolved merge markers | ❌ No |
| `check-ast` | Validate Python syntax | ❌ No |
| `check-json` | Validate JSON syntax | ❌ No |
| `check-toml` | Validate TOML syntax | ❌ No |
| `detect-private-key` | Prevent committing private keys | ❌ No |
| `mixed-line-ending` | Enforce LF line endings (critical for WSL) | ✅ Yes |
| `ruff` | Lint Python code | ✅ Yes (with --fix) |
| `ruff-format` | Format Python code | ✅ Yes |

**Total:** 14 automatic hooks (~1-2 seconds on typical commit)

---

## Manual Hooks (Run on Demand)

These hooks are available but don't run automatically. They're informational-only since:
- CI already runs them comprehensively
- Current codebase has known issues (125 mypy errors, 6 bandit warnings)
- Running on every commit would be slow and noisy

### mypy - Type Checking

**Run manually with:**
```bash
# Check specific files
uv run pre-commit run --hook-stage manual mypy --files path/to/file.py

# Check all files (slow - ~30 seconds)
uv run pre-commit run --hook-stage manual mypy --all-files

# Or run mypy directly for more control
DYNACONF_ENV=development uv run mypy finbot/
```

**Current state:** 125 type errors in 41 files (see `docs/guides/type-safety-improvement-guide.md`)

**When to use:**
- Before opening a PR (check files you modified)
- When adding type hints to a module
- To verify type-related changes
- As part of local testing workflow

### bandit - Security Scanning

**Run manually with:**
```bash
# Check specific files
uv run pre-commit run --hook-stage manual bandit --files path/to/file.py

# Check all files (slow - ~15 seconds)
uv run pre-commit run --hook-stage manual bandit --all-files

# Or run bandit directly for more control
uv run bandit -c pyproject.toml -r finbot/ libs/
```

**Current state:** 6 low-severity warnings (all known and acceptable)

**When to use:**
- Before opening a PR (check files you modified)
- When adding new file I/O or subprocess calls
- When adding new data deserialization code
- To verify security-related changes

---

## Usage Examples

### Daily Development Workflow

```bash
# 1. Make changes to files
vim finbot/services/simulation/fund_simulator.py

# 2. Stage changes
git add finbot/services/simulation/fund_simulator.py

# 3. Commit (automatic hooks run)
git commit -m "Add new fund simulator feature"
# ✅ Automatic hooks pass (1-2 seconds)

# 4. (Optional) Run manual checks before pushing
uv run pre-commit run --hook-stage manual mypy --files finbot/services/simulation/fund_simulator.py
uv run pre-commit run --hook-stage manual bandit --files finbot/services/simulation/fund_simulator.py

# 5. Push to remote
git push origin feature-branch
```

### Pre-PR Checklist

Before opening a pull request:

```bash
# 1. Run all automatic hooks on all files
uv run pre-commit run --all-files

# 2. Run manual type checking on modified files
uv run pre-commit run --hook-stage manual mypy --files path/to/modified.py

# 3. Run manual security scanning on modified files
uv run pre-commit run --hook-stage manual bandit --files path/to/modified.py

# 4. Run tests
DYNACONF_ENV=development uv run pytest tests/ -v

# 5. Verify CI will pass
make check  # Runs lint + format + type + security + tests
```

### Fixing Hook Failures

**If automatic hook fails:**

1. **Auto-fixing hooks** (trailing-whitespace, ruff, etc.) - Changes are staged automatically, just commit again:
   ```bash
   git add -u  # Stage the fixes
   git commit -m "Your message"  # Commit will succeed
   ```

2. **Non-fixing hooks** (check-yaml, debug-statements, etc.) - Fix manually:
   ```bash
   # Fix the issue in the file
   vim path/to/file.py

   # Stage and commit
   git add path/to/file.py
   git commit -m "Your message"
   ```

**If manual hook reports issues:**

These are informational only and don't block commits. CI will catch critical issues. Fix at your discretion:
- Mypy errors: See `docs/guides/type-safety-improvement-guide.md`
- Bandit warnings: Review for actual security concerns vs. false positives

---

## Bypass Hooks (Use Sparingly)

In rare cases where you need to bypass hooks:

```bash
# Bypass all hooks (not recommended)
git commit --no-verify -m "Emergency hotfix"

# Better: Fix specific hook issue or add exception in config
```

**When bypassing is acceptable:**
- Emergency hotfixes to production
- Committing known WIP changes to feature branch
- Automated bot commits

**When bypassing is NOT acceptable:**
- "I don't want to fix the linting errors"
- "The hook is too slow" (file an issue instead)
- Regular development workflow

---

## Troubleshooting

### Hooks are slow

**Problem:** Pre-commit takes >5 seconds
**Solution:**
- Make sure you're only running automatic hooks (manual hooks are opt-in)
- Check if you have uncommitted changes in many files
- Run `uv run pre-commit clean` to clear cache

### Hook installation issues

**Problem:** `pre-commit install` fails with "core.hooksPath set"
**Solution:**
```bash
# Pre-commit hooks run via uv without needing installation
uv run pre-commit run --all-files

# If you really need to install, unset the path first:
git config --global --unset core.hooksPath
uv run pre-commit install
```

### Mypy/bandit dependencies missing

**Problem:** Manual hooks fail with import errors
**Solution:**
```bash
# Reinstall pre-commit environments
uv run pre-commit clean
uv run pre-commit install-hooks
```

### Ruff version mismatch

**Problem:** Pre-commit ruff version differs from project ruff version
**Solution:**
- Check `.pre-commit-config.yaml` rev matches `pyproject.toml` ruff version
- Both should be `^0.11.0` / `v0.11.13`

---

## Updating Hooks

### Update all hooks to latest versions

```bash
uv run pre-commit autoupdate
```

### Update specific hook

Edit `.pre-commit-config.yaml` and change the `rev:` field:

```yaml
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.13  # Update this version
    hooks:
    -   id: ruff
```

Then run:
```bash
uv run pre-commit clean
uv run pre-commit install-hooks
```

---

## CI Integration

Pre-commit hooks are also run in CI (`.github/workflows/ci.yml`):

| Hook | CI Stage | Blocking |
|------|----------|----------|
| ruff check | Lint | ✅ Yes |
| ruff format --check | Format check | ✅ Yes |
| mypy | Type check | ✅ Yes |
| bandit | Security scan | ❌ No (informational) |
| pytest | Tests | ✅ Yes |

**CI runs more comprehensive checks than local hooks:**
- Mypy checks entire codebase (not just staged files)
- Tests run across Python 3.11, 3.12, 3.13
- Coverage reporting to Codecov
- Dependency auditing with pip-audit

---

## Configuration Files

- **`.pre-commit-config.yaml`** - Hook definitions and versions
- **`pyproject.toml`** - Tool configurations (ruff, mypy, bandit)
- **`.coveragerc`** - Coverage exclusions

---

## See Also

- [Type Safety Improvement Guide](type-safety-improvement-guide.md)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
