# Contributing to Finbot

Thank you for your interest in contributing to Finbot!

## Quick Start

```bash
# Clone and setup
git clone https://github.com/jerdaw/finbot.git
cd finbot
uv sync
uv run pre-commit install

# Run tests
uv run pytest
```

## Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run checks: `make check && make test`
5. Commit with descriptive message
6. Push and create pull request

## Code Quality

```bash
make lint      # Ruff linting
make format    # Ruff formatting
make type      # Mypy type checking
make test      # Run test suite
```

## Standards

- **Python**: 3.11+
- **Line length**: 120 characters
- **Docstrings**: Google style
- **Type hints**: Required
- **Testing**: Required for new features

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. This ensures a consistent commit history and enables automated changelog generation.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**Components:**
- **type**: The kind of change (required)
- **scope**: The area of the codebase affected (optional but recommended)
- **subject**: Brief description, max 72 characters (required)
- **body**: Detailed explanation (optional)
- **footer**: Breaking changes, issue references (optional)

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(backtesting): add dual momentum strategy` |
| `fix` | Bug fix | `fix(api): handle rate limit errors in FRED client` |
| `docs` | Documentation only | `docs(readme): update installation instructions` |
| `style` | Code style/formatting | `style: fix trailing whitespace` |
| `refactor` | Code restructuring | `refactor(config): migrate to dynaconf settings` |
| `test` | Add or update tests | `test(simulation): add fund simulator edge cases` |
| `chore` | Maintenance tasks | `chore(deps): update pandas to 2.2.0` |
| `perf` | Performance improvement | `perf(backtesting): optimize batch processing` |
| `ci` | CI/CD changes | `ci: add conventional commit linting` |
| `build` | Build system changes | `build: update python version to 3.12` |
| `revert` | Revert previous commit | `revert: revert "feat: add new strategy"` |

### Scope Examples

Common scopes in this project:
- `api` — API client code
- `cli` — Command-line interface
- `dashboard` — Streamlit dashboard
- `backtesting` — Backtesting engine
- `simulation` — Simulation services
- `config` — Configuration management
- `docs` — Documentation
- `deps` — Dependencies

### Examples

**Simple feature:**
```
feat(backtesting): add risk parity strategy
```

**Bug fix with details:**
```
fix(simulation): correct leverage calculation in fund simulator

The previous calculation did not account for daily compounding
of fees when leverage > 2x. This fix applies the exponential
fee calculation as documented in the methodology.

Fixes #123
```

**Breaking change:**
```
feat(api)!: change API manager initialization signature

BREAKING CHANGE: APIManager now requires explicit rate limit
configuration instead of using defaults. Update all API manager
instantiations to include rate_limit parameter.
```

### Rules Enforced

The pre-commit hook automatically validates:
- Valid commit type from the allowed list
- Subject line ≤ 72 characters
- Proper format with colon separator
- Lowercase type

### Installation

Commit message linting is automatically installed when you run:
```bash
uv run pre-commit install --hook-type commit-msg
```

### Manual Validation

To manually check a commit message:
```bash
echo "feat(api): add new endpoint" | uv run conventional-pre-commit
```

### References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [conventional-pre-commit Hook](https://github.com/compilerla/conventional-pre-commit)

## Changelog Generation

We use [git-changelog](https://github.com/pawamoy/git-changelog) to automatically generate changelog entries from conventional commit messages.

### Generating Changelog

```bash
# Generate full changelog
make changelog

# Or use the script directly
./scripts/generate_changelog.sh

# Generate changelog for specific version range
./scripts/generate_changelog.sh v1.0.0..

# Generate to custom output file
./scripts/generate_changelog.sh -o CHANGES.md
```

### How It Works

1. **git-changelog** scans git history for commits following conventional commit format
2. Groups commits by type (feat, fix, docs, etc.)
3. Generates changelog in Keep a Changelog format
4. Outputs to `CHANGELOG_GENERATED.md`

### Workflow

1. **During development**: Write commits following conventional commit format
2. **Before release**: Run `make changelog` to generate changelog entries
3. **Review output**: Check `CHANGELOG_GENERATED.md` for accuracy
4. **Manual merge**: Copy relevant sections into `CHANGELOG.md`
5. **Edit as needed**: Add context, summaries, or additional notes

### Important Notes

- **git-changelog only recognizes conventional commits**
  - Commits without conventional prefixes (feat:, fix:, etc.) are omitted
  - Historical commits may not appear in generated changelog
- **Generated changelog is a starting point**
  - Review and edit for clarity
  - Add executive summaries for major releases
  - Group related changes for better readability
- **Keep manual changelog**
  - `CHANGELOG.md` remains the authoritative source
  - Generated output is a helper tool, not automatic replacement
  - Preserve manual formatting and additional context

### Configuration

Changelog generation is configured in `.git-changelog.toml`:
- Convention: conventional commits
- Template: keepachangelog format
- Sections: All conventional commit types
- Provider: GitHub (for issue/PR links)

See `.git-changelog.toml` for full configuration options.

## Questions?

See full documentation: [docs_site/contributing.md](docs_site/contributing.md)
