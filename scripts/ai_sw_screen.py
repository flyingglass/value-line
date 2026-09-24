# -*- coding: utf-8 -*-
"""ai_sw_screen.py — A 股「AI 软件」候选池筛选（庶人哑士六类框架）

背景
----
raw/research/articles/2026-09-24-庶人哑士-大模型吞噬软件-是叙事还是事实.md 提出
「AI 利好软件六类」：①开发端 ②需求端 ③产品端 ④竞争端 ⑤商业模式 ⑥新品类。
本脚本把该框架落到 A 股（用户 2026-09-24 指定优先级：原文点名 > A 股 > 港股通）。

数据源（全部绕开东财，本机东财 push2 连接被重置）
------------------------------------------------
1. 行业边界：`ak.stock_sector_detail(sector=...)` —— 新浪 · 证监会行业分类，
   覆盖沪深京全 A。与软件相关的两个类目：
     hangye_ZI65  软件和信息技术服务业      （~364 只）
     hangye_ZI64  互联网和相关服务          （~63 只）
   自带：最新价 / 市盈率(动态) / 市净率 / 总市值 / 流通市值 / 换手率
2. 财务：`ak.stock_financial_abstract(symbol=<6位代码>)` —— 新浪财务摘要，
   列＝报告期（20260630 = 26H1，20250630 = 25H1），行＝指标。
   关键指标：营业总收入 / 归母净利润 / 毛利率 / 营业总收入增长率 / ROE
   ⚠️ 港股 TDX 损益表没有毛利率，第⑤类「营收涨 + 毛利率降」在港股不可证；
      A 股这一据点可以验证，是本脚本最重要的产出。

用法
----
  .venv\\Scripts\\python scripts\\ai_sw_screen.py              # 全量跑
  .venv\\Scripts\\python scripts\\ai_sw_screen.py --limit 20    # 只跑前 20 只（调试）
  .venv\\Scripts\\python scripts\\ai_sw_screen.py --min-cap 30  # 只保留总市值 ≥30 亿

输出
----
  scripts/out/ai_sw_a.csv          全字段明细
  scripts/out/ai_sw_fin_cache.json 逐只财务拉取缓存（避免重复请求）
"""
import argparse
import csv
import json
import os
import sys
import threading
import time

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import akshare as ak  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_HERE, "out")
CSV_PATH = os.path.join(OUT_DIR, "ai_sw_a.csv")
CACHE_PATH = os.path.join(OUT_DIR, "ai_sw_fin_cache.json")

# 证监会行业类目（新浪挂牌的行业板块代码）
SECTORS = [
    ("hangye_ZI65", "软件和信息技术服务业"),
    ("hangye_ZI64", "互联网和相关服务"),
]

