"""
Utility: Directory Operations (Tree Listing)

- Input: working_dir (str), relative_workspace_path (str)
- Output: (success: bool, tree_str: str)
"""

from __future__ import annotations

import os
from typing import Tuple


def _resolve_path(working_dir: str, relative_workspace_path: str) -> str:
    if os.path.isabs(relative_workspace_path):
        return relative_workspace_path
    return os.path.abspath(os.path.join(working_dir, relative_workspace_path))


def _tree(path: str, prefix: str = "") -> str:
    try:
        entries = sorted(os.listdir(path))
    except Exception:
        return f"{prefix}[unreadable]\n"

    lines = []
    for i, name in enumerate(entries):
        full = os.path.join(path, name)
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{name}\n")
        if os.path.isdir(full):
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.append(_tree(full, prefix + extension))
    return "".join(lines)


def list_directory(working_dir: str, relative_workspace_path: str) -> Tuple[bool, str]:
    abs_path = _resolve_path(working_dir, relative_workspace_path)
    if not os.path.exists(abs_path):
        return False, "[path does not exist]\n"
    if not os.path.isdir(abs_path):
        return False, "[not a directory]\n"
    header = os.path.basename(abs_path) or abs_path
    tree_str = header + "\n" + _tree(abs_path)
    return True, tree_str


if __name__ == "__main__":
    ok, tree = list_directory(os.getcwd(), ".")
    print(tree)
