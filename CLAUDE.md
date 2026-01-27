# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mdformat-space-control is an mdformat plugin that provides unified control over Markdown spacing:
- **EditorConfig support**: Configure list indentation via `.editorconfig` files
- **Tight list formatting**: Automatically removes unnecessary blank lines between list items
- **Frontmatter spacing**: Normalizes spacing after YAML frontmatter (works with mdformat-frontmatter)
- **Consecutive blank line normalization**: Limits runs of 3+ empty lines to a maximum of 2
- **Trailing whitespace removal**: Strips trailing whitespace outside code blocks
- **Escaped link repair**: Fixes malformed multi-line links from web-clipped content
- **Wikilink preservation**: Handles Obsidian-style `[[links]]`, `[[links|aliases]]`, `[[page#heading]]`, `[[page#^blockid]]`, and `![[embeds]]`

This plugin merges functionality from mdformat-editorconfig and mdformat-tight-lists into a single plugin, solving the issue where mdformat only applies one set of list renderers when multiple plugins are installed.

## Build and Test Commands

```bash
uv sync --extra test                        # Install dependencies including test deps
uv run python -m pytest                     # Run all tests
uv run python -m pytest -v                  # Run tests verbosely
uv run python -m pytest --cov=mdformat_space_control  # Run with coverage
uv run python -m pytest tests/test_editorconfig.py    # Run specific test file
```

## Architecture

```
mdformat_space_control/
├── __init__.py    # Public API exports, version
├── config.py      # EditorConfig lookup, file context tracking
└── plugin.py      # List renderers (RENDERERS dict)
```

**Key components:**

- **`config.py`**: Uses `contextvars` for thread-safe file path tracking. Falls back to `Path.cwd() / "_.md"` for CLI usage when no explicit file context is set.
- **`plugin.py`**: Provides renderers, postprocessors, and parser extensions:
  - `_wikilink_rule`: Inline parser for Obsidian-style wikilinks
  - `_render_wikilink`: Preserves wikilinks unchanged
  - `_render_list_item`: Per-item tight/loose formatting based on paragraph count
  - `_render_bullet_list`: Configurable indent + content-based tight/loose
  - `_render_ordered_list`: Configurable indent + content-based tight/loose
  - `_postprocess_root`: Combined postprocessor applying frontmatter spacing, escaped link repair, consecutive blank line normalization, and trailing whitespace removal

## Plugin Extension Points

mdformat plugins expose:
1. **`RENDERERS`**: Dict mapping node types to render functions
2. **`POSTPROCESSORS`**: Dict mapping node types to postprocess functions
3. **`update_mdit(mdit)`**: Hook to modify the markdown-it parser (used for wikilink parsing)

Entry point in `pyproject.toml`:
```toml
[project.entry-points."mdformat.parser_extension"]
space_control = "mdformat_space_control"
```

## Test Structure

- **`tests/fixtures.md`**: Markdown-it fixture format for tight-list tests
- **`tests/test_fixtures.py`**: Parametrized fixture tests
- **`tests/test_editorconfig.py`**: EditorConfig-specific tests using temp directories
- **`tests/test_frontmatter.py`**: Frontmatter spacing tests (requires mdformat-frontmatter)
- **`tests/test_spacing_features.py`**: Trailing whitespace, hard breaks, escaped link repair, consecutive blank line tests
- **`tests/test_integration.py`**: Full-stack integration tests combining multiple features
- **`tests/test_plugin_interactions.py`**: Tests for compatibility with other mdformat plugins

## Key Dependencies

- **mdformat** (>=0.7.0): The Markdown formatter being extended
- **editorconfig** (>=0.12.0): EditorConfig file parsing

## Compatible Plugins

Tested to work alongside:
- `mdformat-frontmatter` - YAML frontmatter parsing
- `mdformat-simple-breaks` - Normalizes thematic breaks to `---`

Note: Wikilink support is built-in; `mdformat-wikilink` is not needed.

## Release Process

1. Update version in `__init__.py`
2. Commit changes
3. Tag with `git tag vX.Y.Z`
4. Push tag to trigger PyPI publish: `git push origin vX.Y.Z`

## Claude Code Configuration

This project uses the global `~/.claude/settings.json` for all permissions and settings.

### Tools Manager: tlmgr

The `tlmgr` command manages all tool repositories from the umbrella ~/tools directory:

```bash
tlmgr --json summary  # Overall status of all 14 repos
tlmgr --json list     # Detailed status with branches
tlmgr changes         # Show uncommitted changes
tlmgr unpushed        # Show unpushed commits
```

Always use `tlmgr` (not relative paths like `./bin/tools-manager.sh`).

### Development Workflow

**Auto-allowed git operations:**
- Read: status, diff, log, show, branch, grep, blame
- Write: add, commit, push, pull, checkout, switch, restore, stash

**Require confirmation:**
- Destructive: merge, rebase, reset, cherry-pick, revert
- Force operations: push --force
- Repository changes: clone, init, submodule

### Available Development Tools

**Python:** pytest, pip, poetry, uv (install, run, sync)  
**Node:** npm (test, run, install), node  
**Build:** make, bash scripts in ./scripts/  
**Utilities:** find, grep, rg, cat, ls, tree, jq, yq, head, tail, wc  
**Documents:** pandoc, md2docx, mdformat

### Configuration

All permissions are centralized in `~/.claude/settings.json`:
- Sandbox is disabled globally
- Full read/write access to ~/tools/** and ~/agents/**
- Standard security protections (no ~/.ssh, .env files, etc.)
- Consistent behavior across all projects

No project-specific `.claude/` folders are needed.