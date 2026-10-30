"""Trazado de mapas de muestra en rejilla de esquinas (41 x 24 => 640 x 368 px)."""
import numpy as np

CW, CH = 41, 24


def blank(ch='g'):
    return np.full((CH, CW), ch)


def stroke(g, pts, width, ch):
    yy, xx = np.mgrid[0:CH, 0:CW]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        g[d <= width / 2] = ch
    return g


def blob(g, cx, cy, rx, ry, ch, only=None):
    yy, xx = np.mgrid[0:CH, 0:CW]
    m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    if only is not None:
        m &= np.isin(g, list(only))
    g[m] = ch
    return g


def to_rows(g):
    return [''.join(r) for r in g]


def bosque():
    g = blank('g')
    stroke(g, [(-1, 15), (8, 14), (14, 11), (22, 12), (30, 9), (42, 9)], 2.2, 'd')
    stroke(g, [(18, 12), (19, 18), (17, 25)], 2.0, 'd')
    stroke(g, [(27, -1), (26, 5), (29, 10), (28, 16), (31, 25)], 2.6, 'w')
    # el camino cruza el arroyo: vado de arena
    blob(g, 29, 9.5, 2.2, 1.6, 's', only='w')
    blob(g, 7, 6, 4.5, 2.6, 't')
    blob(g, 35, 17, 4, 2.4, 't')
    blob(g, 10, 20, 3.5, 2, 't')
    return to_rows(g)


def valdehoja():
    g = blank('g')
    stroke(g, [(-1, 12), (12, 12), (20, 13), (42, 13)], 2.4, 'd')
    stroke(g, [(20, 13), (20, -1)], 2.0, 'd')
    stroke(g, [(12, 12), (12, 25)], 2.0, 'd')
    blob(g, 20, 13, 3.6, 2.6, 'd')            # plaza
    stroke(g, [(34, -1), (33, 6), (36, 12), (35, 18), (38, 25)], 3.0, 'w')
    for y in (11.6, 12.4, 13.2, 14.0):          # puente de tierra sobre el río
        pass
    blob(g, 35.5, 13, 2.5, 1.5, 'd', only='wd')
    blob(g, 4, 19, 3.5, 2.2, 't')
    blob(g, 26, 20, 3, 1.6, 't')
    return to_rows(g)
