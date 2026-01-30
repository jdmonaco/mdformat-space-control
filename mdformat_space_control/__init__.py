"""An mdformat plugin for space control: EditorConfig indentation, tight lists, frontmatter spacing, and wikilinks."""

__version__ = "0.3.0"

from .config import (
    get_current_file,
    get_indent_config,
    set_current_file,
)
from .plugin import POSTPROCESSORS, RENDERERS, update_mdit

__all__ = [
    "POSTPROCESSORS",
    "RENDERERS",
    "update_mdit",
    "set_current_file",
    "get_current_file",
    "get_indent_config",
]
