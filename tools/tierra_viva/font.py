"""Fuente «Brote»: pixel art proporcional, mayúsculas de 7 px, minúsculas de 5 px,
descendentes de 2 px y tildes. Exporta BMFont (.fnt + .png) para Godot y TTF/WOFF2 para web."""
import sys
from PIL import Image

U = {
'A': '.###.|#...#|#...#|#####|#...#|#...#|#...#',
'B': '####.|#...#|#...#|####.|#...#|#...#|####.',
'C': '.###.|#...#|#....|#....|#....|#...#|.###.',
'D': '####.|#...#|#...#|#...#|#...#|#...#|####.',
'E': '#####|#....|#....|####.|#....|#....|#####',
'F': '#####|#....|#....|####.|#....|#....|#....',
'G': '.###.|#...#|#....|#.###|#...#|#...#|.####',
'H': '#...#|#...#|#...#|#####|#...#|#...#|#...#',
'I': '###|.#.|.#.|.#.|.#.|.#.|###',
'J': '..###|...#.|...#.|...#.|#..#.|#..#.|.##..',
'K': '#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#',
'L': '#....|#....|#....|#....|#....|#....|#####',
'M': '#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#',
'N': '#...#|##..#|#.#.#|#..##|#...#|#...#|#...#',
'O': '.###.|#...#|#...#|#...#|#...#|#...#|.###.',
'P': '####.|#...#|#...#|####.|#....|#....|#....',
'Q': '.###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#',
'R': '####.|#...#|#...#|####.|#.#..|#..#.|#...#',
'S': '.###.|#...#|#....|.###.|....#|#...#|.###.',
'T': '#####|..#..|..#..|..#..|..#..|..#..|..#..',
'U': '#...#|#...#|#...#|#...#|#...#|#...#|.###.',
'V': '#...#|#...#|#...#|#...#|.#.#.|.#.#.|..#..',
'W': '#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#',
'X': '#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#',
'Y': '#...#|#...#|.#.#.|..#..|..#..|..#..|..#..',
'Z': '#####|....#|...#.|..#..|.#...|#....|#####',
'a': '....|....|.##.|...#|.###|#..#|.###',
'b': '#...|#...|###.|#..#|#..#|#..#|###.',
'c': '....|....|.##.|#..#|#...|#..#|.##.',
'd': '...#|...#|.###|#..#|#..#|#..#|.###',
'e': '....|....|.##.|#..#|####|#...|.###',
'f': '.##|#..|###|#..|#..|#..|#..',
'g': '....|....|.###|#..#|#..#|#..#|.###|...#|.##.',
'h': '#...|#...|###.|#..#|#..#|#..#|#..#',
'i': '#|.|#|#|#|#|#',
'j': '..#|...|..#|..#|..#|..#|..#|#.#|.#.',
'k': '#...|#...|#..#|#.#.|##..|#.#.|#..#',
'l': '#.|#.|#.|#.|#.|#.|.#',
'm': '.....|.....|####.|#.#.#|#.#.#|#.#.#|#.#.#',
'n': '....|....|###.|#..#|#..#|#..#|#..#',
'o': '....|....|.##.|#..#|#..#|#..#|.##.',
'p': '....|....|###.|#..#|#..#|#..#|###.|#...|#...',
'q': '....|....|.###|#..#|#..#|#..#|.###|...#|...#',
'r': '...|...|#.#|##.|#..|#..|#..',
's': '....|....|.###|#...|.##.|...#|###.',
't': '.#.|.#.|###|.#.|.#.|.#.|..#',
'u': '....|....|#..#|#..#|#..#|#..#|.###',
'v': '.....|.....|#...#|#...#|.#.#.|.#.#.|..#..',
'w': '.....|.....|#...#|#.#.#|#.#.#|#.#.#|.#.#.',
'x': '....|....|#..#|#..#|.##.|#..#|#..#',
'y': '....|....|#..#|#..#|#..#|#..#|.###|...#|.##.',
'z': '....|....|####|...#|.##.|#...|####',
'0': '.###.|#...#|#..##|#.#.#|##..#|#...#|.###.',
'1': '.#.|##.|.#.|.#.|.#.|.#.|###',
'2': '.###.|#...#|....#|...#.|..#..|.#...|#####',
'3': '####.|....#|....#|.###.|....#|....#|####.',
'4': '...#.|..##.|.#.#.|#..#.|#####|...#.|...#.',
'5': '#####|#....|####.|....#|....#|#...#|.###.',
'6': '.###.|#....|#....|####.|#...#|#...#|.###.',
'7': '#####|....#|...#.|..#..|..#..|..#..|..#..',
'8': '.###.|#...#|#...#|.###.|#...#|#...#|.###.',
'9': '.###.|#...#|#...#|.####|....#|....#|.###.',
'.': '.|.|.|.|.|.|#',
',': '..|..|..|..|..|.#|.#|#.',
':': '.|.|.|#|.|.|#',
';': '..|..|..|.#|..|..|.#|#.',
'!': '#|#|#|#|#|.|#',
'?': '.###.|#...#|....#|..##.|..#..|.....|..#..',
'¡': '.|.|#|.|#|#|#|#|#',
'¿': '.....|.....|..#..|.....|..#..|.##..|#....|#...#|.###.',
'-': '...|...|...|###|...|...|...',
'+': '...|...|.#.|###|.#.|...|...',
'=': '...|...|###|...|###|...|...',
'/': '..#|..#|.#.|.#.|.#.|#..|#..',
'(': '.#|#.|#.|#.|#.|#.|.#',
')': '#.|.#|.#|.#|.#|.#|#.',
'"': '#.#|#.#|...|...|...|...|...',
"'": '#|#|.|.|.|.|.',
'%': '##..#|##.#.|...#.|..#..|.#...|.#.##|#..##',
'*': '...|#.#|.#.|#.#|...|...|...',
'<': '...|..#|.#.|#..|.#.|..#|...',
'>': '...|#..|.#.|..#|.#.|#..|...',
'_': '....|....|....|....|....|....|####',
'~': '....|....|.#.#|#.#.|....|....|....',
'«': '.....|.....|..#.#|.#.#.|#.#..|.#.#.|..#.#',
'»': '.....|.....|#.#..|.#.#.|..#.#|.#.#.|#.#..',
'·': '.|.|.|#|.|.|.',
'°': '.#.|#.#|.#.|...|...|...|...',
'#': '.#.#.|#####|.#.#.|.#.#.|.#.#.|#####|.#.#.',
'&': '.##..|#..#.|.##..|.#...|#.#.#|#..#.|.##.#',
'[': '##|#.|#.|#.|#.|#.|##',
']': '##|.#|.#|.#|.#|.#|##',
'▶': '#...|##..|###.|####|###.|##..|#...',
'◀': '...#|..##|.###|####|.###|..##|...#',
'▼': '.....|.....|#####|.###.|..#..|.....|.....',
'▲': '.....|.....|..#..|.###.|#####|.....|.....',
'✓': '.....|....#|...##|#..#.|##.#.|.##..|..#..',
'✖': '.....|#...#|.#.#.|..#..|.#.#.|#...#|.....',
'♥': '.....|.#.#.|#####|#####|.###.|..#..|.....',
'★': '..#..|..#..|#####|.###.|.#.#.|#...#|.....',
}

