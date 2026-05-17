"""一次性修复：把 build.py 里 Python 双引号字符串中嵌套的中文引号
对儿（"X" 含中文）替换为「X」。

策略：找到形如 <indent>"...内容..."（或 "...内容...",）的行（即纯字符串续行），
把内容里所有成对的 "..." 替换成 「...」。代码行不动。
"""

import re
import sys
from pathlib import Path

target = Path(__file__).parent / "build.py"
src = target.read_text(encoding="utf-8")
lines = src.split("\n")
fixed = []
changes = 0

inner_pair_re = re.compile(r'"([^"\n]+?)"')

for line in lines:
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]

    # Only process pure string-literal continuation lines:
    # they start with `"` after indentation, end with `"` or `",`
    if not stripped.startswith('"'):
        fixed.append(line)
        continue
    if stripped.endswith('",'):
        suffix = '",'
        body = stripped[:-2]
    elif stripped.endswith('"'):
        suffix = '"'
        body = stripped[:-1]
    else:
        fixed.append(line)
        continue

    # body[0] is opening `"`. Inner content is body[1:].
    inner = body[1:]
    new_inner, n = inner_pair_re.subn(r"「\1」", inner)
    if n:
        changes += n
    fixed.append(indent + '"' + new_inner + suffix)

target.write_text("\n".join(fixed), encoding="utf-8")
print(f"replaced {changes} inner-quote pairs")
