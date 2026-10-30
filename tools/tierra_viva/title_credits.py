"""Concepto de la pantalla de título (parte 10) y de los créditos (parte 12),
con el arte de Tierra Viva y lo que la guía ya recomienda:

- Título: Valdehoja viva en el estado de la partida guardada. En partida nueva
  todo enfermo salvo el jardín de Yara; con tres regiones, ese verde. El frente
  de purificación usa el tramado Bayer 4x4 (su único trabajo en el repertorio).
  Nombre en «Brote» a 4x, un solo punto de entrada. Menú en panel ASH_800 con
  borde ASH_600 de 1 px, radio 0, cursor EMBER_300.
- Créditos: recorrido de cámara por las zonas ya sanas, con los nombres en
  paneles. Enseñan lo que el jugador devolvió.

Salida 640x360 (y x2 para revisar).
"""
import numpy as np
from PIL import Image
import font
import px

OUT = 'out2'
W, H = 640, 360
ASH_950 = (0x17, 0x14, 0x1C, 255)
ASH_800 = (0x2E, 0x28, 0x36, 255)
ASH_600 = (0x4D, 0x46, 0x57, 255)
ASH_400 = (0x9C, 0x95, 0xA7, 255)
ASH_050 = (0xE8, 0xE4, 0xEE, 255)
EMBER_300 = (0xFF, 0xC1, 0x4D, 255)
VITAL_500 = (0x4A, 0xDE, 0x80, 255)
INK = (0x14, 0x10, 0x1C, 255)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def load(state):
    return np.array(Image.open(f'final7/valdehoja_{state}.png').convert('RGBA'))


def scaled_text(s, color, k, shadow=None):
    t = font.render(s, color)
    t = np.kron(t, np.ones((k, k, 1), np.uint8))
    if shadow is None:
        return t
    h, w = t.shape[:2]
    out = np.zeros((h + k, w + k, 4), np.uint8)
    sh = t.copy()
    sh[sh[..., 3] > 0] = shadow
    px.blit(out, sh, k, k)
    px.blit(out, t, 0, 0)
    return out


def outlined(t, ink=INK):
    h, w = t.shape[:2]
    out = np.zeros((h + 2, w + 2, 4), np.uint8)
    a = t[..., 3] > 0
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out[dy:dy + h, dx:dx + w][a] = ink
    out[1:1 + h, 1:1 + w][a] = t[a]
    return out


def panel(w, h):
    p = np.zeros((h, w, 4), np.uint8)
    p[...] = ASH_800
    p[0, :] = ASH_600; p[-1, :] = ASH_600; p[:, 0] = ASH_600; p[:, -1] = ASH_600
    return p


