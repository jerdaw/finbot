# Roadmap Process

How to manage the project roadmap and implementation plans.

## Roadmap Location

The canonical roadmap is `docs/planning/roadmap.md`.

## Roadmap Structure

```markdown
## Priority N: Category Name

### N.M Item Title [✓ if complete]

**Status:** COMPLETED (date) | IN PROGRESS | NOT STARTED

- [x] Completed sub-task
- [ ] Pending sub-task

**What Was Done:** (for completed items)
Brief summary of implementation.
```

## Lifecycle of a Roadmap Item

1. **Add**: New items go under the appropriate priority tier
2. **Implement**: Check off sub-tasks as they're completed
3. **Complete**: Mark with ✓, add status line with date, write "What Was Done"
4. **Record in table**: Add a row to the "Completed Items" table at the bottom
5. **Trim**: Once an item is fully documented in the completed table, the detailed write-up in the main section can be trimmed to just the status and a brief summary (keep full details in git history)

## Deferred Items

Items that are explicitly not being pursued should be marked with rationale:

```markdown
- [ ] Item description -- **Deferred**: reason why
```

## Implementation Plans

For complex features, create a detailed plan before implementation:
- Store in `docs/planning/` during active work
- Archive to `docs/planning/archive/` once fully implemented
- Plan files should include: context, file structure, implementation order, testing approach

## Priority Tiers

| Tier | Description |
|------|-------------|
| Priority 0 | Bugs and architectural hazards (fix first) |
| Priority 1 | Critical gaps |
| Priority 2 | High-impact improvements |
| Priority 3 | Moderate improvements |
| Priority 4 | Polish and extensibility |

New tiers can be added as the project evolves.
