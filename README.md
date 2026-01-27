# mdformat-space-control

[![Build Status][ci-badge]][ci-link]
[![PyPI version][pypi-badge]][pypi-link]

An [mdformat](https://github.com/executablebooks/mdformat) plugin that provides unified control over Markdown spacing:

- **EditorConfig support**: Configure list indentation via `.editorconfig` files
- **Tight list formatting**: Automatically removes unnecessary blank lines between list items
- **Frontmatter spacing**: Normalizes spacing after YAML frontmatter (works with [mdformat-frontmatter](https://github.com/butler54/mdformat-frontmatter))
- **Consecutive blank line normalization**: Limits runs of 3+ empty lines to a maximum of 2
- **Trailing whitespace removal**: Strips trailing whitespace outside code blocks
- **Escaped link repair**: Fixes malformed multi-line links from web-clipped content
- **Wikilink preservation**: Handles Obsidian-style `[[links]]`, `[[links|aliases]]`, `[[page#heading]]`, `[[page#^blockid]]`, and `![[embeds]]`

## Installation

```bash
pip install mdformat-space-control
```

Or with [pipx](https://pipx.pypa.io/) for command-line usage:

```bash
pipx install mdformat
pipx inject mdformat mdformat-space-control
```

## Usage

After installation, mdformat will automatically use this plugin:

```bash
mdformat your-file.md
```

### EditorConfig Support

Create an `.editorconfig` file in your project:

```ini
# .editorconfig
root = true

[*.md]
indent_style = space
indent_size = 4
```

Nested lists will use the configured indentation:

**Before:**
```markdown
- Item 1
  - Nested item
- Item 2
```

**After (with 4-space indent):**
```markdown
- Item 1
    - Nested item
- Item 2
```

### Tight List Formatting

Lists with single-paragraph items are automatically formatted as tight lists:

**Before:**
```markdown
- Item 1

- Item 2

- Item 3
```

**After:**
```markdown
- Item 1
- Item 2
- Item 3
```

Multi-paragraph items preserve loose formatting:

```markdown
- First item with multiple paragraphs

  Second paragraph of first item

- Second item
```

### Frontmatter Spacing

When used with [mdformat-frontmatter](https://github.com/butler54/mdformat-frontmatter), this plugin removes blank lines between the frontmatter closing delimiter and the first content block:

**Before:**
```markdown
---
title: My Document
---


# Introduction
```

**After:**
```markdown
---
title: My Document
---
# Introduction
```

Install both plugins for this feature:

```bash
pip install mdformat-space-control mdformat-frontmatter
```

### EditorConfig Properties

| Property | Status | Notes |
|----------|--------|-------|
| `indent_style` | Supported | `space` or `tab` for list indentation |
| `indent_size` | Supported | Number of spaces per indent level |
| `tab_width` | Supported | Used when `indent_size = tab` |

### Python API

When using the Python API, you can set the file context for EditorConfig lookup:

```python
import mdformat
from mdformat_space_control import set_current_file

set_current_file("/path/to/your/file.md")
try:
    result = mdformat.text(markdown_text, extensions={"space_control"})
finally:
    set_current_file(None)
```

### Wikilink Preservation

Obsidian-style wikilinks are preserved during formatting:

```markdown
Link to [[another note]] or [[note|with alias]].
Embed an image: ![[photo.jpg]]
Link to heading: [[note#section]]
Block reference: [[note#^blockid]]
```

Wikilinks inside markdown link text are correctly handled without duplication:

```markdown
[![[image.jpg]]](http://example.com)
```

## Compatible Plugins

This plugin is tested to work alongside:

- [mdformat-frontmatter](https://github.com/butler54/mdformat-frontmatter) - YAML frontmatter parsing
- [mdformat-simple-breaks](https://github.com/csala/mdformat-simple-breaks) - Normalizes thematic breaks to `---`

For formatting files in an **Obsidian vault**, installing `mdformat-frontmatter` alongside this plugin is recommended:

```bash
pip install mdformat-space-control mdformat-frontmatter
```

Note: Wikilink support is built-in; `mdformat-wikilink` is not needed.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=mdformat_space_control
```

## License

MIT - see LICENSE file for details.

[ci-badge]: https://github.com/jdmonaco/mdformat-space-control/actions/workflows/tests.yml/badge.svg?branch=main
[ci-link]: https://github.com/jdmonaco/mdformat-space-control/actions/workflows/tests.yml
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-space-control.svg
[pypi-link]: https://pypi.org/project/mdformat-space-control
