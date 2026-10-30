"""Mapas escritos casilla a casilla (40x23 = 640x368), con un pequeño
constructor para no teclear 920 caracteres a mano y poder corregir el trazado.

Leyenda del suelo:
  .  hierba          p  camino          w  agua          B  puente (agua debajo)
  S  escalera en la cara del acantilado
  t  hierba alta     f  flores
Altura: 0 cota baja, 1 meseta. La cara de roca aparece sola en la casilla al
sur de cada borde de meseta.
"""

W, H = 40, 23


class Builder:
    def __init__(self, w=W, h=H):
        self.W, self.H = w, h
        self.g = [['.'] * w for _ in range(h)]
        self.h = [[0] * w for _ in range(h)]

    def run(self, ch, spans):
        """spans: {fila: (col_ini, col_fin)} o lista de (fila, ini, fin)."""
        items = spans.items() if isinstance(spans, dict) else [(r, (a, b)) for r, a, b in spans]
        for r, (a, b) in items:
            for c in range(max(0, a), min(self.W - 1, b) + 1):
                cur = self.g[r][c]
                if ch == 'p' and cur in 'wB':
                    self.g[r][c] = 'B'
                elif ch == 'w' and cur in 'pB':
                    self.g[r][c] = 'B'
                else:
                    self.g[r][c] = ch
        return self

    def high(self, spans, level=1):
        for r, a, b in spans:
            for c in range(a, b + 1):
                self.h[r][c] = max(self.h[r][c], level)
        return self

    def spec(self):
        return dict(ground=[''.join(r) for r in self.g],
                    height=[''.join(str(v) for v in r) for r in self.h])


def bosque():
    b = Builder()
    # meseta de borde irregular
    b.high([(r, 0, 8) for r in range(0, 7)] + [(r, 9, 20) for r in range(0, 8)] +
           [(r, 21, 24) for r in range(0, 5)] + [(7, 0, 8)])
    # río
    river = {0: (30, 32), 1: (30, 33), 2: (31, 33), 3: (31, 34), 4: (31, 34), 5: (32, 34), 6: (32, 35),
             7: (32, 35), 8: (32, 34), 9: (31, 34), 10: (31, 33), 11: (31, 34), 12: (32, 35),
             13: (32, 34), 14: (32, 34), 15: (32, 34), 16: (32, 35), 17: (31, 35), 18: (31, 34),
             19: (30, 33), 20: (30, 33), 21: (29, 32), 22: (29, 32)}
    b.run('w', river)
    # estanque abajo a la izquierda
    b.run('w', [(17, 5, 8), (18, 4, 9), (19, 4, 9), (20, 5, 8)])
    # camino principal que serpentea de oeste a este
    b.run('p', [(13, 0, 8), (14, 0, 8), (12, 8, 15), (13, 8, 15), (13, 15, 24), (14, 15, 24),
                (14, 24, 39), (15, 24, 39)])
    # ramal norte hasta la escalera y por la meseta
    b.run('p', [(r, 15, 16) for r in range(8, 13)] + [(r, 14, 15) for r in range(0, 8)])
    b.run('S', [(8, 14, 15)])
    b.run('p', [(8, 16, 16)])
    # ramal sur
    b.run('p', [(r, 22, 23) for r in range(15, 19)] + [(r, 21, 22) for r in range(19, 23)])
    # hierba alta en matas con forma, no en rectángulos
    b.run('t', [(2, 4, 6), (3, 3, 7), (4, 3, 6), (5, 4, 5),
                (18, 12, 15), (19, 11, 16), (20, 12, 16), (21, 13, 15),
                (9, 35, 37), (10, 34, 38), (11, 35, 38)])
    b.run('f', [(9, 19, 21), (10, 18, 20), (2, 18, 19), (3, 17, 20), (17, 25, 27), (18, 26, 27),
                (11, 3, 4), (16, 36, 38)])
    return b.spec()



