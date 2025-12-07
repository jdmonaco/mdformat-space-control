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
    """Tests for frontmatter followed by non-heading content (one blank line)."""

    def test_frontmatter_paragraph_one_blank_line(self):
        """Frontmatter followed by paragraph should have exactly one blank line."""
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
        """Multiple blank lines between frontmatter and paragraph should normalize to one."""
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
        """Frontmatter followed by list should have exactly one blank line."""
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
        """Frontmatter followed by code block should have exactly one blank line."""
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
