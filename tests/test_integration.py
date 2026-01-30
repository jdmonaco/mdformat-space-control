"""Integration tests for complex end-to-end scenarios.

These tests combine multiple features to catch conjunctive regressions:
- EditorConfig indentation + tight/loose lists
- Frontmatter spacing + lists
- Nested lists with multi-paragraph items
- Plugin interactions with all features active
"""

import importlib.util
import tempfile
from pathlib import Path

import mdformat
import pytest

from mdformat_space_control import set_current_file


def format_with_editorconfig(
    text: str, filepath: Path, extensions: set[str] | None = None
) -> str:
    """Format markdown text with EditorConfig file context set."""
    if extensions is None:
        extensions = {"space_control"}
    set_current_file(filepath)
    try:
        return mdformat.text(text, extensions=extensions)
    finally:
        set_current_file(None)


class TestIntegrationEditorConfigWithLists:
    """Tests combining EditorConfig indentation with tight/loose list behavior."""

    def test_4space_indent_mixed_tight_loose_nested(self):
        """4-space indent with nested lists: tight outer, loose inner item.

        Verifies that:
        - Outer list uses 4-space indentation
        - Inner list respects outer's 4-space indent
        - Multi-paragraph nested item stays loose
        - Single-paragraph items stay tight
        """
        editorconfig = """\
root = true

[*.md]
indent_style = space
indent_size = 4
"""
        input_md = """\
- Outer item 1
    - Nested item A

    - Nested item B has

      two paragraphs

    - Nested item C
- Outer item 2
"""
        # Expected: outer tight, nested loose (item B has multiple paragraphs)
        expected = """\
- Outer item 1
    - Nested item A

    - Nested item B has

        two paragraphs

    - Nested item C
- Outer item 2
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ec_path = Path(tmpdir) / ".editorconfig"
            ec_path.write_text(editorconfig)
            md_path = Path(tmpdir) / "test.md"

            result = format_with_editorconfig(input_md, md_path)
            assert result == expected

    def test_tab_indent_ordered_list_continuation(self):
        """Tab indentation with ordered list and continuation lines.

        Verifies:
        - Tab character used for indentation
        - Ordered list numbering preserved
        - Continuation lines properly indented with tabs
        """
        editorconfig = """\
root = true

[*.md]
indent_style = tab
indent_size = 4
"""
        input_md = """\
1. First item with
   continuation line
2. Second item
3. Third item with
   multiple
   continuation lines
"""
        expected = """\
1. First item with\\
\tcontinuation line
2. Second item
3. Third item with\\
\tmultiple\\
\tcontinuation lines
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ec_path = Path(tmpdir) / ".editorconfig"
            ec_path.write_text(editorconfig)
            md_path = Path(tmpdir) / "test.md"

            result = format_with_editorconfig(input_md, md_path)
            assert result == expected


class TestIntegrationFrontmatterWithLists:
    """Tests combining frontmatter spacing with list formatting."""

    def test_frontmatter_tight_heading_then_loose_list(self):
        """Frontmatter + heading (tight) + loose list.

        Verifies:
        - No blank line between frontmatter and heading
        - Loose list (multi-paragraph item) preserved after heading
        """
        input_md = """\
---
title: Test Document
---

# Introduction

- Item one

- Item two has

  multiple paragraphs

- Item three
"""
        expected = """\
---
title: Test Document
---
# Introduction

- Item one

- Item two has

  multiple paragraphs

- Item three
"""
        result = mdformat.text(
            input_md, extensions={"space_control", "frontmatter"}
        )
        assert result == expected

    def test_frontmatter_paragraph_then_tight_list(self):
        """Frontmatter + paragraph (tight) + tight list.

        Verifies:
        - No blank line between frontmatter and paragraph (tight spacing)
        - Tight list properly formatted after paragraph
        """
        input_md = """\
---
date: 2025-01-26
---


Some introductory text.

- Item 1

- Item 2

- Item 3
"""
        # Tight spacing: no blank line after frontmatter for any content type
        expected = """\
---
date: 2025-01-26
---
Some introductory text.

- Item 1
- Item 2
- Item 3
"""
        result = mdformat.text(
            input_md, extensions={"space_control", "frontmatter"}
        )
        assert result == expected