# ── 业务分层（人工按各公司公开主营判定，2026-09-24；仅覆盖 >=50 亿的 228 只）──
# 证监会 ZI65「软件和信息技术服务业」是个大筐，半导体/IDC/游戏/传媒都在里面，必须分层。
# 修改分类请只改这里，重跑即可复现（分层结果写入 out/ai_sw_a_pool.csv）。
EXCLUDE = {
    "芯片/半导体设计": [
        "688256", "688702", "688521", "688536", "688052", "688099", "688368", "688449",
        "688018", "688279", "001270", "300613", "688332", "920138", "300671", "688508",
        "688262", "688325", "688252", "688691", "688699", "300493", "688173", "300183"],
    "传媒/广告/电商/零售": [
        "300413", "002195", "002131", "301171", "603000", "603613", "603888", "600633",
        "002354", "600986", "603533", "003010", "600654", "000676", "600556", "603123",
        "300959", "300785", "002467", "300226", "002123", "300292", "002264", "300792"],
    "游戏": [
        "002602", "002558", "002555", "002517", "603444", "002624", "002174", "300459",
        "300315", "300031", "002605", "300467", "300043"],
    "嵌入式/电力·轨交·军工硬件": [
        "600406", "000997", "600226", "600131", "000682", "300302", "300469", "600640",
        "301248", "301592", "301179", "002970", "300440", "300098", "002298", "688631",
        "000948", "002609"],
    "IDC/算力租赁/机房": [
        "300442", "603881", "300383", "300738", "600589", "300846", "300895", "301085",
        "300249", "603887"],
    "工程/运维/非软商业模式": ["300277", "000032", "002929", "300518"],
}
CORE = {
    "办公与工具软件": ["688111", "688095", "300624", "688615"],
    "企业管理 ERP/OA": ["600588", "603039", "300378", "300687", "300170"],
    "工业/研发设计软件": ["688777", "688083", "301269", "688206", "301095", "688507",
                          "603859", "002410", "300520", "688188"],
    "基础软件/数据库/云": ["688692", "688031", "688158", "600536", "002368", "688365",
                           "920799", "688562", "600845", "688258"],
    "金融IT": ["600570", "688318", "300085", "300674", "603927", "300468", "002987",
               "300377", "600446", "300348", "300872", "603383", "002530"],
    "垂直行业软件": ["002315", "002153", "300253", "300451", "603990", "002063", "301162",
                     "688479", "300525", "301153", "688232", "603171", "300682", "300075",
                     "688109", "002777", "002279", "301556"],
    "网络安全": ["601360", "300454", "688561", "002439", "002268", "600271", "300768",
                 "300188", "002212", "300369", "688225"],
    "AI 原生/智能应用": ["002230", "301638", "300496", "688568", "688343", "300166",
                         "688088", "300229", "688327", "300766", "688787", "688207"],
}
WATCH = {
    "IT服务/系统集成": ["301236", "002065", "600410", "000555", "600718", "300339",
                        "300598", "002649", "300925", "301316", "600797", "300047",
                        "002657", "000158", "300324", "002544", "603220", "600602", "300287"],
    "软硬一体/垂直信息化": ["300418", "301396", "002261", "002990", "002373", "600850",
                            "920116", "600728", "688227", "002093", "301339", "688191",
                            "300300", "002421", "002380", "002232", "000409", "301218",
                            "688228", "300523", "300559"],
    "数据/云/算力服务": ["300017", "300773", "300002", "002405", "301382", "300113",
                         "300634", "300168", "920493", "000503", "300579", "300678"],
}

# 需要的财务指标 → 输出列名
FIN_ITEMS = {
    "营业总收入": "rev",
    "归母净利润": "np",
    "毛利率": "gm",
    "营业总收入增长率": "rev_yoy",
    "归属母公司净利润增长率": "np_yoy",
    "净资产收益率(ROE)": "roe",
}
H1_CUR, H1_PREV = "20260630", "20250630"  # 26H1 / 25H1

_cache_lock = threading.Lock()


def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    with _cache_lock:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=1)


def fetch_sector_members():
    """拉两个行业类目的全部成分（带行情/市值/PE/PB）"""
    rows = []
    for sid, sname in SECTORS:
        try:
            df = ak.stock_sector_detail(sector=sid)
        except Exception as e:
            print("  [ERR] %s %s: %s" % (sid, sname, e))
            continue
        for r in df.to_dict("records"):
            rows.append({
                "symbol": r.get("symbol", ""),
                "code": str(r.get("code", "")).zfill(6),
                "name": str(r.get("name", "")).replace(" ", ""),
                "industry": sname,
                "price": r.get("trade"),
                "pe": r.get("per"),
                "pb": r.get("pb"),
                "mktcap_yi": round((r.get("mktcap") or 0) / 10000.0, 2),   # 万元 → 亿元
                "nmc_yi": round((r.get("nmc") or 0) / 10000.0, 2),
                "turnover": r.get("turnoverratio"),
            })
        print("  %s %-16s %d 只" % (sid, sname, len(df)))
        time.sleep(0.5)
    return rows


