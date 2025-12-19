# Sonnerrise - Project Instructions

## Overview
Suno track management and promotion planning suite.

## Specification
Full specification is in `docs/SPEC.md`. Read it before implementing.

## Implementation Order
1. `sonnerrise-core` - config loader, DB abstraction
2. `sonnerrise-personas` - simplest entity
3. `sonnerrise-definitions` - depends on personas
4. `sonnerrise-tracks` - depends on definitions
5. `sonnerrise-promo` - depends on tracks
6. `sonnerrise-calendar` - read-only view of track events
7. `sonnerrise-tools` - export/import
8. `sonnerrise-web` - Flask app integrating all modules

## Conventions
- Python 3.11+
- Use Pydantic for validation
- pytest for testing
- Black + isort for formatting
```

**Workflow:**
1. Create GitHub/GitLab repository
2. Commit `CLAUDE.md` and `docs/SPEC.md`
3. Open Claude Code, connect to repository
4. Initial prompt: `Read the spec in docs/SPEC.md and begin implementation with sonnerrise-core package`

---

## Option 2: Direct Initial Prompt

If starting with empty repository, paste a condensed version in the first message and attach the full spec file.

**Initial prompt example:**
```
Initialize the Sonnerrise project - a Suno track management suite.

[Attach sonnerrise-spec.md file]

Start by:
1. Creating repository structure per section 1.3
2. Implementing sonnerrise-core package (config loader, DB abstraction)
3. Setting up pyproject.toml for all packages
