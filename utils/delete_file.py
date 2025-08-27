"""
Utility: Delete File

- Input: working_dir (str), target_file (str)
- Output: (success: bool, message: str | None)
"""

from __future__ import annotations

import os
from typing import Tuple, Optional


def _resolve_path(working_dir: str, target_file: str) -> str:
    if os.path.isabs(target_file):
        return target_file
    return os.path.abspath(os.path.join(working_dir, target_file))


def delete_file(working_dir: str, target_file: str) -> Tuple[bool, Optional[str]]:
    try:
        abs_path = _resolve_path(working_dir, target_file)
        if not os.path.exists(abs_path):
            return False, "File does not exist"
        os.remove(abs_path)
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    ok, msg = delete_file(os.getcwd(), "_tmp_insert_test.txt")
    print("success=", ok, "msg=", msg)
