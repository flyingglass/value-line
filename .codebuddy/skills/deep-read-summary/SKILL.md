---
name: deep-read-summary
description: |
  深度阅读 epub 电子书并生成结构化摘要。
  核心原则：尊重原文，不编造不推理。
---

# 深度阅读摘要

## 流程

1. 用 `scripts/extract_epub.py` 提取 epub 为临时 txt
2. 通读全文
3. 读取 `research-wiki/raw/research/articles/哈格斯特朗_2023_查理芒格的智慧-投资的格栅理论.md` 作为格式参考
4. 生成摘要，保存到 `research-wiki/raw/research/articles/作者_年份_书名.md`

raw/ 里存的就是摘要，不存原文全文。不拆子页面。
