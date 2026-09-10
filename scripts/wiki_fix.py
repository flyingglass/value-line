#!/usr/bin/env python3
"""research-wiki Fix — 基于 lint 数据的自动修复脚本。
修复: frontmatter 缺失 + ## 参见 区块缺失 + 交叉引用缺口。
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

WIKI = Path(__file__).resolve().parent.parent / "research-wiki"
FRONT_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
ALIAS_SPLIT = re.compile(r"\s*\|\s*")
TODAY = "2026-09-10"
# 默认只补 frontmatter / 参见区块；交叉引用缺口属系统性（历史结论 diminishing
# returns），仅在显式传 --crossref 时追加，避免一次改动上千行。
CROSSREF = "--crossref" in sys.argv


def split_link(raw):
    parts = ALIAS_SPLIT.split(raw, 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else None)


def resolve_link(link, current_rel, key_to_paths, all_rels):
    cands = []
    cur_dir = Path(current_rel).parent
    p1 = cur_dir / link
    if not p1.suffix:
        p1 = p1.with_suffix(".md")
    cands.append(p1.as_posix())
    if "/" in link:
        p2 = cur_dir / link
        if not p2.suffix:
            p2 = p2.with_suffix(".md")
        cands.append(p2.as_posix())
    link_name = Path(link).name
    for key in (link_name.lower(), Path(link_name).stem.lower()):
        if key in key_to_paths:
            cands.extend(key_to_paths[key])
    return cands


def collect():
    pages = {}
    key_to_paths = defaultdict(list)
    for p in sorted(WIKI.rglob("*.md")):
        rel = p.relative_to(WIKI).as_posix()
        text = p.read_text(encoding="utf-8")
        pages[rel] = (p, text)
        key_to_paths[p.stem.lower()].append(rel)
    return pages, key_to_paths


def infer_frontmatter(rel, text):
    """基于文件路径和首行标题推断最小 frontmatter。"""
    title = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("# 0"):
            title = line[2:].strip()
            break
    if not title:
        title = Path(rel).stem

    # vl 模块页
    if rel.startswith("vl/modules/"):
        return f"""---
module: {Path(rel).name}
category: 流水线编排
depends_on: []
updated: {TODAY}
---
"""
    # 疯狂的里海专题（研究专题目录，非标的目录，无四件套）
    if rel.startswith("research/疯狂的里海/"):
        if "/时间线/" in rel:
            topic, cat = "疯狂的里海 · 年度时间线", "年度档案"
        elif "/案例/" in rel:
            topic, cat = "疯狂的里海 · 案例档案", "案例档案"
        elif "/方法论/" in rel:
            topic, cat = "疯狂的里海 · 方法论", "方法论"
        else:
            topic, cat = "疯狂的里海", "投研-投资体系"
        return f"""---
title: {Path(rel).stem}
topic: {topic}
category: {cat}
created: {TODAY}
updated: {TODAY}
---
"""

    if rel.startswith("vl/concepts/") or rel.startswith("research/articles/concepts/"):
        return f"""---
topic: {title}
category: 投资框架
created: {TODAY}
updated: {TODAY}
---
"""
    elif rel.startswith("vl/entities/") or rel.startswith("research/articles/entities/"):
        return f"""---
entity: {title}
type: 人物/机构
created: {TODAY}
---
"""
    elif rel.startswith("research/articles/papers/"):
        return f"""---
topic: {title}
category: 论文与参考书目
created: {TODAY}
---
"""
    elif rel.startswith("research/articles/synthesis/"):
        return f"""---
title: {title}
type: synthesis
created: {TODAY}
updated: {TODAY}
tags: []
---
"""
    elif rel == "research/overview.md":
        return f"""---
