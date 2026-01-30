"""Tests for soft break to hard break conversion."""

import mdformat


class TestSoftBreakConversion:
    """Tests for converting soft breaks to hard breaks (backslash + newline)."""

    def test_soft_break_gets_backslash(self):
        """Plain newline within a paragraph should become backslash + newline."""
        input_text = "Line one\nLine two.\n"
        expected = "Line one\\\nLine two.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_soft_breaks(self):
        """Multiple soft breaks in a paragraph should all get backslashes."""
        input_text = "Line one\nLine two\nLine three.\n"
        expected = "Line one\\\nLine two\\\nLine three.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_bold_label_lines(self):
        """AI-generated bold label lines should preserve line breaks."""
        input_text = "**Date**: January 30\n**Time**: 2:00 PM\n**Location**: Room 101\n"
        expected = "**Date**: January 30\\\n**Time**: 2:00 PM\\\n**Location**: Room 101\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_paragraph_break_unaffected(self):
        """Double newline (paragraph break) should not be affected."""
        input_text = "First paragraph.\n\nSecond paragraph.\n"
        expected = "First paragraph.\n\nSecond paragraph.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_existing_hard_break_preserved(self):
        """Lines already ending with backslash should remain correct."""
        input_text = "Line one\\\nLine two.\n"
        expected = "Line one\\\nLine two.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_code_block_newlines_unaffected(self):
        """Newlines inside fenced code blocks should not get backslashes."""
        input_text = "```\nline one\nline two\n```\n"
        expected = "```\nline one\nline two\n```\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_single_line_paragraph_unaffected(self):
        """A single-line paragraph should not be modified."""
        input_text = "Just one line.\n"
        expected = "Just one line.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_soft_break_in_list_item(self):
        """Soft breaks within list items should get backslashes."""
        input_text = "- Line one\n  Line two\n"
        expected = "- Line one\\\n  Line two\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected
