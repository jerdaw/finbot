# Release Process

This document describes how to create a new release of finbot.

## Overview

The release process is automated via GitHub Actions. When you push a version tag (e.g., `v1.1.0`), the workflow will:

1. Build the Python package (wheel + source distribution)
2. Extract release notes from CHANGELOG.md
3. Create a GitHub release
4. Upload build artifacts to the release

## Prerequisites

Before creating a release:

1. **Update version number** in `pyproject.toml`:
   ```toml
   [project]
   version = "1.1.0"
   ```

2. **Update CHANGELOG.md**:
   - Add a new version section following [Keep a Changelog](https://keepachangelog.com/) format
   - Move unreleased changes to the new version section
   - Add the release date
   - Example:
     ```markdown
     ## [1.1.0] - 2026-02-16

     ### Added
     - Automated release workflow

     ### Changed
     - Updated documentation

     ### Fixed
     - Bug fixes
     ```

3. **Update version comparison links** at the bottom of CHANGELOG.md:
   ```markdown
   [Unreleased]: https://github.com/jerdaw/finbot/compare/v1.1.0...HEAD
   [1.1.0]: https://github.com/jerdaw/finbot/compare/v1.0.0...v1.1.0
   ```

4. **Commit changes**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Prepare release v1.1.0"
   git push origin main
   ```

## Creating a Release

Once all changes are committed and pushed to main:

```bash
# Create and push a version tag
git tag v1.1.0
git push origin v1.1.0
```

The GitHub Actions workflow will automatically:
- Build the package using `uv build`
- Extract changelog notes for version 1.1.0 from CHANGELOG.md
- Create a GitHub release with the tag name as the title
- Upload `finbot-1.1.0-py3-none-any.whl` and `finbot-1.1.0.tar.gz`
- Mark as prerelease if tag contains "alpha", "beta", or "rc"

## Monitoring the Release

1. Navigate to the [Actions tab](https://github.com/jerdaw/finbot/actions) on GitHub
2. Click on the "Release" workflow run
3. Monitor the build and release jobs
4. Once complete, verify the release at https://github.com/jerdaw/finbot/releases

## Prerelease Versions

For alpha, beta, or release candidate versions, include the identifier in the tag:

```bash
git tag v1.1.0-beta.1
git push origin v1.1.0-beta.1
```

The workflow will automatically mark releases with `alpha`, `beta`, or `rc` in the tag as prereleases.

## Rollback

If you need to delete a release:

```bash
# Delete the tag locally
git tag -d v1.1.0

# Delete the tag remotely
git push origin :refs/tags/v1.1.0

# Manually delete the GitHub release via the web UI
```

Then you can re-tag and push again.

## Troubleshooting

### Build Fails

If `uv build` fails:
1. Check that `pyproject.toml` is valid
2. Ensure all required files are committed
3. Test locally: `uv build`

### Changelog Extraction Fails

If no changelog entry is found:
1. Verify CHANGELOG.md has a section like `## [1.1.0] - 2026-02-16`
2. The version number must match the tag (without the 'v' prefix)
3. The release will still be created, but notes will say "No changelog entry found"

### Release Creation Fails

Check the workflow logs for the specific error. Common issues:
- Insufficient permissions (GITHUB_TOKEN should have `contents: write`)
- Artifacts not found (build job must complete successfully)
- Tag format doesn't match `v*.*.*` pattern

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (v2.0.0): Incompatible API changes
- **Minor** (v1.1.0): New functionality, backward compatible
- **Patch** (v1.0.1): Backward compatible bug fixes
- **Prerelease** (v1.1.0-beta.1): Testing/preview versions

## Testing Before Release (Recommended)

Before creating a production release, test the package on TestPyPI:

1. **Publish to TestPyPI** (see [Publishing to TestPyPI](publishing-to-testpypi.md) for detailed instructions):
   ```bash
   # Trigger the TestPyPI workflow manually or push a test tag
   git tag test-v1.1.0
   git push origin test-v1.1.0
   ```

2. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ \
               --extra-index-url https://pypi.org/simple/ \
               finbot==1.1.0
   ```

3. **Verify package functionality**:
   ```bash
   finbot --version
   finbot status
   ```

See the [TestPyPI Quick Reference](testpypi-quick-reference.md) for common commands.

## Release Checklist

- [ ] Update `pyproject.toml` version
- [ ] Update CHANGELOG.md with version and date
- [ ] Update version comparison links in CHANGELOG.md
- [ ] Run full test suite: `uv run pytest tests/`
- [ ] Run linter: `uv run ruff check .`
- [ ] Run formatter: `uv run ruff format .`
- [ ] **(Recommended)** Test on TestPyPI first
- [ ] Commit and push changes
- [ ] Create and push tag: `git tag v1.1.0 && git push origin v1.1.0`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify release on GitHub
- [ ] Test installation from release artifacts (optional)
