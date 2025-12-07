from typing import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render
from mdformat.renderer._context import (
    make_render_children, 
    get_list_marker_type,
    is_tight_list_item,
    is_tight_list
)


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser, e.g. by adding a plugin: `mdit.use(myplugin)`"""
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


def _render_list_item(node: RenderTreeNode, context: RenderContext) -> str:
    """Return one list item as string with appropriate formatting.

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
    """Render bullet list with appropriate formatting."""
    marker_type = get_list_marker_type(node)
    first_line_indent = " "
    indent = " " * len(marker_type + first_line_indent)
    
    # Check if this should be a loose list
    is_loose = list_has_loose_items(node)
    block_separator = "\n\n" if is_loose else "\n"

    with context.indented(len(indent)):
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
                formatted_lines.append(f"{indent}{line}" if line else "")
            text += "\n".join(formatted_lines)
            if child_idx < len(node.children) - 1:
                text += block_separator
    return text


def _render_ordered_list(node: RenderTreeNode, context: RenderContext) -> str:
    """Render ordered list with appropriate formatting."""
    first_line_indent = " "
    list_len = len(node.children)
    starting_number = node.attrs.get("start")
    if starting_number is None:
        starting_number = 1
    assert isinstance(starting_number, int)
    
    # Check if this should be a loose list
    is_loose = list_has_loose_items(node)
    block_separator = "\n\n" if is_loose else "\n"

    longest_marker_len = len(str(starting_number + list_len - 1) + "." + first_line_indent)
    indent = " " * longest_marker_len
    
    with context.indented(longest_marker_len):
        text = ""
        for child_idx, child in enumerate(node.children):
            list_marker = f"{starting_number + child_idx}."
            marker_len = len(list_marker + first_line_indent)
            
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
                formatted_lines.append(f"{indent}{line}" if line else "")
            
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