"""Tests for YAML frontmatter spacing normalization."""

import mdformat
import pytest


class TestFrontmatterHeadingSpacing:
    """Tests for frontmatter followed by heading (no blank line)."""

    def test_frontmatter_heading_removes_blank_line(self):
        """Frontmatter followed by heading should have no blank line."""
        input_text = """\
---
title: Test
---

# Heading
"""
        expected = """\
---
title: Test
---
# Heading
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_heading_multiple_blank_lines(self):
        """Multiple blank lines between frontmatter and heading should be removed."""
        input_text = """\
---
title: Test
---



# Heading
"""
        expected = """\
---
title: Test
---
# Heading
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_h2_heading(self):
        """Works with any heading level."""
        input_text = """\
---
title: Test
---

## Second Level Heading
"""
        expected = """\
---
title: Test
---
## Second Level Heading
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected


class TestFrontmatterNonHeadingSpacing:
    """Tests for frontmatter followed by non-heading content (tight spacing)."""

    def test_frontmatter_paragraph_tight(self):
        """Frontmatter followed by paragraph should have no blank line (tight)."""
        input_text = """\
---
title: Test
---

This is a paragraph.
"""
        expected = """\
---
title: Test
---
This is a paragraph.
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_paragraph_multiple_blank_lines(self):
        """Multiple blank lines between frontmatter and paragraph should be removed."""
        input_text = """\
---
title: Test
---



This is a paragraph.
"""
        expected = """\
---
title: Test
---
This is a paragraph.
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_list(self):
        """Frontmatter followed by list should have no blank line (tight)."""
        input_text = """\
---
title: Test
---

- Item 1
- Item 2
"""
        expected = """\
---
title: Test
---
- Item 1
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_code_block(self):
        """Frontmatter followed by code block should have no blank line (tight)."""
        input_text = """\
---
title: Test
---

```python
print("hello")
```
"""
        expected = """\
---
title: Test
---
```python
print("hello")
```
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected


class TestNoFrontmatter:
    """Tests for documents without frontmatter (unchanged behavior)."""

    def test_no_frontmatter_unchanged(self):
        """Documents without frontmatter should be unchanged."""
        input_text = """\
# Heading

This is a paragraph.
"""
        expected = """\
# Heading

This is a paragraph.
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_no_frontmatter_list(self):
        """Lists in documents without frontmatter should be unchanged."""
        input_text = """\
# Heading

- Item 1
- Item 2
"""
        expected = """\
# Heading

- Item 1
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected


class TestComplexFrontmatter:
    """Tests for complex frontmatter content."""

    def test_multiline_frontmatter(self):
        """Complex multiline frontmatter should work correctly."""
        input_text = """\
---
title: My Document
author: John Doe
tags:
  - python
  - markdown
---

# Introduction
"""
        expected = """\
---
title: My Document
author: John Doe
tags:
  - python
  - markdown
---
# Introduction
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected


class TestThematicBreakNotFrontmatter:
    """Tests ensuring thematic breaks are NOT treated as frontmatter.

    Note: mdformat-frontmatter renders thematic breaks as 70 underscores
    to distinguish them from frontmatter delimiters (---).
    """

    # 70 underscores as rendered by mdformat-frontmatter
    THEMATIC_BREAK = "_" * 70

    def test_thematic_break_heading_preserves_blank_line(self):
        """Thematic break followed by heading should preserve blank line."""
        input_text = """\
Some content here.

---

## Section Heading
"""
        expected = f"""\
Some content here.

{self.THEMATIC_BREAK}

## Section Heading
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_thematic_break_multiple_blank_lines(self):
        """Thematic break with multiple blank lines before heading."""
        input_text = """\
Content.

---


## Heading
"""
        # mdformat normalizes to one blank line between blocks
        expected = f"""\
Content.

{self.THEMATIC_BREAK}

## Heading
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_thematic_break_paragraph_preserves_blank_line(self):
        """Thematic break followed by paragraph should preserve blank line."""
        input_text = """\
Before.

---

After.
"""
        expected = f"""\
Before.

{self.THEMATIC_BREAK}

After.
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_no_frontmatter_thematic_break_only(self):
        """Document with only thematic break (no frontmatter) is unchanged."""
        input_text = """\
# Title

---

## Section
"""
        expected = f"""\
# Title

{self.THEMATIC_BREAK}

## Section
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_and_thematic_break(self):
        """Document with both frontmatter AND thematic break."""
        input_text = """\
---
title: Test
---

# Introduction

Content here.

---

## Second Section
"""
        expected = f"""\
---
title: Test
---
# Introduction

Content here.

{self.THEMATIC_BREAK}

## Second Section
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected


class TestFrontmatterListIntegration:
    """Integration tests for frontmatter with lists."""

    def test_frontmatter_tight_list(self):
        """Frontmatter followed by loose list should tighten (both frontmatter and list)."""
        input_text = """\
---
title: Tasks
---

- Item 1

- Item 2
"""
        expected = """\
---
title: Tasks
---
- Item 1
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_frontmatter_checkbox_list(self):
        """Frontmatter followed by checkbox list (tight spacing)."""
        input_text = """\
---
title: Todo
---

- [ ] Task 1

- [x] Task 2
"""
        expected = """\
---
title: Todo
---
- [ ] Task 1
- [x] Task 2
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected
