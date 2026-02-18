# Automated Release Workflow - Implementation Summary

## Overview

Automated GitHub Actions workflow for creating releases with a single git tag command. Implements **Priority 5, Item 37** from the roadmap.

## Files Created

### 1. `.github/workflows/release.yml`
**Purpose**: GitHub Actions workflow that automates the release process

**Trigger**: Push of version tags matching `v*.*.*` pattern

**Jobs**:
- **build**: Builds Python package (wheel + sdist) using `uv build`
- **release**: Creates GitHub release with:
  - Tag name as release title
  - Changelog notes extracted from CHANGELOG.md
  - Build artifacts attached (`.whl` and `.tar.gz`)
  - Automatic prerelease detection (for alpha/beta/rc tags)

**Key Features**:
- Extracts version from tag (removes 'v' prefix)
- Parses CHANGELOG.md to extract release notes for specific version
- Detects prereleases based on tag pattern (alpha/beta/rc)
- Uploads build artifacts to release
- Uses official GitHub Actions marketplace actions:
  - `actions/checkout@v4`
  - `actions/upload-artifact@v4` / `actions/download-artifact@v4`
  - `softprops/action-gh-release@v2`

### 2. `docs/guides/release-process.md`
**Purpose**: Comprehensive documentation for the release process

**Contents**:
- Prerequisites (version update, changelog update, commit changes)
- Step-by-step release instructions
- Prerelease version handling
- Rollback procedures
- Troubleshooting guide
- Version numbering guidelines (Semantic Versioning)
- Complete release checklist

### 3. `scripts/test_release_workflow.sh`
**Purpose**: Local validation script to test release workflow logic

**Tests**:
1. YAML syntax validation
2. Version extraction from tags
3. Changelog extraction for existing versions
4. Prerelease detection logic
5. Build command availability (uv)
6. Required files existence check

**Usage**: `./scripts/test_release_workflow.sh` or `make test-release`

### 4. Updated `Makefile`
**Added**:
- `make test-release` target to validate release workflow
- Added to help menu under "Release:" section

## Workflow Architecture

```
Developer                  GitHub Actions              GitHub Release
    │                            │                           │
    │─── git tag v1.1.0 ────────>│                           │
    │─── git push origin v1.1.0 ─>│                           │
    │                            │                           │
    │                            │── Build Job ───────────┐  │
    │                            │   - uv build           │  │
    │                            │   - Upload artifacts   │  │
    │                            │<───────────────────────┘  │
    │                            │                           │
    │                            │── Release Job ─────────┐  │
    │                            │   - Extract version    │  │
    │                            │   - Parse changelog    │  │
    │                            │   - Detect prerelease  │  │
    │                            │   - Create release ────┼──>│
    │                            │<───────────────────────┘  │
    │                            │                           │
    │<─────────── Release Created (v1.1.0) ─────────────────│
```

## Changelog Extraction Logic

The workflow extracts release notes from CHANGELOG.md using this pattern:

```bash
VERSION="1.0.0"
awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | sed '1d;$d'
```

This extracts all content between:
- Start: `## [1.0.0]` (the version header)
- End: The next version header `## [x.x.x]`

