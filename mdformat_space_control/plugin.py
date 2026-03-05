"""mdformat-space-control plugin implementation.

Provides custom renderers that combine:
- EditorConfig-based indentation settings
- Tight list formatting with multi-paragraph awareness
- Frontmatter spacing normalization
- Smart dash conversion (-- → en-dash, --- → em-dash)
- Trailing whitespace removal (outside code blocks)
- Wikilink preservation ([[link]] and ![[embed]] syntax)
"""

import re
from typing import Mapping

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Postprocess, Render
from mdformat.renderer._context import (
    make_render_children,
    get_list_marker_type,
)

from mdformat_space_control.config import get_indent_config


# Wikilink pattern for Obsidian-style links:
#   [[page]], [[page|alias]], [[page#heading]], [[page#^blockid]],
#   [[#heading]], ![[embed]], ![[image.jpg]], etc.
# Pattern breakdown:
#   !?                        - optional embed prefix
#   \[\[                      - opening [[
#   [^\[\]|]*                 - target (no brackets or pipe)
#   (?:#[^\[\]|]*)*           - zero or more #heading/#^block sections
#   (?:\|[^\[\]]+)?           - optional |alias
#   \]\]                      - closing ]]
WIKILINK_PATTERN = re.compile(r"!?\[\[([^\[\]|]*(?:#[^\[\]|]*)*)(?:\|[^\[\]]+)?\]\]")


def _wikilink_rule(state: StateInline, silent: bool) -> bool:
    """Parse wikilinks at the current position.

    Matches Obsidian-style wikilinks including:
    - [[page]] and [[page|alias]]
    - [[page#heading]] and [[page#^blockid]]
    - [[#heading]] (same-page links)
    - ![[embed]] and ![[image.jpg]]

    By running before the link parser, wikilinks inside markdown link text
    are correctly preserved rather than being extracted and duplicated.
    """
    match = WIKILINK_PATTERN.match(state.src, state.pos)
    if not match:
        return False

    if not silent:
        token = state.push("wikilink", "", 0)
        token.content = match.group(0)

    state.pos = match.end()
    return True


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the markdown-it parser.

    Adds wikilink parsing support for Obsidian-style [[link]] and ![[embed]]
    syntax. The rule runs before the link parser to correctly handle wikilinks
    that appear inside markdown link text.
    """
    mdit.inline.ruler.before("link", "wikilink", _wikilink_rule)


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


def _is_task_list_item(node: RenderTreeNode) -> bool:
    """Check if a list item is a GFM task list item.

    When mdformat-gfm is installed, the tasklists markdown-it plugin annotates
    task list items with a 'task-list-item' CSS class.
    """
    classes = node.attrs.get("class", "")
    return isinstance(classes, str) and "task-list-item" in classes


def _extract_task_checkbox(node: RenderTreeNode) -> str | None:
    """Extract and remove the task checkbox HTML from a task list item node.

    The tasklists markdown-it plugin injects an HTML <input> element as the
    first child of the inline token. This function extracts the checked state
    and removes the HTML node so it doesn't appear in the rendered output.

    Returns:
        "x" for checked, " " for unchecked, or None if not a task list item.
    """
    if not _is_task_list_item(node):
        return None

    paragraph_node = node.children[0]
    inline_node = paragraph_node.children[0]
    if inline_node.type != "inline" or not inline_node.children:
        return None

    html_inline_node = inline_node.children[0]
    if 'class="task-list-item-checkbox"' not in getattr(html_inline_node, "content", ""):
        return None

    # Remove the HTML checkbox node before rendering
    inline_node.children.remove(html_inline_node)
    return "x" if 'checked="checked"' in html_inline_node.content else " "


def _render_list_item(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a list item with appropriate tight/loose formatting.

    For single-paragraph items in tight lists, use tight formatting.
    For multi-paragraph items, preserve loose formatting.

    Handles GFM task list items when mdformat-gfm is installed: extracts the
    checkbox state from the HTML token and prepends [x] or [ ] to the output.
    """
    # Extract task checkbox before rendering (mutates the node tree)
    checkmark = _extract_task_checkbox(node)

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

    if checkmark is not None:
        # Strip leading space entities left after removing the HTML checkbox node
        text = re.sub(r"^(&#32;)+", "", text)
        text = text.lstrip()
        return f"[{checkmark}] {text}"

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


