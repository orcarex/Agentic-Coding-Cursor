"""
Utility: Insert File

- Input: working_dir (str), target_file (str), content (str), line_number (int | None)
- Output: (success: bool, message: str | None)
- Behavior: Resolves target_file relative to working_dir. If line_number is None, append.
  If line_number <= 1, insert at top. If beyond end, append.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple


def _resolve_path(working_dir: str, target_file: str) -> str:
    if os.path.isabs(target_file):
        return target_file
    return os.path.abspath(os.path.join(working_dir, target_file))


def insert_file(
    working_dir: str,
    target_file: str,
    content: str,
    line_number: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    try:
        abs_path = _resolve_path(working_dir, target_file)
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
        if not os.path.exists(abs_path):
            # Create new file with content
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, None

        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if line_number is None:
            # Append
            lines.append(content)
        else:
            idx = max(0, min(len(lines), line_number - 1))
            lines.insert(idx, content)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    ok, msg = insert_file(os.getcwd(), "_tmp_insert_test.txt", "hello world\n", 1)
    print("success=", ok, "msg=", msg)
