"""Audio provisional de *Ecos de la Tierra*, generado por código.

    python tools/gen_audio.py

Escribe en `assets/audio/` efectos, ambiente y música en WAV mono de 16 bits.
Todo sale de síntesis con semilla fija: regenerar da los mismos bytes y no hay
muestras de terceros que licenciar (`docs/licencias-audio.md`).

Es provisional: la parte 11 (guía del equipo §4.13) todavía no tiene anexo. Sigue
lo que ya pide la guía: los buses Música, Ambiente, Efectos e Interfaz, y lo
enfermo apagado con un filtro que se abre con la ola (`src/core/game_audio.gd`).

Los bucles se escriben sobre un búfer circular (lo que sobra por el final entra
por el principio), así que no hay salto en la costura.
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "audio"
RATE = 22050
SEED = 11
PEAK = 0.8

## Pentatónica de la menor, con la que se escribe toda la música.
A2 = 110.0


def note(semitones: float, base: float = A2) -> float:
    return base * 2.0 ** (semitones / 12.0)


def times(seconds: float) -> np.ndarray:
    return np.arange(int(seconds * RATE)) / RATE


def env(t: np.ndarray, attack: float, release: float) -> np.ndarray:
    """Envolvente con subida y bajada lineales, para no dar chasquidos."""
    total = t[-1] if len(t) else 0.0
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.clip((total - t) / max(release, 1e-4), 0, 1)


def pluck(freq: float, seconds: float, bright: float = 1.0) -> np.ndarray:
    """Cuerda pulsada: armónicos que se apagan antes cuanto más agudos."""
    t = times(seconds)
    out = np.zeros_like(t)
    for h in range(1, 7):
        out += np.sin(2 * np.pi * freq * h * t) * np.exp(-t * (2.0 + h * 1.2 / bright)) / h ** 1.3
    return out * env(t, 0.002, 0.02)


def flute(freq: float, seconds: float) -> np.ndarray:
    """Flauta suave con vibrato que entra tarde."""
    t = times(seconds)
    vibrato = 0.006 * np.sin(2 * np.pi * 5.0 * t) * np.clip(t / 0.5, 0, 1)
    phase = 2 * np.pi * freq * np.cumsum(1.0 + vibrato) / RATE
    return (np.sin(phase) + 0.18 * np.sin(2 * phase)) * env(t, 0.09, 0.25)


def pad(freqs: list[float], seconds: float) -> np.ndarray:
    t = times(seconds)
    out = np.zeros_like(t)
    for f in freqs:
        out += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.003 * t)
    return out / len(freqs) * env(t, seconds * 0.3, seconds * 0.3)


def tone(freq: float, seconds: float, decay: float = 8.0) -> np.ndarray:
    t = times(seconds)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * decay) * env(t, 0.002, 0.01)


def sweep(f0: float, f1: float, seconds: float, decay: float = 0.0) -> np.ndarray:
    t = times(seconds)
    freq = np.geomspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t * decay) * env(t, 0.005, 0.03)


def noise(rng, seconds: float, low: float, high: float) -> np.ndarray:
    """Ruido en una banda, por FFT: periódico, sirve para bucles sin costura."""
    n = int(seconds * RATE)
    spec = np.fft.rfft(rng.standard_normal(n))
    freqs = np.fft.rfftfreq(n, 1 / RATE)
    spec[(freqs < low) | (freqs > high)] = 0
    out = np.fft.irfft(spec, n)
    return out / (np.abs(out).max() + 1e-9)


def put(buf: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    """Suma `sig` en `at` segundos, dando la vuelta al final del búfer."""
    idx = (int(at * RATE) + np.arange(len(sig))) % len(buf)
    np.add.at(buf, idx, sig * gain)


def seq(parts: list[tuple[np.ndarray, float]], seconds: float) -> np.ndarray:
    """Efecto hecho de piezas, cada una en su instante."""
    out = np.zeros(int(seconds * RATE))
    for sig, at in parts:
        i = int(at * RATE)
        n = min(len(sig), len(out) - i)
        out[i:i + n] += sig[:n]
    return out


# --- efectos e interfaz --------------------------------------------------------

def effects(rng) -> dict[str, np.ndarray]:
    bells = [note(s, 440.0) for s in (0, 3, 5, 7, 10, 12)]
    return {
        "ui_move": tone(880, 0.05, 40),
        "ui_confirm": seq([(tone(660, 0.07, 25), 0.0), (tone(990, 0.1, 22), 0.05)], 0.16),
        "ui_cancel": seq([(tone(520, 0.07, 25), 0.0), (tone(350, 0.1, 22), 0.05)], 0.16),
        "ui_denied": tone(150, 0.14, 16) + 0.5 * tone(155, 0.14, 16),
        "hit": tone(120, 0.16, 18) + 0.8 * noise(rng, 0.16, 400, 5000) * np.exp(-times(0.16) * 30),
        "hit_resisted": tone(90, 0.16, 26) + 0.25 * noise(rng, 0.16, 100, 800) * np.exp(-times(0.16) * 30),
        "heal": seq([(pluck(note(s, 440.0), 0.4), i * 0.07) for i, s in enumerate((0, 5, 7))], 0.6),
        "regen": sweep(70, 210, 0.7, 1.5) + 0.3 * noise(rng, 0.7, 80, 500) * env(times(0.7), 0.2, 0.3),
        "purify": seq([(pluck(f, 0.9, 2.0), i * 0.09) for i, f in enumerate(bells)], 1.5),
        "wave": 0.6 * noise(rng, 0.9, 2000, 9000) * env(times(0.9), 0.3, 0.4)
                + 0.5 * sweep(300, 1400, 0.9) * env(times(0.9), 0.2, 0.3),
        "blinds": noise(rng, 0.3, 300, 3000) * env(times(0.3), 0.15, 0.1),
        "victory": seq([(pluck(note(s, 220.0), 1.2, 2.0), at) for s, at in
                        ((0, 0.0), (3, 0.16), (7, 0.32), (12, 0.48), (10, 0.8), (12, 0.96))], 2.3),
        "defeat": seq([(flute(note(s, 220.0), 0.8), at) for s, at in
                       ((7, 0.0), (5, 0.5), (3, 1.0), (0, 1.5))], 2.5),
    }


def combat_effects(rng) -> dict[str, np.ndarray]:
    """Combate de acción en el mapa (contrato «Tajo»). Cada acción suena distinta
    para que se distinga sin mirar, pero ninguna dice algo que no se vea."""
    return {
        # Tajo: aire cortado, del agudo al grave, corto.
        "slash": 0.7 * noise(rng, 0.14, 1500, 7000) * env(times(0.14), 0.01, 0.12)
                 + 0.3 * sweep(1800, 500, 0.14, 12),
        # Esquiva: soplo más grave y largo que el tajo.
        "dodge": 0.6 * noise(rng, 0.22, 300, 2500) * env(times(0.22), 0.05, 0.16),
        # Cambio de héroe: dos notas que suben, como abrir paso.
        "swap": seq([(pluck(note(7, 440.0), 0.18), 0.0), (pluck(note(12, 440.0), 0.22), 0.06)], 0.3),
        # Aturdido: campana sostenida con trémolo, la cuenta atrás de la ventana.
        "stun": tone(note(3, 440.0), 0.7, 3) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * times(0.7))),
    }


# --- ambiente --------------------------------------------------------------------

def wind(rng) -> np.ndarray:
    """Viento hueco de lo enfermo. El vaivén cierra un número entero de ciclos."""
    seconds = 20.0
    t = times(seconds)
    swell = 0.6 + 0.25 * np.sin(2 * np.pi * 3 * t / seconds) + 0.15 * np.sin(2 * np.pi * 7 * t / seconds + 1)
    return noise(rng, seconds, 80, 900) * swell


def life(rng) -> np.ndarray:
    """Lo purificado: agua que corre y pájaros sueltos."""
    seconds = 20.0
    t = times(seconds)
    buf = 0.35 * noise(rng, seconds, 500, 4000) * (0.8 + 0.2 * np.sin(2 * np.pi * 9 * t / seconds))
    for _ in range(14):
        at = rng.uniform(0, seconds)
        base = rng.uniform(1800, 3200)
        for k in range(int(rng.integers(2, 5))):
            put(buf, sweep(base, base * rng.uniform(1.1, 1.4), 0.09) * env(times(0.09), 0.01, 0.03),
                at + k * 0.13, 0.4)
    return buf


# --- música ------------------------------------------------------------------------

## Acordes en semitonos sobre A2, de la pentatónica de la menor.
CHORDS = {"Am": (0, 7, 12, 15), "C": (3, 10, 15, 19), "G": (-2, 5, 10, 14), "Dm": (5, 12, 17, 20)}
SCALE = (12, 15, 17, 19, 22, 24, 27, 29)


def music_world(rng) -> np.ndarray:
    """Calma andina: cuerda pulsada en arpegio, colchón y flauta a ratos."""
    beat = 60.0 / 84.0
    prog = ["Am", "C", "G", "Am", "Am", "Dm", "C", "Am", "C", "G", "Dm", "Am"]
    seconds = len(prog) * 4 * beat
    buf = np.zeros(int(seconds * RATE))
    pattern = (0, 2, 1, 3, 2, 1, 3, 2)
    for bar, name in enumerate(prog):
        ch = CHORDS[name]
        start = bar * 4 * beat
        put(buf, pad([note(s) for s in ch[:3]], 4 * beat + 0.6), start, 0.28)
        put(buf, pluck(note(ch[0] - 12), 2.2), start, 0.5)
        for i, p in enumerate(pattern):
            put(buf, pluck(note(ch[p]), 1.1), start + i * beat / 2, 0.34 + 0.06 * (i % 4 == 0))
    # La flauta entra en compases alternos, por grados vecinos de la escala.
    degree = 3
    for bar in range(1, len(prog), 2):
        at = bar * 4 * beat
        for length in (1.5, 1.0, 1.5):
            degree = int(np.clip(degree + rng.integers(-2, 3), 0, len(SCALE) - 1))
            put(buf, flute(note(SCALE[degree]), length * beat + 0.25), at, 0.3)
            at += length * beat
    return buf


def music_battle(rng) -> np.ndarray:
    """Combate: bajo insistente, percusión y cuerda a contratiempo."""
    beat = 60.0 / 132.0
    prog = ["Am", "Am", "C", "G", "Am", "Am", "Dm", "G"]
    seconds = len(prog) * 4 * beat
    buf = np.zeros(int(seconds * RATE))
    kick = seq([(tone(65, 0.25, 14), 0.0), (0.5 * tone(110, 0.08, 40), 0.0)], 0.25)
    hat = noise(rng, 0.05, 5000, 10000) * np.exp(-times(0.05) * 70)
    snare = noise(rng, 0.14, 900, 6000) * np.exp(-times(0.14) * 26)
    for bar, name in enumerate(prog):
        ch = CHORDS[name]
        start = bar * 4 * beat
        for i in range(8):
            at = start + i * beat / 2
            put(buf, pluck(note(ch[0] - 12), 0.4, 0.6), at, 0.62 if i % 2 == 0 else 0.42)
            put(buf, hat, at + beat / 4, 0.16)
        for i in (0, 2):
            put(buf, kick, start + i * beat, 0.8)
        for i in (1, 3):
            put(buf, snare, start + i * beat, 0.3)
        for i in (1, 3, 5, 6):
            put(buf, pluck(note(ch[1 + i % 3]), 0.5, 1.4), start + i * beat / 2, 0.3)
    return buf


# --- salida ------------------------------------------------------------------------

def write(name: str, sig: np.ndarray, loop: bool) -> None:
    sig = sig - sig.mean()
    sig = sig / (np.abs(sig).max() + 1e-9) * PEAK
    pcm = np.round(sig * 32767).astype(np.int16)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    rms = float(np.sqrt(np.mean(sig ** 2)))
    typical = float(np.abs(np.diff(sig)).mean()) * 8 + 0.02
    seam = abs(float(sig[0] - sig[-1]))
    if loop and seam > typical:
        print(f"  FALLA {name}: salto de {seam:.3f} en la costura (límite {typical:.3f})")
    print(f"  {name}.wav: {len(sig) / RATE:.2f} s, pico {np.abs(sig).max():.2f}, RMS {rms:.3f}"
          + (f", costura {seam:.3f}" if loop else ""))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    for name, sig in effects(rng).items():
        write(name, sig, False)
    write("amb_wind", wind(rng), True)
    write("amb_life", life(rng), True)
    write("music_world", music_world(rng), True)
    write("music_battle", music_battle(rng), True)
    # Semilla aparte: los audios de arriba siguen saliendo con los mismos bytes.
    for name, sig in combat_effects(np.random.default_rng(SEED + 1)).items():
        write(name, sig, False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
