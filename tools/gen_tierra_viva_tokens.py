"""Genera las rampas `TV_*` del contrato «Piel nueva» (enmienda 13, 2026-10-30).

Una sola tabla, aquí, escribe los dos lados de la paleta: el bloque marcado de
`src/ui/design_tokens.gd` y el de `tools/pixel.py`. Así no puede haber deriva
entre ambos (`python tools/verify_palette.py tokens` lo comprueba).

    python tools/gen_tierra_viva_tokens.py

Cada rampa va de la sombra (índice 0) a la luz. Los grupos `PURIFIED_ONLY` y
`SICK_ONLY` fijan el significado: lo primero solo existe en celdas
purificadas y lo segundo solo en celdas enfermas
(`verify_palette.py tv-state` lo mide sobre un render).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS_GD = ROOT / "src" / "ui" / "design_tokens.gd"
PIXEL_PY = ROOT / "tools" / "pixel.py"

BEGIN = "TIERRA VIVA: BEGIN"
END = "TIERRA VIVA: END"

# (nombre, rampa de sombra a luz, comentario)
RAMPS: list[tuple[str, list[str], str]] = [
    ("ink", ["#14101c", "#231c2e", "#372b42"], "Tinta: contorno del decorado más oscuro"),
    ("stone", ["#2a2434", "#40384d", "#5c5268", "#7d7387", "#a198a8", "#c9c1cc", "#ece6ec"], "Piedra: cotas, muros, rocas"),
    ("grass", ["#123a2e", "#1a5234", "#256e3a", "#358c3e", "#4fa645", "#7cc456", "#b5e073"], "Hierba viva"),
    ("leaf", ["#0f2b26", "#174232", "#215c38", "#2f7a3c", "#48983f", "#74b84a", "#aad65e"], "Copa y arbusto vivos"),
    ("dirt", ["#3b2226", "#5a332c", "#7d4b35", "#a06741", "#c48a52", "#e0b070", "#f4d699"], "Tierra y camino"),
    ("sand", ["#8a6a4a", "#b08d5e", "#d1b077", "#e8cf98", "#f7ebc4"], "Arena limpia"),
    ("water", ["#16244f", "#1b3c7a", "#2360a8", "#3489cc", "#56b3e6", "#92d9f4", "#dff7ff"], "Agua viva"),
    ("wood", ["#2e1a1e", "#4a2a26", "#6b3f2e", "#8f5a3a", "#b27a4c", "#d1a068"], "Madera"),
    ("roof_red", ["#3a1426", "#5e1f30", "#8c2c3a", "#b8443f", "#dc6a4c", "#f29c6e"], "Teja roja"),
    ("roof_blue", ["#1a1d40", "#253366", "#2f4f94", "#3f75be", "#62a2dc", "#9ccdf0"], "Teja azul"),
    ("wall", ["#6b5a66", "#8f7d82", "#b5a598", "#d8cbb4", "#f2e8d2"], "Muro encalado"),
    ("flower", ["#b0304f", "#e8566b", "#ff8fa3", "#ffd34e", "#fff3b0", "#8a6bd9", "#c3a8ff", "#ffffff"], "Flores (tonos sueltos, no rampa)"),
    ("dry_grass", ["#2a1f2a", "#3d2e2e", "#56432f", "#735c37", "#94783f", "#b39a52", "#cfbd70"], "Hierba seca"),
    ("dead_leaf", ["#1e1622", "#2f2229", "#46332e", "#61483a", "#7f6146", "#9c7d55"], "Hoja muerta"),
    ("ash", ["#221d29", "#342d3b", "#4a4252", "#645c6b", "#827a88", "#a39ca6", "#c7c1c6"], "Ceniza del mundo y arena enferma"),
    ("oil", ["#0b0812", "#15111f", "#221b30", "#302744", "#433757"], "Crudo"),
    ("sheen", ["#5a3f8c", "#3f7f86", "#a3963f", "#c0577a"], "Irisado del crudo"),
    ("sludge", ["#2f3a12", "#4f6418", "#77921f", "#a4c42c", "#d2ef5a"], "Lodo tóxico"),
    ("smog", ["#4b3f4a", "#6e5d62", "#93807a", "#b8a594"], "Humo y neblina"),
    ("rust", ["#3a1a16", "#5e2a1e", "#8a4126", "#b5602f", "#d68a45"], "Óxido y metal"),
    ("plastic", ["#2a4f6e", "#3f7fa8", "#7cc0e0", "#c9ecf7", "#e25a6a", "#f2c94c", "#ffffff"], "Plástico (tonos sueltos)"),
    ("fire", ["#3d0f14", "#7a1a16", "#c13a1c", "#ec6a24", "#ffa83a", "#ffe07a", "#fffbe0"], "Fuego de antorcha"),
    ("ice", ["#1d2c52", "#2c4c80", "#4a7fb4", "#7ab6df", "#b0e0f4", "#e4f8ff"], "Hielo"),
    ("gold", ["#3a2412", "#6b4316", "#a6701c", "#d9a52a", "#f5d24a", "#fff1a0"], "Oro y paja"),
    ("eco", ["#0f3b3f", "#14706a", "#20a88f", "#4fd8b0", "#9cf5d4", "#e2fff3"], "Turquesa de detalle"),
    ("turbid", ["#1f2a2c", "#2c3a3a", "#3b4a48", "#4b5a55", "#5f6d66", "#7d877c", "#a3a898"], "Agua turbia"),
    ("oil_water", ["#07050c", "#110c1a", "#1b1428", "#261d36", "#3a2c4c", "#5a3f8c", "#3f7f86"], "Ciénaga de crudo"),
    ("plastic_water", ["#1d2a33", "#2a3b45", "#3a4d57", "#4b5f68", "#61757b", "#839393", "#b5bfbb"], "Mar con plástico"),
    ("sludge_grass", ["#1f1d14", "#2b2a19", "#3a3820", "#4b4826", "#5d592d", "#77713a", "#938b4c"], "Pasto manchado de crudo"),
    ("grey_sand", ["#7d7466", "#988e7d", "#b0a690", "#c4baa2", "#d6cdb6"], "Arena gris de la costa enferma"),
    ("paramo", ["#1c2f2a", "#2a4434", "#3d5c3a", "#587a42", "#7a954c", "#a3b45e", "#cdd17c"], "Pajonal de páramo vivo"),
    ("snow", ["#7d8fb8", "#a9bbd9", "#cfdcef", "#e9f1fa", "#ffffff"], "Nieve del glaciar"),
    ("paramo_dry", ["#2a2226", "#3d302c", "#56432f", "#6e5838", "#8a7044", "#a58a55", "#bea56a"], "Páramo seco"),
    ("scree", ["#3e3943", "#57505a", "#726a72", "#8f878c", "#aca4a6"], "Pedregal del glaciar derretido"),
    ("sick_soil", ["#2a2226", "#3d322f", "#54463d", "#6f5f50", "#8c7a64", "#a8957a", "#c2b092"], "Tierra enferma"),
    ("frailejon", ["#4d6a4a", "#7b9670", "#a7bc9a", "#cfdcc4", "#eef4e6"], "Roseta del frailejón"),
    ("puya", ["#2d4a3c", "#466b4c", "#6a8f62", "#94b183", "#c3d6ae"], "Puya"),
    ("straw", ["#56502e", "#7d7238", "#a6984a", "#cdbd66", "#e6d98a"], "Paja de páramo"),
    ("curse_fire", ["#2a1d3a", "#5a2d6b", "#8f4fb0", "#c98ae0", "#f2d1ff"], "Fuego maldito de la Cripta"),
]

## Solo en celdas purificadas: el color que vuelve.
PURIFIED_ONLY = ["grass", "leaf", "flower", "water", "eco", "paramo", "snow", "frailejon", "puya"]
## Solo en celdas enfermas: la causa y su rastro.
SICK_ONLY = ["dry_grass", "dead_leaf", "oil", "sheen", "sludge", "smog", "plastic", "turbid",
             "oil_water", "plastic_water", "sludge_grass", "grey_sand", "paramo_dry", "scree",
             "sick_soil", "curse_fire"]


def token_names() -> list[tuple[str, str]]:
    out = []
    for name, ramp, _ in RAMPS:
        for i, h in enumerate(ramp):
            out.append((f"tv_{name}_{i}", h.lower()))
    return out


def gd_block() -> str:
    lines = [f"# --- {BEGIN} (enmienda 13, contrato «Piel nueva», 2026-10-30) ---",
             "## Generado por tools/gen_tierra_viva_tokens.py: no se edita a mano.",
             "## Rampas del mundo de Tierra Viva, de la sombra (0) a la luz. El techo",
             "## de saturación no se aplica a estas rampas: su significado lo fijan",
             "## TV_PURIFIED_ONLY y TV_SICK_ONLY, medidos con verify_palette.py tv-state."]
    for name, ramp, note in RAMPS:
        lines.append(f"## {note}.")
        for i, h in enumerate(ramp):
            lines.append(f'const TV_{name.upper()}_{i} := Color("{h.lower()}")')
    lines.append("const TV_PURIFIED_ONLY := [" + ", ".join(f'"{n}"' for n in PURIFIED_ONLY) + "]")
    lines.append("const TV_SICK_ONLY := [" + ", ".join(f'"{n}"' for n in SICK_ONLY) + "]")
    lines.append(f"# --- {END} ---")
    return "\n".join(lines)


def py_block() -> str:
    lines = [f"    # --- {BEGIN} (enmienda 13). Generado por gen_tierra_viva_tokens.py ---"]
    for tok, h in token_names():
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        lines.append(f'    "{tok}": (0x{r:02X}, 0x{g:02X}, 0x{b:02X}, 255),')
    lines.append(f"    # --- {END} ---")
    return "\n".join(lines)


def replace_block(text: str, block: str, anchor: str) -> str:
    pat = re.compile(r"[ \t]*# --- " + re.escape(BEGIN) + r".*?" + re.escape(END) + r" ---\n?", re.S)
    if pat.search(text):
        return pat.sub(block + "\n", text)
    i = text.index(anchor)
    return text[:i] + block + "\n" + text[i:]


def main() -> None:
    gd = TOKENS_GD.read_text(encoding="utf-8")
    gd = replace_block(gd, gd_block() + "\n", "# --- Lenguaje del entorno")
    TOKENS_GD.write_text(gd, encoding="utf-8")
    py = PIXEL_PY.read_text(encoding="utf-8")
    py = replace_block(py, py_block(), '    "transparent": (0, 0, 0, 0),')
    groups = ("\n## Enmienda 13: significado de las rampas TV (ver gen_tierra_viva_tokens.py).\n"
              f"TV_PURIFIED_ONLY = {PURIFIED_ONLY!r}\nTV_SICK_ONLY = {SICK_ONLY!r}\n")
    if "TV_PURIFIED_ONLY" not in py:
        py = py.replace("\n## Rampa de calor de la llama", groups + "\n## Rampa de calor de la llama", 1)
    PIXEL_PY.write_text(py, encoding="utf-8")
    print(f"{len(token_names())} tokens TV escritos en design_tokens.gd y pixel.py")


if __name__ == "__main__":
    main()
