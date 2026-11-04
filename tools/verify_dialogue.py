"""Los textos de diálogo caben y tienen quién los diga (contrato «Columna» §4).

    python tools/verify_dialogue.py

Sobre todo `data/dialogue/*.json` (menos `voices.json` y `talk.json`):

- cada caja cabe en DIALOGUE_LINES líneas de DIALOGUE_CHARS caracteres,
  partida por palabras **con el mismo algoritmo que `DialogueBox.wrap_text`**;
- cada línea tiene texto, una voz que existe en `voices.json`, una expresión
  de esa voz y su retrato en `assets/sprites/portraits/`;
- cada entrada de `talk.json` apunta a una conversación que existe.

Los topes se leen de `src/ui/design_tokens.gd`: no se copian aquí.
Sale con código 1 si algo falla.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dialogue"
PORTRAITS = ROOT / "assets" / "sprites" / "portraits"


def token(name: str) -> int:
    text = (ROOT / "src" / "ui" / "design_tokens.gd").read_text(encoding="utf8")
    return int(re.search(rf"const {name} := (\d+)", text).group(1))


def wrap(text: str, chars: int) -> list[str]:
    """Igual que DialogueBox.wrap_text: palabras enteras, ≤ chars por línea."""
    out, current = [], ""
    for word in text.split():
        candidate = word if not current else current + " " + word
        if len(candidate) <= chars:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def main() -> int:
    chars, lines_max = token("DIALOGUE_CHARS"), token("DIALOGUE_LINES")
    voices = json.loads((DATA / "voices.json").read_text(encoding="utf8"))["voices"]
    fails = 0
    boxes = 0
    longest = (0, "")
    for path in sorted(DATA.glob("*.json")):
        if path.name in ("voices.json", "talk.json"):
            continue
        conv = json.loads(path.read_text(encoding="utf8"))
        for i, line in enumerate(conv["lines"]):
            where = f"{path.name} línea {i + 1}"
            boxes += 1
            who, mood, text = line.get("who"), line.get("mood"), line.get("text", "")
            problems = []
            if who not in voices:
                problems.append(f"voz desconocida «{who}»")
            elif mood not in voices[who]["moods"]:
                problems.append(f"expresión «{mood}» que {who} no tiene")
            elif not (PORTRAITS / f"{who}_{mood}.png").exists():
                problems.append(f"falta el retrato {who}_{mood}.png")
            if not text.strip():
                problems.append("texto vacío")
            wrapped = wrap(text, chars)
            if len(wrapped) > lines_max or any(len(l) > chars for l in wrapped):
                problems.append(f"no cabe: {len(wrapped)} líneas ({' | '.join(wrapped)})")
            if len(text) > longest[0]:
                longest = (len(text), where)
            if problems:
                fails += 1
                print(f"  FALLA {where}: {'; '.join(problems)}")
    talk = json.loads((DATA / "talk.json").read_text(encoding="utf8"))["talk"]
    for key, conv_id in talk.items():
        if not (DATA / f"{conv_id}.json").exists():
            fails += 1
            print(f"  FALLA talk.json «{key}» apunta a {conv_id}.json, que no existe")
    print(f"  {boxes} cajas en {len(list(DATA.glob('*.json'))) - 2} conversaciones; "
          f"la más larga, {longest[0]} caracteres ({longest[1]}); tope {lines_max} × {chars}")
    print("Todo en verde." if fails == 0 else f"{fails} fallos.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
