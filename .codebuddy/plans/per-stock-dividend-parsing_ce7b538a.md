---
name: per-stock-dividend-parsing
overview: 将股息解析从通用 fetcher.py 剥离，改为 per-stock metric_adjustment.py 钩子模式，回退 fetcher.py 修改并新建 00700 个股股息脚本。
todos:
  - id: revert-fetcher
    content: 回退 fetcher.py 股息解析修改（列检测正则、DPS提取逻辑、HKD→CNY换算块），删除 _read_fx_rate 函数
    status: completed
  - id: add-raw-text
    content: 在 dividend 表 schema 增加 raw_text 列，INSERT 时写入原始公告文本 txt
    status: completed
    dependencies:
      - revert-fetcher
  - id: add-dividend-hook
    content: 在 engine.py 新增 _resolve_dividends 函数，按 _resolve_adj_np 模式加载 metric_adjustment.py 的 adjust_dividends 钩子
    status: completed
  - id: wire-hook
    content: 在 engine.py build_metric_table 第 422 行将 reader.dividends() 替换为 _resolve_dividends(reader)
    status: completed
    dependencies:
      - add-dividend-hook
  - id: create-00700-metric
    content: 新建 scripts/00700/metric_adjustment.py，实现 adjust_dividends：正则解析每股派港币/人民币 + HKD→CNY FX 换算
    status: completed
    dependencies:
      - add-raw-text
      - add-dividend-hook
  - id: regenerate-report
    content: 运行 python build.py 00700 --fetch 重新生成腾讯控股报告，验证 DPS 数值正确
    status: completed
    dependencies:
      - create-00700-metric
      - wire-hook
---

## 需求概述

回退上一轮对 fetcher.py 的通用股息解析修改（正则匹配、HKD→CNY 换算、_read_fx_rate），改为在 `scripts/<code>/metric_adjustment.py` 中按个股独立处理股息解析。为腾讯控股 00700 创建独立的股息解析逻辑。

## 核心功能

1. **fetcher.py 回退**：股息解析恢复为原始简单逻辑（仅提取含小数点的数字），不做语义解析和货币换算
2. **dividend 表增加 raw_text 列**：存储 AKShare 返回的原始公告文本，供 per-stock 脚本重新解析
3. **engine.py 新增股息钩子**：`_resolve_dividends(reader)` 检测并调用 `metric_adjustment.py` 中的 `adjust_dividends` 函数
4. **00700 独立股息解析**：新建 `scripts/00700/metric_adjustment.py`，用正则精确匹配"每股派港币X元"格式 + HKD→CNY FX 换算

## 技术方案

### 架构决策

股息解析逻辑放在现有 `scripts/<code>/metric_adjustment.py` 中，新增可选函数 `adjust_dividends(reader, stock_cfg) -> dict`。engine.py 在读取股息时检测并调用该函数，无此函数则使用 DB 中的原始 DPS（fetcher 的简单通用解析结果）。

这与现有的 `adjust_metrics` 钩子模式完全一致：per-stock 脚本 > 默认通用逻辑。

### 数据流

```mermaid
flowchart TD
    A[fetcher.py: AKShare API] --> B[简单通用解析 DPS]
    B --> C[写入 dividend 表 + raw_text]
    C --> D[engine.py: _resolve_dividends]
    D --> E{metric_adjustment.py 有 adjust_dividends?}
    E -->|是| F[调用 adjust_dividends 重新解析 raw_text + FX换算]
    E -->|否| G[使用 DB 中的原始 DPS]
    F --> H[返回 {year: dps_cny}]
    G --> H
```

### 实现细节

#### 1. fetcher.py 回退 + raw_text 列

| 行号 | 变更 |
| --- | --- |
| 69-72 | `CREATE TABLE dividend` 增加 `raw_text TEXT` 列 |
| 258 | 列检测回退为 `any(k in val for k in ["0.", "1.", "2.", "3."])` |
| 269-277 | DPS 提取回退为原始简单逻辑（无"每股派"语义解析） |
| 279-286 | 删除 HKD→CNY 换算代码块 |
| 295-298 | `INSERT OR REPLACE` 增加第7列 raw_text，写入 `txt` |
| 405-420 | 删除 `_read_fx_rate` 辅助函数 |


#### 2. engine.py 新增股息钩子

在 `_resolve_adj_np` 附近（~338 行后）新增 `_resolve_dividends(reader)` 函数：

```python
def _resolve_dividends(reader):
    """加载 per-stock adjust_dividends 钩子，解析 DPS + FX 换算。"""
    code = reader.code
    try:
        script_path = os.path.join(os.path.dirname(__file__), "scripts", code, "metric_adjustment.py")
        if os.path.exists(script_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"ma_{code}", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "adjust_dividends"):
                stock_cfg = config.STOCKS.get(code, {})
                return mod.adjust_dividends(reader, stock_cfg)
    except Exception:
        pass
    return reader.dividends()
```

第 422 行：`divs = reader.dividends()` 替换为 `divs = _resolve_dividends(reader)`。

#### 3. scripts/00700/metric_adjustment.py 新建

`adjust_dividends(reader, stock_cfg)` 接口：

- 从 dividend 表读取 `report_year, raw_text`
- 正则解析：`每股派(港币|港元)?(\d+\.?\d*)` 和 `相当于每股派(\d+\.?\d*)港元`
- 同一财政年度多笔分红累加（普通 + 特别）
- 检测文本含"港元"且不含"人民币"的，按 `fx_rates.db` 的 `hkd_cny` 字段（`value/100.0`）换算
- 返回 `{year: dps_cny}` 字典