#!/usr/bin/env python3
"""research-wiki Lint — 健康检查脚本

检查项（按 WIKI-SCHEMA.md 定义）：
  1. 结构完整性 — 必需文件/目录
  2. Frontmatter — 每个页面 YAML 头
  3. 交叉引用 — [[...]] 断链
  4. 参见区块 — 页面底部反向链接
  5. index 注册 — 页面是否被 index.md 收录
  6. 孤立页面 — 无入链的页面
  7. 内容质量 — 空文件/占位符/过短
  8. raw 命名规范 — 日期前缀
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

WIKI = Path(__file__).resolve().parent.parent / "research-wiki"

# 必需文件
REQUIRED = {
    "vl/index.md", "vl/overview.md", "vl/log.md",
    "research/index.md", "research/overview.md", "research/log.md",
}
# 标的必需文件（中英文文件名等价，任一存在即可）
STOCK_FILES = {
    "overview.md": ["overview.md", "概览.md", "数据目录.md"],
    "thesis.md": ["thesis.md", "投资论点.md"],
    "industry-chain.md": ["industry-chain.md", "产业链.md"],
    "operating-metrics.md": ["operating-metrics.md", "运营指标.md"],
}
# 标的【可选】文件：不存在不报错；存在但为占位页则 WARN
# 背景：研报索引的内容依赖外部研报获取（宪法规定 AKShare 列表 + web_search 转载，
# PDF 不可直链下载），强制要求会催生无内容的占位页（2026-08-30 已清理 6 个）。
# 故改为可选：有实质内容才保留，没有就不建。
OPTIONAL_STOCK_FILES = {
    "research-reports.md": ["research-reports.md", "研报索引.md", "券商研报.md"],
}
# 研报索引页的占位特征
REPORT_STUB_MARKERS = ["无已拉取研报", "当前无研报", "暂无研报", "待拉取", "无研报"]
REPORT_MIN_LINES = 5
STOCK_DIRS = [d.name for d in (WIKI / "research").iterdir()
              if d.is_dir() and d.name != "articles"]
VL_DIRS = ["modules", "concepts", "entities", "synthesis"]
RESEARCH_ARTICLE_DIRS = ["concepts", "entities", "papers", "synthesis"]

# 页面集合 (相对路径, 小写 key)
def collect_pages():
    pages = {}          # rel_path -> text
    rel_to_key = {}     # rel -> wikilink key (无扩展名, 小写)
    key_to_paths = defaultdict(list)
    for p in sorted(WIKI.rglob("*.md")):
        rel = p.relative_to(WIKI).as_posix()
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            text = ""
        pages[rel] = (p, text)
        stem = p.stem  # 不含扩展名
        key_to_paths[stem.lower()].append(rel)
    return pages, key_to_paths

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FRONT_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
ALIAS_SPLIT = re.compile(r"\s*\|\s*")
PLACEHOLDERS = ["TODO", "TBD", "待补充", "待完善", "lorem ipsum", "FIXME", "XXX"]

def split_link(raw):
    """[[a|b]] -> (a, b) ; [[a]] -> (a, None)"""
    parts = ALIAS_SPLIT.split(raw, 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else None)

def resolve_link(link, current_rel, key_to_paths):
    """把 wikilink 解析为候选目标 rel 路径列表（相对路径 + 全局 stem 匹配）。"""
    cands = []
    cur_dir = Path(current_rel).parent  # research/泡泡玛特
    # 1. 当前目录下 link (无扩展名时加 .md)
    p1 = cur_dir / link
    if not p1.suffix:
        p1 = p1.with_suffix(".md")
    cands.append(p1.as_posix())
    # 2. 含路径前缀时按相对路径
    if "/" in link:
        p2 = cur_dir / link
        if not p2.suffix:
            p2 = p2.with_suffix(".md")
        cands.append(p2.as_posix())
    # 3. 全局 stem 匹配: 用 link 的 name (保留 .py 等点号) 作为 key
    link_name = Path(link).name
    for key in (link_name.lower(), Path(link_name).stem.lower()):
        if key in key_to_paths:
            cands.extend(key_to_paths[key])
    return cands

def main():
    pages, key_to_paths = collect_pages()
    all_rels = set(pages.keys())
    errs = []   # (级别, 文件, 描述)
    info = []   # 信息

    # ---- 1. 结构完整性 ----
    for req in REQUIRED:
        if req not in all_rels:
            errs.append(("ERROR", req, f"缺失必需文件 {req}"))
    # vl 子目录
    for d in VL_DIRS:
        dp = WIKI / "vl" / d
        if not dp.exists():
            errs.append(("WARN", f"vl/{d}/", f"vl/ 缺失子目录 {d}/"))
    # 标的目录（必需文件）
    for code in STOCK_DIRS:
        for sf, alts in STOCK_FILES.items():
            if not any(f"research/{code}/{a}" in all_rels for a in alts):
                errs.append(("ERROR", f"research/{code}/{sf}",
                             f"标的 {code} 缺失 {sf}"))
        # 可选文件：存在则校验内容，防止无实质内容的占位页
        for sf, alts in OPTIONAL_STOCK_FILES.items():
            hit = next((a for a in alts
                        if f"research/{code}/{a}" in all_rels), None)
            if not hit:
                continue
            rel = f"research/{code}/{hit}"
            _, text = pages[rel]
            body = FRONT_RE.sub("", text).strip()
            n_lines = len([l for l in body.splitlines() if l.strip()])
            if n_lines < REPORT_MIN_LINES or any(m in body for m in REPORT_STUB_MARKERS):
                errs.append(("WARN", rel,
                             f"研报索引为占位页（仅 {n_lines} 行有效正文），建议填充或删除"))
    # research/articles 子目录
    for d in RESEARCH_ARTICLE_DIRS:
        ap = WIKI / "research" / "articles" / d
        if not ap.exists():
            errs.append(("WARN", f"research/articles/{d}/",
                         f"research/articles/ 缺失子目录 {d}/"))

    # ---- 2. Frontmatter ----
    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md",):
            continue
        # raw/ 不强制 frontmatter; index.md / log.md 是结构性页面, 豁免
        is_raw = rel.startswith("raw/")
        base_name = rel.rsplit("/", 1)[-1]
        if not is_raw and base_name not in ("index.md", "log.md"):
            if not FRONT_RE.search(text):
                errs.append(("WARN", rel, "缺少 YAML frontmatter (---...---)"))

    # ---- 3 & 4 & 5 & 6: 链接、参见、index、孤立 ----
    # 先构建反向引用图
    incoming = defaultdict(set)  # 目标 rel -> {来源 rel}
    seealso_refs = defaultdict(set)  # 页面 rel -> {其参见区块引用的目标 rel}
    seealso_missing = set()          # 缺参见区块的页面
    index_files = {"vl/index.md", "research/index.md"}
    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md",):
            continue
        # 3. 链接检查
        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1)
            if raw.startswith("!"):  # 图片嵌入
                continue
            link, alias = split_link(raw)
            if not link:
                continue
            # 跳过外部 URL
            if link.startswith("http"):
                continue
            # 跨域引用: 指向 report/ 生成报告 (不在 wiki 内, 合理)
            if "../report/" in link or "report/reading/" in link:
                continue
            cands = resolve_link(link, rel, key_to_paths)
            found = False
            for c in cands:
                # 规范化比较
                cn = c.replace("\\", "/")
                if cn in all_rels:
                    incoming[cn].add(rel)
                    found = True
                    break
            if not found:
                errs.append(("WARN", rel, f"断链: [[{raw}]] 无对应文件"))
        # 4. 参见区块 (vl/research 页面, 非 index/log)
        if not rel.startswith("raw/"):
            base = rel.split("/")[-1]
            if base not in ("index.md", "log.md"):
                need_seealso = (
                    rel.startswith("vl/concepts/") or
                    rel.startswith("vl/modules/") or
                    rel.startswith("vl/entities/") or
                    rel.startswith("research/articles/") or
                    (rel.startswith("research/") and "/" in rel[9:])
                )
                if need_seealso:
                    # 提取参见区块链接
                    sl = None
                    for hdr in ("## 参见", "## 相关页面", "## 相关链接", "## 相关"):
                        idx = text.find(hdr)
                        if idx >= 0:
                            tail = text[idx + len(hdr):]
                            m_next = re.search(r'\n## ', tail)
                            sl = tail[:m_next.start()] if m_next else tail
                            break
                    if sl:
                        for _m in WIKILINK_RE.finditer(sl):
                            _raw = _m.group(1)
                            if _raw.startswith("!") or _raw.startswith("http"):
                                continue
                            _link, _ = split_link(_raw)
                            if _link:
                                _cands = resolve_link(_link, rel, key_to_paths)
                                for _c in _cands:
                                    _cn = _c.replace("\\", "/")
                                    if _cn in all_rels:
                                        seealso_refs[rel].add(_cn)
                                        break
                    else:
                        errs.append(("WARN", rel, "缺少 ## 参见 / ## 相关页面 反向链接区块"))
                        seealso_missing.add(rel)

    # 5. index 注册: 每个非 index/log 页面应在某 index.md 中出现
    def check_index(idx_rel, namespace_prefix):
        if idx_rel not in pages:
            return
        _, idx_text = pages[idx_rel]
        for rel, (p, text) in pages.items():
            if rel == idx_rel or rel == "WIKI-SCHEMA.md":
                continue
            if not rel.startswith(namespace_prefix):
                continue
            if rel.endswith("/log.md") or rel.endswith("/index.md"):
                continue
            # 用 stem 检查是否在 index 文本中出现
            stem = Path(rel).stem
            # 去掉子目录前缀做模糊匹配
            name = Path(rel).name
            if stem not in idx_text and name not in idx_text:
                errs.append(("INFO", rel, f"未在 {idx_rel} 中注册"))

    check_index("vl/index.md", "vl/")
    check_index("research/index.md", "research/")

    # 6. 孤立页面
    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md", "vl/index.md", "research/index.md",
                   "vl/log.md", "research/log.md", "vl/overview.md",
                   "research/overview.md"):
            continue
        if rel.startswith("raw/"):
            continue  # raw 不要求入链
        if rel not in incoming and rel not in index_files:
            errs.append(("INFO", rel, "孤立页面（无入链）"))

    # 6.5 交叉引用缺口
    for target_rel, sources in incoming.items():
        if target_rel.startswith("raw/"):
            continue  # raw 不要求参见区块
        if target_rel in seealso_missing:
            continue  # 已在上面报"缺参见区块"
        target_refs = seealso_refs.get(target_rel, set())
        for source_rel in sorted(sources):
            if source_rel.startswith("raw/"):
                continue  # raw 不要求反引
            src_base = source_rel.split("/")[-1]
            if src_base in ("index.md", "log.md"):
                continue
            if source_rel in target_refs:
                continue
            errs.append(("WARN", target_rel,
                        f"交叉引用缺口: {source_rel} → 本页未反引"))

    # ---- 7. 内容质量 ----
    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md",):
            continue
        body = FRONT_RE.sub("", text) if not rel.startswith("raw/") else text
        stripped = body.strip()
        if not stripped:
            errs.append(("WARN", rel, "空文件（无正文内容）"))
            continue
        line_count = len([l for l in stripped.splitlines() if l.strip()])
        if line_count < 5 and not rel.startswith("raw/"):
            errs.append(("WARN", rel, f"内容过少（仅 {line_count} 行有效正文）"))
        for ph in PLACEHOLDERS:
            if ph.lower() in stripped.lower():
                errs.append(("INFO", rel, f"含占位符 '{ph}'"))

    # ---- 8. raw 命名规范 ----
    for rel, (p, text) in pages.items():
        if not rel.startswith("raw/"):
            continue
        name = Path(rel).name
        # 日期前缀 YYYY-MM-DD- 或已知例外
        if not re.match(r"\d{4}-\d{2}-\d{2}-", name):
            # 例外: 数据源参考文件 (akshare/tdx/karpathy/style)
            if name.startswith(("hagstrom", "akshare", "tdx",
                                "karpathy", "style")):
                continue
            # 例外: 作者_年份_ 格式 (如 道金斯_1976_xxx)
            if re.match(r".+_\d{4}_", name):
                continue
            # 例外: 书名_艾德勒阅读法 / _参考 / _指导手册 等阅读笔记格式
            if any(s in name for s in ("艾德勒阅读法", "参考著作",
                                       "指导手册", "参考")):
                continue
            errs.append(("INFO", rel, f"raw 文件未用日期前缀命名: {name}"))

    # ---- 输出 ----
    # 统计
    by_level = defaultdict(int)
    for lvl, _, _ in errs:
        by_level[lvl] += 1

    print("=" * 60)
    print("research-wiki Lint Report")
    print("=" * 60)
    print(f"Wiki 根: {WIKI}")
    print(f"Markdown 文件总数: {len(pages)}")
    print(f"  raw/: {sum(1 for r in pages if r.startswith('raw/'))}")
    print(f"  vl/: {sum(1 for r in pages if r.startswith('vl/'))}")
    print(f"  research/: {sum(1 for r in pages if r.startswith('research/'))}")
    print()
    print(f"问题统计: ERROR={by_level['ERROR']}  WARN={by_level['WARN']}  INFO={by_level['INFO']}")
    print()

    # 按文件分组输出
    by_file = defaultdict(list)
    for lvl, f, desc in errs:
        by_file[f].append((lvl, desc))

    for f in sorted(by_file.keys()):
        print(f"--- {f} ---")
        for lvl, desc in sorted(by_file[f]):
            print(f"  [{lvl}] {desc}")
        print()

    # 空目录
    empty_dirs = []
    for d in WIKI.rglob("*"):
        if d.is_dir():
            try:
                next(d.iterdir())
            except StopIteration:
                empty_dirs.append(d.relative_to(WIKI).as_posix())
    if empty_dirs:
        print("=== 空目录 ===")
        for ed in sorted(empty_dirs):
            print(f"  {ed}/")
        print()

    print("Lint 完成。")

if __name__ == "__main__":
    main()
