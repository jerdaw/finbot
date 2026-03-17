# Dependabot Configuration Guide

## Overview

Dependabot is configured to keep dependencies current while limiting notification noise. Python and GitHub Actions updates are grouped, low-risk updates can be auto-approved, and major updates remain manual.

## Configuration Details

**File:** `.github/dependabot.yml`

### Python Dependencies

- **Schedule:** Weekly on Monday at 9:00 AM ET
- **PR Limit:** Maximum 2 open PRs at once
- **Grouping Strategy:**
  - Minor and patch updates are grouped together (e.g., 1.2.3 → 1.2.4, 1.2.0 → 1.3.0)
  - Major updates are grouped separately for manual review
- **Labels:** `dependencies`, `python`
- **Commit Prefix:** `deps`

### GitHub Actions

- **Schedule:** Weekly on Monday at 9:00 AM ET
- **PR Limit:** Maximum 2 open PRs at once
- **Monitors:** Workflow files in `.github/workflows/`
- **Labels:** `dependencies`, `github-actions`
- **Commit Prefix:** `ci`
- **Grouping Strategy:**
  - Minor and patch updates are grouped together
  - Major updates are grouped separately for manual review

### Auto-Approval and Auto-Merge

- Patch and minor Dependabot PRs are auto-approved by [`dependabot-auto-merge.yml`](../.github/workflows/dependabot-auto-merge.yml).
- Fully automatic merge is only enabled when repository secret `DEPENDABOT_AUTOMERGE_PAT` is set to a human-owned token.
- Without that secret, low-risk PRs are still auto-approved but require a human merge to preserve the repository's human-only commit authorship policy.
- Major updates are labeled `major-update` and left for manual review.

### Notification Noise Controls

- Dependency-only PRs touching `uv.lock`, `pyproject.toml`, or `.github/workflows/` are intentionally excluded from CODEOWNERS review requests.
- GitHub Actions auto-approval only runs on PR open/reopen/ready-for-review events, which avoids repeated approval notifications when Dependabot pushes follow-up commits.
- Missing Dependabot labels create extra bot comments and email noise. Ensure `dependencies`, `python`, and `github-actions` labels exist in the repository.

## What to Expect

Expect up to two active version-update PRs per ecosystem:
- One grouped patch/minor PR
- One grouped major-update PR

## How to Handle Dependabot PRs

### 1. Grouped Minor/Patch Updates

These are usually safe to merge:

```bash
# Review the PR on GitHub
# Check that CI passes
# Merge manually unless DEPENDABOT_AUTOMERGE_PAT is configured
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

# Update uv.lock with the new version
# (Dependabot will have done this in the PR)
git fetch origin pull/XXX/head:test-numpy-2

# Install and test
uv sync
uv run pytest tests/

# If tests pass, merge the PR
```

### 3. GitHub Actions Updates

These now arrive as grouped patch/minor or grouped major PRs:
- Patch/minor updates are usually safe after CI passes
- Major updates still need manual review for breaking workflow changes

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
open-pull-requests-limit: 10  # Increase from the current limit of 2
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

### Enable Human-Authored Auto-Merge

To keep automated merges compliant with the repository's human-only authorship policy:

1. Create a fine-grained personal access token owned by a human maintainer with repository contents and pull request write access.
2. Save it as repository secret `DEPENDABOT_AUTOMERGE_PAT`.
3. Dependabot patch/minor PRs will then be auto-approved and auto-merged after required checks pass.

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
4. Verify GitHub Actions minor/patch updates are grouped

### Too Many Emails

**Common causes:**
1. CODEOWNERS review requests on dependency-only PRs
2. Missing labels causing Dependabot comment spam
3. Repeated workflow approvals on `synchronize` events
4. Personal GitHub/Gmail notification settings

**Repository-side fixes already in place:**
1. No catch-all CODEOWNERS owner for `uv.lock`
2. No `.github/` or `pyproject.toml` CODEOWNERS entry for dependency-only PRs
3. Existing Dependabot labels created in the repo
4. Auto-approval workflow no longer reruns on `synchronize`

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

1. **Review major updates locally** - Don't rely solely on CI
2. **Keep CI comprehensive** - Your tests are your safety net
3. **Use grouped updates** - Minimize PR churn and notification volume
4. **Use human-owned automation credentials deliberately** - Only if you want fully automatic merges without bot authorship in history
5. **Pair repo-side reduction with personal notification filters** - GitHub watch settings and Gmail filters matter too

## Resources

- [Dependabot documentation](https://docs.github.com/en/code-security/dependabot)
- [Configuration options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Dependabot security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates)
