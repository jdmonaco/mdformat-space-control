"""Tests for interaction with other mdformat plugins."""

import pytest
import mdformat

try:
    import mdformat_simple_breaks

    HAS_SIMPLE_BREAKS = True
except ImportError:
    HAS_SIMPLE_BREAKS = False

try:
    import mdformat_wikilink

    HAS_WIKILINK = True
except ImportError:
    HAS_WIKILINK = False


class TestSpaceControlAlone:
    """Tests for space_control without other plugins."""

    def test_tight_list_basic(self):
        """Verify basic tight list works."""
        input_text = "- Item 1\n\n- Item 2\n"
        expected = "- Item 1\n- Item 2\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestWithFrontmatter:
    """Tests with mdformat-frontmatter plugin."""

    def test_frontmatter_heading_spacing(self):
        """Frontmatter + heading spacing works."""
        input_text = "---\ntitle: Test\n---\n\n# Heading\n"
        result = mdformat.text(
            input_text, extensions={"space_control", "frontmatter"}
        )
        assert "---\n# Heading" in result


@pytest.mark.skipif(not HAS_WIKILINK, reason="mdformat-wikilink not installed")
class TestWithWikilink:
    """Tests requiring mdformat-wikilink plugin.

    Note: mdformat-wikilink is the plugin that preserves [[wikilinks]].
    mdformat-obsidian handles callouts, footnotes, math, and task lists,
    but does NOT handle wikilinks.
    """

    def test_wikilinks_preserved(self):
        """Wikilinks should be preserved with mdformat-wikilink."""
        input_text = "- [[Note]]\n- [[Other|alias]]\n"
        result = mdformat.text(
            input_text, extensions={"space_control", "wikilink"}
        )
        assert "[[Note]]" in result
        assert "[[Other|alias]]" in result


@pytest.mark.skipif(not HAS_SIMPLE_BREAKS, reason="mdformat-simple-breaks not installed")
class TestWithSimpleBreaks:
    """Tests for interaction with mdformat-simple-breaks plugin.

    simple_breaks converts thematic breaks to uniform '---' format,
    which could potentially conflict with frontmatter detection.
    """

    def test_thematic_break_not_confused_with_frontmatter(self):
        """Mid-document thematic break should not trigger frontmatter spacing."""
        input_text = """\
# Title

Some content.

---

## Section
"""
        expected = """\
# Title

Some content.

---

## Section
"""
        result = mdformat.text(
            input_text, extensions={"space_control", "simple_breaks"}
        )
        assert result == expected

    def test_thematic_break_at_start_not_frontmatter(self):
        """Thematic break at document start (no closing ---) is not frontmatter."""
        input_text = """\
---

# Heading
"""
        expected = """\
---

# Heading
"""
        result = mdformat.text(
            input_text, extensions={"space_control", "simple_breaks"}
        )
        assert result == expected

    def test_all_three_plugins_frontmatter_and_thematic(self):
        """Frontmatter + simple_breaks + space_control with both frontmatter and thematic break."""
        input_text = """\
---
title: Test
---

# Introduction

Content here.

---

## Second Section
"""
        expected = """\
---
title: Test
---
# Introduction

Content here.

---

## Second Section
"""
        result = mdformat.text(
            input_text, extensions={"frontmatter", "simple_breaks", "space_control"}
        )
        assert result == expected

    def test_all_three_plugins_no_frontmatter(self):
        """simple_breaks + space_control + frontmatter with no actual frontmatter."""
        input_text = """\
# Title

---

## Section
"""
        expected = """\
# Title

---

## Section
"""
        result = mdformat.text(
            input_text, extensions={"frontmatter", "simple_breaks", "space_control"}
        )
        assert result == expected
