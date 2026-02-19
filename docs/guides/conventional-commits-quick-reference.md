# Conventional Commits Quick Reference

This guide provides a quick reference for writing conventional commit messages in the finbot project.

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Types

| Type | Use When | Example |
|------|----------|---------|
| `feat` | Adding a new feature | `feat(backtesting): add dual momentum strategy` |
| `fix` | Fixing a bug | `fix(api): handle rate limit errors` |
| `docs` | Documentation changes | `docs(readme): update installation steps` |
| `style` | Code formatting, whitespace | `style: fix trailing whitespace` |
| `refactor` | Code restructuring (no feature/bug change) | `refactor(config): migrate to dynaconf` |
| `test` | Adding or updating tests | `test(simulation): add edge case tests` |
| `chore` | Build, deps, maintenance | `chore(deps): update pandas to 2.2.0` |
| `perf` | Performance improvements | `perf(backtesting): optimize batch processing` |
| `ci` | CI/CD configuration | `ci: add commitlint to workflow` |
| `build` | Build system changes | `build: update python to 3.12` |
| `revert` | Reverting a previous commit | `revert: revert "feat: add strategy"` |

## Scopes

Common scopes in this project:

- `api` — API client code
- `cli` — Command-line interface
- `dashboard` — Streamlit dashboard
- `backtesting` — Backtesting engine
- `simulation` — Simulation services
- `optimization` — Portfolio optimizers
- `config` — Configuration
- `docs` — Documentation
- `deps` — Dependencies
- `tests` — Test suite

## Examples

### Simple Commits

```bash
# New feature
git commit -m "feat(cli): add status command"

# Bug fix
git commit -m "fix(simulation): correct fee calculation"

# Documentation
git commit -m "docs(api): improve docstring coverage"

# Dependency update
git commit -m "chore(deps): update numpy to 2.0"
```

### Commits with Body

```bash
git commit -m "fix(backtesting): correct rebalance timing logic

The previous implementation rebalanced on the wrong day due to
an off-by-one error in date indexing. This fix ensures rebalancing
occurs on the specified day of month.

Fixes #456"
```

### Breaking Changes

```bash
git commit -m "feat(api)!: change APIManager initialization

BREAKING CHANGE: APIManager now requires explicit rate_limit
parameter. Update all instantiations to include this parameter.

Migration:
- Old: APIManager()
- New: APIManager(rate_limit=10)"
```

## Rules

1. **Type**: Must be one of the allowed types (lowercase)
2. **Scope**: Optional, use parentheses: `(scope)`
3. **Subject**:
   - Max 72 characters
   - Lowercase first word
   - No period at the end
   - Imperative mood ("add" not "added")
4. **Body**: Separate from subject with blank line
5. **Footer**: Use for breaking changes and issue references

## Validation

Commits are automatically validated by the `conventional-pre-commit` hook.

### Install Hook

```bash
uv run pre-commit install --hook-type commit-msg
```

### Test a Message

```bash
# Valid - will pass
echo "feat(api): add new endpoint" > .git/COMMIT_EDITMSG
uv run pre-commit run --hook-stage commit-msg

# Invalid - will fail
echo "Add new endpoint" > .git/COMMIT_EDITMSG
uv run pre-commit run --hook-stage commit-msg
```

## Common Mistakes

❌ **Wrong:**
```
Add new feature
fixed bug
WIP
Update README
FEAT: add feature
feat:add feature (missing space)
feat(api) add endpoint (missing colon)
```

✅ **Correct:**
```
feat: add new feature
fix: resolve calculation bug
chore: work in progress
docs: update README
feat: add feature
feat: add feature
feat(api): add endpoint
```

## Configuration

- `.pre-commit-config.yaml` — Hook configuration
- `.commitlintrc.yaml` — Commit message rules
- `CONTRIBUTING.md` — Detailed guidelines

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit)
- [Why Conventional Commits?](https://www.conventionalcommits.org/en/v1.0.0/#why-use-conventional-commits)