def valdehoja():
    b = Builder()
    # loma al norte con escalera
    b.high([(r, 0, 39) for r in range(0, 3)] + [(3, 0, 14), (3, 23, 39)])
    # río al este
    river = {r: (34, 36) for r in range(0, 23)}
    river.update({0: (33, 35), 1: (33, 35), 2: (33, 36), 8: (34, 37), 9: (34, 37), 16: (35, 37), 17: (35, 37),
                  18: (35, 38), 19: (35, 38), 20: (34, 37), 21: (34, 37), 22: (34, 36)})
    b.run('w', river)
    # plaza y caminos
    b.run('c', [(r, 14, 24) for r in range(10, 15)])
    b.run('p', [(11, 0, 14), (12, 0, 14), (11, 24, 39), (12, 24, 39)])
    b.run('p', [(r, 18, 19) for r in range(0, 10)] + [(r, 18, 19) for r in range(15, 23)])
    b.run('S', [(3, 18, 19)])
    # caminitos a las puertas
    for c0, r0, r1 in [(6, 9, 10), (27, 9, 10)]:
        b.run('p', [(r, c0, c0 + 1) for r in range(r0, r1 + 1)])
    # callejón sur, delante de las casas de abajo
    b.run('p', [(21, 3, 33), (22, 3, 33)])
    # huertos de flores y hierba alta
    b.run('f', [(8, 11, 13), (8, 22, 24), (19, 11, 13), (19, 24, 26), (6, 2, 3)])
    b.run('t', [(16, 0, 2), (17, 0, 3), (18, 0, 2), (5, 37, 39), (6, 38, 39)])
    return b.spec()



def valdehoja2():
    """Valdehoja, pueblo de las terrazas (60x34 = 960x544).

    Arriba, dos terrazas: la capilla y la cabaña de Bruma en la primera; los
    bancales de papa y maíz escalonados a la derecha. Abajo, la plaza con el
    Árbol del Vínculo, la fuente y el mercado; la posada a la izquierda, el
    almacén a la derecha; el molino sobre el río; el taller de Nix y las casas
    al sur.
    """
    b = Builder(60, 34)
    # terrazas
    # la terraza baja con entrantes y salientes: no una línea recta
    b.high([(r, 0, 59) for r in range(0, 9)] + [(9, 4, 59), (10, 3, 9), (11, 4, 8),
            (10, 21, 34), (10, 55, 59)])
    b.high([(r, 40, 59) for r in range(0, 4)], level=2)
    # río del este, bajando desde la terraza (cascada en la cara)
    river = {r: (51, 53) for r in range(0, 34)}
    river.update({0: (50, 52), 1: (50, 52), 2: (50, 53), 3: (51, 53), 12: (51, 54), 13: (51, 54),
                  14: (52, 54), 15: (52, 55), 16: (52, 55), 17: (52, 54), 24: (51, 54), 25: (51, 54),
                  26: (50, 53), 27: (50, 53), 30: (51, 54), 31: (51, 54)})
    b.run('w', river)
    # bancales: tres franjas en la terraza alta y dos en la de en medio
    b.run('u', [(r, 42, 47) for r in (1, 2)] + [(r, 55, 58) for r in (1, 2)] +
          [(r, 41, 46) for r in (6, 7)] + [(r, 55, 58) for r in (6, 7, 8)])
    # camino principal de oeste a este, con puente
    b.run('p', [(22, 0, 59), (23, 0, 59)])
    # plaza
    b.run('c', [(r, 19, 36) for r in range(13, 22)])
    # escalera central: sube directa a la puerta de la capilla
    b.run('p', [(r, 27, 28) for r in range(10, 13)])
    b.run('S', [(11, 27, 28)])
    # paseo de la terraza delante de la capilla, de la cabaña a los bancales
    b.run('p', [(8, 10, 49), (9, 10, 49)])
    b.run('p', [(r, 10, 11) for r in (6, 7)] + [(r, 36, 37) for r in (6, 7)])
    # escalera a la terraza alta, junto al río
    b.run('p', [(r, 48, 49) for r in range(5, 8)])
    b.run('S', [(4, 48, 49)])
    b.run('p', [(r, 48, 49) for r in range(0, 4)])
    # calle sur y sendas a las puertas
    b.run('p', [(r, 27, 28) for r in range(24, 31)] + [(31, 2, 48), (32, 2, 48)])
    for c0, r0, r1 in [(13, 20, 21), (39, 20, 21), (7, 29, 30), (18, 29, 30), (37, 29, 30), (47, 19, 21)]:
        b.run('p', [(r, c0, c0 + 1) for r in range(r0, r1 + 1)])
    # jardines y hierba alta
    b.run('f', [(12, 3, 6), (13, 2, 6), (26, 31, 33), (27, 30, 33), (2, 22, 25), (3, 21, 24)])
    b.run('t', [(r, 0, 3) for r in range(24, 30)] + [(r, 56, 59) for r in range(20, 26)] + [(1, 30, 34), (2, 31, 35)])
    return b.spec()




