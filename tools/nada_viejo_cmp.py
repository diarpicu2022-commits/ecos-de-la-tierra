"""Pone una captura del juego y su referencia del sistema lado a lado, a la
misma altura y sin filtrar: python tools/nada_viejo_cmp.py <salida> <a> <b> [alto]"""
import sys
from PIL import Image

out, a, b = sys.argv[1:4]
h = int(sys.argv[4]) if len(sys.argv) > 4 else 720
ims = [Image.open(p).convert("RGB") for p in (a, b)]
ims = [i.resize((round(i.width * h / i.height), h), Image.NEAREST) for i in ims]
w = Image.new("RGB", (ims[0].width + ims[1].width + 8, h), (0, 0, 0))
w.paste(ims[0], (0, 0))
w.paste(ims[1], (ims[0].width + 8, 0))
w.save(out)
