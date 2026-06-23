# 2026-06-23 — business_commentary.py 自动生成机制

## 背景

新增标的时，Business 和 AI Commentary 需要手写 `business_commentary.py`（5段分析 + 业务描述）。
手写耗时且容易遗漏现金流分析等关键段落。需要自动化生成初稿。

## 方案

新增 `scripts/generate_business_commentary.py` 生成器 + `build.py` Step 4.5 自动调用。

## 源文件

- `scripts/generate_business_commentary.py` — 自动生成器（376行）
  - 读取 config.business_desc → Business 段落
  - 读取 revenue_structure → 产品/地区拆分
  - 14 个行业专属 moat 模板（P3）
  - 9 个行业专属 catalyst 模板（P5）
  - P1/P2/P4 纯数据驱动公式
  - 已存在不覆盖

- `scripts/build.py` — 新增 Step 4.5
  ```python
  def step_4_5_auto_gen_commentary(code):
      """自动生成 business_commentary.py（如不存在）"""
      if os.path.exists(script_path):
          跳过  # 保留手工精调版本
      调用 generate_business_commentary.py
      非阻断：失败时回退 engine 内置通用模板
  ```

## 流水线变更

```
Step 0 → config 检查
Step 1 → 数据拉取
Step 2 → PDF 下载
Step 3 → MD&A 提取
Step 4 → 营收结构入库
Step 4.5 → 🆕 自动生成 business_commentary.py
Step 5 → config final
Step 6 → engine 计算
Step 7 → HTML 生成
Step 8 → 验证
```

## 涉及的行业模板

| 行业 | P3 Moat | P5 Catalyst |
|------|---------|-------------|
| Consumer Staples | ✓ | ✓ |
| Consumer | ✓ | ✓ |
| Technology | ✓ | ✓ |
| Energy | ✓ | ✓ |
| Metals & Mining | ✓ | ✓ |
| Media | ✓ | ✓ |
| Semiconductor | ✓ | ✓ |
| Packaging | ✓ | ✓ |
| Automotive | ✓ | ✓ |
| Home Appliances | ✓ | ✓ |
| Pharmaceuticals | ✓ | ✓ |
| Healthcare | ✓ | ✓ |
| Building Materials | ✓ | ✓ |
| Insurance | ✓ | ✓ |
| Financial Services | ✓ | ✓ |
| Utilities | ✓ | ✓ |
| 通用默认 | ✓ | ✓ |
