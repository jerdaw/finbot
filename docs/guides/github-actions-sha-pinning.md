# GitHub Actions SHA Pinning Guide

**Created:** 2026-02-17
**Status:** Active
**Category:** Security, CI/CD

## Overview

All GitHub Actions in this repository are pinned to specific SHA hashes rather than version tags. This is a security best practice that prevents potential supply chain attacks where action versions could be maliciously updated.

## Why SHA Pinning?

### Security Benefits

1. **Immutability**: SHA hashes cannot be changed, while tags (like `v4`) can be moved to point to different commits
2. **Supply Chain Protection**: Prevents attackers from hijacking popular action repositories and updating tags to malicious code
3. **Reproducibility**: Ensures the exact same action code runs every time, not just "version 4"
4. **Audit Trail**: Makes it clear exactly which code version is being executed

### OpenSSF Scorecard Requirement

SHA pinning is one of the checks performed by [OpenSSF Scorecard](https://github.com/ossf/scorecard), a security tool that assesses open source project risk. Pinning actions improves the "Pinned-Dependencies" score.

## Current SHA Pins

All workflow files (`.github/workflows/*.yml`) use SHA-pinned actions with version comments:

```yaml
# Format: uses: owner/repo@<SHA> # <version>

# Example from ci.yml:
- name: Checkout code
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6

- name: Install uv
  uses: astral-sh/setup-uv@d0d8abe699bfb85fec6de9f7adb5ae17292296ff # v6
```

### Pinned Actions

| Action | Version | SHA (first 8 chars) |
|--------|---------|---------------------|
| `actions/checkout` | v6 | `de0fac2e` |
| `actions/checkout` | v4 | `34e11487` |
| `astral-sh/setup-uv` | v6 | `d0d8abe6` |
| `codecov/codecov-action` | v5 | `671740ac` |
| `actions/upload-artifact` | v4 | `ea165f8d` |
| `actions/download-artifact` | v4 | `d3f86a10` |
| `aquasecurity/trivy-action` | 0.29.0 | `18f2510e` |
| `github/codeql-action/upload-sarif` | v3 | `60d8f0d1` |
| `softprops/action-gh-release` | v2 | `a06a81a0` |
| `ossf/scorecard-action` | v2.4.0 | `ff5dd892` |

## Updating Actions

When you want to update an action to a newer version:

### 1. Find the New Version SHA

```bash
# Get SHA for a specific tag
git ls-remote https://github.com/actions/checkout.git refs/tags/v7

# Output example:
# abc123def456... refs/tags/v7
```

### 2. Update the Workflow File

Replace both the SHA and the version comment:

```yaml
# Old (v6):
uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6

# New (v7):
uses: actions/checkout@abc123def456... # v7
```

### 3. Test the Change

```bash
# Commit and push to trigger CI
git add .github/workflows/
git commit -m "chore: update actions/checkout from v6 to v7"
git push

# Watch the workflow run in GitHub Actions tab
```

### 4. Update This Documentation

Add the new version to the "Pinned Actions" table above.

## Automated Monitoring (Future)

Consider using:
- [Dependabot](https://docs.github.com/en/code-security/dependabot) for GitHub Actions updates
- [Renovate](https://github.com/renovatebot/renovate) for automated PR creation

**Note:** Dependabot can update SHA-pinned actions while preserving the security benefits. Configure in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    # Dependabot will update to new SHAs when new versions are released
```

## Verifying Pinned Actions

Use this bash script to verify all actions are properly pinned:

```bash
#!/bin/bash
# Check all workflow files for unpinned actions

echo "Checking for unpinned GitHub Actions..."
echo ""

unpinned=0

for file in .github/workflows/*.yml; do
    echo "Checking $file..."

    # Find uses: lines that don't have SHA (40 hex chars)
    if grep -n "uses:" "$file" | grep -v "@[a-f0-9]\{40\}"; then
        echo "  ❌ Found unpinned action(s)"
        grep -n "uses:" "$file" | grep -v "@[a-f0-9]\{40\}"
        unpinned=1
    else
        echo "  ✅ All actions properly pinned"
    fi
    echo ""
done

if [ $unpinned -eq 0 ]; then
    echo "✅ All GitHub Actions are properly pinned to SHA hashes"
    exit 0
else
    echo "❌ Some actions are not pinned to SHA hashes"
    exit 1
fi
```

Save as `scripts/verify_action_pins.sh` and run before committing workflow changes.

## Resources

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [OpenSSF Scorecard - Pinned Dependencies](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies)
- [Supply Chain Security Best Practices](https://slsa.dev/)

## History

- **2026-02-17**: Initial SHA pinning across all 5 workflow files
  - `ci.yml`: 6 actions pinned (checkout, setup-uv, codecov, upload-artifact, trivy, codeql)
  - `docs.yml`: 2 actions pinned (checkout, setup-uv)
  - `release.yml`: 5 actions pinned (checkout, setup-uv, upload-artifact, download-artifact, action-gh-release)
  - `publish-testpypi.yml`: 3 actions pinned (checkout, setup-uv, upload-artifact)
  - `scorecard.yml`: 4 actions pinned (checkout, scorecard-action, upload-artifact, codeql)
