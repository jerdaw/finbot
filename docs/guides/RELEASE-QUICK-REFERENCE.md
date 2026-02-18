# Release Quick Reference

**One-page cheat sheet for creating releases**

## TL;DR

```bash
# 1. Update version and changelog
vim pyproject.toml CHANGELOG.md

# 2. Test, commit, push
make test-release
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare release v1.1.0"
git push origin main

# 3. Create release
git tag v1.1.0 && git push origin v1.1.0
```

## Files to Update

### pyproject.toml
```toml
[project]
version = "1.1.0"  # ← Update this
```

### CHANGELOG.md
```markdown
## [1.1.0] - 2026-02-16  # ← Add this section

### Added
- New features

### Changed
- Modifications

### Fixed
- Bug fixes

---

## [1.0.0] - 2026-02-11
[Previous content...]

---

[Unreleased]: https://github.com/jerdaw/finbot/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/jerdaw/finbot/compare/v1.0.0...v1.1.0  # ← Add this
[1.0.0]: https://github.com/jerdaw/finbot/compare/v0.1.0...v1.0.0
```

## Commands

| Task | Command |
|------|---------|
| Validate workflow | `make test-release` |
| Run tests | `make test` |
| Check code quality | `make check` |
| Commit changes | `git add . && git commit -m "Prepare release vX.Y.Z"` |
| Create tag | `git tag vX.Y.Z` |
| Push tag | `git push origin vX.Y.Z` |
| Delete local tag | `git tag -d vX.Y.Z` |
| Delete remote tag | `git push origin :refs/tags/vX.Y.Z` |

## Version Numbering

| Type | Pattern | Example |
|------|---------|---------|
| Stable | `vMAJOR.MINOR.PATCH` | `v1.2.3` |
| Beta | `vMAJOR.MINOR.PATCH-beta.N` | `v1.2.0-beta.1` |
| Alpha | `vMAJOR.MINOR.PATCH-alpha.N` | `v2.0.0-alpha.1` |
| RC | `vMAJOR.MINOR.PATCH-rc.N` | `v1.0.0-rc.2` |

## Checklist

- [ ] Update `pyproject.toml` version
- [ ] Add version section to `CHANGELOG.md`
- [ ] Update version links in `CHANGELOG.md`
- [ ] Run `make test-release`
- [ ] Run `make test`
- [ ] Run `make check`
- [ ] Commit changes
- [ ] Push to main
- [ ] Create and push tag
- [ ] Monitor GitHub Actions
- [ ] Verify release on GitHub

## Monitoring

| Resource | URL |
|----------|-----|
| Actions | https://github.com/jerdaw/finbot/actions |
| Releases | https://github.com/jerdaw/finbot/releases |
| Tags | https://github.com/jerdaw/finbot/tags |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Test locally: `uv build` |
| Changelog not found | Check format: `## [X.Y.Z] - YYYY-MM-DD` |
| Tag exists | Delete: `git tag -d vX.Y.Z && git push origin :refs/tags/vX.Y.Z` |
| Workflow fails | Check logs at https://github.com/jerdaw/finbot/actions |

## What Gets Created

A GitHub release contains:

- **Title**: "Release v1.1.0"
- **Notes**: Extracted from CHANGELOG.md
- **Artifacts**:
  - `finbot-1.1.0-py3-none-any.whl`
  - `finbot-1.1.0.tar.gz`
- **Status**: Stable (or Prerelease if alpha/beta/rc)

## Help

| Resource | Location |
|----------|----------|
| Full guide | `docs/guides/release-process.md` |
| Examples | `docs/guides/release-example.md` |
| Implementation | `docs/guides/release-workflow-summary.md` |
| Workflow | `.github/workflows/release.yml` |

## Support

If something goes wrong:

1. Check workflow logs: https://github.com/jerdaw/finbot/actions
2. Run local validation: `make test-release`
3. Review documentation: `docs/guides/release-process.md`
4. Check existing releases for examples: https://github.com/jerdaw/finbot/releases
