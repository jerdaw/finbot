# Dependabot Configuration Guide

## Overview

Dependabot is now configured to automatically create pull requests for dependency updates. This helps keep the project secure and up-to-date with minimal manual effort.

## Configuration Details

**File:** `.github/dependabot.yml`

### Python Dependencies

- **Schedule:** Weekly on Monday at 9:00 AM ET
- **PR Limit:** Maximum 5 open PRs at once
- **Grouping Strategy:**
  - Minor and patch updates are grouped together (e.g., 1.2.3 → 1.2.4, 1.2.0 → 1.3.0)
  - Major updates create individual PRs (e.g., 1.x → 2.x) for careful review
- **Labels:** `dependencies`, `python`
- **Commit Prefix:** `deps`

### GitHub Actions

- **Schedule:** Weekly on Monday at 9:00 AM ET
- **PR Limit:** Maximum 3 open PRs at once
- **Monitors:** Workflow files in `.github/workflows/`
- **Labels:** `dependencies`, `github-actions`
- **Commit Prefix:** `ci`

## What to Expect

### First Week After Setup

Once this is pushed to GitHub, Dependabot will scan dependencies and likely create:
- 1-2 grouped PRs for minor/patch Python updates
- 3-5 individual PRs for major Python updates (numpy 2.x, pandas 3.0, etc.)
- 0-1 PRs for GitHub Actions updates

**Total:** ~5-8 PRs in the first week

### Ongoing Weekly Updates

After the initial wave, expect:
- 0-2 PRs per week for Python dependencies
- 0-1 PRs per week for GitHub Actions

## How to Handle Dependabot PRs

### 1. Grouped Minor/Patch Updates

These are usually safe to merge:

```bash
# Review the PR on GitHub
# Check that CI passes
# If CI passes, merge via GitHub UI
```

### 2. Major Version Updates

Require more careful review:

**For numpy 2.x:**
- Review breaking changes: https://numpy.org/doc/stable/release/2.0.0-notes.html
- Test locally before merging
- May require code changes

**For pandas 3.0:**
- Review breaking changes: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
- Test data processing utilities
- May require API updates

**For yfinance 1.x:**
- Check if data collection utilities still work
- Test `get_history()` and related functions

**Testing major updates locally:**
```bash
# Create a test branch
git checkout -b test-numpy-2

# Update poetry.lock with the new version
# (Dependabot will have done this in the PR)
git fetch origin pull/XXX/head:test-numpy-2

# Install and test
poetry install
poetry run pytest tests/

# If tests pass, merge the PR
```

### 3. GitHub Actions Updates

Usually safe to merge:
- Check that CI workflow syntax is still valid
- Ensure no breaking changes in action versions

## Reviewing Dependabot PRs

### Quick Checklist

- [ ] CI passes (green checkmark)
- [ ] Review changelog linked in PR description
- [ ] For major updates: No breaking changes that affect your code
- [ ] For security updates: Merge ASAP

### Priority Levels

**🔴 Critical (Merge ASAP):**
- Security vulnerabilities
- Critical bug fixes

**🟡 Medium (Review within a week):**
- Major version updates
- Updates with known breaking changes

**🟢 Low (Review when convenient):**
- Minor/patch updates
- Grouped dependency updates

## Configuration Changes

### Increase PR Limit

If you want more PRs per week, edit `.github/dependabot.yml`:

```yaml
open-pull-requests-limit: 10  # Increase from 5
```

### Change Schedule

To check more or less frequently:

```yaml
schedule:
  interval: "daily"  # Options: daily, weekly, monthly
```

### Disable for Specific Packages

If a package causes issues, you can ignore it:

```yaml
ignore:
  - dependency-name: "numpy"
    versions: ["2.x"]  # Ignore numpy 2.x updates
```

### Auto-merge Minor Updates

For fully automated minor updates (not recommended initially):

```yaml
auto-merge:
  - update-type: "semver:patch"
  - update-type: "semver:minor"
```

⚠️ **Warning:** Only enable auto-merge after you're confident in your test coverage.

## Troubleshooting

### Dependabot Not Creating PRs

**Check:**
1. `.github/dependabot.yml` is valid YAML
2. Repository has Dependabot enabled in Settings → Security
3. Check "Insights" → "Dependency graph" → "Dependabot" for errors

### Too Many PRs

**Solutions:**
1. Lower `open-pull-requests-limit`
2. Change schedule to monthly
3. Add problematic packages to ignore list

### PRs Conflict with Each Other

**Solution:**
Dependabot will automatically rebase PRs when needed. Just wait for it to update.

## Benefits

✅ **Security:** Automatic updates for vulnerabilities
✅ **Freshness:** Stay current with ecosystem improvements
✅ **Automation:** No manual checking for updates
✅ **Transparency:** All updates are documented in PRs
✅ **Tested:** CI runs before merge
✅ **Grouped:** Minor updates bundled to reduce noise

## Monitoring

View Dependabot activity:
- **GitHub Repository** → Insights → Dependency graph → Dependabot
- **Security tab** → View dependency security alerts
- **Pull requests tab** → Filter by label: `dependencies`

## Best Practices

1. **Review PRs promptly** - Don't let them pile up
2. **Test major updates locally** - Don't rely solely on CI
3. **Read changelogs** - Understand what's changing
4. **Keep CI comprehensive** - Your tests are your safety net
5. **Group reviews** - Review multiple dependency PRs together once a week

## Resources

- [Dependabot documentation](https://docs.github.com/en/code-security/dependabot)
- [Configuration options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Dependabot security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates)