topic: 投研 wiki 概述
category: 索引
created: {TODAY}
updated: {TODAY}
---
"""
    elif rel.startswith("research/") and "/" in rel[9:]:
        # 标的子页面（中英文文件名均可）
        cat = {
            "overview": "数据目录", "概览": "数据目录", "数据目录": "数据目录",
            "thesis": "投资论点", "投资论点": "投资论点",
            "industry-chain": "产业链", "产业链": "产业链",
            "operating-metrics": "运营指标", "运营指标": "运营指标",
            "research-reports": "研报索引", "研报索引": "研报索引",
        }.get(Path(rel).stem, "标的分析")
        return f"""---
topic: {title}
category: {cat}
created: {TODAY}
updated: {TODAY}
---
"""
    return ""


def seealso_specific(rel):
    """按目录返回确定性参见链接。

    一律使用全局唯一的页面名，避免 resolve_link 的 stem 兜底匹配到同名页
    （如各标的目录下都有「运营指标.md」）。
    """
    if rel.startswith("research/泡泡玛特/业绩/"):
        if rel.endswith("业绩会纪要索引（2020-2026）.md"):
            return ["[[经营时间序列（2020-2026）]]"]
        return ["[[业绩会纪要索引（2020-2026）]]"]
    if rel.startswith(("research/拼多多/业绩/", "research/阿里巴巴/业绩/",
                       "research/TME/业绩/")):
        return ["[[艾德勒-四级阅读法]]"]
    if rel.startswith("research/疯狂的里海/"):
        if rel.endswith("疯狂的里海.md"):
            return ["[[里海体系-总览]]", "[[里海-2444投资体系]]"]
        if rel.endswith("里海-2444投资体系.md"):
            return ["[[里海体系-总览]]", "[[疯狂的里海]]"]
        if "/时间线/" in rel:
            return ["[[里海体系-总览]]", "[[里海-2444投资体系]]"]
    if rel.endswith("渠道价格链与经销商利润推演.md"):
        return ["[[渠道改革]]", "[[销量与吨价]]"]
    if rel.endswith(("ben-thompson-ai-capital-cycle.md",
                     "盲眼钟表匠-芒格评价与多元思维模型启示.md")):
        return ["[[芒格格栅理论-多学科思维投资框架]]"]
    return []


def gen_seealso(rel, incoming, seealso_refs, pages):
    """为页面生成 ## 参见 区块内容。"""
    links = list(seealso_specific(rel))
    # 已有的参见链接
    existing = seealso_refs.get(rel, set())
    # 从 incoming 里取 3-5 个最相关的来源页（仅在无确定性规则时使用）
    candidates = []
    if not links:
        for src in incoming.get(rel, set()):
            if src.startswith("raw/"):
                continue
            # 同在 research/articles/ 或 vl/ 下，优先
            if src.startswith("vl/") and rel.startswith("vl/"):
                candidates.append((0, src))
            elif src.startswith("research/") and rel.startswith("research/"):
                candidates.append((0, src))
            else:
                candidates.append((1, src))
        candidates.sort()
        added = set(existing)
        for _, cand in candidates[:5]:
            if cand not in added:
                # 生成相对 wikilink
                cand_stem = Path(cand).stem
                cand_parts = Path(cand).parts
                rel_parts = Path(rel).parts
                # 如果同目录，直接用 stem
                if cand_parts[:-1] == rel_parts[:-1]:
                    links.append(f"[[{cand_stem}]]")
                else:
                    links.append(f"[[{cand}]]")
                added.add(cand)
    if not links:
        return ""
    return "## 参见\n\n" + " · ".join(links) + "\n"


