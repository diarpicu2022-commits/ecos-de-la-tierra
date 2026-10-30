import json, sys
from pal import R
ROLE = {
 'ink': ('Tinta', ['Contorno exterior y texto sobre papel', 'Texto sobre papel (14,6:1 sobre paper-5)', 'Sombra profunda de la interfaz']),
 'stone': ('Piedra', None), 'grass': ('Hierba sana', None), 'leaf': ('Copa de árbol sana', None),
 'dirt': ('Tierra y caminos', None), 'sand': ('Arena', None), 'water': ('Agua viva', None),
 'wood': ('Madera', None), 'roofr': ('Teja roja', None), 'roofb': ('Teja azul y mando HUIR', None),
 'wall': ('Adobe y muros', None), 'skin': ('Piel', None),
 'flower': ('Flores: rojo, rosa, oro, crema, lila, lavanda, blanco', None),
 'drygrass': ('Hierba seca y suelo agotado (enfermo)', None), 'deadleaf': ('Follaje muerto (enfermo)', None),
 'ash': ('Ceniza y carbón (enfermo: incendio)', None), 'oil': ('Crudo (enfermo: petróleo)', None),
 'sheen': ('Irisado del crudo: violeta, verde, oro, magenta', None), 'sludge': ('Lodo tóxico (enfermo: agroquímicos)', None),
 'smog': ('Humo y neblina sucia', None), 'rust': ('Óxido y mando LUCHAR', None),
 'plastic': ('Plástico de residuos (enfermo: costa)', None), 'fire': ('Fuego y brasas', None), 'ice': ('Hielo', None),
 'gold': ('Oro, avaricia y mando BOLSA', None),
 'eco': ('Eco: el acento de la purificación y mando ECO', None),
 'ui': ('Pizarra de la interfaz', None), 'paper': ('Papel de diálogo', None), 'hp': ('Barras de vida', None),
}
toks = []
for ramp, vals in R.items():
    name, notes = ROLE[ramp]
    n = len(vals)
    for i, v in enumerate(vals):
        if notes and i < len(notes):
            u = notes[i]
        else:
            pos = 'sombra más honda' if i == 0 else ('luz más alta' if i == n - 1 else ('sombra' if i < n / 2 - 0.5 else ('tono base' if i <= n / 2 else 'luz')))
            u = f'{name}, {pos} ({i + 1}/{n}). Rampa de oscuro a claro: las sombras viran a azul/violeta y las luces a amarillo.'
        toks.append({'name': f'{ramp}-{i + 1}', 'value': v, 'usage': u})
SEM = [
 ('text-on-paper', 'ink-2', 'Texto de diálogo y mensajes sobre paper-5 (14,6:1).'),
 ('text-shadow-paper', 'paper-3', 'Sombra de 1 px del texto sobre papel, abajo a la derecha.'),
 ('text-on-slate', 'ui-7', 'Texto sobre la pizarra ui-2 (13,8:1).'),
 ('text-muted-slate', 'ui-6', 'Cifras y texto secundario sobre ui-2 (12,3:1).'),
 ('text-highlight', 'gold-5', 'Etiqueta PV y nombre de quien tiene el turno, sobre ui-2 (9,3:1).'),
 ('paper', 'paper-5', 'Fondo de caja de diálogo y mensajes.'),
 ('paper-edge', 'wood-2', 'Marco exterior de 2 px de la caja de papel (11,3:1 sobre paper-5).'),
 ('slate', 'ui-2', 'Fondo de placas de combate y filas del grupo.'),
 ('slate-edge', 'ink-1', 'Contorno exterior de 1 px de toda placa.'),
 ('focus-ring', 'ui-7', 'Anillo de selección de 2 px alrededor del mando elegido.'),
 ('hp-high', 'hp-2', 'PV por encima del 50 %.'), ('hp-mid', 'hp-5', 'PV entre 20 y 50 %.'), ('hp-low', 'hp-7', 'PV por debajo del 20 %.'),
 ('energy', 'eco-4', 'Barra de energía eco, bajo la de PV.'),
 ('cmd-fight', 'rust-3', 'Mando LUCHAR (texto blanco 7,3:1).'), ('cmd-eco', 'eco-2', 'Mando ECO (texto blanco 5,9:1).'),
 ('cmd-bag', 'gold-2', 'Mando BOLSA (texto blanco 8,6:1).'), ('cmd-run', 'roofb-3', 'Mando HUIR (texto blanco 7,9:1).'),
 ('status-corrupt', 'rust-2', 'Chapa CORRUPTO, con texto paper-5.'), ('status-purified', 'eco-2', 'Chapa PURIFICADO, con texto eco-5.'),
]
for n, a, u in SEM:
    toks.append({'name': n, 'value': '{%s}' % a, 'usage': u})
