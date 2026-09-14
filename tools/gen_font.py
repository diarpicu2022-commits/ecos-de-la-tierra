"""Genera la fuente de mapa de bits del juego: atlas PNG + descriptor BMFont.

Contrato de diseño 2026-09-13, cláusula «Tipografía y escala»:
fuente propia de 6x8 px con cobertura de español completa.

La celda real es de 6x9 px: dos filas superiores reservadas al acento y siete
filas para el glifo de 5x7. Los glifos se dibujan en blanco sobre transparente,
de modo que Godot pueda teñirlos con cualquier token de la paleta mediante
`modulate` sin generar una textura por color.

Uso:
    python tools/gen_font.py
"""

from pathlib import Path

from PIL import Image

# --- Geometría de la celda ---------------------------------------------------

GLYPH_W = 5                  # Ancho de la caja de dibujo.
BODY_ROWS = 7                # Filas de la caja principal: de la altura de
                             # mayúscula hasta la línea base.
DESCENDER_ROWS = 2           # Filas bajo la línea base, para g j p q y.
GLYPH_H = BODY_ROWS + DESCENDER_ROWS
ACCENT_ROWS = 2              # Filas reservadas arriba para tildes y diéresis.
CELL_W = 6                   # 5 de glifo + 1 de separación.
CELL_H = ACCENT_ROWS + GLYPH_H
BASELINE = ACCENT_ROWS + BODY_ROWS
COLUMNS = 16                 # Columnas del atlas.

# --- Acentos, que se componen sobre el glifo base ----------------------------

ACCENT_ACUTE = ["...#.", "..#.."]
ACCENT_TILDE = ["..##.", ".##.."]
ACCENT_DIAERESIS = [".#.#.", "....."]

# --- Glifos base -------------------------------------------------------------
# Cada glifo son 7 cadenas de 5 caracteres. '#' es píxel encendido.

GLYPHS = {
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],

    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],

    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "c": [".....", ".....", ".###.", "#....", "#....", "#...#", ".###."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "f": ["..##.", ".#...", "####.", ".#...", ".#...", ".#...", ".#..."],
    "g": [".....", ".####", "#...#", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "j": ["...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#...#", "#...#"],
    "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "p": [".....", "####.", "#...#", "#...#", "####.", "#....", "#...."],
    "q": [".....", ".####", "#...#", "#...#", ".####", "....#", "....#"],
    "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "y": [".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],

    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#...#", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "#...#", ".###."],

    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "[": ["..##.", "..#..", "..#..", "..#..", "..#..", "..#..", "..##."],
    "]": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".##.."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    # La tilde de onda marca el daño que el monstruo resiste («~2»). Va a la
    # altura del centro de las cifras, no a la de las minúsculas.
    "~": [".....", ".....", ".....", ".##..", "#..##", ".....", "....."],

    # Signos propios del español.
    "¿": ["..#..", ".....", "..#..", ".#...", "#....", "#...#", ".###."],
    "¡": ["..#..", ".....", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "«": [".....", "..#.#", ".#.#.", "#.#..", ".#.#.", "..#.#", "....."],
    "»": [".....", "#.#..", ".#.#.", "..#.#", ".#.#.", "#.#..", "....."],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    "°": [".##..", "#..#.", ".##..", ".....", ".....", ".....", "....."],

    # Glifos de interfaz: cursor, orden de turnos y sello de purificación.
    "▶": ["#....", "##...", "###..", "####.", "###..", "##...", "#...."],
    "◀": ["....#", "...##", "..###", ".####", "..###", "...##", "....#"],
    "▲": ["..#..", "..#..", ".###.", ".###.", "#####", "#####", "....."],
    "▼": [".....", "#####", "#####", ".###.", ".###.", "..#..", "..#.."],
    "✖": [".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."],
    "✓": [".....", "....#", "...#.", "#..#.", ".##..", ".#...", "....."],
    "♥": [".....", ".#.#.", "#####", "#####", ".###.", "..#..", "....."],
}

# Letras acentuadas: glifo base + acento, compuestos en tiempo de generación.
ACCENTED = {
    "á": ("a", ACCENT_ACUTE), "é": ("e", ACCENT_ACUTE),
    "í": ("i", ACCENT_ACUTE), "ó": ("o", ACCENT_ACUTE),
    "ú": ("u", ACCENT_ACUTE), "ü": ("u", ACCENT_DIAERESIS),
    "ñ": ("n", ACCENT_TILDE),
    "Á": ("A", ACCENT_ACUTE), "É": ("E", ACCENT_ACUTE),
    "Í": ("I", ACCENT_ACUTE), "Ó": ("O", ACCENT_ACUTE),
    "Ú": ("U", ACCENT_ACUTE), "Ü": ("U", ACCENT_DIAERESIS),
    "Ñ": ("N", ACCENT_TILDE),
}

# Letras con rasgo descendente. Se definen con las nueve filas completas: el
# cuenco ocupa la altura de x (filas 2-6) y la cola baja de la línea base
# (filas 7-8). Sin esto la «g» se lee como un «9» y la «p» como una «P».
DESCENDERS = {
    "g": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####",
          "....#", "####."],
    "j": ["...#.", ".....", "...#.", "...#.", "...#.", "...#.", "...#.",
          "#..#.", ".##.."],
    "p": [".....", ".....", "####.", "#...#", "#...#", "#...#", "####.",
          "#....", "#...."],
    "q": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####",
          "....#", "....#"],
    "y": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####",
          "....#", "####."],
}