ACUTE_CAP = ['..#', '.#.']
ACUTE_LOW = ['.#', '#.']


def with_accent(base, acc, low=True):
    rows = U[base].split('|')
    w = len(rows[0])
    off = (w - len(acc[0]) + 1) // 2
    acc_rows = [('.' * off + r).ljust(w, '.') for r in acc]
    return '|'.join(acc_rows + rows[2:])


ACC = {}
for b, a in zip('aeiou', 'áéíóú'):
    ACC[a] = with_accent(b, ACUTE_LOW, True)
ACC['ü'] = '|'.join(['#..#', '....'] + U['u'].split('|')[2:])
ACC['ñ'] = '|'.join(['.#.#', '#.#.'] + U['n'].split('|')[2:])
ACC['í'] = '.#|#.|.#|.#|.#|.#|.#'
CAP_ACC = {}
for b, a in zip('AEIOU', 'ÁÉÍÓÚ'):
    CAP_ACC[a] = (b, ['..#' if len(U[b].split('|')[0]) > 3 else '.#', '.#.' if len(U[b].split('|')[0]) > 3 else '#.'])
CAP_ACC['Ñ'] = ('N', ['.#.#', '#.#.'])
CAP_ACC['Ü'] = ('U', ['#...#', '.....'])

ROWS = 11      # 0-1 tildes de mayúscula, 2-8 cuerpo, 9-10 descendentes
BASE = 9       # línea base: filas 0-8 por encima
SPACE = 3


def glyph_bitmap(ch):
    """Devuelve (ancho, lista de (x, y) encendidos) en la celda de 11 filas."""
    if ch == ' ':
        return SPACE, []
    pts = []
    if ch in CAP_ACC:
        b, acc = CAP_ACC[ch]
        rows = U[b].split('|')
        w = len(rows[0])
        for j, r in enumerate(acc):
            off = (w - len(r)) // 2
            for i, c in enumerate(r):
                if c == '#':
                    pts.append((off + i, j))
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == '#':
                    pts.append((i, 2 + j))
        return w, pts
    src = ACC.get(ch, U.get(ch))
    if src is None:
        return None
    rows = src.split('|')
    w = max(len(r) for r in rows)
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c == '#':
                pts.append((i, 2 + j))
    return w, pts


CHARS = sorted(set(list(U.keys()) + list(ACC.keys()) + list(CAP_ACC.keys()) + [' ']), key=ord)