**Requirements**:
- CHANGELOG.md must follow [Keep a Changelog](https://keepachangelog.com/) format
- Version headers must use format: `## [1.0.0] - 2026-02-16`
- Version in header must match tag (without 'v' prefix)

## Prerelease Detection

Tags containing these keywords are automatically marked as prereleases:
- `alpha` (e.g., `v1.1.0-alpha.1`)
- `beta` (e.g., `v1.1.0-beta.2`)
- `rc` (e.g., `v1.1.0-rc.1`)

All other tags are marked as stable releases.

## Testing & Validation

### Local Testing
```bash
# Validate workflow files and logic
make test-release

# Or run script directly
./scripts/test_release_workflow.sh
```

### What's Tested
- YAML syntax validity
- Version extraction (v1.2.3 → 1.2.3)
- Changelog parsing for existing versions
- Prerelease detection patterns
- Build tool availability (uv)
- Required file existence

### Validation Output
```
=== Release Workflow Validation ===
✓ YAML syntax valid
✓ Version extraction works
✓ Found changelog entry for 1.0.0
✓ Prerelease detection works
✓ uv is available and can build
✓ All required files exist
=== Validation Complete ===
```

## Release Process (Quick Reference)

1. **Update files**:
   ```bash
   # Edit pyproject.toml (update version)
   # Edit CHANGELOG.md (add version section with date)
   git add pyproject.toml CHANGELOG.md
   git commit -m "Prepare release v1.1.0"
   git push origin main
   ```

2. **Create release**:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

3. **Monitor**: Watch workflow at https://github.com/jerdaw/finbot/actions

4. **Verify**: Check release at https://github.com/jerdaw/finbot/releases

## Example Release

Given this CHANGELOG.md:
```markdown
## [1.1.0] - 2026-02-16

### Added
- Automated release workflow

### Changed
- Updated documentation
```

And this command:
```bash
git tag v1.1.0 && git push origin v1.1.0
```

Creates a GitHub release with:
- **Title**: "Release v1.1.0"
- **Body**: Extracted changelog content
- **Artifacts**: `finbot-1.1.0-py3-none-any.whl`, `finbot-1.1.0.tar.gz`
- **Status**: Stable release (not prerelease)

## Permissions

The workflow requires `contents: write` permission to create releases. This is granted via:

```yaml
permissions:
  contents: write
```

The `GITHUB_TOKEN` is automatically provided by GitHub Actions.

## Dependencies

**GitHub Actions**:
- `actions/checkout@v4` - Check out repository code
- `actions/upload-artifact@v4` - Upload build artifacts between jobs
- `actions/download-artifact@v4` - Download artifacts in release job
- `softprops/action-gh-release@v2` - Create GitHub release

**Build Tools**:
- `uv` - Python package manager (installed via `astral-sh/setup-uv@v6`)
- Python 3.13 (for building)

## Troubleshooting

### Build Fails
**Symptom**: Build job fails during `uv build`

**Solutions**:
- Test locally: `uv build`
- Check pyproject.toml for syntax errors
- Ensure all required files are committed

### Changelog Not Found
**Symptom**: Release notes say "No changelog entry found"

**Solutions**:
- Verify CHANGELOG.md has section like `## [1.1.0] - 2026-02-16`
- Ensure version matches tag (without 'v')
- Check that version section is properly formatted

### Release Creation Fails
**Symptom**: Release job fails when creating release

**Common Causes**:
- Insufficient permissions (need `contents: write`)
- Artifacts not uploaded from build job
- Tag already exists with a release

**Solutions**:
- Check workflow logs for specific error
- Verify build job completed successfully
- Delete existing release if recreating

### Tag Already Exists
**Symptom**: Cannot push tag, already exists

**Solutions**:
```bash
# Delete local tag
git tag -d v1.1.0

# Delete remote tag
git push origin :refs/tags/v1.1.0

# Recreate and push
git tag v1.1.0
git push origin v1.1.0
```

## Future Enhancements

Potential improvements for future iterations:

1. **PyPI Publishing**: Add job to publish to PyPI/TestPyPI
2. **Docker Image**: Build and push Docker image on release
3. **Documentation**: Deploy docs to GitHub Pages on release
4. **Notifications**: Post release announcement to Slack/Discord
5. **Checksums**: Generate SHA256 checksums for artifacts
6. **GPG Signing**: Sign releases with GPG key
7. **Release Notes**: Generate from commits if CHANGELOG missing
8. **Semantic Release**: Auto-increment version based on commit messages

## References

- GitHub Actions Workflow: `.github/workflows/release.yml`
- Release Process Guide: `docs/guides/release-process.md`
- Test Script: `scripts/test_release_workflow.sh`
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- GitHub Actions Docs: https://docs.github.com/en/actions