BOSQUE = bosque()
VALDEHOJA = valdehoja()
VALDEHOJA2 = valdehoja2()

if __name__ == '__main__':
    s = BOSQUE
    for g, h in zip(s['ground'], s['height']):
        print(g, h)


def valdehoja3():
    """Valdehoja grande (90x60 = 1440x960): un pueblo para explorar.

    Norte: la terraza de la capilla, la cabaña de Bruma, la casa de labranza y
    los bancales; arriba del todo, el mirador. Centro: la plaza del Árbol del
    Vínculo con la posada, el almacén y el molino. Oeste: la escuela, el vivero
    y el huerto de frutales. Sur: la plazoleta del ayuntamiento con su fuente,
    la calle de los oficios (taller, panadería, herrería, casas) y la salida al
    bosque. Este: el río, el lago con su muelle y la casa de los pescadores.
    """
    b = Builder(90, 60)
    # terrazas con entrantes y salientes
    b.high([(r, 0, 89) for r in range(0, 12)] + [(12, 3, 30), (12, 34, 58), (13, 5, 26), (13, 44, 56),
            (12, 62, 89), (13, 66, 72)])
    b.high([(r, 58, 89) for r in range(0, 5)] + [(5, 62, 74)], level=2)
    # río del este y lago
    river = {}
    for r in range(60):
        c = 77 + int(round(1.6 * np.sin(r / 6.0)))
        river[r] = (c, c + 2)
    b.run('w', river)
    b.run('w', [(36, 72, 79), (37, 70, 80), (38, 69, 80), (39, 68, 80), (40, 68, 80), (41, 69, 80),
                (42, 70, 79), (43, 72, 78)])
    # camino real de oeste a este, con puente
    b.run('p', [(30, 0, 89), (31, 0, 89)])
    # plaza del Árbol del Vínculo
    b.run('c', [(r, 30, 49) for r in range(18, 28)])
    # escalera de la plaza a la terraza y paseo de la terraza
    b.run('S', [(13, 39, 40)] if False else [])
    b.run('p', [(r, 39, 40) for r in range(13, 18)])
    b.run('S', [(12, 39, 40)])
    b.run('p', [(10, 8, 72), (11, 8, 72)])
    b.run('p', [(r, 39, 40) for r in (8, 9)] + [(r, 12, 13) for r in (8, 9)] + [(r, 56, 57) for r in (8, 9)])
    # escalera a la terraza alta y sendero al mirador
    b.run('S', [(5, 60, 61)] if False else [])
    b.run('p', [(r, 60, 61) for r in range(6, 10)])
    b.run('S', [(6, 60, 61)])
    b.run('p', [(r, 60, 61) for r in range(2, 6)] + [(2, 60, 70), (3, 60, 70)])
    # bancales
    b.run('u', [(r, 63, 72) for r in (1,)] + [(r, 66, 72) for r in (6, 7, 8)] + [(r, 46, 52) for r in (3, 4, 5)])
    # sendas de la plaza a las puertas
    for c0, r0, r1 in [(24, 26, 29), (54, 26, 29), (72, 24, 29), (10, 26, 29)]:
        b.run('p', [(r, c0, c0 + 1) for r in range(r0, r1 + 1)])
    # oeste: vivero y huerto al sur del camino
    b.run('p', [(r, 8, 9) for r in range(32, 40)])
    # torre del vigía al oeste de la terraza y casa de botes en la orilla del lago
    b.run('p', [(10, 3, 8), (11, 3, 8), (8, 4, 5), (9, 4, 5)])
    b.run('p', [(r, 65, 66) for r in range(45, 50)])
    # sur: bajada a la plazoleta, plazoleta y calle de los oficios
    b.run('p', [(r, 32, 33) for r in range(32, 42)])
    b.run('c', [(r, 34, 47) for r in range(42, 49)])
    b.run('p', [(50, 4, 66), (51, 4, 66)])
    b.run('p', [(r, 40, 41) for r in range(49, 50)] + [(r, 40, 41) for r in range(52, 60)])
    for c0 in (10, 18, 27, 52):
        b.run('p', [(r, c0, c0 + 1) for r in (48, 49)])
    # este: senda al lago, muelle y casa de pescadores
    b.run('p', [(r, 62, 63) for r in range(32, 40)] + [(39, 62, 67), (40, 62, 67)])
    b.run('B', [(r, 68, 69) for r in range(39, 42)])
    # bancales del noreste
    b.run('u', [(r, 81, 88) for r in (7, 8)] + [(r, 81, 88) for r in (10,)])
    # flores, hierba alta
    b.run('f', [(15, 30, 33), (16, 29, 33), (15, 46, 49), (16, 46, 50), (24, 2, 5), (25, 1, 5),
                (44, 22, 26), (45, 21, 26), (35, 52, 55), (36, 52, 56)])
    b.run('t', [(r, 0, 4) for r in range(52, 60)] + [(r, 82, 89) for r in range(46, 56)] +
          [(r, 84, 89) for r in range(14, 22)] + [(1, 20, 26), (2, 21, 27), (3, 22, 26)])
    return b.spec()


