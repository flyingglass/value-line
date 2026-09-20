---
name: research-ingest
description: |
  投研原始资料入库（业绩会逐字稿、调研纪要、公众号文章、研报、书籍章节等）。
  三段式结构：头部元数据（来源/链接/作者/时间）→ 摘要（速读）→ 正文（完整原文）。
  含研报 PDF 图表数值提取：坐标吸附法把图表数值重建为表格；另附公众号/网页文章配图提取法（可选，默认不做）。见 references/pdf-chart-extraction.md。
  核心原则：来源可追溯、摘要可速读、原文可验证、图表可复原、raw 只进不改。
  触发场景：将外部资料整理入库到 research-wiki/raw/；从研报 PDF 提取图表数值；提取文章配图/图表内容；
  把图表数据表格化（"图表变表格""弄成表格""提取图表数值""为什么不提取图表"）。
---

# 投研原始资料入库

## 适用对象

业绩会逐字稿、调研纪要、公众号文章、研报、书籍章节等说明性资料。

## 流程

1. 获取原始资料全文（用户粘贴 / web_fetch / PDF 提取）
2. 核对来源链接（宪法强制：禁止只记来源名称不记链接，缺失则索要或 web_search 补齐，找不到标注"原文链接待补"）
3. **研报 PDF 先做图表判定**：`--probe` 探测文本层 → 有文本层走坐标吸附法重建图表数值，
   无文本层走 OCR（图表数值通常无法配对，只转写文字）。详见 `references/pdf-chart-extraction.md`
4. **（可选，默认不做）文章配图**：`web_fetch` 只回文本、正文图片全丢。**仅当用户明确要求、或该图承载关键数据时**，
   才按 `references/pdf-chart-extraction.md` 第五节处理（curl 抓 HTML → 捞 `data-src` → 临时读图 → 转写为表格；
   **转写完成即达标，不留原图副本**，只在 raw 里记原图 CDN 链接供回溯）
5. 按三段式模板整理入库（见 `references/raw_template.md`），**图表数值一律表格化**
6. 保存到 `research-wiki/raw/research/<code 或 articles>/<YYYY-MM-DD>-<标题>.md`
7. 如需深度加工，继续走 wiki ingest 流程（`adler-reading` / `deep-read-summary` skill）

## 三段式结构

1. **头部元数据**：来源、原文链接、作者、发布时间、会议信息、参会管理层、原始来源 → 可追溯
2. **摘要**：结构化分点（一句话核心 / 关键数据 / 核心矛盾 / 跟踪要点），**关键数据与核心结论加粗** → 3 分钟速读
3. **正文**：**发言人加粗**；问答环节按 `Q1 主题（机构）` 编号小标题；完整保留原文，保留"发言人：原话"

## 格式规范（突出重点）

- **摘要禁用大段平铺**：一律分点列表，核心结论加粗，避免一坨文字
- **发言人一律加粗**：`**王宁**：`，长段落中可快速定位谁在说话
- **问答加导航小标题**：每个问题前加 `**Q1 主题（机构）**`（主题从原文提炼，不加编造内容）
- **关键数字加粗**：收入、利润、增速等重点数字用 `**数值**` 突出
- **图表数值一律表格化**：不得写成行内散文（如「（图表数值：a% / b%…对应 X / Y / Z）」）；
  横纵按可读性择一（选项为行/分组为列、单行横表、左右分栏横表、纵表，见 `references/pdf-chart-extraction.md`）；
  **每张表下用 `> ` 引用块写校验注或存疑提示**，表体只留「选项 | 数值」
- 参照标杆：`research-wiki/raw/research/泡泡玛特/2026-08-20-中期业绩发布会完整逐字稿.md`

## 研报 PDF 图表数值提取

配套脚本：`scripts/extract_pdf_chart_values.py`（`pdfplumber`，用项目 `.venv` 运行）

```bash
# 1) 探测文本层（决定走坐标吸附还是 OCR）
.venv\Scripts\python.exe .codebuddy\skills\research-ingest\scripts\extract_pdf_chart_values.py <pdf> --probe
# 2) 诊断单页版面（看数值是否与图例列 x 对齐、有无第二套标签）
.venv\Scripts\python.exe .codebuddy\skills\research-ingest\scripts\extract_pdf_chart_values.py <pdf> --dump 14 --y 440 600
# 3) 批量提取草表
.venv\Scripts\python.exe .codebuddy\skills\research-ingest\scripts\extract_pdf_chart_values.py <pdf> --pages 3-24 --columns Overall,China,Japan,US,UK,Australia
```

**脚本只做吸附，不判断配对是否正确**，必须用正文数字交叉校验（正文锚点 + 加总 ≈100% + 跨题一致性）。
七个必查坑（两套标签 / 数值按柱高降序 / 水印遮挡 / 双面板 / 折线图无标签 / 小样本 / 原文自身矛盾）
与完整流程见 `references/pdf-chart-extraction.md`。

## 核心原则

- 来源可追溯：来源 / 链接 / 作者 / 时间齐全，缺失主动补齐
- 摘要可速读：结构化分点，3 分钟读完核心，不淹没在正文中
- 原文可验证：正文完整保留原文，问答保留"发言人：原话"
- 图表可复原：图表数值一律表格化并附校验注/存疑注；提取不出的**逐图说明原因**，宁标"待核"不硬凑。
  文章配图**转写为表格即达标，不保存原图副本**（只留链接回溯）
- 只进不改：raw/ 原始资料入库后不改动（格式调整不改变原文内容）
