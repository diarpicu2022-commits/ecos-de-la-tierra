"""Genera el sprite de Ilan en el mundo (contrato «Umbral», fase 5, paso 5).

Hoja de 2 columnas por 4 filas de 16x24 px, con los pies en la fila 23:

    columna 0   de pie (y primera pose del paso)
    columna 1   segunda pose del paso
    filas       abajo, arriba, izquierda, derecha

Decisiones (anexo de la parte 2, paso 5):

- **Contorno oscuro, `ash_950`.** El contorno `ash_050` es la firma de «esto
  responde» (catálogo del paso 2a) y la llevan las personas con las que se
  habla. Ilan no responde: se le encuentra por ser lo único que obedece al
  teclado, por su silueta y por su túnica, la más clara del centro de la
  pantalla.
- **Rampa de ceniza, sin color propio**, igual que su sprite de batalla: túnica
  clara (`ash_050`/`ash_200`), pelo oscuro y, de espaldas, el Fragmento del
  Vínculo entre los omóplatos, con borde oscuro como en batalla.
- **Dos poses de paso.** No es una animación por tiempo: `PlayerBody` cambia
  de pose cada 8 px recorridos, así que se para justo cuando el cuerpo se para
  y no añade ninguna duración.

Cada sprite se dibuja como una cuadrícula de letras (una por píxel) para que
se pueda leer y revisar en un diff. Frente y espalda se dibujan a media
anchura y se reflejan; el perfil izquierdo es el derecho reflejado.

Uso:
    python tools/gen_world_sprites.py
"""

from __future__ import annotations

from pathlib import Path

from pixel import Canvas, color

W, H = 16, 24
OUT = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "world" / "ilan.png"

INK = {
    ".": None,
    "o": "ash_950",  # contorno
    "h": "ash_700",  # pelo
    "H": "ash_600",  # brillo del pelo
    "s": "ash_200",  # piel
    "k": "ash_400",  # sombra de la piel
    "e": "ash_900",  # ojos
    "T": "ash_050",  # túnica, luz
    "t": "ash_200",  # túnica
    "d": "ash_400",  # túnica, sombra y cinturón
    "l": "ash_600",  # piernas
    "L": "ash_700",  # piernas, sombra
    "f": "ash_050",  # Fragmento, centro
    "F": "ash_800",  # Fragmento, borde
}

# --- Cabeza y cuerpo, a media anchura (columnas 0-7; se reflejan) -----------

HEAD_FRONT = [
    "......oo",
    "....oohh",
    "...ohhhh",
    "..ohhHHh",
    "..ohhhhh",
    "..ohssss",
    "..osesss",
    "..osssss",
    "...ossks",
    "....ooss",
]
HEAD_BACK = [
    "......oo",
    "....oohh",
    "...ohhhh",
    "..ohhHHh",
    "..ohhhhh",
    "..ohhhhh",
    "..ohhhhh",
    "..ohhhhh",
    "...ohhhh",
    "....ooss",
]
BODY_FRONT = [
    "...ootTT",
    "..otttTT",
    ".ostttTT",
    ".odttTTT",
    ".odttTTT",
    ".osdttTT",
    "..oddddd",
    "..odtttT",
    "..oddddd",
]
BODY_BACK = [
    "...ootTT",
    "..otttTT",
    ".ostttTF",
    ".odttTFf",
    ".odtttTF",
    ".osdttTT",
    "..oddddd",
    "..odtttT",
    "..oddddd",
]
LEGS_STAND = [
    "....olLo",
    "....olLo",
    "....olLo",
    "...ooLLo",
    "...oooo.",
]
LEGS_STEP = [
    "...olLo.",
    "...olLo.",
    "..olLo..",
    "..oLLo..",
    "..oooo..",
]

# --- Perfil derecho, a anchura completa --------------------------------------

SIDE_TOP = [
    ".....oooo.......",
    "...oohhhhoo.....",
    "..ohhhhhhhho....",
    "..ohhHHhhhhho...",
    "..ohhhhhhhhho...",
    "..ohhhhhsssso...",
    "..ohhhhssseso...",
    "..ohhhsssssso...",
    "...ohhssskso....",
    "....oossssoo....",
    "....ootTTToo....",
    "...otttTTTto....",
    "...ottdTTTTo....",
    "...ottdTTTTo....",
    "...ottddTTTo....",
    "...ottsdTTTo....",
    "...oddddddo.....",
    "...otttttto.....",
    "...oddddddo.....",
]
SIDE_STAND = [
    "....olllo.......",
    "....olLlo.......",
    "....olLlo.......",
    "....oLLLoo......",
    "....oooooo......",
]
SIDE_STEP = [
    "...ollllo.......",
    "...olLoLlo......",
    "..olLo.oLlo.....",
    "..oLLo.oLLoo....",
    "..oooo.ooooo....",
]


def mirror(half: list[str]) -> list[str]:
    return [row + row[::-1] for row in half]


def flip(rows: list[str]) -> list[str]:
    return [row[::-1] for row in rows]


def frames() -> dict[tuple[int, int], list[str]]:
    front = mirror(HEAD_FRONT + BODY_FRONT)
    back = mirror(HEAD_BACK + BODY_BACK)
    stand, step = mirror(LEGS_STAND), mirror(LEGS_STEP)
    right_stand, right_step = SIDE_TOP + SIDE_STAND, SIDE_TOP + SIDE_STEP
    return {
        (0, 0): front + stand, (1, 0): front + step,
        (0, 1): back + stand, (1, 1): back + step,
        (0, 2): flip(right_stand), (1, 2): flip(right_step),
        (0, 3): right_stand, (1, 3): right_step,
    }


def main() -> None:
    sheet = Canvas(W * 2, H * 4)
    for (col, row), rows in frames().items():
        assert len(rows) == H, f"pose {col},{row}: {len(rows)} filas"
        for y, line in enumerate(rows):
            assert len(line) == W, f"pose {col},{row} fila {y}: {len(line)} columnas"
            for x, ch in enumerate(line):
                if INK[ch] is not None:
                    sheet.set(col * W + x, row * H + y, color(INK[ch]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    print(f"  sprite: {OUT.relative_to(OUT.parent.parent.parent.parent)} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