def purified_mask(shape, blobs, t=1.0):
    """Máscara de lo purificado con borde tramado Bayer 4x4: el verde no
    aparece de golpe, avanza (enmienda 3)."""
    h, w = shape
    yy, xx = np.indices((h, w))
    from scipy import ndimage as ndi
    rng = np.random.default_rng(5)
    noise = ndi.zoom(rng.uniform(-1, 1, (h // 40 + 3, w // 40 + 3)), 40, order=3)[:h, :w]
    noise = ndi.gaussian_filter(noise, 8)
    noise /= np.abs(noise).max() + 1e-6
    field = np.zeros((h, w))
    for cx, cy, r in blobs:
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.25) ** 2) + noise * r * 0.45
        field = np.maximum(field, np.clip((r * t - d) / 28 + 0.5, 0, 1))
    thr = BAYER[yy % 4, xx % 4]
    return field > thr


def title(stage, out):
    sick, pure = load('enfermo'), load('sano')
    x0, y0 = 300, 210
    sick = sick[y0:y0 + H, x0:x0 + W].copy()
    pure = pure[y0:y0 + H, x0:x0 + W].copy()
    # jardín de Yara (siempre), y las partes de tres regiones en la etapa media
    blobs = {'nueva': [(470, 250, 70)],
             'media': [(470, 250, 90), (130, 120, 110), (330, 300, 90), (560, 70, 80)],
             'final': [(320, 180, 900)]}[stage]
    m = purified_mask((H, W), blobs)
    img = np.where(m[..., None], pure, sick)
    # viñeta de valor: la mitad izquierda baja un poco para que el nombre mande
    yy, xx = np.indices((H, W))
    k = np.clip(1 - (xx / W) * 1.6, 0, 1) * 0.42
    img = img.astype(float)
    img[..., :3] *= (1 - k)[..., None]
    img = img.astype(np.uint8)
    # nombre del juego, un solo punto de entrada
    t1 = outlined(scaled_text('Ecos de la', ASH_050, 3))
    t2 = outlined(scaled_text('Tierra', VITAL_500 if stage != 'nueva' else ASH_050, 5))
    px.blit(img, t1, 32, 40)
    px.blit(img, t2, 30, 40 + t1.shape[0] + 2)
    # menú
    items = ['Continuar', 'Nueva partida', 'Opciones', 'Salir']
    pw, ph = 132, 12 + len(items) * 16
    p = panel(pw, ph)
    for i, s in enumerate(items):
        sel = i == 0
        tx = font.render(s, ASH_050 if sel else ASH_400)
        px.blit(p, tx, 18, 8 + i * 16)
        if sel:
            p[8 + i * 16 + 1:8 + i * 16 + 6, 8:10] = EMBER_300
            p[8 + i * 16 + 2:8 + i * 16 + 5, 10] = EMBER_300
            p[8 + i * 16 + 3, 11] = EMBER_300
    px.blit(img, p, 32, H - ph - 32)
    # estado de la partida, discreto
    info = {'nueva': 'Partida nueva', 'media': 'Tres regiones devueltas', 'final': 'Solmira devuelta'}[stage]
    ti = font.render(info, ASH_400)
    px.blit(img, ti, W - font.width(info) - 16, H - 20)
    Image.fromarray(img).save(f'{OUT}/{out}.png')
    Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save(f'{OUT}/{out}_x2.png')


CREDITS = [
    ('valdehoja', None, ['Ecos de la Tierra', '', 'Un proyecto de Diseño de Interfaces de Software']),
    ('costa', 'Dirección, diseño y desarrollo', ['Diego']),
    ('cuenca', 'Desarrollo e integración', ['Juan José Rueda']),
    ('llanura', 'Arte y mundo', ['Tierra Viva: pixel art propio y del equipo']),
    ('cumbre', 'Fuentes y audio', ['Fuente Brote: propia', 'Audio: licencias en LICENCIAS.md']),
    ('cripta', None, ['Gracias por devolverle el color a Solmira']),
]


def credits():
    frames = []
    for zone, role, names in CREDITS:
        if zone == 'valdehoja':
            bg = load('sano')[260:260 + H, 360:360 + W].copy()
        else:
            bg = np.array(Image.open(f'{OUT}/z_{zone}_sano.png').convert('RGBA'))[::2, ::2][:H, :W].copy()
        lines = ([role] if role else []) + names
        widths = [font.width(s) for s in lines]
        pw = max(widths) + 32
        ph = 16 + len(lines) * 14
        p = panel(pw, ph)
        y = 9
        for i, s in enumerate(lines):
            c = ASH_400 if (role and i == 0) else ASH_050
            px.blit(p, font.render(s, c), (pw - font.width(s)) // 2 if not role else 16, y)
            y += 14
        # el panel va abajo a la izquierda: el mundo devuelto ocupa el resto
        px.blit(bg, p, 24, H - ph - 24)
        frames.append(bg)
        Image.fromarray(bg).save(f'{OUT}/creditos_{zone}.png')
    # hoja de contacto 3x2
    sheet = np.zeros((H * 2 + 8, W * 3 + 16, 4), np.uint8)
    sheet[...] = ASH_950
    for i, f in enumerate(frames):
        px.blit(sheet, f, (i % 3) * (W + 8), (i // 3) * (H + 8))
    Image.fromarray(sheet).save(f'{OUT}/creditos_hoja.png')


if __name__ == '__main__':
    title('nueva', 'titulo_nueva')
    title('media', 'titulo_media')
    title('final', 'titulo_final')
    credits()
