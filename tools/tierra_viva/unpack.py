import json, base64, sys, os
src, name = sys.argv[1], sys.argv[2]
d = json.load(open(src))
os.makedirs(f'pl/{name}', exist_ok=True)
for k, v in d.items():
    if not v.startswith('data:'):
        print('FALLO', k, v[:40]); continue
    ext = 'gif' if 'image/gif' in v[:30] else 'png'
    open(f'pl/{name}/{k}.{ext}', 'wb').write(base64.b64decode(v.split(',')[1]))
print(name, sorted(d))
