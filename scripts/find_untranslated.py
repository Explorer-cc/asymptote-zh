#!/usr/bin/env python3
"""Detect potentially untranslated English sentences in a Texinfo file.

Adapted for this project from skill tex-manual-translation:
scans for lines with 5+ consecutive English words OUTSIDE code
environments, which may indicate missed translations.

Usage: python find_untranslated.py <file.texi>

Exit codes:
  0 — no suspicious lines found
  1 — one or more suspicious lines found
  2 — usage error
"""

import re
import sys
from pathlib import Path

# Environments whose content is code / never translated
CODE_ENVS = {
    "example", "smallexample", "lisp", "smalllisp",
    "verbatim", "verbatim*",
}

# 5+ consecutive English words (2+ letters each, whitespace separated)
ENGLISH_SENTENCE = re.compile(r"\b[A-Za-z]{2,}(?:\s+[A-Za-z]{2,}){4,}\b")


def find_untranslated(filepath: str) -> int:
    text = Path(filepath).read_text(encoding="utf-8")
    lines = text.splitlines()

    code_depth = 0
    issues = []

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        for env in CODE_ENVS:
            if stripped == "@end " + env or stripped.startswith("@end " + env):
                code_depth = max(0, code_depth - 1)
            if stripped == "@" + env or stripped.startswith("@" + env + " "):
                code_depth += 1

        if code_depth > 0:
            continue
        # Comment lines, node/menu/index/verbatiminclude lines: skip
        if stripped.startswith("@c ") or stripped == "@c":
            continue
        if stripped.startswith("@node") or stripped.startswith("* "):
            continue
        if stripped.startswith("@verbatiminclude"):
            continue

        # Strip @commands (with optional {...} args) and inline math
        clean = re.sub(r"@[A-Za-z]+\*?(?:\{[^{}]*\})*", "", line)
        clean = re.sub(r"\$[^$]*\$", "", clean)

        for m in ENGLISH_SENTENCE.finditer(clean):
            matched = m.group().strip()
            if len(matched) < 25:
                continue
            issues.append((lineno, matched, line))

    if not issues:
        print("No potentially untranslated English sentences found.")
        return 0

    print(f"Found {len(issues)} potentially untranslated line(s):\n")
    for lineno, matched, content in issues:
        print(f"  Line {lineno}")
        print(f"    Matched: {matched[:80]}{'...' if len(matched) > 80 else ''}")
        print(f"    Full:    {content.rstrip()[:120]}")
    print("\nReview these lines — they may contain untranslated English text.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.texi>", file=sys.stderr)
        sys.exit(2)
    sys.exit(find_untranslated(sys.argv[1]))
