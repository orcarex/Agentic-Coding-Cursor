"""
Utility: Replace File Content Range

- Input: working_dir (str), target_file (str), start_line (int), end_line (int), new_content (str)
- Output: (success: bool, message: str | None)
- Behavior: Lines are 1-indexed and inclusive. Inserts new_content as-is; caller must include trailing newlines as desired.
"""

from __future__ import annotations

import os
from typing import Tuple, Optional


def _resolve_path(working_dir: str, target_file: str) -> str:
    if os.path.isabs(target_file):
        return target_file
    return os.path.abspath(os.path.join(working_dir, target_file))


def replace_range(
    working_dir: str,
    target_file: str,
    start_line: int,
    end_line: int,
    new_content: str,
) -> Tuple[bool, Optional[str]]:
    try:
        if start_line <= 0 or end_line <= 0 or end_line < start_line:
            return False, "Invalid line range"
        abs_path = _resolve_path(working_dir, target_file)
        if not os.path.exists(abs_path):
            return False, "File does not exist"
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        s = max(1, start_line)
        e = min(len(lines), end_line)
        prefix = lines[: s - 1]
        suffix = lines[e:]
        replacement_lines = [new_content] if "\n" not in new_content else list(new_content)
        # If new_content is a whole string, write directly; else assume it's already lines
        new_text = "".join(prefix) + (new_content if isinstance(new_content, str) else "".join(replacement_lines)) + "".join(suffix)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    ok, msg = replace_range(os.getcwd(), "_tmp_insert_test.txt", 1, 1, "replaced line\n")
    print("success=", ok, "msg=", msg)
