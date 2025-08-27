"""
Utility: Read File

- Input: target_file (str), working_dir (str)
- Output: (success: bool, content: str, error: str | None)
- Behavior: Resolves target_file relative to working_dir if not absolute.
"""

from __future__ import annotations

import os
from typing import Tuple, Optional


def _resolve_path(working_dir: str, target_file: str) -> str:
    if os.path.isabs(target_file):
        return target_file
    return os.path.abspath(os.path.join(working_dir, target_file))


def read_file(working_dir: str, target_file: str) -> Tuple[bool, str, Optional[str]]:
    try:
        abs_path = _resolve_path(working_dir, target_file)
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return True, content, None
    except FileNotFoundError as e:
        return False, "", f"File not found: {e}"
    except UnicodeDecodeError as e:
        return False, "", f"Unicode decode error: {e}"
    except Exception as e:
        return False, "", f"Unexpected error: {e}"


if __name__ == "__main__":
    wd = os.getcwd()
    ok, content, err = read_file(wd, __file__)
    print("success=", ok)
    print("error=", err)
    print("content preview=", content[:80])