def _norm(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f     # NaN → None


def fetch_fin(code, cache, force=False):
    """取某只 A 股的 26H1/25H1 关键财务。返回 dict（金额单位：亿元）"""
    if not force and code in cache:
        return cache[code]
    out = {"ok": False}
    try:
        df = ak.stock_financial_abstract(symbol=code)
        if df is None or df.empty:
            out["err"] = "empty"
        else:
            cols = set(df.columns)
            idx = {}
            for i, row in df.iterrows():
                idx.setdefault(str(row["指标"]), i)
            for cn, key in FIN_ITEMS.items():
                if cn not in idx:
                    continue
                for period, suffix in ((H1_CUR, "_26h1"), (H1_PREV, "_25h1")):
                    if period in cols:
                        out[key + suffix] = _norm(df.at[idx[cn], period])
            # 营收/净利统一为亿元
            for k in ("rev_26h1", "rev_25h1", "np_26h1", "np_25h1"):
                if out.get(k) is not None:
                    out[k] = round(out[k] / 1e8, 4)
            out["ok"] = any(k in out for k in ("rev_26h1", "np_26h1"))
    except Exception as e:
        out["err"] = type(e).__name__
    return out


def compute_derived(row):
    """补齐自算同比（新浪自带增长率缺失时用两期金额自算）"""
    def yoy(cur, prev):
        if cur is None or prev is None or prev == 0:
            return None
        return round((cur - prev) / abs(prev) * 100, 2)

    if row.get("rev_26h1") is not None and row.get("rev_25h1") is not None:
        row["rev_yoy_calc"] = yoy(row["rev_26h1"], row["rev_25h1"])
    if row.get("np_26h1") is not None and row.get("np_25h1") is not None:
        row["np_yoy_calc"] = yoy(row["np_26h1"], row["np_25h1"])
    # 第⑤类判据：营收涨 + 毛利率降（pp）
    g26, g25 = row.get("gm_26h1"), row.get("gm_25h1")
    if g26 is not None and g25 is not None:
        row["gm_chg_pp"] = round(g26 - g25, 2)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 只（调试）")
    ap.add_argument("--min-cap", type=float, default=0.0, help="总市值下限（亿元）")
    ap.add_argument("--workers", type=int, default=6, help="并发数")
    ap.add_argument("--force", action="store_true", help="忽略财务缓存重拉")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    requests.DEFAULT_TIMEOUT = 20

    print("== 1. 拉行业成分 ==")
    rows = fetch_sector_members()
    if not rows:
        raise SystemExit("没有拿到任何成分股")

    print("\n== 2. 清洗 ==")
    before = len(rows)
    # 去重（同一只可能跨两个类目？理论上不会，但保险）
    seen, uniq = set(), []
    for r in rows:
        if r["code"] in seen:
            continue
        seen.add(r["code"])
        uniq.append(r)
    rows = uniq
    # 剔除 ST / *ST / 退市
    bad = [r for r in rows if ("ST" in r["name"].upper() or "退" in r["name"])]
    rows = [r for r in rows if r not in bad]
    # 市值门槛
    if args.min_cap > 0:
        rows = [r for r in rows if (r["mktcap_yi"] or 0) >= args.min_cap]
    print("  成分 %d → 去重 %d → 剔 ST/退市(-%d) → 市值≥%s亿：%d 只"
          % (before, len(uniq), len(bad), args.min_cap or 0, len(rows)))

    rows.sort(key=lambda r: -(r["mktcap_yi"] or 0))
    if args.limit:
        rows = rows[:args.limit]

    print("\n== 3. 拉 26H1/25H1 财务（新浪，并发 %d）==" % args.workers)
    cache = load_cache()
    todo = [r for r in rows if args.force or r["code"] not in cache]
    print("  需拉取 %d / %d 只（其余走缓存）" % (len(todo), len(rows)))

    def worker(chunk):
        for r in chunk:
            res = fetch_fin(r["code"], cache, force=args.force)
            with _cache_lock:
                cache[r["code"]] = res
            if res.get("ok"):
                print("    %s %s ok" % (r["code"], r["name"]))
            else:
                print("    %s %s FAIL %s" % (r["code"], r["name"], res.get("err", "?")))

    if todo:
        n = max(1, args.workers)
        chunks = [todo[i::n] for i in range(n)]
        threads = [threading.Thread(target=worker, args=(c,)) for c in chunks]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        save_cache(cache)

    print("\n== 4. 汇总 ==")
    for r in rows:
        fin = cache.get(r["code"], {})
        for k, v in fin.items():
            if k not in ("ok", "err"):
                r[k] = v
        if fin.get("err"):
            r["fin_err"] = fin["err"]
        compute_derived(r)

    ok_cnt = sum(1 for r in rows if r.get("rev_26h1") is not None)
    gm_cnt = sum(1 for r in rows if r.get("gm_chg_pp") is not None)
    print("  有 26H1 营收 %d 只；有毛利率同比 %d 只" % (ok_cnt, gm_cnt))

    fields = ["code", "name", "industry", "price", "pe", "pb", "mktcap_yi", "nmc_yi",
              "rev_26h1", "rev_25h1", "rev_yoy_calc", "np_26h1", "np_25h1", "np_yoy_calc",
              "gm_26h1", "gm_25h1", "gm_chg_pp", "roe_26h1", "fin_err"]
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("  已写入 %s（%d 行）" % (CSV_PATH, len(rows)))

    # ── 5. 业务分层（仅对 >=50 亿的池子，--limit 调试时跳过）──
    if not args.limit:
        pool = [r for r in rows if (r["mktcap_yi"] or 0) >= 50]
        idx_core = {c: g for g, cs in CORE.items() for c in cs}
        idx_watch = {c: g for g, cs in WATCH.items() for c in cs}
        idx_excl = {c: g for g, cs in EXCLUDE.items() for c in cs}
        for r in pool:
            c6 = r["code"]
            if c6 in idx_core:
                r["tier"], r["group"] = "核心", idx_core[c6]
            elif c6 in idx_watch:
                r["tier"], r["group"] = "观望", idx_watch[c6]
            elif c6 in idx_excl:
                r["tier"], r["group"] = "剔除", idx_excl[c6]
            else:
                r["tier"], r["group"] = "未归类", ""

        print("\n== 5. 业务分层（总市值 >=50 亿：%d 只）==" % len(pool))
        for t in ("核心", "观望", "剔除", "未归类"):
            n = sum(1 for r in pool if r["tier"] == t)
            print("  %-4s %3d 只" % (t, n))
        for t, mapping in (("核心", CORE), ("观望", WATCH)):
            print("  — %s明细 —" % t)
            for g in mapping:
                n = sum(1 for r in pool if r["tier"] == t and r["group"] == g)
                print("      %-22s %2d 只" % (g, n))
        un = [r for r in pool if r["tier"] == "未归类"]
        if un:
            print("  ⚠️ 未归类：%s" % ", ".join("%s %s" % (r["code"], r["name"]) for r in un))

        pcols = ["code", "name", "tier", "group", "mktcap_yi", "pe", "pb", "rev_26h1",
                 "rev_yoy_calc", "np_26h1", "gm_26h1", "gm_chg_pp"]
        with open(os.path.join(OUT_DIR, "ai_sw_a_pool.csv"), "w",
                  encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=pcols, extrasaction="ignore")
            w.writeheader()
            w.writerows(pool)
        print("  分层明细已写入 %s" % os.path.join(OUT_DIR, "ai_sw_a_pool.csv"))

        # 第⑤类判据：营收涨 + 毛利率降（原文「订阅转 token」的本地验证）
        cw = [r for r in pool if r["tier"] in ("核心", "观望")]
        down = sum(1 for r in cw if (r.get("gm_chg_pp") or 0) < 0)
        up = sum(1 for r in cw if (r.get("gm_chg_pp") or 0) > 0)
        t5 = [r for r in cw if (r.get("rev_yoy_calc") or -999) >= 25
              and (r.get("gm_chg_pp") or 999) <= -1]
        both_down = sum(1 for r in cw if (r.get("rev_yoy_calc") or 0) < 0
                        and (r.get("gm_chg_pp") or 0) < 0)
        print("\n== 6. 第⑤类判据（核心+观望 %d 只）==" % len(cw))
        print("  毛利率降 %d / 升 %d ；营收增 %d / 减 %d" % (
            down, up, sum(1 for r in cw if (r.get("rev_yoy_calc") or 0) > 0),
            sum(1 for r in cw if (r.get("rev_yoy_calc") or 0) < 0)))
        print("  严格满足「营收>=25%% 且 毛利率降>=1pp」：%d 只 → %s" % (
            len(t5), "、".join("%s %s" % (r["code"], r["name"]) for r in sorted(
                t5, key=lambda x: -(x.get("rev_yoy_calc") or 0)))))
        print("  双降（营收负增长 + 毛利率降）：%d 只" % both_down)

    print("\n== 7. 前 30 只（按总市值降序）==")
    hdr = "%-6s %-8s %8s %8s %7s %9s %9s %8s %8s" % (
        "代码", "名称", "总市值亿", "PE", "PB", "26H1营收", "同比%", "毛利率%", "Δpp")
    print(hdr)
    print("-" * len(hdr))
    for r in rows[:30]:
        print("%-6s %-8s %8s %8s %7s %9s %9s %8s %8s" % (
            r["code"], r["name"][:8],
            r["mktcap_yi"], r["pe"] if r["pe"] is not None else "-",
            r["pb"] if r["pb"] is not None else "-",
            r.get("rev_26h1"), r.get("rev_yoy_calc") if r.get("rev_yoy_calc") is not None else "-",
            r.get("gm_26h1") if r.get("gm_26h1") is not None else "-",
            r.get("gm_chg_pp") if r.get("gm_chg_pp") is not None else "-"))


if __name__ == "__main__":
    main()
