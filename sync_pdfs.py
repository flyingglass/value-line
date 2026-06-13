# -*- coding: utf-8 -*-
"""
sync_pdfs.py — 微云双向增量同步 data/pdfs 目录
  用法:
    python sync_pdfs.py upload     # 上传本地新/变更的 PDF
    python sync_pdfs.py download   # 从微云下载缺失的 PDF
    python sync_pdfs.py status     # 查看同步状态

  增量策略: 文件名 + 文件大小比对, 跳过已同步文件。
  微云:  value-line-pdfs/<stock_code>/<filename>.pdf
  本地:  data/pdfs/<stock_code>/<filename>.pdf
"""
import os, sys, json, io, argparse, time, subprocess, hashlib, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests as _requests

BASE = os.path.dirname(os.path.abspath(__file__))
PDFS = os.path.join(BASE, "data", "pdfs")
WEIYUN_SKILL = os.path.join(os.environ.get("USERPROFILE",
    os.path.expanduser("~")), ".codebuddy", "skills", "weiyun")
UPLOAD_SCRIPT = os.path.join(WEIYUN_SKILL, "scripts", "upload_to_weiyun.py")
MCP_URL = "https://www.weiyun.com/api/v3/mcpserver"

# ═══ 配置 (从 weiyun MCP 连接器获取) ═══
TOKEN = "dc6f586424684555634a37d31e774d8c"
_VL_ROOT_PDIR = "98405d2ff0a739ae12b58dcd423dce4a"
_VL_PDFS_PDIR = "98405d2f491a350c331c685eaaf47b48"
_WORKERS = 8  # 上传并发数

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_lock = threading.Lock()  # 终端输出互斥

# ══════════════════════════════════════════════════════
# JSON-RPC 2.0 MCP 调用 (与 upload_to_weiyun.py 同协议)
# ══════════════════════════════════════════════════════

_request_id = 0
_HEADERS = {"Content-Type": "application/json", "WyHeader": f"mcp_token={TOKEN}"}

def _mcp_call(tool_name, arguments, timeout=60):
    global _request_id
    _request_id += 1
    payload = {"jsonrpc": "2.0", "id": _request_id, "method": "tools/call",
               "params": {"name": tool_name, "arguments": arguments}}
    try:
        resp = _requests.post(MCP_URL, headers=_HEADERS, json=payload, timeout=timeout)
        resp.raise_for_status()
        result = resp.json()
        for item in result.get("result", {}).get("content", []):
            if item.get("type") == "text":
                return json.loads(item["text"])
        return result.get("result", {})
    except Exception as e:
        print(f"  [API err] {tool_name}: {e}")
        return None

# ══════════════════════════════════════════════════════
# 微云操作
# ══════════════════════════════════════════════════════

def _list_dir(dir_key, pdir_key=_VL_PDFS_PDIR):
    """列出微云目录下所有文件: [{name, file_id, size, pdir_key}, ...]"""
    files = []
    offset = 0
    while True:
        r = _mcp_call("weiyun.list", {"limit": 50, "offset": offset, "get_type": 2,
                                       "dir_key": dir_key, "pdir_key": pdir_key,
                                       "order_by": 1})
        if not r:
            break
        pdir = r.get("pdir_key", pdir_key)
        for f in r.get("file_list", []):
            fn = f.get("filename") or f.get("file_name", "")
            sz = f.get("file_size") or 0
            if sz == 0:  # try ext_info
                sz = f.get("ext_info", {}).get("file_size", 0) or 0
            if fn and f.get("file_id"):
                files.append({"name": fn, "file_id": f["file_id"], "size": sz, "pdir_key": pdir})
        if r.get("finish_flag") or not r.get("file_list"):
            break
        offset += len(r.get("file_list", []))
    return files


def _list_code_dirs():
    """列出微云 value-line-pdfs/ 下所有 stock code 子目录: {code: dir_key}"""
    r = _mcp_call("weiyun.list", {"limit": 50, "get_type": 1, "dir_key": _VL_PDFS_PDIR,
                                   "pdir_key": _VL_PDFS_PDIR, "order_by": 1})
    if not r:
        return {}
    return {d.get("dir_name", ""): d.get("dir_key", "")
            for d in r.get("dir_list", []) if d.get("dir_name")}


def _ensure_code_dir(code):
    """确保微云上存在 stock code 子目录, 返回 dir_key"""
    existing = _list_code_dirs()
    if code in existing:
        return existing[code]
    cr = _mcp_call("weiyun.create_dir", {"dir_name": code, "pdir_key": _VL_PDFS_PDIR})
    if cr and cr.get("dir_key"):
        print(f"  创建微云目录: {code}")
        return cr["dir_key"]
    return None


def _scan_remote():
    """扫描微云全部文件: {(code, filename): {file_id, size, pdir_key}}"""
    code_dirs = _list_code_dirs()
    result = {}
    for code, dk in code_dirs.items():
        for f in _list_dir(dk, pdir_key=_VL_PDFS_PDIR):
            if f["name"] and f["file_id"]:
                result[(code, f["name"])] = f
    return result


def _download_one(file_id, pdir_key, size):
    """获取单个文件的下载链接，返回 (url, cookie) 或 (None, None)"""
    dl = _mcp_call("weiyun.download",
                   {"items": [{"file_id": file_id, "pdir_key": pdir_key}]})
    if not dl:
        return None, None
    items = dl.get("download_url_list") or dl.get("items") or []
    if not items:
        return None, None
    return items[0].get("https_download_url", ""), items[0].get("cookie", "")


