# Instructions: Update Ruff Version and Lock File

## What Was Done

1. ✅ Updated `pyproject.toml`: `ruff = "^0.1.8"` → `ruff = "^0.11.0"`
2. ✅ Updated `.pre-commit-config.yaml`: `rev: v0.2.0` → `rev: v0.11.0"`
3. ✅ Expanded ruff rules in `pyproject.toml` to include:
   - `C901` (complexity)
   - `N` (naming conventions)
   - `A` (builtin shadowing)
   - `C4` (comprehensions)
   - `RUF` (ruff-specific)
   - `LOG` (logging)
   - `PERF` (performance)

## What You Need to Do

### Step 1: Update Poetry Lock File

Run this command to update the lock file with the new ruff version:

```bash
poetry lock --no-update
```

This will update only the ruff dependency in `poetry.lock` without updating other packages.

### Step 2: Install Updated Dependencies

```bash
poetry install
```

### Step 3: Update Pre-commit Hooks

```bash
poetry run pre-commit autoupdate
```

This will ensure pre-commit uses the latest hooks.

### Step 4: Run Ruff to Check for New Violations

```bash
poetry run ruff check .
```

This will show any new lint violations from the expanded rule set.

### Step 5: Auto-fix What Can Be Fixed

```bash
poetry run ruff check . --fix
```

Ruff will automatically fix many issues.

### Step 6: Review Remaining Violations

Any violations that can't be auto-fixed will need manual review. Common ones:

**C901 (Complexity):**
- Functions with cyclomatic complexity > 10
- Consider breaking into smaller functions or adding `# noqa: C901` if justified

**N (Naming):**
- Variable/function names not following PEP 8
- E.g., `SOME_VAR` should be `some_var` for local variables

**A (Builtin Shadowing):**
- Variables named `id`, `type`, `list`, `dict`, etc.
- Rename to avoid shadowing builtins

**PERF (Performance):**
- Inefficient patterns like `list()` in loops
- Usually safe to fix

### Step 7: Format Code

```bash
poetry run ruff format .
```

### Step 8: Verify Pre-commit Works

```bash
poetry run pre-commit run --all-files
```

This should pass with the same results as `poetry run ruff check .`

### Step 9: Commit Changes

```bash
git add pyproject.toml .pre-commit-config.yaml poetry.lock
git commit -m "Update ruff to 0.11.0 and expand lint rules

- Update ruff from ^0.1.8 to ^0.11.0
- Sync pre-commit ruff version to v0.11.0
- Add rules: C901, N, A, C4, RUF, LOG, PERF
- Fix lint violations from expanded rules"
```

## Expected Violations

Based on the new rules, expect to see:

1. **C901 (Complexity):** Some functions in `finbot/services/` may be flagged as too complex
2. **N (Naming):** Variable names in data science utils might not follow PEP 8 strictly
3. **A (Builtin Shadowing):** May find some `id`, `type`, or `list` variable names
4. **PERF:** Potentially some inefficient list operations

Most should be auto-fixable or require minor changes.

## Rollback (If Needed)

If the new rules create too many violations:

```bash
git checkout pyproject.toml .pre-commit-config.yaml
poetry lock --no-update
poetry install
```

Or, selectively disable problematic rules in `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I", "C901", "N", "A", "C4", "RUF", "LOG", "PERF"]
ignore = ["C901", "N"]  # Add rules to ignore here
```

## Verification

After completing all steps, verify:

```bash
# Check ruff version
poetry run ruff --version
# Should show 0.11.x

# Verify rules are active
poetry run ruff check . --select C901 --select N --select A
# Should show violations from new rules (or none if all fixed)

# Verify pre-commit uses same version
poetry run pre-commit run ruff --all-files --verbose
# Should match poetry run ruff check results
```
