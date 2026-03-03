"""Tests for smart dash conversion (-- → en-dash, --- → em-dash)."""

import mdformat
import pytest


class TestDashConversionBasic:
    """Tests for basic dash sequence conversion."""

    def test_em_dash_conversion(self):
        """Triple dashes should convert to em-dash."""
        input_text = "word---word\n"
        expected = "word\u2014word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_en_dash_conversion(self):
        """Double dashes should convert to en-dash."""
        input_text = "word--word\n"
        expected = "word\u2013word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_em_dash_with_spaces(self):
        """Em-dash with surrounding spaces."""
        input_text = "word --- word\n"
        expected = "word \u2014 word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_en_dash_with_spaces(self):
        """En-dash with surrounding spaces."""
        input_text = "word -- word\n"
        expected = "word \u2013 word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_mixed_dashes(self):
        """Both em-dash and en-dash in same line."""
        input_text = "first--second---third\n"
        expected = "first\u2013second\u2014third\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_en_dashes(self):
        """Multiple en-dashes in same line."""
        input_text = "a--b and c--d\n"
        expected = "a\u2013b and c\u2013d\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_em_dash_in_sentence(self):
        """Em-dash used in a typical sentence."""
        input_text = "The result---unexpected as it was---changed everything.\n"
        expected = "The result\u2014unexpected as it was\u2014changed everything.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_en_dash_range(self):
        """En-dash used for a numeric range."""
        input_text = "Pages 10--20\n"
        expected = "Pages 10\u201320\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestDashConversionPreserved:
    """Tests for contexts where dashes should NOT be converted."""

    def test_fenced_code_block_backticks(self):
        """Dashes inside backtick-fenced code blocks should be preserved."""
        input_text = "Text.\n\n```\na--b and c---d\n```\n"
        expected = "Text.\n\n```\na--b and c---d\n```\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_fenced_code_block_tildes(self):
        """Dashes inside tilde-fenced code blocks should be preserved.

        Note: mdformat normalizes tilde fences to backtick fences.
        """
        input_text = "Text.\n\n~~~\na--b\n~~~\n"
        expected = "Text.\n\n```\na--b\n```\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_inline_code_preserved(self):
        """Dashes inside inline code spans should be preserved."""
        input_text = "Use `a--b` for ranges.\n"
        expected = "Use `a--b` for ranges.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_inline_code_double_backtick(self):
        """Dashes inside double-backtick inline code should be preserved.

        Note: mdformat normalizes double backticks to single backticks.
        """
        input_text = "Use ``a---b`` for dashes.\n"
        expected = "Use `a---b` for dashes.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_inline_code_with_surrounding_dashes(self):
        """Dashes outside inline code should convert, inside should not."""
        input_text = "before--`code--here`--after\n"
        expected = "before\u2013`code--here`\u2013after\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_thematic_break_preserved(self):
        """Thematic breaks (---) should not be converted."""
        input_text = "Above.\n\n---\n\nBelow.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        # mdformat renders thematic breaks; the break itself should remain
        assert "\u2014" not in result
        assert "\u2013" not in result

    def test_frontmatter_delimiters_preserved(self):
        """Frontmatter delimiters (---) should not be converted."""
        input_text = "---\ntitle: Test\n---\n\nContent with---em-dash.\n"
        expected = "---\ntitle: Test\n---\nContent with\u2014em-dash.\n"
        result = mdformat.text(
            input_text, extensions={"space_control", "frontmatter"}
        )
        assert result == expected

    def test_code_block_with_language(self):
        """Code block with language specifier preserves dashes."""
        input_text = "Text.\n\n```python\nx = a--b\n```\n"
        expected = "Text.\n\n```python\nx = a--b\n```\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestDashConversionEdgeCases:
    """Tests for edge cases in dash conversion."""

    def test_four_dashes_unchanged(self):
        """Four or more dashes should not be converted."""
        input_text = "word----word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "\u2014" not in result
        assert "\u2013" not in result

    def test_five_dashes_unchanged(self):
        """Five dashes should not be converted."""
        input_text = "word-----word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "\u2014" not in result
        assert "\u2013" not in result

    def test_single_hyphen_unchanged(self):
        """Single hyphen should not be affected."""
        input_text = "hyphen-ated word\n"
        expected = "hyphen-ated word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_line_of_only_dashes(self):
        """A line of only dashes should not be converted."""
        # Note: mdformat may interpret this as a thematic break
        input_text = "Above.\n\n----\n\nBelow.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "\u2014" not in result
        assert "\u2013" not in result

    def test_idempotency(self):
        """Running conversion twice should produce same result."""
        input_text = "word--word and word---word\n"
        first_pass = mdformat.text(input_text, extensions={"space_control"})
        second_pass = mdformat.text(first_pass, extensions={"space_control"})
        assert first_pass == second_pass

    def test_already_unicode_en_dash(self):
        """Already-existing Unicode en-dash should pass through."""
        input_text = "word\u2013word\n"
        expected = "word\u2013word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_already_unicode_em_dash(self):
        """Already-existing Unicode em-dash should pass through."""
        input_text = "word\u2014word\n"
        expected = "word\u2014word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_dash_at_start_of_line(self):
        """Dashes at start of line in text context should convert."""
        # Note: "-- text" at start could be interpreted as list by mdformat
        # Test within a paragraph context
        input_text = "Start.\n\nSo---yes.\n"
        expected = "Start.\n\nSo\u2014yes.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_dashes_in_list_item(self):
        """Dashes inside list item content should convert."""
        input_text = "- Item with--en-dash\n- Item with---em-dash\n"
        expected = "- Item with\u2013en-dash\n- Item with\u2014em-dash\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_dashes_in_blockquote(self):
        """Dashes inside blockquotes should convert."""
        input_text = "> The result---was clear.\n"
        expected = "> The result\u2014was clear.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_dashes_in_heading(self):
        """Dashes inside headings should convert."""
        input_text = "# Title---Subtitle\n"
        expected = "# Title\u2014Subtitle\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestDashConversionFunction:
    """Direct tests for _convert_dash_sequences function."""

    def test_basic_em_dash(self):
        """Direct function test: triple dashes to em-dash."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("a---b") == "a\u2014b"

    def test_basic_en_dash(self):
        """Direct function test: double dashes to en-dash."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("a--b") == "a\u2013b"

    def test_code_block_skipped(self):
        """Direct function test: code blocks are skipped."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "before--after\n```\ncode--here\n```\nmore--text"
        expected = "before\u2013after\n```\ncode--here\n```\nmore\u2013text"
        assert _convert_dash_sequences(text) == expected

    def test_inline_code_preserved(self):
        """Direct function test: inline code is preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "text--`code--span`--text"
        expected = "text\u2013`code--span`\u2013text"
        assert _convert_dash_sequences(text) == expected

    def test_only_dashes_line_skipped(self):
        """Direct function test: line of only dashes is skipped."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "text--here\n---\nmore--text"
        expected = "text\u2013here\n---\nmore\u2013text"
        assert _convert_dash_sequences(text) == expected

    def test_four_dashes_not_matched(self):
        """Direct function test: four dashes remain unchanged."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("a----b") == "a----b"

    def test_multiple_inline_code_spans(self):
        """Direct function test: multiple inline code spans preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "`a--b` and `c---d` with e--f"
        expected = "`a--b` and `c---d` with e\u2013f"
        assert _convert_dash_sequences(text) == expected

    def test_empty_string(self):
        """Direct function test: empty string."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("") == ""

    def test_html_comment_preserved(self):
        """Direct function test: HTML comments are preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("<!-- comment -->") == "<!-- comment -->"

    def test_html_triple_dash_comment_preserved(self):
        """Direct function test: triple-dash HTML comments are preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        assert _convert_dash_sequences("<!--- comment --->") == "<!--- comment --->"

    def test_html_tag_with_dashes_preserved(self):
        """Direct function test: HTML tags with dash attributes are preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = '<div data-value="test--value">'
        assert _convert_dash_sequences(text) == text

    def test_html_self_closing_tag_preserved(self):
        """Direct function test: self-closing HTML tags with dashes preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = '<img alt="a--b" />'
        assert _convert_dash_sequences(text) == text

    def test_html_comment_with_surrounding_dashes(self):
        """Direct function test: dashes outside HTML convert, inside preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "word--word <!-- comment --> word---word"
        expected = "word\u2013word <!-- comment --> word\u2014word"
        assert _convert_dash_sequences(text) == expected

    def test_multiline_html_comment_preserved(self):
        """Direct function test: multi-line HTML comments are preserved."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "<!--\ncomment with--dashes\n-->"
        assert _convert_dash_sequences(text) == text

    def test_multiline_html_comment_with_surrounding_text(self):
        """Direct function test: text around multi-line HTML comment converts."""
        from mdformat_space_control.plugin import _convert_dash_sequences

        text = "before--after\n<!--\ncomment--here\n-->\nmore--text"
        expected = "before\u2013after\n<!--\ncomment--here\n-->\nmore\u2013text"
        assert _convert_dash_sequences(text) == expected


