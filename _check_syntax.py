import os, py_compile
err = 0
total = 0
for r, ds, fs in os.walk('scripts'):
    for f in fs:
        if f.endswith('.py') and not f.startswith('__'):
            total += 1
            fp = os.path.join(r, f)
            try:
                py_compile.compile(fp, doraise=True)
            except py_compile.PyCompileError as e:
                print(f'ERR {fp}: {e}')
                err += 1
print(f'Total: {total}, Errors: {err}')
