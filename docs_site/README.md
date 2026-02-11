# Finbot Documentation Site

This directory contains the source files for Finbot's MkDocs documentation site.

## Structure

```
docs_site/
├── index.md                    # Home page
├── user-guide/                 # User documentation
│   ├── getting-started.md      # Installation and first steps
│   ├── installation.md         # Detailed installation instructions
│   ├── quick-start.md          # 5-minute quick start
│   ├── cli-reference.md        # CLI command reference
│   └── configuration.md        # Configuration guide
├── api/                        # API reference documentation
│   ├── index.md                # API overview
│   ├── services/               # Core services
│   │   ├── backtesting/        # Backtesting engine
│   │   ├── simulation/         # Simulators
│   │   └── optimization/       # Optimizers
│   └── utils/                  # Utility functions
│       └── finance-utils.md    # Finance utilities reference
├── research/                   # Research documentation
│   └── index.md                # Research overview
├── contributing.md             # Contributing guide
└── changelog.md                # Version history

## Building the Documentation

### Local Development

```bash
# Serve with auto-reload (recommended for development)
make docs-serve
# or
uv run mkdocs serve

# Access at http://127.0.0.1:8000
```

### Build Static Site

```bash
# Build to site/ directory
make docs-build
# or
uv run mkdocs build
```

### Deploy to GitHub Pages

```bash
# Build and deploy (requires push access)
uv run mkdocs gh-deploy
```

## Configuration

Documentation is configured in `mkdocs.yml` at the project root:

- **Theme**: Material for MkDocs (modern, responsive)
- **Plugins**: mkdocstrings (API reference generation), search
- **Extensions**: Code highlighting, admonitions, tabs, tasklists
- **Navigation**: Structured sidebar with user guide, API reference, research

## Writing Documentation

### Page Format

All pages use Markdown with GitHub-flavored extensions:

```markdown
# Page Title

Brief introduction.

## Section

Content with **bold**, *italic*, `code`.

### Subsection

Code examples:

\`\`\`python
from finbot import something
result = something()
\`\`\`

Tables:

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### API Reference

API pages document functions, classes, and modules:

```markdown
## Function Name

Brief description.

**Location:** `module.path.to.function`

\`\`\`python
def function_name(arg1: type, arg2: type) -> return_type
\`\`\`

**Parameters:**
- `arg1` (type): Description
- `arg2` (type): Description

**Returns:** Description

**Example:**
\`\`\`python
from module import function_name
result = function_name(value1, value2)
\`\`\`
```

### Adding New Pages

1. Create Markdown file in appropriate directory
2. Add to `nav` section in `mkdocs.yml`
3. Test with `make docs-serve`
4. Commit changes

## Style Guidelines

- **Headings**: Use title case for main headings
- **Code blocks**: Always specify language (python, bash, yaml)
- **Links**: Use relative links for internal pages
- **Examples**: Include practical, runnable examples
- **Conciseness**: Keep pages focused and scannable

## Generated Site

The built documentation is output to `site/` directory (gitignored).

## Dependencies

- **mkdocs**: Static site generator
- **mkdocs-material**: Material Design theme
- **mkdocstrings**: API reference generation from docstrings
- **pymdown-extensions**: Additional Markdown extensions

All dependencies are in `pyproject.toml` dev dependencies.