# ══════════════════════════════════════════════════════
# 本地扫描
# ══════════════════════════════════════════════════════

def _scan_local():
    """{(code, filename): size}"""
    local = {}
    if not os.path.isdir(PDFS):
        return local
    for code in os.listdir(PDFS):
        dp = os.path.join(PDFS, code)
        if not os.path.isdir(dp):
            continue
        for fn in os.listdir(dp):
            if fn.endswith((".pdf", ".json")):
                local[(code, fn)] = os.path.getsize(os.path.join(dp, fn))
    return local


# ══════════════════════════════════════════════════════
# 同步命令
# ══════════════════════════════════════════════════════

def status():
    local = _scan_local()
    print(f"本地: {len(local)} 个 PDF")
    remote = _scan_remote()
    print(f"微云: {len(remote)} 个 PDF")

    lk, rk = set(local.keys()), set(remote.keys())
    ul = lk - rk; dl = rk - lk
    common = lk & rk
    size_diff = {k for k in common if abs(local[k] - remote[k]["size"]) > 10}

    print(f"\n  仅本地(需上传): {len(ul)}")
    print(f"  仅微云(需下载): {len(dl)}")
    print(f"  大小差异(需更新): {len(size_diff)}")
    print(f"  已同步: {len(common)-len(size_diff)}")


def _upload_one(code, fn, fp, local_sz, pdir, tag, idx, total):
    """上传单个文件，返回 (code, fn, ok)"""
    with _lock:
        print(f"  [{tag}] {code}/{fn} ({local_sz/1024:.0f}KB) [{idx}/{total}]...", end=" ", flush=True)
    try:
        cmd = [sys.executable, UPLOAD_SCRIPT, fp, "--token", TOKEN,
               "--pdir_key", pdir, "--mcp_url", MCP_URL]
        r2 = subprocess.run(cmd, capture_output=True, timeout=180,
                            encoding="utf-8", errors="replace")
        if r2.returncode == 0:
            with _lock:
                print("OK")
            return (code, fn, True)
        else:
            err = (r2.stderr or r2.stdout or "unknown")[:120]
            with _lock:
                print(f"FAIL: {err}")
            return (code, fn, False)
    except subprocess.TimeoutExpired:
        with _lock:
            print("TIMEOUT")
        return (code, fn, False)
    except Exception as e:
        with _lock:
            print(f"ERR: {e}")
        return (code, fn, False)


def upload():
    local = _scan_local()
    remote = _scan_remote()
    print(f"本地 {len(local)} 个, 微云 {len(remote)} 个, {_WORKERS} 线程并发")

    # 筛选需上传的文件
    tasks = []
    for (code, fn), local_sz in sorted(local.items()):
        r = remote.get((code, fn))
        if r and abs(local_sz - r["size"]) <= 10:
            continue
        pdir = _ensure_code_dir(code)
        if not pdir:
            print(f"  SKIP {code}/{fn}: 无法创建微云目录")
            continue
        fp = os.path.join(PDFS, code, fn)
        tag = "UPDATE" if r else "NEW"
        tasks.append((code, fn, fp, local_sz, pdir, tag))

    if not tasks:
        print("全部已同步!")
        return

    total = len(tasks)
    print(f"待上传: {total} 个\n")
    ok, fail = 0, 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=_WORKERS) as pool:
        futures = {pool.submit(_upload_one, code, fn, fp, sz, pdir, tag, i+1, total):
                   (code, fn) for i, (code, fn, fp, sz, pdir, tag) in enumerate(tasks)}
        for fut in as_completed(futures):
            code, fn, success = fut.result()
            if success:
                ok += 1
            else:
                fail += 1

    elapsed = time.time() - t0
    print(f"\n上传完成: {ok} 成功, {fail} 失败, 耗时 {elapsed/60:.1f} 分钟")


def download():
    local = _scan_local()
    remote = _scan_remote()
    print(f"本地 {len(local)} 个, 微云 {len(remote)} 个")
    count = 0
    for (code, fn), info in sorted(remote.items()):
        local_sz = local.get((code, fn))
        if local_sz and abs(local_sz - info["size"]) <= 10:
            continue
        local_dir = os.path.join(PDFS, code)
        os.makedirs(local_dir, exist_ok=True)
        url, cookie = _download_one(info["file_id"], info["pdir_key"], info["size"])
        if not url:
            print(f"  SKIP {code}/{fn}: 无下载链接")
            continue
        fp = os.path.join(local_dir, fn)
        tag = "UPDATE" if local_sz else "NEW"
        print(f"  [{tag}] {code}/{fn} ({info['size']/1024:.0f}KB)...", end=" ", flush=True)
        try:
            r = _requests.get(url, headers={"Cookie": cookie} if cookie else {},
                              timeout=120, allow_redirects=True)
            r.raise_for_status()
            with open(fp, "wb") as f:
                f.write(r.content)
            print("OK"); count += 1
        except Exception as e:
            print(f"ERR: {e}")
    print(f"\n下载完成: {count} 个")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="微云增量同步 data/pdfs")
    p.add_argument("action", choices=["upload", "download", "status"])
    a = p.parse_args()
    if a.action == "status":   status()
    elif a.action == "upload":  upload()
    elif a.action == "download": download()
