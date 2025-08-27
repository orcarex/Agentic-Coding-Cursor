"""
Utility: Remove File Content Range

- Input: working_dir (str), target_file (str), start_line (int | None), end_line (int | None)
- Output: (success: bool, message: str | None)
- Behavior: If both start_line and end_line are None, truncate file to empty.
  Lines are 1-indexed and inclusive.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple


def _resolve_path(working_dir: str, target_file: str) -> str:
    if os.path.isabs(target_file):
        return target_file
    return os.path.abspath(os.path.join(working_dir, target_file))


def remove_range(
    working_dir: str,
    target_file: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    try:
        abs_path = _resolve_path(working_dir, target_file)
        if not os.path.exists(abs_path):
            return False, "File does not exist"
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if start_line is None and end_line is None:
            new_lines = []
        else:
            s = 1 if start_line is None else max(1, start_line)
            e = len(lines) if end_line is None else max(s, end_line)
            new_lines = []
            for i, line in enumerate(lines, start=1):
                if s <= i <= e:
                    continue
                new_lines.append(line)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    ok, msg = remove_range(os.getcwd(), "_tmp_insert_test.txt", 1, 1)
    print("success=", ok, "msg=", msg)
