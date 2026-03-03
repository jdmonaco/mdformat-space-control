"""Tests for soft break joining (space normalization)."""

import mdformat


class TestSoftBreakJoining:
    """Tests for joining soft breaks into single lines."""

    def test_soft_break_joined_with_space(self):
        """Plain newline within a paragraph should be joined with a space."""
        input_text = "Line one\nLine two.\n"
        expected = "Line one Line two.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_multiple_soft_breaks(self):
        """Multiple soft breaks in a paragraph should all be joined."""
        input_text = "Line one\nLine two\nLine three.\n"
        expected = "Line one Line two Line three.\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_bold_label_lines(self):
        """Bold label lines with soft breaks should be joined."""
        input_text = "**Date**: January 30\n**Time**: 2:00 PM\n**Location**: Room 101\n"
        expected = "**Date**: January 30 **Time**: 2:00 PM **Location**: Room 101\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_bold_label_with_description(self):
        """Bold label followed by description on next line should be joined."""
        input_text = "**Label:**\nDescription text.\n"
        expected = "**Label:** Description text.\n"
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
        """Newlines inside fenced code blocks should not be joined."""
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
        """Soft breaks within list items should be joined."""
        input_text = "- Line one\n  Line two\n"
        expected = "- Line one Line two\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_list_item_continuation_text(self):
        """List item with indented continuation text should be joined."""
        input_text = "- First line\n  continuation text\n"
        expected = "- First line continuation text\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_blockquote_soft_break_joining(self):
        """Soft breaks in blockquotes should be joined."""
        input_text = "> Line one\n> Line two\n"
        expected = "> Line one Line two\n"
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_idempotency(self):
        """Running formatter twice on joined output should produce identical output."""
        input_text = "Line one\nLine two\nLine three.\n"
        first_pass = mdformat.text(input_text, extensions={"space_control"})
        second_pass = mdformat.text(first_pass, extensions={"space_control"})
        assert first_pass == second_pass
