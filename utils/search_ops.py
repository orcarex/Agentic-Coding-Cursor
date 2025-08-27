"""
Utility: Search Operations (grep-like)

- Input: query (str), case_sensitive (bool|None), include_pattern (str|None), exclude_pattern (str|None), working_dir (str)
- Output: (success: bool, results: list[dict], error: str | None)
- Behavior: Walks working_dir, filters filenames by include/exclude glob patterns, scans text files line-by-line for matches.
"""

from __future__ import annotations

import fnmatch
import os
import re
from typing import Dict, List, Optional, Tuple


_TEXT_EXTS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".js", ".ts", ".tsx", ".jsx", ".css", ".scss", ".html", ".sh",
}


def _is_text_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in _TEXT_EXTS or ext == ""


def grep_search(
    working_dir: str,
    query: str,
    case_sensitive: Optional[bool] = None,
    include_pattern: Optional[str] = None,
    exclude_pattern: Optional[str] = None,
) -> Tuple[bool, List[Dict], Optional[str]]:
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(query, flags)
    except re.error as e:
        return False, [], f"Invalid regex: {e}"

    results: List[Dict] = []
    for root, dirs, files in os.walk(working_dir):
        # Skip typical vendor/build dirs
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "venv", "__pycache__"}]
        for fname in files:
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, working_dir)
            if include_pattern and not fnmatch.fnmatch(rel, include_pattern):
                continue
            if exclude_pattern and fnmatch.fnmatch(rel, exclude_pattern):
                continue
            if not _is_text_file(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if regex.search(line):
                            results.append({
                                "file": rel,
                                "line": i,
                                "content": line.rstrip("\n"),
                            })
            except Exception:
                # Ignore unreadable files
                continue

    return True, results, None


if __name__ == "__main__":
    ok, res, err = grep_search(os.getcwd(), r"Design Doc", True, "**/*.md", None)
    print("success=", ok, "count=", len(res), "err=", err)
