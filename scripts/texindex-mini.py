#!/usr/bin/env python3
"""Minimal texindex replacement: jobname.cp -> jobname.cps

Input lines (written by texinfo.tex):
  @entry{sortkey}{page}{text}                         plain entry
  @entry{parent@subentry child}{page}{parent}{child}  entry with subtopic

Output (format expected by texinfo.tex \\printindex):
  @initial {X}                     letter group header
  @entry {text}{p1, p2}            main entry with its own pages
  @primary {text}                  main entry header when it has no own pages
  @secondary {child}{p1, p2}       indented subentry

Usage: python texindex-mini.py <jobname.cp>"""
import sys
from collections import OrderedDict

SUB = '@subentry '


def split_entries(line):
    """Parse @entry{..}{..}{..}[{..}] with balanced braces -> list of args."""
    parts, depth, start, i = [], 0, len('@entry{'), 7
    while i < len(line):
        c = line[i]
        if c == '{':
            depth += 1
        elif c == '}':
            if depth == 0:
                parts.append(line[start:i])
                if len(parts) == 4:
                    return parts
                # skip to next '{'; loop's i += 1 moves past it
                j = line.find('{', i + 1)
                if j == -1:
                    return parts  # 3-arg entry at end of line
                start, i = j + 1, j
            else:
                depth -= 1
        i += 1
    raise ValueError('unterminated @entry: ' + line)


def sortkey(s):
    return [(ch.lower(), ch) for ch in s]


def pagenum(p):
    return (0, int(p)) if p.lstrip('-').isdigit() else (1, p)


def main():
    src = sys.argv[1]
    mains = {}       # parent sortkey -> [pages, text]
    children = {}    # parent sortkey -> OrderedDict(child sortkey -> [pages, text])
    with open(src, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if not line:
                continue
            parts = split_entries(line)
            if len(parts) == 4 and SUB in parts[0]:
                parent, child = parts[0].split(SUB, 1)
                mains.setdefault(parent, [[], parts[2]])
                d = children.setdefault(parent, OrderedDict())
                rec = d.setdefault(child, [[], parts[3]])
                rec[0].append(parts[1])
            else:
                key, page, text = parts[0], parts[1], parts[2]
                rec = mains.setdefault(key, [[], text])
                rec[0].append(page)

    out = src[:-3] + '.cps' if src.endswith('.cp') else src + 's'
    groups = OrderedDict()
    for key in sorted(mains, key=lambda k: (sortkey(k), k)):
        pages, text = mains[key]
        lines = []
        if pages:
            lines.append('@entry {%s}{%s}' % (
                text, ', '.join(sorted(set(pages), key=pagenum))))
        else:
            lines.append('@primary {%s}' % text)
        kids = children.get(key, {})
        for ck in sorted(kids, key=lambda k: (sortkey(k), k)):
            cpages, ctext = kids[ck]
            lines.append('@secondary {%s}{%s}' % (
                ctext, ', '.join(sorted(set(cpages), key=pagenum))))
        groups.setdefault(key[0].upper(), []).extend(lines)

    with open(out, 'w', encoding='utf-8') as f:
        for initial, lines in groups.items():
            f.write('@initial {%s}\n' % initial)
            for ln in lines:
                f.write(ln + '\n')
    n_kids = sum(len(v) for v in children.values())
    print('texindex-mini: %d main + %d sub entries -> %s'
          % (len(mains), n_kids, out))


if __name__ == '__main__':
    main()
