"""Batch: first fetch+insert HK stocks, then build them."""
import subprocess, sys, os

PYTHON = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
BASE = os.path.dirname(os.path.abspath(__file__))

# HK stocks: need --fetch (01378 no DB, others have DB but stale revenue)
hk_stocks = [
    ("01378", "--cf 15.0 --fetch"),  # no DB
    ("00883", "--cf 15.0 --fetch"),  # DB exists but revenue=0 after fetch
    ("01368", "--cf 15.0 --fetch"),  # same
]
# A stocks: reuse DB
a_stocks = [
    "000807", "000933", "600595", "002128", "002532", "300308", "000651"
]

failed = []
for code, args in hk_stocks:
    cmd = f'"{PYTHON}" build.py {code} {args}'
    print(f"\n{'='*60}\n  HK: {code}\n{'='*60}")
    r = subprocess.run(cmd, shell=True, cwd=BASE, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        failed.append(code)
    else:
        print(f"  OK: {code}")

for code in a_stocks:
    cmd = f'"{PYTHON}" build.py {code} --cf 15.0'
    print(f"\n{'='*60}\n  A: {code}\n{'='*60}")
    r = subprocess.run(cmd, shell=True, cwd=BASE, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        failed.append(code)
    else:
        print(f"  OK: {code}")

print(f"\n{'='*60}")
total = len(hk_stocks) + len(a_stocks)
print(f"  Done. Success: {total-len(failed)}/{total}")
if failed:
    print(f"  Failed: {', '.join(failed)}")