import numpy as np  # noqa: E402
VALDEHOJA3 = valdehoja3()


# ---------------------------------------------------------------------------
# Valdehoja densa: calles paralelas con las casas en fila mirando a la calle,
# como un pueblo de verdad. Las casas ocupan ~7 casillas de ancho y ~8 de alto;
# cada calle lleva casas a lo largo de su lado norte, puerta sobre la acera.
STREETS4 = {'terraza': 10, 'mayor': 30, 'media': 41, 'sur': 52}   # fila de cada calle (2 filas de ancho)
SLOTS4 = {   # calle -> columnas de las puertas
    'terraza': [5, 13, 21, 29, 39, 48, 56, 65],
    'mayor': [5, 13, 22, 55, 63, 71],
    'media': [5, 13, 21, 29, 40, 51, 59],
    'sur': [5, 13, 21, 29, 52, 60, 68],
}


def valdehoja4():
    b = Builder(90, 60)
    # terraza con entrantes y salientes; terraza alta solo en el noreste
    b.high([(r, 0, 89) for r in range(0, 12)] + [(12, 3, 30), (12, 34, 58), (13, 5, 26), (13, 44, 56),
            (12, 62, 89), (13, 66, 72)])
    b.high([(r, 76, 89) for r in range(0, 5)] + [(5, 78, 86)], level=2)
    river = {}
    for r in range(60):
        c = 78 + int(round(1.4 * np.sin(r / 6.0)))
        river[r] = (c, c + 2)
    b.run('w', river)
    # lago al sureste, entre la calle media y la sur
    b.run('w', [(43, 70, 76), (44, 68, 77), (45, 67, 78), (46, 67, 78), (47, 68, 77), (48, 70, 76)])
    # calles
    b.run('p', [(10, 2, 74), (11, 2, 74)])
    b.run('p', [(30, 0, 89), (31, 0, 89)])
    b.run('p', [(41, 0, 66), (42, 0, 66)])
    b.run('p', [(52, 0, 74), (53, 0, 74)])
    # callejones norte-sur que cosen las calles
    b.run('p', [(r, 0, 1) for r in range(30, 54)])
    for c0 in (33, 47):
        b.run('p', [(r, c0, c0 + 1) for r in range(32, 41)])
    # plaza del Árbol del Vínculo y escalera a la terraza
    b.run('c', [(r, 30, 49) for r in range(18, 28)])
    b.run('p', [(r, 39, 40) for r in range(13, 18)])
    b.run('S', [(12, 39, 40)])
    # plazoleta de la fuente, al sur de la alcaldía, y salida al sur
    b.run('c', [(r, 34, 47) for r in range(43, 51)])
    b.run('p', [(r, 40, 41) for r in range(54, 60)])
    # sendas cortas a las puertas (2 filas sobre la calle)
    for st, cols in SLOTS4.items():
        r = STREETS4[st]
        for c in cols:
            b.run('p', [(r - 2, c, c + 1), (r - 1, c, c + 1)])
    # escalera a la terraza alta y bancales
    b.run('p', [(r, 82, 83) for r in range(6, 10)] + [(10, 75, 83), (11, 75, 83)])
    b.run('S', [(5, 82, 83)] if False else [])
    b.run('u', [(r, 77, 88) for r in (1, 2)] + [(r, 84, 88) for r in (7, 8)])
    # este del río: prado y salida
    b.run('f', [(r, 82, 87) for r in range(16, 20)] + [(r, 83, 88) for r in range(36, 39)])
    b.run('t', [(r, 84, 89) for r in range(22, 28)] + [(r, 0, 3) for r in range(55, 60)] +
          [(r, 81, 89) for r in range(48, 58)])
    # flores junto a la plaza
    b.run('f', [(15, 30, 33), (16, 29, 33), (15, 46, 49), (16, 46, 50)])
    return b.spec()


VALDEHOJA4 = valdehoja4()