# La «i» pierde su punto cuando lleva tilde, como en tipografía real.
DOTLESS = {"i": [".....", ".....", ".##..", "..#..", "..#..", "..#..", ".###."]}


def _pad(rows: list[str]) -> list[str]:
    """Completa un glifo de siete filas hasta la altura total de la caja."""
    return rows + [".....", ] * (GLYPH_H - len(rows)) if len(rows) < GLYPH_H else rows


def build_charset() -> list[tuple[str, list[str], list[str] | None]]:
    """Devuelve (carácter, glifo base, acento) para cada signo de la fuente."""
    entries: list[tuple[str, list[str], list[str] | None]] = []
    for char, rows in GLYPHS.items():
        entries.append((char, _pad(DESCENDERS.get(char, rows)), None))
    for char, (base, accent) in ACCENTED.items():
        rows = DOTLESS.get(base) or DESCENDERS.get(base) or GLYPHS[base]
        entries.append((char, _pad(rows), accent))
    return entries


def render(entries: list[tuple[str, list[str], list[str] | None]]) -> tuple[Image.Image, list[str]]:
    """Dibuja el atlas y devuelve también las líneas `char` del descriptor."""
    rows_needed = (len(entries) + COLUMNS - 1) // COLUMNS
    width, height = COLUMNS * CELL_W, rows_needed * CELL_H
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = atlas.load()

    char_lines: list[str] = []
    for index, (char, glyph, accent) in enumerate(entries):
        cell_x = (index % COLUMNS) * CELL_W
        cell_y = (index // COLUMNS) * CELL_H

        if accent is not None:
            for y, line in enumerate(accent):
                for x, dot in enumerate(line):
                    if dot == "#":
                        pixels[cell_x + x, cell_y + y] = (255, 255, 255, 255)

        for y, line in enumerate(glyph):
            for x, dot in enumerate(line):
                if dot == "#":
                    pixels[cell_x + x, cell_y + ACCENT_ROWS + y] = (255, 255, 255, 255)

        char_lines.append(
            "char id=%d   x=%d    y=%d    width=%d    height=%d    "
            "xoffset=0     yoffset=0     xadvance=%d    page=0    chnl=15"
            % (ord(char), cell_x, cell_y, CELL_W, CELL_H, CELL_W)
        )
    return atlas, char_lines


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "assets" / "fonts"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = build_charset()
    atlas, char_lines = render(entries)

    png_path = out_dir / "ceniza.png"
    atlas.save(png_path)

    # Descriptor BMFont en texto plano, que Godot 4 carga como FontFile.
    fnt = [
        'info face="Ceniza" size=%d bold=0 italic=0 charset="" unicode=1 '
        "stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0 outline=0" % CELL_H,
        "common lineHeight=%d base=%d scaleW=%d scaleH=%d pages=1 packed=0 "
        "alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0"
        % (CELL_H + 1, BASELINE, atlas.width, atlas.height),
        'page id=0 file="ceniza.png"',
        "chars count=%d" % len(char_lines),
        *char_lines,
    ]
    (out_dir / "ceniza.fnt").write_text("\n".join(fnt) + "\n", encoding="utf-8")

    print("Atlas:      %s  (%dx%d px)" % (png_path.name, *atlas.size))
    print("Celda:      %dx%d px · línea base en %d · interlineado %d"
          % (CELL_W, CELL_H, BASELINE, CELL_H + 1))
    print("Glifos:     %d" % len(entries))


if __name__ == "__main__":
    main()
