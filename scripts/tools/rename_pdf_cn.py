# -*- coding: utf-8 -*-
"""把 data/pdfs/<中文名>/ 下的财报文件统一为「<代码>_<中文名>_<年>_<期次>.pdf」。

背景：
  data/pdfs 的目录已按中文公司名命名（config.pdf_name），但目录内文件仍是
  <code>_<年>_<期次>.pdf（如 600519_贵州茅台_2024_年报.pdf）。两者混用不便于人工检索，
  也和「目录/文件都能看出是哪家公司」的初衷不一致，故把文件名补上中文名。

规则：
  1. 标准财报  <code>_<年>_<期次>.pdf|.htm   →  <code>_<中文名>_<年>_<期次>.pdf|.htm
  2. 招股书    <code>_<年>_招股书_<后缀>.pdf →  <code>_<中文名>_<年>_招股书_<后缀>.pdf
  3. validation.json 随主文件改名，并把内部 "pdf" 字段刷成新的绝对路径
     （原值停留在旧的数字目录时代，如 data\\pdfs\\600519\\...，已失效）
  4. 中文名取文件所在目录名（= config.pdf_name），保证文件与目录一致
  5. 已是中文全名的研报（如 2025-03-27-海通国际-泡泡玛特点评报告...pdf）不动

幂等：文件已含中文名则跳过；json 独立成一个 pass，因此主文件已改名、
json 仍是旧名时（上一轮中断留下的孤儿 json）重跑即可补齐。

用法：
  .venv\\Scripts\\python scripts\\tools\\rename_pdf_cn.py            # dry-run，只写清单
  .venv\\Scripts\\python scripts\\tools\\rename_pdf_cn.py --apply     # 真正改名
"""
import argparse
import json
import os
import re
import sys
import traceback

if sys.platform == "win32":
    sys.stdout = __import__("io").TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "pdfs"))
PERIOD = r"(?:年报|中报|一季报|三季报|Q[1-4])"
TAIL = PERIOD + r"|招股书_.+"

# <code>_<年>_<期次|招股书后缀>.pdf/.htm
RE_STD = re.compile(r"^([0-9A-Za-z]{4,6})_((?:19|20)\d{2})_(%s)\.(pdf|htm)$" % TAIL)
# 已带中文名（幂等：重复跑不改名）
RE_DONE = re.compile(r"^[0-9A-Za-z]{4,6}_[^_]+_((?:19|20)\d{2})_")


def new_name(fname, cn):
    """返回新文件名；不符合规则或已含中文名则返回 None。"""
    m = RE_STD.match(fname)
    if not m or RE_DONE.match(fname):
        return None
    return "%s_%s_%s_%s.%s" % (m.group(1), cn, m.group(2), m.group(3), m.group(4))


def old_json_re(fname):
    """旧式 validation.json → (code, year, tail)；否则 None。"""
    if not fname.endswith(".validation.json"):
        return None
    stem = fname[:-len(".validation.json")]
    for ext in (".pdf", ".htm"):
        m = RE_STD.match(stem + ext)
        if m and not RE_DONE.match(stem + ext):
            return m.group(1), m.group(2), m.group(3)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正执行改名（默认 dry-run）")
    a = ap.parse_args()

    renamed, json_fixed, failed, orphan = [], 0, [], []

    for dirpath, _dirs, files in os.walk(BASE):
        cn = os.path.basename(dirpath)
        parent = os.path.basename(os.path.dirname(dirpath))
        if cn == "data" or (parent == "pdfs" and cn == "研报"):
            continue
        fileset = set(files)

        # ---- Pass 1: validation.json（改名 + 刷内部 pdf 字段）----
        for f in sorted(files):
            key = old_json_re(f)
            if not key:
                continue
            code, year, tail = key
            j_old = os.path.join(dirpath, f)
            j_new = os.path.join(dirpath, "%s_%s_%s_%s.validation.json"
                                 % (code, cn, year, tail))
            # 主文件（已改名取新名，否则取旧名）
            new_main = os.path.join(dirpath, "%s_%s_%s_%s" % (code, cn, year, tail))
            main_path = None
            for ext in (".pdf", ".htm"):
                if new_main + ext in fileset:
                    main_path = new_main + ext
                    break
            if main_path is None:
                for ext in (".pdf", ".htm"):
                    p = os.path.join(dirpath, "%s_%s_%s%s" % (code, year, tail, ext))
                    if os.path.exists(p):
                        main_path = p
                        break
            if main_path is None:
                orphan.append(os.path.relpath(j_old, BASE))
                continue
            renamed.append((os.path.relpath(j_old, BASE), os.path.basename(j_new)))
            if not a.apply:
                continue
            try:
                with open(j_old, encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict) and "pdf" in data:
                    data["pdf"] = main_path
                with open(j_new, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                os.remove(j_old)
                json_fixed += 1
            except Exception as e:
                failed.append("json %s: %s\n%s"
                              % (f, e, traceback.format_exc().strip()[-300:]))

        # ---- Pass 2: 主文件 ----
        for f in sorted(files):
            if not (f.endswith(".pdf") or f.endswith(".htm")):
                continue
            nf = new_name(f, cn)
            if nf is None:
                continue
            old, new = os.path.join(dirpath, f), os.path.join(dirpath, nf)
            renamed.append((os.path.relpath(old, BASE), nf))
            if not a.apply:
                continue
            if os.path.exists(new):
                failed.append("目标已存在，跳过: %s" % nf)
                continue
            try:
                os.rename(old, new)
            except OSError as e:
                failed.append("%s -> %s : %s" % (f, nf, e))

    out = ["模式: %s" % ("APPLY" if a.apply else "DRY-RUN"),
           "改名总数: %d   json 同步: %d   孤儿 json(无主文件): %d   失败: %d"
           % (len(renamed), json_fixed, len(orphan), len(failed))]
    if failed:
        out.append("--- 失败 ---")
        out += ["  " + s for s in failed[:20]]
    if orphan:
        out.append("--- 孤儿 json ---")
        out += ["  " + s for s in orphan[:20]]
    dst = os.path.normpath(os.path.join(BASE, "..", "..", "scripts", "out", "_rename.txt"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("\n".join(out[:3]))


if __name__ == "__main__":
    main()
