import subprocess, sys, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(BASE, ".venv", "Scripts", "python.exe")

codes = ["000807","000933","600595","002128","002532","300308","000651","00883","01368","01378"]
passed, failed = [], []

def set_active(code):
    with open(os.path.join(BASE, "config.py"), "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'ACTIVE_STOCK\s*=\s*"[^"]*"', f'ACTIVE_STOCK = "{code}"', content)
    with open(os.path.join(BASE, "config.py"), "w", encoding="utf-8") as f:
        f.write(content)

for code in codes:
    print(f"\n=== {code} ===")
    set_active(code)
    r1 = subprocess.run([PY, "engine.py"], cwd=BASE, capture_output=True, text=True)
    if r1.returncode != 0:
        print(f"  ENGINE FAILED: {r1.stderr[-200:]}")
        failed.append(code)
        continue
    r2 = subprocess.run([PY, "generate_report.py"], cwd=BASE, capture_output=True, text=True)
    if r2.returncode != 0:
        print(f"  GEN FAILED: {r2.stderr[-200:]}")
        failed.append(code)
        continue
    print(f"  OK: {r2.stdout.strip()}")
    passed.append(code)

set_active("09992")
print(f"\n=== DONE === Pass:{len(passed)} Fail:{len(failed)}")
if failed: print(f"Failed: {failed}")
