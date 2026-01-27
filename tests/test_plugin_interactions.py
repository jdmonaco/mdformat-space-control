"""Tests for interaction with other mdformat plugins."""

import pytest
import mdformat

try:
    import mdformat_simple_breaks

    HAS_SIMPLE_BREAKS = True
except ImportError:
    HAS_SIMPLE_BREAKS = False


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


class TestBuiltinWikilinks:
    """Tests for built-in wikilink support.

    Wikilink support is built into space_control (not a separate plugin).
    Supports Obsidian-style [[links]], [[links|aliases]], [[page#heading]],
    [[page#^blockid]], and ![[embeds]].
    """

    def test_basic_wikilink_preserved(self):
        """Basic wikilinks should be preserved."""
        input_text = "Link to [[Note]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note]]" in result

    def test_wikilink_with_alias_preserved(self):
        """Wikilinks with aliases should be preserved."""
        input_text = "Link to [[Note|my alias]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note|my alias]]" in result

    def test_wikilink_with_heading_preserved(self):
        """Wikilinks with heading references should be preserved."""
        input_text = "Link to [[Note#Section]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note#Section]]" in result

    def test_wikilink_with_block_ref_preserved(self):
        """Wikilinks with block references should be preserved."""
        input_text = "Link to [[Note#^blockid]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note#^blockid]]" in result

    def test_embed_preserved(self):
        """Embed syntax ![[...]] should be preserved."""
        input_text = "Embed: ![[image.jpg]]\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "![[image.jpg]]" in result

    def test_embed_with_alias_preserved(self):
        """Embeds with aliases should be preserved."""
        input_text = "Embed: ![[image.jpg|caption]]\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "![[image.jpg|caption]]" in result

    def test_wikilinks_in_list(self):
        """Wikilinks in lists should be preserved."""
        input_text = "- [[Note]]\n- [[Other|alias]]\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note]]" in result
        assert "[[Other|alias]]" in result

    def test_wikilink_in_markdown_link_text(self):
        """Wikilinks inside markdown link text should not be duplicated."""
        input_text = "[![[image.jpg]]](http://example.com)\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == "[![[image.jpg]]](http://example.com)\n"
        # Critical: no duplication
        assert result.count("[[image.jpg]]") == 1

    def test_wikilink_formatting_is_idempotent(self):
        """Multiple format passes should produce identical output."""
        input_text = "[![[nested.jpg]]](http://example.com)\n"
        result1 = mdformat.text(input_text, extensions={"space_control"})
        result2 = mdformat.text(result1, extensions={"space_control"})
        result3 = mdformat.text(result2, extensions={"space_control"})
        assert result1 == result2 == result3

    def test_same_page_heading_link(self):
        """Same-page heading links should be preserved."""
        input_text = "Jump to [[#Section]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[#Section]]" in result

    def test_same_page_block_ref(self):
        """Same-page block references should be preserved."""
        input_text = "See [[#^blockid]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[#^blockid]]" in result

    def test_complex_wikilink(self):
        """Complex wikilink with heading, block ref, and alias."""
        input_text = "See [[Note#Section#^blockid|alias]].\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "[[Note#Section#^blockid|alias]]" in result


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
