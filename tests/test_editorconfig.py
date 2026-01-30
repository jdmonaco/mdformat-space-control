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
- Item 1\\
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
        """Without .editorconfig in cwd or HOME, use mdformat defaults."""
        # No .editorconfig file created in temp_project
        monkeypatch.chdir(temp_project)

        # Also isolate from real HOME ~/.editorconfig
        fake_home = temp_project / "fake_home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

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


class TestHomeFallback:
    """Tests for HOME ~/.editorconfig fallback."""

    def test_home_fallback_when_cwd_outside_home(self, temp_project, monkeypatch):
        """Should use ~/.editorconfig when CWD has no .editorconfig and is outside HOME."""
        # Create a "fake home" directory with .editorconfig
        fake_home = temp_project / "fake_home"
        fake_home.mkdir()
        create_editorconfig(
            fake_home,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        # Create a separate "app" directory with NO .editorconfig
        app_dir = temp_project / "app"
        app_dir.mkdir()

        # Monkeypatch Path.home() to return fake_home
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Change CWD to app_dir (which has no .editorconfig)
        monkeypatch.chdir(app_dir)

        # Clear any file context
        set_current_file(None)

        input_text = """\
- Item 1
  - Nested item
- Item 2
"""
        # Should pick up 4-space indent from fake_home/.editorconfig
        expected = """\
- Item 1
    - Nested item
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control"})
        assert result == expected

    def test_no_fallback_when_explicit_file_set(self, temp_project, monkeypatch):
        """Should NOT use HOME fallback when explicit file context is set."""
        # Create a "fake home" with 4-space .editorconfig
        fake_home = temp_project / "fake_home"
        fake_home.mkdir()
        create_editorconfig(
            fake_home,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        # Create a project directory with NO .editorconfig
        project_dir = temp_project / "project"
        project_dir.mkdir()

        # Monkeypatch Path.home() to return fake_home
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        input_text = """\
- Item 1
  - Nested item
- Item 2
"""
        # With explicit file context set (even if in dir without .editorconfig),
        # HOME fallback should NOT be used - should use mdformat defaults (2 space)
        expected = """\
- Item 1
  - Nested item
- Item 2
"""
        result = format_with_context(input_text, project_dir / "test.md")
        assert result == expected

    def test_no_fallback_when_home_editorconfig_missing(self, temp_project, monkeypatch):
        """Should use defaults when HOME has no .editorconfig."""
        # Create a "fake home" with NO .editorconfig
        fake_home = temp_project / "fake_home"
        fake_home.mkdir()

        # Create a separate "app" directory with NO .editorconfig
        app_dir = temp_project / "app"
        app_dir.mkdir()

        # Monkeypatch Path.home() to return fake_home
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Change CWD to app_dir
        monkeypatch.chdir(app_dir)

        # Clear any file context
        set_current_file(None)

        input_text = """\
- Item 1
    - Nested item
- Item 2
"""
        # Should use mdformat defaults (2-space)
        expected = """\
- Item 1
  - Nested item
- Item 2
"""
        result = mdformat.text(input_text, extensions={"space_control"})
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


class TestEditorConfigDebug:
    """Tests documenting EditorConfig resolution behavior."""

    def test_cwd_differs_from_file_location(self, temp_project, monkeypatch):
        """When CWD differs from file location, explicit file context wins."""
        create_editorconfig(
            temp_project,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        other_dir = temp_project / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)

        md_file = temp_project / "doc.md"
        result = format_with_context("- A\n  - B\n", md_file)
        assert "    - B" in result  # 4-space indent

    def test_obsidian_scenario_no_file_context(self, temp_project, monkeypatch):
        """Document behavior when no file context is set (Obsidian-like)."""
        vault = temp_project / "vault"
        vault.mkdir()
        create_editorconfig(
            vault,
            """
root = true

[*.md]
indent_style = space
indent_size = 4
""",
        )

        app_dir = temp_project / "app"
        app_dir.mkdir()
        monkeypatch.chdir(app_dir)

        fake_home = temp_project / "fake_home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        set_current_file(None)

        # Without file context, vault's .editorconfig is NOT found
        result = mdformat.text("- A\n  - B\n", extensions={"space_control"})
        assert "  - B" in result  # 2-space default
