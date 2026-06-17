# 2026-06-17 项目结构重构：所有 .py 移入 scripts/

## 背景

项目根目录有 11 个 .py 文件和 40+ 个 scripts/<code>/ 子目录，混在一起不清晰。
同时也为投研 wiki 扩展做准备，需要清理根目录。

## 改动

### 移动
全部 11 个根目录 .py → scripts/：

| 文件 | 用途 | 路径修改 |
|------|------|---------|
| build.py | 主入口，8步流水线 | BASE 上移一层到项目根，子进程调用加 scripts/ 前缀 |
| config.py | 标的配置 + 路径 | BASE_DIR 上移一层到项目根 |
| engine.py | 指标计算引擎 | scripts/<code>/ 引用去掉 scripts/ 前缀 |
| fetcher.py | 数据拉取 | 无需改动 |
| pdf_downloader.py | PDF 下载 | 无需改动 |
| extract_mda.py | MD&A 提取 | sys.path(".") → 绝对路径 |
| generate_report.py | HTML 生成 | BASE 上移一层 |
| generate_reading.py | 阅读报告 | BASE_DIR 上移一层 |
| generate_index.py | 索引页 | BASE_DIR + sys.path |
| list_refs.py | 估值参考 | BASE 上移一层 |
| tdx_client.py | TDX API | .env 路径上移一层 |

### 路径模式

所有文件统一使用 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` 指向项目根，
用于 `data/`、`report/`、`report_data.json` 等路径。

`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` 插入 scripts/ 用于模块互导入。

### 修复

- engine.py `_safe_float()` 容错 spot 数据中 pe/pb/div_y 可能为字符串 "-"

## 验证

`python scripts/build.py 09992 --cf 15.0` — 8步流水线全部通过，HTML 正常生成。

## 影响

- 使用方式从 `python build.py 09992` 变为 `python scripts/build.py 09992`
- 根目录不再有 .py 文件