class TestDashConversionHTML:
    """Tests for HTML comment and tag preservation through mdformat."""

    def test_single_line_html_comment(self):
        """Single-line HTML comment should be preserved."""
        input_text = "<!-- comment -->\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "<!--" in result
        assert "-->" in result
        assert "\u2013" not in result
        assert "\u2014" not in result

    def test_triple_dash_comment(self):
        """Triple-dash HTML comment should be preserved."""
        input_text = "<!--- comment --->\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "<!---" in result
        assert "--->" in result
        assert "\u2014" not in result

    def test_block_level_html_comment(self):
        """Block-level HTML comment (own paragraph) should be preserved."""
        input_text = "Text.\n\n<!-- block comment -->\n\nMore text.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "<!-- block comment -->" in result

    def test_inline_html_comment_with_dashes(self):
        """Dashes outside HTML comment convert; comment preserved."""
        input_text = "Text--here <!-- comment --> more---text.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "<!-- comment -->" in result
        assert "\u2013" in result  # en-dash from --
        assert "\u2014" in result  # em-dash from ---

    def test_multi_line_html_comment(self):
        """Multi-line HTML comment should be preserved."""
        input_text = "Text.\n\n<!--\ncomment with--dashes\n-->\n\nMore text.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert "\u2013" not in result
        assert "\u2014" not in result

    def test_html_tag_with_dash_attributes(self):
        """HTML tags with dash-containing attributes should be preserved."""
        input_text = '<div data-value="test--value">\n\nContent.\n\n</div>\n'
        result = mdformat.text(input_text, extensions={"space_control"})
        assert 'data-value="test--value"' in result

    def test_self_closing_tag_with_dashes(self):
        """Self-closing HTML tags with dashes should be preserved."""
        input_text = '<img alt="a--b" />\n'
        result = mdformat.text(input_text, extensions={"space_control"})
        assert 'alt="a--b"' in result

    def test_dashes_outside_html_still_convert(self):
        """Dashes outside HTML elements should still convert normally."""
        input_text = "word--word and word---word\n"
        expected = "word\u2013word and word\u2014word\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected
