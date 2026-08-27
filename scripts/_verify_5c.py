# -*- coding: utf-8 -*-
"""校验步骤5c: 门店/机器人数量 PDF 提取（逐个文件）"""
import pdfplumber, re, warnings, sys
warnings.filterwarnings('ignore')

path = sys.argv[1]
tag = sys.argv[2]
print("=====", tag, "=====")
with pdfplumber.open(path) as pdf:
    for i, p in enumerate(pdf.pages):
        t = p.extract_text() or ''
        if ('機器人商店' in t or '零售店' in t) and re.search(r'[\d,]{3,}', t):
            out = []
            for kw in ['零售店', '機器人商店']:
                for m in re.finditer(kw, t):
                    s = t[max(0, m.start()-70): m.end()+150].replace('\n', ' ')
                    if re.search(r'[\d,]{3,}', s):
                        out.append(s.strip())
            if out:
                print("--- p%d ---" % (i+1))
                seen = set()
                for s in out:
                    if s[:25] in seen:
                        continue
                    seen.add(s[:25])
                    print("  " + s[:200])
