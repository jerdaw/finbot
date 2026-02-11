# ADR-003: Add MkDocs Documentation System

**Date:** 2026-02-11
**Status:** Accepted
**Deciders:** Jeremy Dawson
**Context:** Priority 3.1 - Improve Documentation

---

## Context and Problem Statement

Finbot had comprehensive module-level docstrings (160 files) but lacked a user-friendly, searchable API reference and documentation site. Users needed:

1. Professional documentation site with good UX
2. Searchable API reference
3. User guides and tutorials
4. Easy local development and deployment

## Decision Drivers

- **Ease of use**: Simple Markdown-based authoring
- **Modern UX**: Professional appearance with search, navigation, dark mode
- **API auto-generation**: Extract documentation from docstrings
- **Fast builds**: Quick iteration during development
- **Deployment**: Easy GitHub Pages deployment
- **Maintenance**: Low overhead, widely adopted tool

## Considered Options

1. **MkDocs with Material theme**
2. **Sphinx** (traditional Python documentation)
3. **Docusaurus** (React-based)
4. **GitBook**
5. **Read the Docs** (hosting platform)

## Decision Outcome

**Chosen option:** MkDocs with Material theme and mkdocstrings plugin

### Rationale

**MkDocs advantages:**
- Simple Markdown-based (no reStructuredText learning curve)
- Beautiful Material theme with excellent UX out of the box
- Fast builds (~2 seconds for entire site)
- Excellent search functionality
- Easy local development (`mkdocs serve`)
- One-command GitHub Pages deployment
- Wide Python community adoption

**Material theme advantages:**
- Modern, professional design
- Dark mode toggle
- Responsive mobile layout
- Instant navigation
- Code syntax highlighting
- Search as you type

**mkdocstrings advantages:**
- Auto-generates API docs from Google-style docstrings
- Python handler for proper type hint rendering
- Preserves all docstring information

### Implementation

**Dependencies added:**
```toml
[tool.poetry.group.dev.dependencies]
mkdocs = "^1.6.1"
mkdocs-material = "^9.5.49"
mkdocstrings = {extras = ["python"], version = "^0.27.0"}
```

**Structure created:**
```
docs_site/
├── index.md                 # Home page
├── user-guide/             # Installation, quick start, CLI ref, config
├── api/                    # API reference
│   ├── services/          # Backtesting, simulation, optimization
│   └── utils/             # Utility functions
├── research/              # Research documentation
├── contributing.md        # Contributing guide
└── changelog.md           # Version history
```

**Key pages:**
- Index: Project overview, features, quick start
- User guide: 5 pages (getting-started, installation, quick-start, cli-reference, configuration)
- API reference: BacktestRunner, Fund Simulator, DCA Optimizer, Monte Carlo, Finance Utils
- Supporting: Contributing, changelog, research overview

**Makefile integration:**
```makefile
docs: docs-build docs-serve
docs-serve: mkdocs serve
docs-build: mkdocs build
```

### Consequences

**Positive:**
- Professional documentation site with excellent UX
- Searchable API reference
- Fast builds enable rapid iteration
- Easy contribution (Markdown familiarity)
- Simple deployment workflow
- Material theme requires no CSS customization
- Dark mode support out of the box

**Negative:**
- Additional dev dependency (19 packages)
- Separate docs_site/ directory alongside docs/
- Manual API page creation (mkdocstrings had module resolution issues)
- Static site requires regeneration after code changes

**Neutral:**
- GitHub Pages deployment requires separate branch
- site/ directory added to .gitignore

## Implementation Details

**Configuration (`mkdocs.yml`):**
- Material theme with indigo color scheme
- Dark/light mode toggle
- Navigation tabs and sections
- Search with suggestions
- Code copy buttons
- Markdown extensions (admonitions, code highlighting, tabs, task lists)

**Build process:**
1. `mkdocs build` generates static site to `site/`
2. `mkdocs serve` runs local dev server on port 8000
3. `mkdocs gh-deploy` builds and pushes to gh-pages branch

**Documentation workflow:**
1. Write/edit Markdown in docs_site/
2. Run `make docs-serve` for live preview
3. Commit changes
4. CI can build docs to verify no errors
5. Deploy with `mkdocs gh-deploy` when ready

## Alternatives Not Chosen

**Sphinx:**
- Pros: Python standard, rst flexibility, extensive extensions
- Cons: reStructuredText learning curve, slower builds, less modern UX, configuration complexity
- Reason not chosen: MkDocs simpler and faster, Material theme superior UX

**Docusaurus:**
- Pros: Modern React-based, versioning built-in
- Cons: Requires Node.js, heavier dependency, less Python-native
- Reason not chosen: Adds another tech stack, overkill for project size

**GitBook:**
- Pros: Beautiful UI, git-based
- Cons: Proprietary platform, paid plans for private repos
- Reason not chosen: Prefer open-source, self-hosted solution

## Related Decisions

- ADR-002: CLI interface provides commands documented in cli-reference.md
- Priority 3.1: All 160 utility files have comprehensive docstrings (foundation for API docs)

## Future Enhancements

- [ ] Auto-deploy docs to GitHub Pages via CI on main branch push
- [ ] Add more utility API reference pages (datetime, pandas, data science)
- [ ] Add architecture diagrams using Mermaid
- [ ] Add notebook gallery with example outputs
- [ ] API reference completeness (currently 6 pages, could expand to 160+)
- [ ] Investigate mkdocstrings Python handler improvements for better auto-generation

## References

- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Priority 3.1 in Roadmap](../planning/roadmap.md#31-improve-documentation-)
