"""mdformat-space-control plugin implementation.

Provides custom renderers that combine:
- EditorConfig-based indentation settings
- Tight list formatting with multi-paragraph awareness
- Frontmatter spacing normalization
- Trailing whitespace removal (outside code blocks)
"""

import re
from typing import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Postprocess, Render
from mdformat.renderer._context import (
    make_render_children,
    get_list_marker_type,
)

from mdformat_space_control.config import get_indent_config


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the markdown-it parser.

    This hook can be used to add markdown-it plugins or modify parser behavior.
    Currently a no-op for this plugin.
    """
    pass


def has_multiple_paragraphs(list_item_node: RenderTreeNode) -> bool:
    """Check if a list item has multiple paragraphs."""
    paragraph_count = 0
    for child in list_item_node.children:
        if child.type == "paragraph":
            paragraph_count += 1
            if paragraph_count > 1:
                return True
    return False


def list_has_loose_items(list_node: RenderTreeNode) -> bool:
    """Check if any item in the list has multiple paragraphs."""
    for item in list_node.children:
        if item.type == "list_item" and has_multiple_paragraphs(item):
            return True
    return False


def _get_indent(default_width: int) -> tuple[str, int]:
    """Get the indentation string and width based on editorconfig.

    Args:
        default_width: The default indent width (from marker length).

    Returns:
        Tuple of (indent_string, indent_width) where:
        - indent_string: The string to use for indentation
        - indent_width: The width in columns (for context.indented)
    """
    config = get_indent_config()
    if config is None:
        # No editorconfig - use default (passthrough behavior)
        return (" " * default_width, default_width)

    style, size = config
    if style == "tab":
        return ("\t", size)  # Tab char, but track column width
    else:
        return (" " * size, size)


def _render_list_item(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a list item with appropriate tight/loose formatting.

    For single-paragraph items in tight lists, use tight formatting.
    For multi-paragraph items, preserve loose formatting.
    """
    # Check if this item has multiple paragraphs
    if has_multiple_paragraphs(node):
        # Use loose list formatting for multi-paragraph items
        block_separator = "\n\n"
    else:
        # Check if we're in a loose list (any item has multiple paragraphs)
        parent = node.parent
        if parent and list_has_loose_items(parent):
            # Even single paragraph items get loose formatting in a loose list
            block_separator = "\n\n"
        else:
            # Use tight formatting
            block_separator = "\n"

    text = make_render_children(block_separator)(node, context)

    if not text.strip():
        return ""
    return text


def _render_bullet_list(node: RenderTreeNode, context: RenderContext) -> str:
    """Render bullet list with configurable indentation and tight formatting."""
    marker_type = get_list_marker_type(node)
    first_line_indent = " "
    default_indent_width = len(marker_type + first_line_indent)

    # Get configurable indent from editorconfig
    indent_str, indent_width = _get_indent(default_indent_width)

    # Determine tight/loose based on multi-paragraph items
    is_loose = list_has_loose_items(node)
    block_separator = "\n\n" if is_loose else "\n"

    with context.indented(indent_width):
        text = ""
        for child_idx, child in enumerate(node.children):
            list_item = child.render(context)
            formatted_lines = []
            line_iterator = iter(list_item.split("\n"))
            first_line = next(line_iterator, "")
            formatted_lines.append(
                f"{marker_type}{first_line_indent}{first_line}"
                if first_line
                else marker_type
            )
            for line in line_iterator:
                formatted_lines.append(f"{indent_str}{line}" if line else "")
            text += "\n".join(formatted_lines)
            if child_idx < len(node.children) - 1:
                text += block_separator
    return text


def _render_ordered_list(node: RenderTreeNode, context: RenderContext) -> str:
    """Render ordered list with configurable indentation and tight formatting."""
    first_line_indent = " "
    list_len = len(node.children)
    starting_number = node.attrs.get("start")
    if starting_number is None:
        starting_number = 1
    assert isinstance(starting_number, int)

    # Determine tight/loose based on multi-paragraph items
    is_loose = list_has_loose_items(node)
    block_separator = "\n\n" if is_loose else "\n"

    # Calculate default indent width based on longest marker
    longest_marker_len = len(
        str(starting_number + list_len - 1) + "." + first_line_indent
    )

    # Get configurable indent from editorconfig
    indent_str, indent_width = _get_indent(longest_marker_len)

    with context.indented(indent_width):
        text = ""
        for child_idx, child in enumerate(node.children):
            list_marker = f"{starting_number + child_idx}."

            list_item = child.render(context)
            formatted_lines = []
            line_iterator = iter(list_item.split("\n"))
            first_line = next(line_iterator, "")
            formatted_lines.append(
                f"{list_marker}{first_line_indent}{first_line}"
                if first_line
                else list_marker
            )

            for line in line_iterator:
                formatted_lines.append(f"{indent_str}{line}" if line else "")

            text += "\n".join(formatted_lines)
            if child_idx < len(node.children) - 1:
                text += block_separator
    return text


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "list_item": _render_list_item,
    "bullet_list": _render_bullet_list,
    "ordered_list": _render_ordered_list,
}


def _normalize_frontmatter_spacing(text: str) -> str:
    """Normalize spacing after YAML frontmatter.

    Removes all blank lines between frontmatter closing delimiter and the
    first content block, producing tight spacing universally.

    IMPORTANT: Only matches actual frontmatter (document starts with ---)
    not thematic breaks appearing mid-document.
    """
    # Only process if document starts with frontmatter opening delimiter
    if not text.startswith("---\n"):
        return text

    # Find the closing delimiter (second --- on its own line)
    # Pattern: opening --- at start, content, closing --- on its own line
    frontmatter_match = re.match(r"^---\n.*?\n(---\n)", text, flags=re.DOTALL)
    if not frontmatter_match:
        return text

    # Get position after closing delimiter
    closing_end = frontmatter_match.end(1)
    before_content = text[:closing_end]
    after_content = text[closing_end:]

    # Remove all blank lines after frontmatter (tight spacing for any content)
    after_content = re.sub(r"^\n+", "", after_content)

    return before_content + after_content


def _strip_trailing_whitespace(text: str) -> str:
    """Strip trailing whitespace, preserving code blocks.

    Fenced code blocks (``` or ~~~) preserve trailing whitespace
    since it may be semantically meaningful in code.
    """
    lines = text.split("\n")
    result = []
    in_code_block = False

    for line in lines:
        # Track fenced code block state
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            result.append(line.rstrip())  # Strip fence line itself
        elif in_code_block:
            # Preserve trailing whitespace inside code blocks
            result.append(line)
        else:
            # Strip trailing whitespace everywhere else
            result.append(line.rstrip())

    return "\n".join(result)


def _postprocess_root(text: str, node: RenderTreeNode, context: RenderContext) -> str:
    """Combined postprocessor for all space control features.

    Applies the following transformations in order:
    1. Frontmatter spacing normalization
    2. Trailing whitespace removal
    """
    # 1. Frontmatter spacing
    text = _normalize_frontmatter_spacing(text)

    # 2. Trailing whitespace removal
    text = _strip_trailing_whitespace(text)

    return text


# A mapping from syntax tree node type to a postprocessing function.
# Postprocessors run after rendering and can modify the output text.
POSTPROCESSORS: Mapping[str, Postprocess] = {
    "root": _postprocess_root,
}
