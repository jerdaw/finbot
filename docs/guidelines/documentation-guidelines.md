# Documentation Guidelines

Standards for maintaining project documentation.

## Documentation Structure

```
docs/
  adr/              # Architectural Decision Records
  guidelines/       # Development guidelines (this directory)
  guides/           # How-to guides for specific topics
  planning/         # Roadmap and implementation plans
    archive/        # Completed plans
  research/         # Research findings and analysis
docs_site/          # MkDocs source for generated site
notebooks/          # Jupyter notebooks with demos
```

## When to Write Documentation

| Change Type | Required Documentation |
|---|---|
| New module/service | AGENTS.md entry, module docstring, README if complex |
| Architectural decision | ADR in `docs/adr/` |
| New CLI command | CLI reference in docs_site, AGENTS.md update |
| New notebook | Entry in `notebooks/README.md` |
| New strategy/simulator | AGENTS.md strategies list update |
| Config changes | AGENTS.md environment section update |
| Research findings | Document in `docs/research/` |

## Module Docstrings

Every Python module should have a Google-style module docstring:

```python
"""Brief one-line summary.

Longer description explaining purpose, context, and relationships
to other modules. Include typical usage example if helpful.

Typical usage:
    result = my_function(data)
"""
```

## ADR Format

Use the standard ADR template:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** YYYY-MM-DD

## Context
Why this decision is needed.

## Decision
What we decided to do.

## Consequences
What results from this decision (positive and negative).
```

Number ADRs sequentially (ADR-001, ADR-002, etc.).

## README Standards

- `README.md` (root): Project overview, quick start, installation
- `notebooks/README.md`: Notebook index with descriptions
- Module READMEs: Only when a module has complex structure worth explaining

## Commit Messages

Use imperative mood, focus on "why" over "what":
- Good: `Add health economics QALY simulator`
- Bad: `Added some new files`

Only list human authors and contributors. No AI attribution.

## AGENTS.md

`AGENTS.md` is the canonical reference for AI coding agents. `CLAUDE.md` is a symlink to it. Keep it updated when:
- Adding new modules, services, or entry points
- Changing dependencies or environment requirements
- Modifying the package structure
- Adding new CLI commands or dashboard pages
