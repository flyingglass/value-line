# -*- coding: utf-8 -*-
"""校验: 各期官方渠道Note (全集团/中国/子渠道)"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def find_pages(path, pat, maxpages=320):
    out = []
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            if re.search(pat, t):
                out.append((i+1, t))
    return out

def dump(path, pat, tag, maxpages=320, max_hits=3):
    print("="*12, tag, "="*12)
    hits = find_pages(path, pat, maxpages)
    for pg, t in hits[:max_hits]:
        m = re.search(pat, t)
        idx = m.start()
        seg = t[max(0, idx-150): idx+1200].replace('\n', ' ')
        print("--- p%d ---" % pg)
        print("  " + seg[:950])
        print()

# 2021年报 Note 渠道（Retail store sales 零售店銷售收益 出现于 Note）
dump(r'data\pdfs\09992\09992_2021_年报.pdf', r'Retail store sales 零售店銷售收益', '2021年报 渠道Note', 320)
dump(r'data\pdfs\09992\09992_2021_年报.pdf', r'Pop Draw 抽盒機|抽盒機', '2021年报 子渠道', 320)
# 2022年报 Note 渠道
dump(r'data\pdfs\09992\09992_2022_年报.pdf', r'Retail store sales 零售店銷售收益', '2022年报 渠道Note', 320)
dump(r'data\pdfs\09992\09992_2022_年报.pdf', r'Pop Draw 抽盒機|抽盒機', '2022年报 子渠道', 320)
# 2023年报 子渠道完整
dump(r'data\pdfs\09992\09992_2023_年报.pdf', r'Pop Draw 抽盒機|抽盒機', '2023年报 子渠道', 320)
# 2024年报 渠道Note + 子渠道
dump(r'data\pdfs\09992\09992_2024_年报.pdf', r'Retail store sales 零售店銷售收益', '2024年报 渠道Note', 320)
dump(r'data\pdfs\09992\09992_2024_年报.pdf', r'Pop Draw 抽盒機|抽盒機', '2024年报 子渠道', 320)
# 2026中报 Note 渠道 + 子渠道
dump(r'data\pdfs\09992\09992_2026_中报.pdf', r'Retail store sales 零售店銷售收益', '2026中报 渠道Note', 320)
dump(r'data\pdfs\09992\09992_2026_中报.pdf', r'抽盒機', '2026中报 子渠道', 320)