def _render_wikilink(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a wikilink token, preserving it unchanged."""
    return node.content


def _render_softbreak(node: RenderTreeNode, context: RenderContext) -> str:
    """Join soft breaks into a single line.

    Soft breaks (plain newlines within paragraphs) are editor-inserted
    line wraps, not intentional visible breaks. Join them with a space
    to normalize to single-line paragraphs. This matches CommonMark
    rendering behavior where soft breaks produce spaces in HTML output.
    """
    return " "


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "list_item": _render_list_item,
    "bullet_list": _render_bullet_list,
    "ordered_list": _render_ordered_list,
    "wikilink": _render_wikilink,
    "softbreak": _render_softbreak,
}


def _repair_escaped_links(text: str) -> str:
    """Repair escaped markdown links that span multiple lines.

    mdformat escapes brackets when links are malformed (contain newlines).
    This function detects these patterns and reconstructs valid links by:
    - Removing newlines immediately after \\[
    - Removing newlines immediately before \\](
    - Unescaping remaining bracket escapes to form valid links

    Pattern: \\[content\\](url) spanning multiple lines
    Result: [content](url) with internal newlines preserved

    Handles standard markdown link syntax including image embeds inside links,
    which is common in web-clipped content.
    """
    # Step 1: Remove newlines immediately after escaped opening bracket
    # \[ followed by one or more newlines → [
    text = re.sub(r"\\\[\n+", "[", text)

    # Step 2: Remove newlines immediately before escaped closing bracket with URL
    # one or more newlines followed by \]( → ](
    text = re.sub(r"\n+\\\]\(", "](", text)

    # Step 3: Unescape \]( that follows non-backslash character
    # This handles cases where only the opening had newlines
    text = re.sub(r"(?<=[^\\\n])\\\]\(", "](", text)

    # Step 4: Unescape \[ at start of a repaired link
    # Pattern: \[ followed by any content ending with ](
    # This handles cases where only the closing had newlines
    # Use non-greedy match to find the first ]( after \[
    text = re.sub(r"\\\[(.+?)\]\(", r"[\1](", text)

    return text


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


def _convert_dash_sequences(text: str) -> str:
    """Convert markdown dash sequences to Unicode em-dash and en-dash.

    Converts ``---`` to em-dash (U+2014) and ``--`` to en-dash (U+2013).
    Preserves dashes inside fenced code blocks, inline code spans,
    HTML comments, and HTML tags.
    Skips lines that are only dashes (thematic breaks, frontmatter delimiters).

    Em-dash is matched first (longer sequence) to prevent ``---`` from being
    partially converted as en-dash + hyphen.
    """
    # Patterns for inline code span placeholders
    inline_code_re = re.compile(r"(`+)(.+?)\1")

    # HTML protection patterns
    html_comment_re = re.compile(r"<!--.*?-->")
    html_tag_re = re.compile(r"<[^>]+>")

    # Dash conversion patterns: negative lookahead/behind prevent matching
    # 4+ dash sequences (e.g., ---- horizontal rules in some contexts)
    em_dash_re = re.compile(r"(?<!-)---(?!-)")
    en_dash_re = re.compile(r"(?<!-)--(?!-)")

    # CLI option pattern: --word or ---word preceded by whitespace or line start
    cli_option_re = re.compile(r"(?<=\s)-{2,3}(?=\w)")


    # URI pattern: protect scheme://... tokens from dash conversion
    uri_re = re.compile(r"\w+://\S+")

    # Lines that are only dashes (thematic breaks, frontmatter delimiters),
    # separator lines starting/ending with dashes (e.g., "--- Title ---"),
    # or GFM table separator rows (e.g., "| -- | -- |" or "| --- | --- |")
    only_dashes_re = re.compile(r"^-{2,}\s*$")
    separator_line_re = re.compile(r"^-{2,}\s+.*\s+-{2,}\s*$")
    table_sep_re = re.compile(r"^\|[\s\-:|]+\|$")

    lines = text.split("\n")
    result = []
    in_code_block = False
    in_html_comment = False

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            result.append(line)
        elif in_code_block:
            result.append(line)
        elif in_html_comment:
            # Inside a multi-line HTML comment, skip dash conversion
            if "-->" in line:
                in_html_comment = False
            result.append(line)
        elif (only_dashes_re.match(line) or separator_line_re.match(stripped)
              or table_sep_re.match(stripped)):
            result.append(line)
        else:
            # Check for multi-line HTML comment opening (no closing on same line)
            if "<!--" in line and "-->" not in line:
                in_html_comment = True
                result.append(line)
                continue

            # Protect inline code spans and HTML elements with placeholders
            placeholders = []

            def _save_placeholder(m: re.Match) -> str:
                placeholders.append(m.group(0))
                return f"\x00CODE{len(placeholders) - 1}\x00"

            protected = inline_code_re.sub(_save_placeholder, line)

            # Protect HTML comments first (longer matches), then tags
            protected = html_comment_re.sub(_save_placeholder, protected)
            protected = html_tag_re.sub(_save_placeholder, protected)

            # Protect URIs (e.g., gs://bucket--name/path)
            protected = uri_re.sub(_save_placeholder, protected)

            # Protect CLI option dashes (e.g., --output, ---long-opt)
            protected = cli_option_re.sub(_save_placeholder, protected)

            # Convert em-dash first (longer match), then en-dash
            protected = em_dash_re.sub("\u2014", protected)
            protected = en_dash_re.sub("\u2013", protected)

            # Restore placeholders in reverse order so nested captures
            # (where a later placeholder's value contains an earlier tag)
            # are unwound correctly
            for i in range(len(placeholders) - 1, -1, -1):
                protected = protected.replace(
                    f"\x00CODE{i}\x00", placeholders[i]
                )

            result.append(protected)

    return "\n".join(result)


def _normalize_consecutive_blank_lines(text: str) -> str:
    """Limit consecutive blank lines to a maximum of 2.

    Collapses runs of 3+ empty lines down to 2 empty lines (3 newlines).
    Preserves content inside fenced code blocks.
    """
    lines = text.split("\n")
    result = []
    in_code_block = False
    consecutive_empty = 0

    for line in lines:
        # Track code block state
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block

        if in_code_block:
            # Preserve everything inside code blocks
            result.append(line)
            consecutive_empty = 0
        elif line == "":
            consecutive_empty += 1
            if consecutive_empty <= 2:
                result.append(line)
            # else: skip this empty line (collapse)
        else:
            consecutive_empty = 0
            result.append(line)

    return "\n".join(result)


def _postprocess_root(text: str, node: RenderTreeNode, context: RenderContext) -> str:
    """Combined postprocessor for all space control features.

    Applies the following transformations in order:
    1. Frontmatter spacing normalization
    2. Escaped link repair
    3. Smart dash conversion (-- → en-dash, --- → em-dash)
    4. Consecutive blank line normalization
    5. Trailing whitespace removal
    """
    # 1. Frontmatter spacing
    text = _normalize_frontmatter_spacing(text)

    # 2. Repair escaped links (before trailing whitespace removal)
    text = _repair_escaped_links(text)

    # 3. Smart dash conversion
    text = _convert_dash_sequences(text)

    # 4. Limit consecutive blank lines to 2
    text = _normalize_consecutive_blank_lines(text)

    # 5. Trailing whitespace removal
    text = _strip_trailing_whitespace(text)

    return text


# A mapping from syntax tree node type to a postprocessing function.
# Postprocessors run after rendering and can modify the output text.
POSTPROCESSORS: Mapping[str, Postprocess] = {
    "root": _postprocess_root,
}
