# Changelog Generation Guide

This guide explains how to automatically generate changelog entries from git commit history using conventional commits.

## Overview

Finbot uses [git-changelog](https://github.com/pawamoy/git-changelog) to automatically generate changelog entries from commit messages that follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Key Points:**
- Changelog generation is **semi-automated** - it generates entries that you review and manually merge
- Only commits following conventional commit format are included
- The generated changelog is a starting point, not a replacement for manual curation
- `CHANGELOG.md` remains the authoritative source

## Quick Start

```bash
# Generate changelog from all git history
make changelog

# Review the generated output
less CHANGELOG_GENERATED.md

# Manually merge relevant sections into CHANGELOG.md
# (edit CHANGELOG.md to incorporate the generated entries)
```

## How It Works

### 1. Conventional Commits

git-changelog scans git history for commits following this format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Example:**
```
feat(backtesting): add dual momentum strategy

Implements relative and absolute momentum with safe-asset fallback.
Uses 12-month lookback period and monthly rebalancing.

Closes #123
```

### 2. Commit Types

Commits are grouped by type in the generated changelog:

| Type | Changelog Section | Description |
|------|------------------|-------------|
| `feat` | Features | New features |
| `fix` | Bug Fixes | Bug fixes |
| `refactor` | Code Refactoring | Code restructuring |
| `perf` | Performance Improvements | Performance optimizations |
| `docs` | Documentation | Documentation changes |
| `test` | Tests | Test additions/updates |
| `build` | Build System | Build system changes |
| `ci` | Continuous Integration | CI/CD changes |
| `chore` | Chore | Maintenance tasks |
| `style` | Style | Code style/formatting |
| `revert` | Reverts | Reverted commits |

### 3. Version Detection

git-changelog uses git tags to determine versions:
- Each git tag (e.g., `v1.0.0`) defines a version
- Commits between tags are grouped under the newer version
- Commits since the last tag are grouped as "Unreleased"

## Usage

### Basic Usage

```bash
# Generate full changelog (all versions)
make changelog

# Or use the script directly
./scripts/generate_changelog.sh
```

This creates `CHANGELOG_GENERATED.md` with all versions from git history.

### Generate for Specific Range

```bash
# Generate changelog since v1.0.0
./scripts/generate_changelog.sh v1.0.0..

# Generate changelog for last 20 commits
./scripts/generate_changelog.sh HEAD~20..
```

### Custom Output File

```bash
# Generate to custom file
./scripts/generate_changelog.sh -o CHANGES.md
```

### Script Help

```bash
./scripts/generate_changelog.sh --help
```

## Workflow for Releases

### Before a Release

1. **Review recent commits:**
   ```bash
   git log --oneline v1.0.0..HEAD
   ```

2. **Generate changelog entries:**
   ```bash
   make changelog
   ```

3. **Review generated changelog:**
   ```bash
   less CHANGELOG_GENERATED.md
   ```

4. **Manual merge:**
   - Open `CHANGELOG.md` in your editor
   - Copy relevant sections from `CHANGELOG_GENERATED.md`
   - Edit for clarity and readability
   - Add context or summaries as needed
   - Group related changes

5. **Clean up:**
   ```bash
   rm CHANGELOG_GENERATED.md  # (auto-ignored by git)
   ```

6. **Commit changelog:**
   ```bash
   git add CHANGELOG.md
   git commit -m "docs(changelog): update for v1.1.0 release"
   ```

### Example Manual Merge

**Generated entry:**
```markdown
### Features

- add dual momentum strategy ([abc123])
- add risk parity rebalancing ([def456])
```

**After manual editing:**
```markdown
### Added
- **Dual Momentum Strategy**: Relative and absolute momentum with safe-asset fallback
  - 12-month lookback period with monthly rebalancing
  - Automatically switches to treasury bonds during drawdowns
- **Risk Parity Rebalancing**: Inverse-volatility portfolio weighting
  - Quarterly rebalance schedule
  - Volatility calculated over trailing 60-day window
```

## Configuration

Configuration is in `.git-changelog.toml`:

```toml
# Commit convention
convention = "conventional"

# Output template
template = "keepachangelog"

# Include all conventional commit sections
sections = ":all:"

# Omit versions with no conventional commits
omit_empty_versions = true

# Parse GitHub issue/PR references
parse_refs = true
provider = "github"
```

### Available Options

- **convention**: `conventional`, `angular`, or `basic`
- **template**: `keepachangelog`, `angular`, or custom Jinja2 template
- **sections**: `:all:` or comma-separated list (e.g., `"feat,fix,docs"`)
- **include_all**: Include non-conventional commits in "Misc" section
- **omit_empty_versions**: Skip versions with no commits
- **parse_refs**: Parse `#123` as GitHub issue links

See [git-changelog documentation](https://pawamoy.github.io/git-changelog/) for all options.

## Important Notes

### Conventional Commits Required

**git-changelog only recognizes conventional commits.**

Non-conventional commits are omitted:

```bash
# This commit WILL appear in changelog
git commit -m "feat(api): add new FRED endpoint"

# This commit will NOT appear in changelog
git commit -m "Add new FRED endpoint"
```

### Historical Commits

Most commits before Priority 5 Item 36 (conventional commits adoption) don't follow conventional format and won't appear in the generated changelog.

**Solutions:**
1. **Accept it**: Focus on future releases using conventional commits
2. **Manual entries**: Add historical changes manually to `CHANGELOG.md`
3. **One-time import**: Review git history and manually write entries for past versions

### Generated vs Manual Changelog

**Generated changelog is a helper tool, not a replacement:**

| Aspect | Generated | Manual |
|--------|-----------|--------|
| **Source** | Git commit messages | Human-written |
| **Format** | Consistent, flat list | Rich, contextualized |
| **Content** | All conventional commits | Curated, grouped changes |
| **Audience** | Developers | End users |
| **Detail** | Technical commit messages | High-level summaries |

**Best practice:** Use generated changelog as a checklist, then write human-readable entries.

## Troubleshooting

### No entries in generated changelog

**Cause:** No commits follow conventional format.

**Solution:**
1. Check recent commits: `git log --oneline`
2. Verify conventional format (e.g., `feat:`, `fix:`)
3. Use `--include-all` flag to see all commits:
   ```bash
   uv run git-changelog --config-file .git-changelog.toml --include-all -o test.md
   ```

### Wrong version detected

**Cause:** git-changelog uses git tags to detect versions.

**Solution:**
1. Check tags: `git tag -l`
2. Ensure tags follow semver (v1.0.0, v0.1.0, etc.)
3. Use `--filter-commits` to limit range

### Duplicate entries

**Cause:** Running changelog generation multiple times without cleaning up.

**Solution:**
- `CHANGELOG_GENERATED.md` is regenerated each time (overwrites previous)
- Don't commit `CHANGELOG_GENERATED.md` (it's gitignored)
- Merge to `CHANGELOG.md` only once

## Integration with Release Workflow

The release workflow (`.github/workflows/release.yml`) extracts release notes from `CHANGELOG.md`, not the generated file.

**Release workflow:**
1. Developer updates `CHANGELOG.md` (using generated entries as input)
2. Developer creates git tag (e.g., `git tag v1.1.0`)
3. Developer pushes tag (`git push origin v1.1.0`)
4. GitHub Actions release workflow runs
5. Workflow extracts changelog section for that version from `CHANGELOG.md`
6. Creates GitHub release with extracted notes

**No automation needed** - the workflow reads from the manually-curated `CHANGELOG.md`.

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [git-changelog Documentation](https://pawamoy.github.io/git-changelog/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Finbot Contributing Guide](../../CONTRIBUTING.md) - Conventional commit guidelines
- [Finbot Roadmap Process](../planning/roadmap-process.md) - Release process

## See Also

- `CONTRIBUTING.md` - Commit message guidelines
- `.git-changelog.toml` - Changelog generation configuration
- `scripts/generate_changelog.sh` - Changelog generation script
- `.github/workflows/release.yml` - Release automation workflow
