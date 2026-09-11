# -*- coding: utf-8 -*-
"""临时脚本：逐字符定位「重新生成 view」后与 HEAD 的差异内容（一次性，跑完删除）。"""
import difflib
import io
import subprocess
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FILES = [
    'research-wiki/index.html',
    'research-wiki/view/stocks/贵州茅台/原始资料/2026-03-28-两轮茅台下跌有何异同.html',
    'research-wiki/view/cases/疯狂的里海/原始资料/2021-03-26-选股模型.html',
]

out = []
for f in FILES:
    old = subprocess.run(['git', 'show', 'HEAD:' + f], capture_output=True).stdout.decode('utf-8', 'replace')
    new = io.open(f, encoding='utf-8').read()
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    out.append('### ' + f + '  len %d -> %d' % (len(old), len(new)))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            out.append('  %s\n    OLD %r\n    NEW %r' % (tag, old[i1:i2][:400], new[j1:j2][:400]))

io.open('.diff_probe.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written')
