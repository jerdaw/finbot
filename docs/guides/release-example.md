# Release Workflow Example

This document shows a complete example of creating a release using the automated workflow.

## Scenario

We want to release version 1.1.0 with new automated release features.

## Step 1: Update Version

Edit `pyproject.toml`:

```diff
[project]
name = "finbot"
-version = "1.0.0"
+version = "1.1.0"
description = "Financial data collection, simulation, and backtesting platform"
```

## Step 2: Update Changelog

Edit `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Future features go here

## [1.1.0] - 2026-02-16

### Added
- Automated GitHub release workflow (Priority 5 Item 37)
- Release process documentation with comprehensive guides
- Local release validation script (`scripts/test_release_workflow.sh`)
- `make test-release` target for workflow validation

### Changed
- Updated Makefile with release validation target

### Infrastructure
- GitHub Actions workflow for automated releases on version tags
- Automatic changelog extraction and release note generation
- Build artifact publishing (wheel + source distribution)

## [1.0.0] - 2026-02-11

[Previous content...]
```

Update version links at bottom:

```diff
-[Unreleased]: https://github.com/jerdaw/finbot/compare/v1.0.0...HEAD
+[Unreleased]: https://github.com/jerdaw/finbot/compare/v1.1.0...HEAD
+[1.1.0]: https://github.com/jerdaw/finbot/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jerdaw/finbot/compare/v0.1.0...v1.0.0
```

## Step 3: Validate Changes

```bash
# Test that everything works
make test-release

# Run full test suite
make test

# Run code quality checks
make check
```

Expected output:

```
=== Release Workflow Validation ===
✓ YAML syntax valid
✓ Version extraction works
✓ Found changelog entry for 1.1.0
✓ Prerelease detection works
✓ uv is available and can build
✓ All required files exist
=== Validation Complete ===
```

## Step 4: Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare release v1.1.0"
git push origin main
```

## Step 5: Create and Push Tag

```bash
# Create annotated tag (recommended)
git tag -a v1.1.0 -m "Release v1.1.0: Automated release workflow"

# Or lightweight tag
git tag v1.1.0

# Push tag to trigger workflow
git push origin v1.1.0
```

## Step 6: Monitor Workflow

Navigate to: https://github.com/jerdaw/finbot/actions

You'll see a workflow run with two jobs:

```
Release (v1.1.0)
├── Build Distribution
│   ├── Checkout code
│   ├── Install uv
│   ├── Set up Python
│   ├── Install dependencies
│   ├── Build package
│   └── Upload build artifacts
└── Create GitHub Release (needs: build)
    ├── Checkout code
    ├── Download build artifacts
    ├── Extract version from tag
    ├── Extract changelog for version
    ├── Determine if prerelease
    └── Create GitHub Release
```

## Step 7: Verify Release

Once the workflow completes, visit: https://github.com/jerdaw/finbot/releases

You should see:

```
v1.1.0
Release v1.1.0

Added
• Automated GitHub release workflow (Priority 5 Item 37)
• Release process documentation with comprehensive guides
• Local release validation script (scripts/test_release_workflow.sh)
• make test-release target for workflow validation

Changed
• Updated Makefile with release validation target

Infrastructure
• GitHub Actions workflow for automated releases on version tags
• Automatic changelog extraction and release note generation
• Build artifact publishing (wheel + source distribution)

Assets
📦 finbot-1.1.0-py3-none-any.whl (123 KB)
📦 finbot-1.1.0.tar.gz (456 KB)
```

## Prerelease Example

For a beta release:

```bash
# Update version to 1.2.0-beta.1 in pyproject.toml
# Add changelog entry for [1.2.0-beta.1]
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare beta release v1.2.0-beta.1"
git push origin main

# Create and push tag
git tag v1.2.0-beta.1
git push origin v1.2.0-beta.1
```

The workflow automatically detects "beta" in the tag and marks it as a prerelease:

```
v1.2.0-beta.1  [Pre-release]
Release v1.2.0-beta.1
[Release notes...]
```

## Hotfix Release Example

For a patch release (bugfix):

```bash
# Update version to 1.0.1 in pyproject.toml
# Add changelog entry for [1.0.1] with "Fixed" section
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare hotfix release v1.0.1"
git push origin main

git tag v1.0.1
git push origin v1.0.1
```

## Troubleshooting Example

### Build Fails Due to Missing Files

**Symptom**: Build job fails with "file not found"

**Solution**:
```bash
# Test build locally first
uv build

# Check what would be included
uv build --list

# Fix any missing files, commit, delete tag, retry
git add missing_file.py
git commit -m "Add missing file for release"
git push origin main

git tag -d v1.1.0
git push origin :refs/tags/v1.1.0
git tag v1.1.0
git push origin v1.1.0
```

### Changelog Section Missing

**Symptom**: Release notes show "No changelog entry found for version 1.1.0"

**Solution**:
```bash
# Verify changelog format
grep "## \[1.1.0\]" CHANGELOG.md

# Should output: ## [1.1.0] - 2026-02-16
# If not found, add the section and amend

git add CHANGELOG.md
git commit --amend -m "Prepare release v1.1.0"
git push origin main --force

# Delete and recreate tag
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0
git tag v1.1.0
git push origin v1.1.0
```

## Complete Script Example

Here's a complete script to automate the release process:

```bash
#!/bin/bash
# scripts/create_release.sh - Automated release helper
# Usage: ./scripts/create_release.sh 1.1.0

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.1.0"
    exit 1
fi

echo "Creating release v$VERSION..."

# 1. Update version in pyproject.toml
sed -i "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
echo "✓ Updated pyproject.toml"

# 2. Validate release workflow
make test-release
echo "✓ Workflow validated"

# 3. Run tests
make test
echo "✓ Tests passed"

# 4. Show changelog preview
echo ""
echo "Changelog preview for v$VERSION:"
awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | sed '1d;$d' | head -20

echo ""
echo "Next steps:"
echo "  1. Review and update CHANGELOG.md if needed"
echo "  2. git add pyproject.toml CHANGELOG.md"
echo "  3. git commit -m 'Prepare release v$VERSION'"
echo "  4. git push origin main"
echo "  5. git tag v$VERSION && git push origin v$VERSION"
```

Make it executable:
```bash
chmod +x scripts/create_release.sh
```

Use it:
```bash
./scripts/create_release.sh 1.1.0
```

## Summary

The automated release workflow makes releasing as simple as:

```bash
# One-time setup: Update version and changelog
vim pyproject.toml CHANGELOG.md
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare release vX.Y.Z"
git push origin main

# Create release with one command
git tag vX.Y.Z && git push origin vX.Y.Z
```

Then sit back and watch GitHub Actions do the rest:
1. Build the package
2. Extract release notes from changelog
3. Create GitHub release
4. Upload build artifacts

All in under 2 minutes!
