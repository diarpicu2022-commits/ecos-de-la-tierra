import json, base64, sys, os
d = json.load(open(sys.argv[1]))
for k, v in d.items():
    n, dr = k.split('__')
    os.makedirs(f'pl/npc/{n}', exist_ok=True)
    if v.startswith('data:'):
        open(f'pl/npc/{n}/{dr}.png', 'wb').write(base64.b64decode(v.split(',')[1]))
print(sorted({k.split('__')[0] for k in d}))
