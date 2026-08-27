#!/usr/bin/env python3
"""Find '@' or '\\' immediately followed by CJK characters/punctuation.

In Texinfo '@' is the escape character: '@，' or '@中' parses as an
undefined command and breaks compilation. Inside @math{}/@tex blocks a
'\\' control-space before Chinese punctuation has the same effect as in
LaTeX. This detects both.

Usage: python find_at_before_cjk.py <file.texi>

Exit codes:
  0 — no issues found
  1 — one or more issues found
  2 — usage error
"""

import re
import sys
from pathlib import Path

CJK_PUNCT = "，。；：（）？！、·“”‘’……—《》【】"
# CJK ideographs + fullwidth forms + CJK punctuation
CJK_CLASS = r"\u3000-\u303f\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef"

# '@' directly followed by a CJK char (not @code{...} which is ASCII-headed)
AT_BEFORE_CJK = re.compile(r"@([" + CJK_CLASS + "])")
# '\' directly followed by CJK punctuation (control-space bug, in @math/@tex)
BS_BEFORE_CJK = re.compile(r"\\([" + CJK_CLASS + "])")

# Environments where '@' is literal text, not an escape
VERBATIM_ENVS = {"verbatim", "verbatim*"}


def find_issues(filepath: str) -> int:
    text = Path(filepath).read_text(encoding="utf-8")
    issues = []
    in_verbatim = False

    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if any(stripped == "@end " + e or stripped.startswith("@end " + e)
               for e in VERBATIM_ENVS):
            in_verbatim = False
            continue
        if in_verbatim:
            continue
        if any(stripped == "@" + e or stripped.startswith("@" + e)
               for e in VERBATIM_ENVS):
            in_verbatim = True
            continue

        for m in AT_BEFORE_CJK.finditer(line):
            issues.append((lineno, m.start() + 1, "@" + m.group(1), line))
        for m in BS_BEFORE_CJK.finditer(line):
            issues.append((lineno, m.start() + 1, "\\" + m.group(1), line))

    if not issues:
        print("No @/\\ before CJK issues found.")
        return 0

    print(f"Found {len(issues)} issue(s):\n")
    for lineno, col, tok, content in issues:
        print(f"  Line {lineno}:{col}  token='{tok}'")
        print(f"    {content.rstrip()}")
    print("\nFix: '@x' -> '@code{x}@' style separation; remove stray "
          "'\\' before Chinese punctuation.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.texi>", file=sys.stderr)
        sys.exit(2)
    sys.exit(find_issues(sys.argv[1]))