def main():
    pages, key_to_paths = collect()
    all_rels = set(pages.keys())

    # 构建 incoming
    incoming = defaultdict(set)
    seealso_refs = defaultdict(set)
    seealso_missing = set()

    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md",):
            continue
        if rel.startswith("raw/"):
            continue

        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1)
            if raw.startswith("!") or raw.startswith("http"):
                continue
            if "../report/" in raw:
                continue
            link, _ = split_link(raw)
            if not link:
                continue
            cands = resolve_link(link, rel, key_to_paths, all_rels)
            for c in cands:
                cn = c.replace("\\", "/")
                if cn in all_rels and not cn.startswith("raw/"):
                    incoming[cn].add(rel)
                    break

        # 提取参见
        sl = None
        for hdr in ("## 参见", "## 相关页面", "## 相关链接", "## 相关", "## 相关概念"):
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
                    for _c in resolve_link(_link, rel, key_to_paths, all_rels):
                        _cn = _c.replace("\\", "/")
                        if _cn in all_rels:
                            seealso_refs[rel].add(_cn)
                            break
        else:
            base = rel.split("/")[-1]
            need = (
                rel.startswith("vl/concepts/") or rel.startswith("vl/modules/") or
                rel.startswith("vl/entities/") or rel.startswith("research/articles/") or
                (rel.startswith("research/") and "/" in rel[9:])
            )
            if need and base not in ("index.md", "log.md"):
                seealso_missing.add(rel)

    # ----- 执行修复 -----
    fixes_done = []

    for rel, (p, text) in pages.items():
        if rel in ("WIKI-SCHEMA.md",):
            continue
        if rel.startswith("raw/"):
            continue
        base = rel.split("/")[-1]
        if base in ("index.md", "log.md"):
            continue

        new_text = text
        modified = False

        # 1. Frontmatter
        if not FRONT_RE.search(text):
            fm = infer_frontmatter(rel, text)
            if fm:
                new_text = fm + "\n" + text.lstrip("\n")
                modified = True
                fixes_done.append(f"{rel}: +frontmatter")

        # 2. 参见区块（缺或需补反引）
        need_seealso = (
            rel.startswith("vl/concepts/") or rel.startswith("vl/modules/") or
            rel.startswith("vl/entities/") or rel.startswith("research/articles/") or
            (rel.startswith("research/") and "/" in rel[9:])
        )
        if need_seealso:
            if rel in seealso_missing:
                # 完全没有参见区块，生成一个
                sa = gen_seealso(rel, incoming, seealso_refs, pages)
                if sa:
                    new_text = new_text.rstrip() + "\n\n" + sa + "\n"
                    modified = True
                    fixes_done.append(f"{rel}: +seealso")
                    seealso_missing.discard(rel)
            elif rel in seealso_refs and CROSSREF:
                # 有参见但可能缺反引 → 在已有参见后追加（仅 --crossref）
                incoming_srcs = {s for s in incoming.get(rel, set())
                                 if not s.startswith("raw/")}
                missing = incoming_srcs - seealso_refs[rel]
                if missing:
                    # 只补前 2 个最重要的
                    to_add = []
                    for src in list(missing)[:2]:
                        if rel.split("/")[0] == src.split("/")[0]:
                            to_add.append(f"[[{src}]]")
                        else:
                            to_add.append(f"[[{src}]]")
                    if to_add:
                        # 在最后一个参见链接后追加
                        last_idx = new_text.rfind("## 参见")
                        if last_idx < 0:
                            last_idx = new_text.rfind("## 相关")
                        if last_idx >= 0:
                            lines = new_text[last_idx:].split("\n")
                            insert_pos = last_idx + sum(len(l) + 1 for l in lines)
                            if lines[-1].strip():
                                insert_pos = len(new_text)
                            insert_str = "\n" + " · ".join(to_add)
                            new_text = new_text[:insert_pos].rstrip() + insert_str + "\n"
                            modified = True
                            fixes_done.append(f"{rel}: +crossref ({len(to_add)} links)")

        if modified:
            p.write_text(new_text, encoding="utf-8")

    # 报告
    print(f"修复 {len(fixes_done)} 项")
    for f in fixes_done[:30]:
        print(f"  {f}")
    if len(fixes_done) > 30:
        print(f"  ... and {len(fixes_done) - 30} more")
    print(f"\n缺参见区块(未修复): {len(seealso_missing)} 页面")


if __name__ == "__main__":
    main()
