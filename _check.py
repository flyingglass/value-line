import os
d = 'scripts'
required = ['business_commentary.py','insert_revenue.py','metric_adjustment.py','extract_business.py']
ok = 0
partial = []
for code in sorted(os.listdir(d)):
    path = os.path.join(d, code)
    if not os.path.isdir(path): continue
    files = [f for f in os.listdir(path) if f.endswith('.py') and not f.startswith('__')]
    missing = [s for s in required if s not in files]
    if missing:
        partial.append(code)
    else:
        ok += 1
print(f'FULL: {ok}')
print(f'PARTIAL: {len(partial)}')
for p in partial:
    print(f'  {p}: {[f for f in os.listdir(os.path.join(d,p)) if f.endswith(".py") and not f.startswith("__")]}')