def build(out_prefix):
    glyphs = {}
    for ch in CHARS:
        g = glyph_bitmap(ch)
        if g:
            glyphs[ch] = g
    # Atlas BMFont
    cols = 16
    cw, chh = 8, ROWS
    rows_n = (len(glyphs) + cols - 1) // cols
    atlas = Image.new('RGBA', (cols * cw, rows_n * chh), (0, 0, 0, 0))
    lines = []
    for k, (ch, (w, pts)) in enumerate(glyphs.items()):
        x0, y0 = (k % cols) * cw, (k // cols) * chh
        for (x, y) in pts:
            atlas.putpixel((x0 + x, y0 + y), (255, 255, 255, 255))
        lines.append(f'char id={ord(ch)} x={x0} y={y0} width={max(w,1)} height={chh} '
                     f'xoffset=0 yoffset=0 xadvance={w + 1} page=0 chnl=15')
    atlas.save(out_prefix + '.png')
    name = out_prefix.split('/')[-1]
    with open(out_prefix + '.fnt', 'w') as f:
        f.write(f'info face="Brote" size={ROWS} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0 outline=0\n')
        f.write(f'common lineHeight=13 base={BASE} scaleW={atlas.width} scaleH={atlas.height} pages=1 packed=0\n')
        f.write(f'page id=0 file="{name}.png"\nchars count={len(lines)}\n')
        f.write('\n'.join(lines) + '\n')
    return glyphs


def build_ttf(glyphs, out_prefix):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from collections import defaultdict
    Uu = 100

    def outline_pts(pixels):
        edges = defaultdict(int)
        for (px_, py) in pixels:
            x0, x1 = px_ * Uu, (px_ + 1) * Uu
            y1, y0 = (BASE - py) * Uu, (BASE - py - 1) * Uu
            for e in [((x0, y1), (x1, y1)), ((x1, y1), (x1, y0)), ((x1, y0), (x0, y0)), ((x0, y0), (x0, y1))]:
                rev = (e[1], e[0])
                if edges.get(rev):
                    edges[rev] -= 1
                else:
                    edges[e] += 1
        nxt = defaultdict(list)
        for e, n in edges.items():
            for _ in range(n):
                nxt[e[0]].append(e[1])
        contours = []
        while any(nxt.values()):
            start = next(k for k, v in nxt.items() if v)
            cur, ptsl = start, []
            while True:
                ptsl.append(cur)
                cur = nxt[cur].pop()
                if cur == start:
                    break
            clean = []
            L = len(ptsl)
            for i in range(L):
                a, b, c = ptsl[i - 1], ptsl[i], ptsl[(i + 1) % L]
                if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
                    clean.append(b)
            contours.append(clean)
        return contours

    order = ['.notdef']
    cmap, gl, met = {}, {}, {}
    gl['.notdef'] = TTGlyphPen(None).glyph(); met['.notdef'] = (400, 0)
    for ch, (w, pts) in glyphs.items():
        name = 'space' if ch == ' ' else f'uni{ord(ch):04X}'
        pen = TTGlyphPen(None)
        for c in outline_pts(pts):
            pen.moveTo(c[0])
            for p in c[1:]:
                pen.lineTo(p)
            pen.closePath()
        gl[name] = pen.glyph()
        met[name] = ((w + 1) * Uu, min([p[0] for p in pts]) * Uu if pts else 0)
        order.append(name); cmap[ord(ch)] = name
    fb = FontBuilder(ROWS * Uu, isTTF=True)
    fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap); fb.setupGlyf(gl)
    fb.setupHorizontalMetrics(met)
    fb.setupHorizontalHeader(ascent=BASE * Uu, descent=-(ROWS - BASE) * Uu, lineGap=2 * Uu)
    fb.setupNameTable({'familyName': 'Brote', 'styleName': 'Regular', 'version': 'Version 1.000', 'psName': 'Brote-Regular'})
    fb.setupOS2(sTypoAscender=BASE * Uu, sTypoDescender=-(ROWS - BASE) * Uu, sTypoLineGap=2 * Uu,
                usWinAscent=BASE * Uu, usWinDescent=(ROWS - BASE) * Uu, fsType=0)
    fb.setupPost()
    fb.save(out_prefix + '.ttf')
    fb.font.flavor = 'woff2'
    fb.font.save(out_prefix + '.woff2')


def render(text, color=(40, 36, 56, 255), shadow=None):
    """Render de una línea con la propia fuente (para composiciones en PIL)."""
    import numpy as np
    gl = {}
    w = 0
    for ch in text:
        g = glyph_bitmap(ch) or glyph_bitmap('?')
        gl[ch] = g
        w += g[0] + 1
    img = np.zeros((ROWS + 1, w + 1, 4), np.uint8)
    x = 0
    for ch in text:
        gw, pts = gl[ch]
        for (px_, py) in pts:
            if shadow is not None:
                img[py + 1, x + px_ + 1] = shadow
        x += gw + 1
    x = 0
    for ch in text:
        gw, pts = gl[ch]
        for (px_, py) in pts:
            img[py, x + px_] = color
        x += gw + 1
    return img


def width(text):
    return sum((glyph_bitmap(c) or glyph_bitmap('?'))[0] + 1 for c in text) - 1


if __name__ == '__main__':
    g = build(sys.argv[1])
    build_ttf(g, sys.argv[1])
    print(len(g), 'glyphs')
