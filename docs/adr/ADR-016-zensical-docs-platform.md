# ADR-016: Migrate Generated Documentation to Zensical

**Status:** Accepted
**Date:** 2026-06-14

## Context

Finbot's generated documentation site was originally built with MkDocs,
Material for MkDocs, and `mkdocstrings`. The project is entering a long-term
stable baseline, so the docs platform should use the current supported path and
avoid a legacy deployment command that mutates the `gh-pages` branch directly.

Zensical now provides a compatibility path for existing Material for MkDocs
projects, including support for reading `mkdocs.yml` and preliminary
`mkdocstrings` support through `mkdocstrings-python`. It also expects GitHub
Pages deployment through the Pages artifact workflow rather than a `gh-deploy`
command.

## Decision

Finbot will build the generated documentation site with Zensical.

- Keep `docs_site/` as the public documentation source directory.
- Keep `mkdocs.yml` as the compatibility configuration file.
- Replace direct MkDocs dev dependencies with `zensical` and
  `mkdocstrings-python`.
- Build docs with `uv run zensical build --clean --strict`.
- Deploy docs through GitHub Pages artifact upload/deploy actions.

## Consequences

The stable baseline has a strict docs build with no known link warnings. The
workflow no longer needs write access to repository contents for documentation
deployment and no longer commits generated site output to `gh-pages`.

Some MkDocs packages may still appear transitively while `mkdocstrings-python`
uses compatibility-layer dependencies. That is acceptable as long as the
project-facing build and deploy surface remains Zensical.

Future docs-platform work should only introduce a native `zensical.toml` after
API-reference parity is explicitly validated against the current `mkdocs.yml`
configuration.
