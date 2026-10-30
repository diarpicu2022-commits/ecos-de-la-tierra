"""Maquetas del combate de acción en el mapa (640x360)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import scene2, hud, ui, px, scene, font
from pal import P

def spr(path):
    return scene.trim(np.array(Image.open(path)))

ILAN = spr('final/chars/ilan_east.png')
BRUMA = spr('final/chars/bruma_east.png')
LLAMA = spr('pl/monsters/llama_corrupto.png')
GUARD = spr('pl/monsters/llama_purificado.png')
MX, MY = 400, 262          # pie del monstruo
HX, HY = 300, 262          # pie del héroe


def base(state, hero, monster, frame=0):
    actors = [(hero, HX - hero.shape[1] // 2, HY, 26), (monster, MX - monster.shape[1] // 2 + 30, MY, 60)]
    return scene2.render(state, actors=actors, frame=frame)


def hud_common(img, hero, hp, en, others, eco_ready, item=0, cause='0/3'):
    px.blit(img, hud.hero_card(hero, hp, 120, en, 30), 8, 8)
    px.blit(img, hud.party_strip(others), 8, 52)
    s = ui.sign('Bosque de las Cenizas', f'Causas atajadas {cause}')
    px.blit(img, s, 640 - s.shape[1] - 8, 8)
    items = [('hierba', 3), ('agua', 2), ('antidoto', 1), ('racion', 4)]
    px.blit(img, hud.quickbar(items, item), 8, 360 - 52)
    px.blit(img, hud.action_pad(eco_ready, hud.ECO_OF[hero.lower()][2]), 640 - 116, 360 - 102)


def mock_ataque():
    img = base('enfermo', ILAN, LLAMA)
    # tajo y chispa sobre el monstruo
    sl = hud.slash(28, -80, 70, 7)
    px.blit(img, sl, HX - 6, HY - 52)
    px.blit(img, hud.spark(9), MX - 6, HY - 40)
    px.blit(img, hud.spark(7), MX + 6, HY - 56)
    d = hud.dmg('~12', P['ui'][4])
    px.blit(img, d, MX + 4, HY - 120)
    np_ = hud.nameplate('Llama de la Deforestación', 'FUEGO', 138, 180)
    px.blit(img, np_, MX + 30 - np_.shape[1] // 2, HY - LLAMA.shape[0] - 44)
    hud_common(img, 'Ilan', 92, 18, [('bruma', 1.0), ('coral', 0.8), ('nix', 0.55), ('suri', 0.3)], eco_ready=True)
    t = hud.toast([[('La llama se rehace.', P['ink'][1]), ('Su causa es', P['ink'][1]), ('FUEGO', P['rust'][2]) ],
                   [('Cambia a', P['ink'][1]), ('Bruma [Q]', P['eco'][1]), ('y usa Línea Cortafuegos.', P['ink'][1])]], w=320)
    px.blit(img, t, 160, 360 - t.shape[0] - 8)
    return img


def mock_purifica():
    sick = base('enfermo', BRUMA, GUARD)
    sano = base('sano', BRUMA, GUARD)
    # la ola de purificación: el mundo sano vuelve en un círculo tramado
    H, W = sick.shape[:2]
    yy, xx = np.indices((H, W))
    d = np.hypot(xx - MX, (yy - (HY - 20)) * 1.25)
    R = 150
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
    th = bayer[yy % 4, xx % 4] / 16
    m = (d < R - 16) | ((d < R) & (th > (d - (R - 16)) / 16))
    img = sick.copy()
    img[m] = sano[m]
    ring = (np.abs(d - R) < 1.2)
    img[ring & ((xx + yy) % 3 != 0)] = px.col(P['eco'][4])
    # Línea Cortafuegos: franja de hojas y luz eco entre Bruma y el guardián
    for k in range(9):
        x = HX + 18 + k * 9
        y = HY - 6 + (k % 2) * 3
        px.blit(img, hud.icon('hoja'), x, y - 10)
    for x in range(HX + 14, MX + 10):
        img[HY - 2, x] = px.col(P['eco'][3]); img[HY - 1, x] = px.col(P['eco'][1])
    for k, (sx, sy) in enumerate([(MX - 30, HY - 90), (MX + 50, HY - 110), (MX + 70, HY - 40), (MX - 10, HY - 130)]):
        px.blit(img, hud.spark(7 if k % 2 else 9), sx, sy)
    np_ = hud.nameplate('Guardián del Bosque', 'FUEGO', 180, 180, purified=True)
    px.blit(img, np_, MX + 30 - np_.shape[1] // 2, HY - GUARD.shape[0] - 44)
    hud_common(img, 'Bruma', 104, 12, [('ilan', 0.77), ('coral', 0.8), ('nix', 0.55), ('suri', 0.3)], eco_ready=True, cause='1/3')
    t = hud.toast([[('¡Purificado!', P['eco'][1]), ('El Guardián del Bosque vuelve en sí.', P['ink'][1])],
                   [('El bosque recupera el color a su alrededor.', P['ink'][1])]], w=320)
    px.blit(img, t, 160, 360 - t.shape[0] - 8)
    return img


if __name__ == '__main__':
    px.save(mock_ataque(), 'out2/combate_accion.png', scale=2)
    px.save(mock_purifica(), 'out2/combate_purifica.png', scale=2)
