# -*- coding: utf-8 -*-
"""
fetch_us_pdf.py — SEC EDGAR 10-K 年报下载
通过 SEC EDGAR API 下载美股 10-K 年报，存入 data/pdfs/<code>/

用法: python scripts/fetch_us_pdf.py GOOGL
     python scripts/fetch_us_pdf.py GOOGL --years 5  # 下载最近5年
"""
import json, os, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# SEC EDGAR API 端点
SEC_SUBMISSIONS_API = "https://data.sec.gov/submissions/CIK{}.json"
SEC_ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data"

# User-Agent (SEC 要求)
HEADERS = {"User-Agent": "ValueLine-Research value-line@example.com"}

# ⚠️ SEC API 限速: 10 req/sec, 使用延迟避免被封
RATE_LIMIT = 0.15  # seconds between requests


def _cik_padded(cik: str) -> str:
    """CIK 去掉前导零，用于 EDGAR URL"""
    return cik.lstrip("0")


def _get_submissions(cik: str) -> dict:
    """获取公司 filing 历史 (JSON)"""
    padded = cik.zfill(10)
    url = SEC_SUBMISSIONS_API.format(padded)
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"SEC API 请求失败: {e}")


def _get_historical_filings(cik: str, submissions: dict) -> list:
    """获取历史 filings (SEC 'recent' 只返回 ~2年, 需读取 'files' 历史文件)"""
    all_filings = {
        "accessionNumber": [],
        "form": [],
        "primaryDocument": [],
        "reportDate": [],
    }
    # Step 1: recent filings
    recent = submissions.get("filings", {}).get("recent", {})
    for key in all_filings:
        if key in recent:
            all_filings[key].extend(recent[key])

    # Step 2: historical files (older years)
    # URL pattern: https://data.sec.gov/submissions/<filename>
    SEC_SUBMISSIONS_DIR = "https://data.sec.gov/submissions"
    files_list = submissions.get("filings", {}).get("files", [])
    for f_info in files_list:
        file_name = f_info.get("name", "")
        if not file_name:
            continue
        url = f"{SEC_SUBMISSIONS_DIR}/{file_name}"
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for key in all_filings:
                    if key in data:
                        all_filings[key].extend(data[key])
            time.sleep(RATE_LIMIT)
        except Exception as e:
            print(f"    历史文件 {file_name} 读取失败: {e}")
    return all_filings


def _download_filing(cik_short: str, accession: str, primary_doc: str, dest: str) -> bool:
    """下载单个 filing 文件到 dest"""
    # accession number 去连字符: 0001652044-25-000006 → 000165204425000006
    acc_no_dash = accession.replace("-", "")
    url = f"{SEC_ARCHIVE_BASE}/{cik_short}/{acc_no_dash}/{primary_doc}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            # SEC 返回 HTML/PDF，保存时保留原始扩展名
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"    下载失败: {e}")
        return False


def fetch_us_pdfs(code: str, years: int = 5):
    """下载美股 10-K 年报到 data/pdfs/<code>/"""
    stock = config.STOCKS.get(code, {})
    if not stock or stock.get("market") != "us":
        raise SystemExit(f"{code} 不是有效的美股标的")

    cik = stock.get("cik", "")
    if not cik:
        raise SystemExit(f"{code} 缺少 CIK 配置")

    pdf_dir = config.pdf_dir(code)
    name = stock["name"]
    cik_short = _cik_padded(cik)

    print(f"\n{'='*50}")
    print(f"SEC EDGAR → {name} ({code}) CIK={cik}")
    print(f"目标: {pdf_dir}")
    print(f"{'='*50}\n")

    # 1. 获取 filing 历史 (recent + historical)
    print("  获取 filing 列表...", end=" ", flush=True)
    submissions = _get_submissions(cik)
    filings = _get_historical_filings(cik, submissions)
    accessions = filings.get("accessionNumber", [])
    forms = filings.get("form", [])
    primary_docs = filings.get("primaryDocument", [])
    report_dates = filings.get("reportDate", [])
    print(f"{len(accessions)} 条记录 (含历史)")

    # 2. 筛选 10-K 年报 (排除 10-K/A 修正版)
    k10_list = []
    for i in range(len(forms)):
        if forms[i] == "10-K" and accessions[i] and primary_docs[i]:
            # 检查是否已下载
            dest_name = f"{code}-10K-{report_dates[i]}.htm"
            dest = os.path.join(pdf_dir, dest_name)
            if not os.path.exists(dest):
                k10_list.append({
                    "accession": accessions[i],
                    "primary_doc": primary_docs[i],
                    "report_date": report_dates[i],
                    "dest": dest,
                })

    k10_list.sort(key=lambda x: x["report_date"], reverse=True)
    k10_list = k10_list[:years]

    if not k10_list:
        existing = len([f for f in os.listdir(pdf_dir) if f.endswith(".htm")])
        print(f"  所有 10-K 已下载 ({existing} 份)")
        return

    print(f"  待下载: {len(k10_list)} 份 10-K\n")

    # 3. 下载
    success = 0
    for i, k in enumerate(k10_list):
        rd = k["report_date"]
        print(f"  [{i+1}/{len(k10_list)}] FY{rd[:4]} 10-K ({k['accession']}) ", end="", flush=True)
        if _download_filing(cik_short, k["accession"], k["primary_doc"], k["dest"]):
            size_kb = os.path.getsize(k["dest"]) / 1024
            print(f"OK ({size_kb:.0f}KB)")
            success += 1
        time.sleep(RATE_LIMIT)

    # 4. 汇总
    total = len([f for f in os.listdir(pdf_dir) if f.endswith((".htm", ".pdf"))])
    print(f"\n  完成: 下载 {success}/{len(k10_list)}, 共 {total} 份年报文件")
    return success


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "GOOGL"
    years = 5
    for i, arg in enumerate(sys.argv):
        if arg == "--years" and i + 1 < len(sys.argv):
            years = int(sys.argv[i + 1])
    fetch_us_pdfs(code, years)
