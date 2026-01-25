# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This folder (`dev/`) is a workspace containing three mdformat plugin repositories and reference documentation:

```
mdformat-plugins/
├── dev/                       # Reference docs (mdformat official docs)
├── mdformat-editorconfig/     # Complete - EditorConfig indentation support
├── mdformat-tight-lists/      # Complete - Tight list formatting
└── mdformat-space-control/    # In development - merges both plugins
```

## Build and Test Commands

All three plugins use `uv` with `flit_core` as the build backend:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=mdformat_<plugin_name>

# Run a single test
uv run pytest tests/test_fixtures.py::test_fixtures[test_name]
```

## Plugin Architecture

mdformat plugins use the `mdformat.parser_extension` entry point and must expose:

1. **`RENDERERS`**: A `Mapping[str, Render]` that overrides node type renderers
2. **`update_mdit(mdit: MarkdownIt)`**: Hook to modify the markdown-it parser (can be no-op)

Key renderer node types for list plugins:
- `bullet_list` - unordered lists
- `ordered_list` - numbered lists
- `list_item` - individual list items (tight-lists uses this)

Entry point in `pyproject.toml`:
```toml
[project.entry-points."mdformat.parser_extension"]
plugin_name = "mdformat_plugin_name"
```

## Test Fixture Format

Tests use `fixtures.md` files with markdown-it fixture format:

```markdown
test title
.
input markdown
.
expected output
.
```

The test runner uses `markdown_it.utils.read_fixture_file()` to parse these.

## Key Dependencies

- **mdformat** (>=0.7.0): The formatter being extended
- **editorconfig** (>=0.12.0): EditorConfig file parsing (editorconfig plugin)
- **mdformat-frontmatter** (>=2.0.0): Required by tight-lists

## mdformat Renderer Internals

Plugins import from `mdformat.renderer._context`:
- `get_list_marker_type(node)` - returns marker (`-`, `*`, `.`, `)`)
- `is_tight_list(node)` - checks if list has tight formatting
- `is_tight_list_item(node)` - checks if item is tight
- `make_render_children(separator)` - factory for child rendering

The `RenderContext` provides:
- `context.indented(width)` - context manager for tracking indent level
- `context.options` - mdformat options dict

## EditorConfig Integration Pattern

The editorconfig plugin uses `contextvars` for thread-safe file tracking since mdformat doesn't pass file paths to renderers:

```python
from contextvars import ContextVar
_current_file: ContextVar[Path | None] = ContextVar("current_file", default=None)
```

CLI fallback uses `Path.cwd() / "_.md"` for editorconfig lookup.

## Release Process

1. Update version in `__init__.py`
2. Commit changes
3. Tag with `git tag vX.Y.Z`
4. Push tag to trigger PyPI publish