class TestIntegrationComplexNesting:
    """Tests for deeply nested and complex list structures."""

    def test_three_level_nesting_mixed_tight_loose(self):
        """Three levels of nesting with mixed tight/loose at each level.

        Verifies correct propagation of tight/loose state through nesting.
        When any item in a list has multiple paragraphs, the whole list is loose.
        """
        input_md = """\
- Level 1 item 1
  - Level 2 item A
    - Level 3 tight
    - Level 3 tight
  - Level 2 item B
- Level 1 item 2

  This item has two paragraphs.

  - Level 2 under loose parent
    - Level 3 under loose grandparent
"""
        # Level 1 is loose because item 2 has multiple paragraphs
        # This affects the blank line before item 1's nested content too
        expected = """\
- Level 1 item 1

  - Level 2 item A
    - Level 3 tight
    - Level 3 tight
  - Level 2 item B

- Level 1 item 2

  This item has two paragraphs.

  - Level 2 under loose parent
    - Level 3 under loose grandparent
"""
        result = mdformat.text(input_md, extensions={"space_control"})
        assert result == expected

    def test_ordered_bullet_interleaved_nesting(self):
        """Ordered list containing bullet lists and vice versa.

        Uses default 2-space indentation.
        """
        input_md = """\
1. First ordered item
   - Bullet under ordered
   - Another bullet
2. Second ordered item
   1. Nested ordered
   2. Nested ordered two
      - Deep bullet
"""
        # Default 2-space indent for bullet lists under ordered
        expected = """\
1. First ordered item
  - Bullet under ordered
  - Another bullet
2. Second ordered item
  1. Nested ordered
  2. Nested ordered two
    - Deep bullet
"""
        result = mdformat.text(input_md, extensions={"space_control"})
        assert result == expected


class TestIntegrationFullStack:
    """End-to-end tests with all plugins and features combined."""

    @pytest.mark.skipif(
        not all(
            [
                importlib.util.find_spec("mdformat_frontmatter"),
                importlib.util.find_spec("mdformat_wikilink"),
                importlib.util.find_spec("mdformat_simple_breaks"),
            ]
        ),
        reason="Requires all optional plugins",
    )
    def test_obsidian_note_full_scenario(self):
        """Realistic Obsidian note with all features.

        Combines:
        - Frontmatter (tight heading after)
        - Wikilinks in list items
        - Thematic break mid-document
        - Mixed tight/loose lists
        - EditorConfig 4-space indent
        """
        editorconfig = """\
root = true

[*.md]
indent_style = space
indent_size = 4
"""
        input_md = """\
---
title: Project Notes
tags: [project, notes]
---


# Overview

Key references:
- [[Main Document]]

- [[Supporting Notes]]

---

## Tasks

- [x] Complete [[Setup Guide]]
- [ ] Review [[Architecture]]
    - Check dependencies
    - Verify tests
- [ ] Write documentation

  Include examples in the docs.

## Links

See also [[Related Project]].
"""
        # Expected output with 4-space indent
        expected = """\
---
title: Project Notes
tags: [project, notes]
---
# Overview

Key references:
- [[Main Document]]
- [[Supporting Notes]]

---

## Tasks

- [x] Complete [[Setup Guide]]

- [ ] Review [[Architecture]]
    - Check dependencies
    - Verify tests

- [ ] Write documentation

  Include examples in the docs.

## Links

See also [[Related Project]].
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ec_path = Path(tmpdir) / ".editorconfig"
            ec_path.write_text(editorconfig)
            md_path = Path(tmpdir) / "test.md"

            result = format_with_editorconfig(
                input_md,
                md_path,
                extensions={"space_control", "frontmatter", "wikilink", "simple_breaks"},
            )

            # Verify key features
            assert "---\n# Overview" in result  # Tight frontmatter-heading
            assert "[[Main Document]]" in result  # Wikilinks preserved
            assert "---\n\n## Tasks" in result  # Thematic break preserved
            assert "    - Check dependencies" in result  # 4-space indent

    def test_edge_case_empty_list_items_with_frontmatter(self):
        """Empty list items should be handled correctly with frontmatter.

        Edge case that could expose issues with frontmatter postprocessing
        interacting with list rendering.
        """
        input_md = """\
---
test: true
---

# List with empty items

-
- Content
-
"""
        result = mdformat.text(
            input_md, extensions={"space_control", "frontmatter"}
        )
        # Verify it doesn't crash and basic structure is preserved
        assert "---\n# List" in result
        assert "- Content" in result
