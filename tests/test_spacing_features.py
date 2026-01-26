"""Tests for spacing control features."""

import mdformat
import pytest


class TestTrailingWhitespace:
    """Tests for trailing whitespace removal.

    Note: mdformat already normalizes most trailing whitespace during rendering.
    These tests verify the postprocessor handles edge cases correctly.
    """

    def test_paragraph_trailing_spaces_stripped(self):
        """Paragraph with trailing spaces should be stripped."""
        input_text = "This is a paragraph.   \n"
        expected = "This is a paragraph.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_heading_trailing_spaces_stripped(self):
        """Heading with trailing spaces should be stripped."""
        input_text = "# Heading   \n\nContent here.\n"
        expected = "# Heading\n\nContent here.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_list_item_trailing_spaces_stripped(self):
        """List item with trailing spaces should be stripped."""
        input_text = "- Item 1   \n- Item 2  \n"
        expected = "- Item 1\n- Item 2\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_code_block_content_preserved(self):
        """Code block content should be preserved (mdformat handles this)."""
        input_text = """\
```python
def foo():
    return "bar"
```
"""
        expected = """\
```python
def foo():
    return "bar"
```
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_tilde_code_block_content_preserved(self):
        """Tilde-fenced code block content should be preserved.

        Note: mdformat normalizes tilde fences to backtick fences.
        """
        input_text = """\
~~~
code content
more code
~~~
"""
        # mdformat converts ~~~ to ```
        expected = """\
```
code content
more code
```
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_blockquote_stripped(self):
        """Blockquote trailing whitespace is stripped by mdformat."""
        # mdformat normalizes blockquotes during rendering
        input_text = "> Quote content\n"
        expected = "> Quote content\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_lines_mixed(self):
        """Multiple lines with mixed content types."""
        input_text = """\
# Title

Paragraph text.

- List item

```
code
```

> Blockquote
"""
        expected = """\
# Title

Paragraph text.

- List item

```
code
```

> Blockquote
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestHardBreaks:
    """Tests for hard break preservation.

    mdformat natively converts `two spaces + newline` to `backslash + newline`
    for visibility. These tests verify the behavior is maintained.
    """

    def test_two_spaces_to_backslash(self):
        """Two trailing spaces convert to backslash for hard break."""
        # mdformat converts two-space hard breaks to backslash style
        input_text = "Line one  \nLine two\n"
        expected = "Line one\\\nLine two\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_backslash_hard_break_preserved(self):
        """Backslash hard break should be preserved."""
        input_text = "Line one\\\nLine two\n"
        expected = "Line one\\\nLine two\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_hard_breaks(self):
        """Multiple hard breaks in sequence."""
        input_text = "Line one\\\nLine two\\\nLine three\n"
        expected = "Line one\\\nLine two\\\nLine three\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestPseudoHeadingSpacing:
    """Tests for pseudo-heading list separation.

    mdformat ensures a blank line between paragraphs and lists.
    These tests verify this behavior is maintained with space_control enabled.
    """

    def test_bold_pseudo_heading_before_list(self):
        """Bold pseudo-heading before list should have blank line."""
        input_text = "**Important:**\n- Item 1\n- Item 2\n"
        expected = "**Important:**\n\n- Item 1\n- Item 2\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_italic_pseudo_heading_before_list(self):
        """Italic pseudo-heading before list should have blank line."""
        input_text = "*Note:*\n- Item 1\n- Item 2\n"
        expected = "*Note:*\n\n- Item 1\n- Item 2\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_already_has_blank_line(self):
        """Already having blank line should remain unchanged."""
        input_text = "Some text.\n\n- Item 1\n- Item 2\n"
        expected = "Some text.\n\n- Item 1\n- Item 2\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_colon_pseudo_heading_before_list(self):
        """Colon-terminated pseudo-heading before list."""
        input_text = "Prerequisites:\n- Python 3.8+\n- pip\n"
        expected = "Prerequisites:\n\n- Python 3.8+\n- pip\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestNormalLinks:
    """Tests for normal markdown links.

    Note: mdformat escapes malformed link syntax (links spanning paragraphs)
    before postprocessing, so we can only operate on valid rendered links.
    """

    def test_normal_link_preserved(self):
        """Normal links should be preserved unchanged."""
        input_text = "[normal link](https://example.com)\n"
        expected = "[normal link](https://example.com)\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_link_in_paragraph(self):
        """Links in paragraphs should work correctly."""
        input_text = "Check out [this link](https://example.com) for more info.\n"
        expected = "Check out [this link](https://example.com) for more info.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_links(self):
        """Multiple links in content should work correctly."""
        input_text = "[link1](url1) and [link2](url2)\n"
        expected = "[link1](url1) and [link2](url2)\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestIntegration:
    """Integration tests for multiple features working together."""

    def test_frontmatter_with_trailing_whitespace(self):
        """Frontmatter with trailing whitespace in content."""
        input_text = """\
---
title: Test
---

# Heading

Content.
"""
        expected = """\
---
title: Test
---
# Heading

Content.
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected

    def test_all_features_combined(self):
        """All features working together."""
        input_text = """\
---
title: Test
---

# Main Title

**Important:**
- Item 1
- Item 2

Check [link](url).

```python
code
```

> Quote
"""
        expected = """\
---
title: Test
---
# Main Title

**Important:**

- Item 1
- Item 2

Check [link](url).

```python
code
```

> Quote
"""
        result = mdformat.text(input_text, extensions={"space_control", "frontmatter"})
        assert result == expected