data = {
 'name': 'Ecos de la Tierra', 'version': 2,
 'meta': {'source': 'github', 'repo': 'diarpicu2022-commits/ecos-de-la-tierra', 'ref': 'main@f293da0',
          'note': 'Rediseño «Tierra Viva» (2026-10-29): paleta, fuente e interfaz nuevas; personajes y monstruos generados con PixelLab.',
          'synced': '2026-10-29'},
 'color': {'themes': [{'id': 'juego', 'name': 'Juego'}], 'tokens': toks},
 'type': {
  'fonts': [{'family': 'Brote', 'file': 'fonts/Brote.woff2', 'weight': '400', 'style': 'normal'}],
  'families': {'pixel': 'Brote, monospace'},
  'groups': [{'name': 'Brote', 'family': 'pixel', 'styles': [
     {'name': 'texto', 'fontSize': '11px', 'lineHeight': '15px', 'fontWeight': 400, 'sample': '¡Bruma usó Línea Cortafuegos!',
      'usage': 'Todo el texto del juego, 1×. Mayúsculas de 7 px, minúsculas de 5, descendentes de 2. Diálogo a 15 px de interlínea; placas a 13.'},
     {'name': 'titular', 'fontSize': '22px', 'lineHeight': '28px', 'fontWeight': 400, 'sample': 'ECOS DE LA TIERRA',
      'usage': 'Títulos de pantalla y desenlaces, 2×. Solo múltiplos enteros: es una fuente de píxel.'}]}]},
 'spacing': {'tokens': [{'name': f'space-{v}', 'value': f'{v}px', 'usage': u} for v, u in [
   (2, 'Anillo de selección; separación texto-sombra.'), (4, 'Relleno de chapas; hueco entre mandos.'),
   (6, 'Relleno lateral de placas y filas.'), (8, 'Margen de pantalla para placas.'), (12, 'Margen de cajas de diálogo.'),
   (16, 'Rejilla del mundo; relleno de diálogo.'), (24, 'Separación entre bloques de interfaz.')]]},
 'radius': {'tokens': [
   {'name': 'corner-1', 'value': '1px', 'usage': 'Chapas de tipo y estado: esquina recortada de 1 píxel.'},
   {'name': 'corner-2', 'value': '2px', 'usage': 'Filas del grupo, carteles y retratos: escalón 2-1.'},
   {'name': 'corner-3', 'value': '3px', 'usage': 'Cajas de diálogo, placas y mandos: escalón 3-1-1.'}]},
 'border': {'tokens': [
   {'name': 'outline', 'value': '1px', 'usage': 'Contorno exterior de toda pieza en ink-1.'},
   {'name': 'paper-frame', 'value': '2px', 'usage': 'Marco de madera de la caja de papel.'},
   {'name': 'selection', 'value': '2px', 'usage': 'Anillo blanco del mando elegido.'}]},
 'grid': {'tokens': [
   {'name': 'screen-width', 'value': '640px', 'usage': 'Lienzo lógico; escala entera 2× (1280×720) y 3× (1920×1080).'},
   {'name': 'screen-height', 'value': '360px', 'usage': 'Alto del lienzo lógico.'},
   {'name': 'tile', 'value': '16px', 'usage': 'Rejilla del terreno; transiciones en rejilla dual de esquinas.'},
   {'name': 'character', 'value': '48px', 'usage': 'Lienzo de personaje (unos 46 px de alto), 8 direcciones.'},
   {'name': 'monster', 'value': '128px', 'usage': 'Lienzo de monstruo de combate, 1×.'},
   {'name': 'battle-back', 'value': '96px', 'usage': 'Personaje de espaldas en combate: el de 48 px escalado 2×, como los sprites traseros de NB.'}]},
 'duration': {'tokens': [
   {'name': 'dur-walk-frame', 'value': '200ms', 'usage': 'Cada cuadro de la caminata de 4 cuadros.'},
   {'name': 'dur-cursor', 'value': '80ms', 'usage': 'Salto del anillo de selección.'},
   {'name': 'dur-text-char', 'value': '25ms', 'usage': 'Escritura del diálogo, letra a letra; Enter completa.'},
   {'name': 'dur-hp', 'value': '400ms', 'usage': 'La barra de PV baja hacia su valor.'},
   {'name': 'dur-sign', 'value': '2000ms', 'usage': 'Cartel de lugar en pantalla al entrar a una zona.'},
   {'name': 'dur-purify', 'value': '1200ms', 'usage': 'Transformación del monstruo y ola de color que vuelve al mapa.'}]},
}
json.dump(data, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
print(len(toks))
