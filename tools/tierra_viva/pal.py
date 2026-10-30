"""Paleta maestra «Tierra Viva». Rampas de oscuro a claro, con desplazamiento de matiz:
las sombras viran a azul/violeta y las luces a amarillo, como en Minish Cap y Pokémon NB."""

def h(x):
    x = x.lstrip('#'); return (int(x[0:2],16), int(x[2:4],16), int(x[4:6],16), 255)

R = {
 # --- tinta y neutros
 'ink':     ['#14101c', '#231c2e', '#372b42'],
 'stone':   ['#2a2434', '#40384d', '#5c5268', '#7d7387', '#a198a8', '#c9c1cc', '#ece6ec'],
 # --- sano
 'grass':   ['#123a2e', '#1a5234', '#256e3a', '#358c3e', '#4fa645', '#7cc456', '#b5e073'],
 'leaf':    ['#0f2b26', '#174232', '#215c38', '#2f7a3c', '#48983f', '#74b84a', '#aad65e'],
 'dirt':    ['#3b2226', '#5a332c', '#7d4b35', '#a06741', '#c48a52', '#e0b070', '#f4d699'],
 'sand':    ['#8a6a4a', '#b08d5e', '#d1b077', '#e8cf98', '#f7ebc4'],
 'water':   ['#16244f', '#1b3c7a', '#2360a8', '#3489cc', '#56b3e6', '#92d9f4', '#dff7ff'],
 'wood':    ['#2e1a1e', '#4a2a26', '#6b3f2e', '#8f5a3a', '#b27a4c', '#d1a068'],
 'roofr':   ['#3a1426', '#5e1f30', '#8c2c3a', '#b8443f', '#dc6a4c', '#f29c6e'],
 'roofb':   ['#1a1d40', '#253366', '#2f4f94', '#3f75be', '#62a2dc', '#9ccdf0'],
 'wall':    ['#6b5a66', '#8f7d82', '#b5a598', '#d8cbb4', '#f2e8d2'],
 'skin':    ['#4a2228', '#7a3a34', '#b4654a', '#de9466', '#f5c08e', '#ffe2bc'],
 'flower':  ['#b0304f', '#e8566b', '#ff8fa3', '#ffd34e', '#fff3b0', '#8a6bd9', '#c3a8ff', '#ffffff'],
 # --- enfermo
 'drygrass':['#2a1f2a', '#3d2e2e', '#56432f', '#735c37', '#94783f', '#b39a52', '#cfbd70'],
 'deadleaf':['#1e1622', '#2f2229', '#46332e', '#61483a', '#7f6146', '#9c7d55'],
 'ash':     ['#221d29', '#342d3b', '#4a4252', '#645c6b', '#827a88', '#a39ca6', '#c7c1c6'],
 'oil':     ['#0b0812', '#15111f', '#221b30', '#302744', '#433757'],
 'sheen':   ['#5a3f8c', '#3f7f86', '#a3963f', '#c0577a'],
 'sludge':  ['#2f3a12', '#4f6418', '#77921f', '#a4c42c', '#d2ef5a'],
 'smog':    ['#4b3f4a', '#6e5d62', '#93807a', '#b8a594'],
 'rust':    ['#3a1a16', '#5e2a1e', '#8a4126', '#b5602f', '#d68a45'],
 'plastic': ['#2a4f6e', '#3f7fa8', '#7cc0e0', '#c9ecf7', '#e25a6a', '#f2c94c', '#ffffff'],
 # --- fuego y hielo
 'fire':    ['#3d0f14', '#7a1a16', '#c13a1c', '#ec6a24', '#ffa83a', '#ffe07a', '#fffbe0'],
 'ice':     ['#1d2c52', '#2c4c80', '#4a7fb4', '#7ab6df', '#b0e0f4', '#e4f8ff'],
 'gold':    ['#3a2412', '#6b4316', '#a6701c', '#d9a52a', '#f5d24a', '#fff1a0'],
 # --- acento eco: la purificación
 'eco':     ['#0f3b3f', '#14706a', '#20a88f', '#4fd8b0', '#9cf5d4', '#e2fff3'],
 # --- interfaz
 'ui':      ['#1d1a2b', '#2e2a42', '#4a4566', '#a49ec0', '#d8d3e8', '#f4f1fa', '#ffffff'],
 'paper':   ['#5b4a3c', '#8a7560', '#c9b694', '#e8dbbd', '#f8f1de'],
 'hp':      ['#2b8a3e', '#5ad06a', '#a8f08a', '#b8860b', '#f5c33b', '#a3261b', '#ee5840'],
}
P = {k: [h(c) for c in v] for k, v in R.items()}
CLEAR = (0, 0, 0, 0)
