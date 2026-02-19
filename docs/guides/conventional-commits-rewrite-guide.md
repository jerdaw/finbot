# Conventional Commits History Rewrite Guide

**Created:** 2026-02-17
**Priority:** Priority 7, Item P7.4
**Risk:** Medium (force-push required)

This guide walks you through rewriting recent git history to use conventional commit format, enabling proper changelog generation.

---

## Why Conventional Commits?

The project uses `conventional-pre-commit` to enforce conventional commits going forward. However, older commits (before this enforcement was added) don't follow the format. Rewriting them enables:

- `make changelog` to generate accurate changelogs
- Clean, machine-readable history
- Better pull request titles and release notes

---

## Before You Start

**This is a destructive operation.** Create a backup first:

```bash
# Create a backup branch (save your current state)
git branch main-backup-pre-rebase-$(date +%Y%m%d)

# Verify backup exists
git branch | grep backup
```

**Check how many commits need rewriting:**

```bash
# Count commits since v1.0.0 tag
git log v1.0.0..HEAD --oneline | wc -l

# View them
git log v1.0.0..HEAD --oneline
```

---

## Conventional Commit Format

Each commit message should follow:

```
type(scope): short description

Optional longer body.
```

**Types:**
| Type | When to use |
|------|-------------|
| `feat` | New feature added |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Maintenance, dependency updates, CI |
| `perf` | Performance improvement |
| `style` | Formatting, missing semicolons, etc. |
| `ci` | CI/CD changes |

**Scopes (for this project):**
- `backtesting`, `simulation`, `contracts`, `execution`
- `cli`, `dashboard`, `api`, `config`
- `docs`, `tests`, `ci`, `deps`

**Examples:**
```
feat(backtesting): add regime-adaptive strategy
fix(simulation): correct LIBOR approximation formula
docs(api): add health economics methodology reference
test(contracts): add schema versioning round-trip tests
chore(deps): update ruff to v0.11.0
ci(workflows): pin all GitHub Actions to SHA hashes
```

---

## Step-by-Step Rewrite

### Step 1: Start interactive rebase

```bash
# Rebase from v1.0.0 tag (or use number of commits)
git rebase -i v1.0.0

# Alternative: rebase last N commits
git rebase -i HEAD~50
```

This opens your editor with a list of commits.

### Step 2: Mark commits to edit

In the editor, change `pick` to `reword` for commits you want to rename:

```
reword abc1234 Update roadmap and documentation
reword def5678 Add performance benchmarks
pick   ghi9012 Fix typo in README
```

Save and close the editor.

### Step 3: Rewrite each message

For each `reword` commit, git opens your editor. Change the message:

**Before:**
```
Add performance benchmarks
```

**After:**
```
test(performance): add fund simulator and backtest benchmarks
```

Save and close for each commit.

### Step 4: Verify the result

```bash
# Check last 20 commits look right
git log --oneline -20

# Verify conventional commit format
git log --pretty=format:"%s" -20 | head -20
```

### Step 5: Push (with backup safety)

```bash
# Force push (only safe because this is a solo project)
git push --force-with-lease origin main

# Verify remote is updated
git log origin/main --oneline -5
```

---

## Commit Message Reference

Below is a suggested mapping for common recent commit types in this project:

| Old style | New conventional style |
|-----------|------------------------|
| `Update roadmap` | `docs(roadmap): update Priority 5/6 completion status` |
| `Add integration tests` | `test(integration): add end-to-end tests for backtesting and CLI` |
| `Pin GitHub Actions to SHA hashes` | `ci(security): pin all GitHub Actions to SHA hashes` |
| `Add CODEOWNERS file` | `chore(governance): add .github/CODEOWNERS for automatic review requests` |
| `Fix mypy errors in...` | `fix(types): resolve mypy errors in <module>` |
| `Add property-based testing` | `test(property): add Hypothesis tests for finance utilities` |
| `Create audit logging infrastructure` | `feat(audit): add structured audit logging with JSON output` |
| `Add performance regression testing` | `ci(performance): add benchmark runner with 20% regression threshold` |
| `Add walk-forward analysis` | `feat(backtesting): add walk-forward testing and regime detection` |

---

## After the Rewrite

1. **Test changelog generation:**
   ```bash
   make changelog
   cat CHANGELOG_GENERATED.md | head -50
   ```

2. **Update CHANGELOG.md** if the generated output looks good

3. **Inform any collaborators** (if any) that history was rewritten

---

## If Something Goes Wrong

Restore from backup:

```bash
# Check backup branch exists
git branch | grep backup

# Restore
git checkout main-backup-pre-rebase-YYYYMMDD
git checkout -b main-recovered
git push --force-with-lease origin main-recovered

# Or just reset main to backup
git checkout main
git reset --hard main-backup-pre-rebase-YYYYMMDD
git push --force-with-lease origin main
```

---

## Note on Commit Authorship Policy

Per CLAUDE.md commit policy: commits must list only **human authors**. Do not add:
- `Co-Authored-By: <non-human entity> ...`
- `AI-Assisted: ...`

All conventional commit rewrites should be attributed to you as the human author.

---

**Status:** Guide created — user action required to execute rewrite.
