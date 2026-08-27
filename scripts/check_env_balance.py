#!/usr/bin/env python3
"""Check @env / @end env balance in a Texinfo file.

Adapted for this project from skill tex-manual-translation
(LaTeX version) to Texinfo syntax: environments are written as
"@example ... @end example" (name may carry an argument on the
opening line, e.g. "@table @code").

Usage: python check_env_balance.py <file.texi>

Exit codes:
  0 — all environments balanced
  1 — one or more environments unbalanced
  2 — usage error
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

# @end line: captures environment name
END_RE = re.compile(r"^\s*@end\s+([A-Za-z]\w*)\s*$")
# Opening line: env name must be the first token on the line.
# Only names that also appear in some @end are counted (filters out
# plain one-token commands like @contents or @page).
OPEN_RE = re.compile(r"^\s*@([A-Za-z]\w*)\b")


def check_balance(filepath: str) -> int:
    text = Path(filepath).read_text(encoding="utf-8")

    opens: dict[str, list[int]] = defaultdict(list)
    ends: dict[str, list[int]] = defaultdict(list)
    env_names: set[str] = set()

    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        m = END_RE.match(line)
        if m:
            env_names.add(m.group(1))
            ends[m.group(1)].append(lineno)

    for lineno, line in enumerate(lines, 1):
        if END_RE.match(line):
            continue
        m = OPEN_RE.match(line)
        if m and m.group(1) in env_names:
            opens[m.group(1)].append(lineno)

    if not env_names:
        print("No environments found.")
        return 0

    has_mismatch = False
    for env in sorted(env_names):
        o = len(opens.get(env, []))
        e = len(ends.get(env, []))
        if o != e:
            has_mismatch = True
            print(f"MISMATCH  @{env}={o}  @end {env}={e}  (diff={o - e:+d})")
            print(f"  open lines: {opens.get(env, [])}")
            print(f"  end  lines: {ends.get(env, [])}")
        else:
            print(f"OK        @{env}={o}  @end {env}={e}")

    if has_mismatch:
        print("\nUnbalanced environments detected. "
              "Check for lost @env/@end markers.")
    else:
        print("\nAll environments balanced.")
    return 1 if has_mismatch else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.texi>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check_balance(sys.argv[1]))
