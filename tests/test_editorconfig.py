"""Tests for EditorConfig integration."""

import tempfile
from pathlib import Path

import mdformat
import pytest

from mdformat_space_control import set_current_file


@pytest.fixture
def temp_project():
    """Create a temporary project directory with .editorconfig."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def create_editorconfig(project_dir: Path, content: str) -> None:
    """Create an .editorconfig file in the project directory."""
    editorconfig_path = project_dir / ".editorconfig"
    editorconfig_path.write_text(content)


def format_with_context(text: str, filepath: Path) -> str:
    """Format markdown text with file context set."""
    set_current_file(filepath)
    try:
        return mdformat.text(text, extensions={"space_control"})
    finally:
        set_current_file(None)


class TestFourSpaceIndent:
    """Tests for 4-space indentation."""

    def test_bullet_list_nested(self, temp_project):
        """Nested bullet lists should use 4-space indentation."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
- Item 1
  - Nested item
- Item 2
"""
        expected = """\
- Item 1
    - Nested item
- Item 2
"""
        result = format_with_context(input_text, md_file)
        assert result == expected

    def test_bullet_list_continuation(self, temp_project):
        """Continuation lines should use 4-space indentation."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
- Item 1
  with continuation
- Item 2
"""
        expected = """\
- Item 1
    with continuation
- Item 2
"""
        result = format_with_context(input_text, md_file)
        assert result == expected

    def test_ordered_list_nested(self, temp_project):
        """Nested ordered lists should use 4-space indentation."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
1. Item 1
   1. Nested item
2. Item 2
"""
        expected = """\
1. Item 1
    1. Nested item
2. Item 2
"""
        result = format_with_context(input_text, md_file)
        assert result == expected


class TestTabIndent:
    """Tests for tab indentation."""

    def test_bullet_list_with_tabs(self, temp_project):
        """Bullet lists should use tab indentation when configured."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = tab
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
- Item 1
  - Nested item
- Item 2
"""
        expected = """\
- Item 1
\t- Nested item
- Item 2
"""
        result = format_with_context(input_text, md_file)
        assert result == expected


class TestNoEditorConfig:
    """Tests for behavior when no .editorconfig is present."""

    def test_passthrough_without_editorconfig(self, temp_project):
        """Without .editorconfig, use mdformat defaults (2 spaces)."""
        # No .editorconfig file created
        md_file = temp_project / "test.md"

        input_text = """\
- Item 1
    - Nested item
- Item 2
"""
        # mdformat default is 2-space indentation
        expected = """\
- Item 1
  - Nested item
- Item 2
"""
        result = format_with_context(input_text, md_file)
        assert result == expected


class TestCwdFallback:
    """Tests for cwd-based fallback when no file context is set."""

    def test_uses_cwd_editorconfig(self, temp_project, monkeypatch):
        """Without file context, should use .editorconfig from cwd."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        # Change to temp_project directory
        monkeypatch.chdir(temp_project)

        # Clear any existing file context
        set_current_file(None)

        input_text = """\
- Item 1
  - Nested item
- Item 2
"""
        expected = """\
- Item 1
    - Nested item
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_fallback_without_editorconfig(self, temp_project, monkeypatch):
        """Without .editorconfig in cwd, use mdformat defaults."""
        # No .editorconfig file created
        monkeypatch.chdir(temp_project)
        set_current_file(None)

        input_text = """\
- Item 1
    - Nested item
- Item 2
"""
        # mdformat default is 2-space indentation
        expected = """\
- Item 1
  - Nested item
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected


class TestEditorConfigInheritance:
    """Tests for .editorconfig inheritance behavior."""

    def test_reads_parent_editorconfig(self, temp_project):
        """Should read .editorconfig from parent directories."""
        # Create .editorconfig in parent
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        # Create subdirectory
        subdir = temp_project / "docs"
        subdir.mkdir()
        md_file = subdir / "test.md"

        input_text = """\
- Item 1
  - Nested item
"""
        expected = """\
- Item 1
    - Nested item
"""
        result = format_with_context(input_text, md_file)
        assert result == expected


class TestTightListWithCustomIndent:
    """Integration tests for tight lists with custom indentation."""

    def test_tight_list_with_4space(self, temp_project):
        """Tight lists should work with 4-space indentation."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        # Loose list input should become tight
        input_text = """\
- Item 1

- Item 2

- Item 3
"""
        expected = """\
- Item 1
- Item 2
- Item 3
"""
        result = format_with_context(input_text, md_file)
        assert result == expected

    def test_multi_paragraph_with_custom_indent(self, temp_project):
        """Multi-paragraph items should use custom indentation."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
- First item with multiple paragraphs

  Second paragraph here

- Second item
"""
        expected = """\
- First item with multiple paragraphs

    Second paragraph here

- Second item
"""
        result = format_with_context(input_text, md_file)
        assert result == expected

    def test_nested_with_multi_paragraph(self, temp_project):
        """Nested lists with multi-paragraph items and custom indent."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )
        md_file = temp_project / "test.md"

        input_text = """\
- Outer item

  With second paragraph

  - Nested item
  - Another nested

- Second outer
"""
        expected = """\
- Outer item

    With second paragraph

    - Nested item
    - Another nested

- Second outer
"""
        result = format_with_context(input_text, md_file)
        assert result == expected
