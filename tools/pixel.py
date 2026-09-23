"""Utilidades compartidas para generar el pixel art de *Ecos de la Tierra*.

La paleta es la del contrato «Ceniza y Brasa» (bloqueado el 2026-09-13). Ningún
sprite introduce un color que no salga de aquí: así el mundo entero comparte la
misma rampa de ceniza y el verde conserva un único significado.

El ruido es determinista: con la misma semilla sale exactamente el mismo sprite,
de modo que regenerar los assets no cambia el juego por sorpresa.
"""

from __future__ import annotations

import math
import random

from PIL import Image

# --- Paleta del contrato -----------------------------------------------------

PALETTE: dict[str, tuple[int, int, int, int]] = {
    # Ceniza: estructura del mundo apagado.
    "ash_950": (0x17, 0x14, 0x1C, 255),
    "ash_900": (0x22, 0x1D, 0x2A, 255),
    "ash_800": (0x2E, 0x28, 0x36, 255),
    "ash_700": (0x3A, 0x35, 0x40, 255),
    "ash_600": (0x4D, 0x46, 0x57, 255),
    "ash_400": (0x9C, 0x95, 0xA7, 255),
    "ash_200": (0xB8, 0xB0, 0xC4, 255),
    "ash_050": (0xE8, 0xE4, 0xEE, 255),
    # Brasa: el daño y la causa todavía activa.
    "ember_700": (0x7A, 0x25, 0x18, 255),  # Borde apagado de la llama.
    "ember_500": (0xE8, 0x56, 0x2E, 255),
    "ember_400": (0xF0, 0x8A, 0x3C, 255),
    "ember_300": (0xFF, 0xC1, 0x4D, 255),
    # Acento único: la purificación.
    "vital_500": (0x4A, 0xDE, 0x80, 255),
    "vital_700": (0x2B, 0x9D, 0x5A, 255),
    "vital_900": (0x1A, 0x5E, 0x38, 255),
    # Mundo: tres rampas de material, enmienda 1 del contrato «Vereda»
    # (2026-09-14). Techo de saturación 0,22: el mundo sigue apagado.
    "soil_700": (0x40, 0x37, 0x32, 255),
    "soil_500": (0x59, 0x4D, 0x46, 255),
    "soil_300": (0x73, 0x64, 0x5A, 255),
    "water_700": (0x1E, 0x24, 0x26, 255),
    "water_500": (0x36, 0x41, 0x45, 255),
    "water_300": (0x4E, 0x5E, 0x63, 255),
    "flora_700": (0x43, 0x45, 0x36, 255),
    "flora_500": (0x57, 0x59, 0x46, 255),
    "flora_300": (0x6A, 0x6E, 0x56, 255),
    "transparent": (0, 0, 0, 0),
}

## Rampa de calor de la llama, de la brasa apagada al núcleo blanco.
EMBER_RAMP = ["ember_700", "ember_500", "ember_400", "ember_300", "ash_050"]

## Rampa de carbón, del hollín a la ceniza clara.
CHAR_RAMP = ["ash_950", "ash_900", "ash_800", "ash_700", "ash_600"]

## Rampa de la vida que vuelve, para las variantes purificadas. El verde manda:
## la ceniza clara solo asoma como reflejo puntual en el borde iluminado.
VITAL_RAMP = ["vital_900", "vital_700", "vital_700", "vital_500", "ash_200"]


def color(name: str) -> tuple[int, int, int, int]:
    return PALETTE[name]


def ramp(ramp_names: list[str], t: float) -> tuple[int, int, int, int]:
    """Toma el color de una rampa según `t` en [0, 1], sin interpolar.

    Sin interpolación a propósito: el pixel art vive de tener pocos colores
    planos. Mezclarlos produciría una rampa sucia de cientos de tonos.
    """
    index = int(max(0.0, min(0.999, t)) * len(ramp_names))
    return PALETTE[ramp_names[index]]


# --- Ruido determinista ------------------------------------------------------


class ValueNoise:
    """Ruido de valor con interpolación suave, reproducible por semilla."""

    def __init__(self, seed: int, size: int = 64) -> None:
        rng = random.Random(seed)
        self._size = size
        self._grid = [[rng.random() for _ in range(size)] for _ in range(size)]

    def _at(self, ix: int, iy: int) -> float:
        return self._grid[iy % self._size][ix % self._size]

    def sample(self, x: float, y: float) -> float:
        x0, y0 = math.floor(x), math.floor(y)
        fx, fy = x - x0, y - y0
        # Suavizado de Hermite: evita las aristas del ruido bilineal puro.
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        top = self._at(x0, y0) * (1 - sx) + self._at(x0 + 1, y0) * sx
        bottom = self._at(x0, y0 + 1) * (1 - sx) + self._at(x0 + 1, y0 + 1) * sx
        return top * (1 - sy) + bottom * sy

    def fbm(self, x: float, y: float, octaves: int = 3) -> float:
        """Ruido fractal: varias octavas sumadas, para una silueta orgánica."""
        total, amplitude, frequency, norm = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.sample(x * frequency, y * frequency) * amplitude
            norm += amplitude
            amplitude *= 0.5
            frequency *= 2.0
        return total / norm


# --- Lienzo ------------------------------------------------------------------


class Canvas:
    """Lienzo de sprite con acceso por píxel y volcado a PNG."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.px = self.image.load()

    def set(self, x: int, y: int, rgba: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height and rgba[3] > 0:
            self.px[x, y] = rgba

    def get(self, x: int, y: int) -> tuple[int, int, int, int]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.px[x, y]
        return (0, 0, 0, 0)

    def filled(self, x: int, y: int) -> bool:
        return self.get(x, y)[3] > 0

    def rect(self, x: int, y: int, w: int, h: int, rgba) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, rgba)

    def outline(self, rgba: tuple[int, int, int, int]) -> None:
        """Contorno de 1 px por fuera de la silueta.

        Da al sprite un borde legible sobre cualquier fondo, que es la razón por
        la que casi todo el pixel art de RPG lo lleva.
        """
        edges: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if self.filled(x, y):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.filled(x + dx, y + dy):
                        edges.append((x, y))
                        break
        for x, y in edges:
            self.set(x, y, rgba)

    def save(self, path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path)
