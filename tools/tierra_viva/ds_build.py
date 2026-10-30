"""Escribe los componentes del design system «Tierra Viva» (preview.html + README.md)."""
import json, os, sys

ROOT = sys.argv[1]
B = json.load(open(sys.argv[2]))   # nombre lógico -> /_blob/<id>
C = os.path.join(ROOT, 'components')


def comp(name, marker, body, readme, script=''):
    d = os.path.join(C, name)
    os.makedirs(d, exist_ok=True)
    html = (f'{marker}\n<!doctype html>\n<html><head><meta charset="utf-8"><title>{name}</title></head>\n'
            f'<body>\n{body}\n' + (f'<script>{script}</script>\n' if script else '') + '</body></html>\n')
    open(os.path.join(d, 'preview.html'), 'w').write(html)
    if readme is not None:
        open(os.path.join(d, 'README.md'), 'w').write(f'# {name}\n\n' + readme)


def bar(ratio, kind=''):
    return f'<div class="bar {kind}"><s></s><i style="width:calc(({ratio}) * (100% - 2px))"></i></div>'


def hpcls(r):
    return '' if r > 0.5 else ('mid' if r > 0.2 else 'low')


# --- TypeBadge -------------------------------------------------------------
badges = ''.join(f'<span class="badge b-{c}">{t}</span>' for t, c in [
    ('FUEGO', 'fuego'), ('PETRÓLEO', 'petroleo'), ('PLÁSTICO', 'plastico'), ('MONOCULTIVO', 'monocultivo'),
    ('DESHIELO', 'deshielo'), ('AVARICIA', 'avaricia'), ('ECO', 'eco')])
comp('TypeBadge', '<!-- @dsCard group="Combate" height=90 subtitle="Tipo de daño y estado del monstruo" -->',
     f'<div class="tv tv-wrap" style="background:var(--ui-2)"><div class="tv-col"><div>{badges}</div>'
     f'<div><span class="badge b-corrupto">CORRUPTO</span><span class="badge b-purificado">PURIFICADO</span></div></div></div>',
     """Chapa de 11 px de alto con el tipo de daño o el estado del monstruo.

## Qué aporta quien la usa
- El texto en MAYÚSCULAS y su clase: `b-fuego`, `b-petroleo`, `b-plastico`, `b-monocultivo`, `b-deshielo`, `b-avaricia`, `b-eco`, `b-corrupto`, `b-purificado`.

## Reglas
- Esquina `corner-1` y contorno `ink-1`. Relleno de 3 px a cada lado.
- Texto blanco sobre el color del tipo (todos ≥ 5,4:1). CORRUPTO: `paper-5` sobre `status-corrupt`; PURIFICADO: `eco-5` sobre `status-purified`.
- Va en la placa del enemigo y en los menús de habilidades; nunca sola en el mapa.
""")

# --- EnemyPlate ------------------------------------------------------------
def enemy(name, typ, cls, hp, mx, pur):
    r = hp / mx
    st = '<span class="badge b-purificado">PURIFICADO</span>' if pur else '<span class="badge b-corrupto">CORRUPTO</span>'
    return (f'<div class="tv-frame f-plate enemy"><div class="t-slate">{name}</div>'
            f'<div class="row"><span class="badge b-{cls}">{typ}</span>{st}</div>'
            f'<div class="pv"><span class="t-hi">PV</span>{bar(r, hpcls(r))}<span class="t-muted">{hp}/{mx}</span></div></div>')

comp('EnemyPlate', '<!-- @dsCard group="Combate" height=260 subtitle="Arriba a la izquierda en combate: nombre, tipo, estado y PV" -->',
     '<div class="tv tv-wrap">' + enemy('Llama de la Deforestación', 'FUEGO', 'fuego', 152, 180, False)
     + enemy('Gólem de Plástico', 'PLÁSTICO', 'plastico', 61, 240, False)
     + enemy('Sombra de la Avaricia', 'AVARICIA', 'avaricia', 38, 420, False)
     + enemy('Guardián del Bosque', 'FUEGO', 'fuego', 180, 180, True) + '</div>',
     """Placa del monstruo enemigo, en la esquina superior izquierda del combate (10, 10).

## Qué aporta quien la usa
- Nombre, tipo de daño, si está purificado y sus PV.

## Anatomía (184 px de ancho)
- Marco `f-plate`: pizarra `slate` con contorno `slate-edge`, esquina `corner-3`.
- Nombre en `text-on-slate` con sombra `ui-1`.
- Fila de chapas: tipo (`TypeBadge`) y estado CORRUPTO / PURIFICADO.
- «PV» en `text-highlight`, barra de 5 px y la cifra `actual/máx` en `text-muted-slate`. La barra pasa de `hp-high` a `hp-mid` (≤ 50 %) y `hp-low` (≤ 20 %).

## No
- No se oculta la cifra: la barra sola obliga a estimar.
""")

# --- PartyRow --------------------------------------------------------------
def prow(name, hp, mx, en, emax, active=False, status=None):
    r = hp / mx
    st = f' <span class="badge b-corrupto">{status}</span>' if status else ''
    nm = f'<span class="{"t-hi" if active else "t-slate"}">{name}{st}</span>'
    return (f'<div class="tv-frame {"f-active" if active else "f-row"} prow"><div class="top">{nm}<span class="t-muted">{hp}/{mx}</span></div>'
            f'{bar(r, hpcls(r))}{bar(en / emax, "en")}</div>')

comp('PartyRow', '<!-- @dsCard group="Combate" height=230 subtitle="Una fila por miembro del grupo: turno, estado, PV y energía" -->',
     '<div class="tv tv-wrap"><div class="tv-col">' + prow('Ilan', 116, 120, 30, 30, True)
     + prow('Bruma', 52, 110, 12, 34, False, 'QUEM.') + prow('Coral', 18, 100, 38, 38)
     + prow('Nix', 0, 115, 0, 30, False, 'FUERA') + '</div></div>',
     """Fila de un miembro del grupo, apiladas abajo a la derecha del combate (456, 196), 27 px entre filas.

## Qué aporta quien la usa
- Nombre, PV, energía, estado alterado y si tiene el turno.

## Anatomía (176 px)
- Marco `f-row` (pizarra); quien tiene el turno usa `f-active`, con borde `gold-5` y el nombre en `text-highlight`.
- Estado en chapa corta: «QUEM.», «VEN.», «CEG.», «FUERA».
- Barra de PV de 5 px y, debajo, barra de energía de 4 px en `energy`.
""")

# --- CommandMenu -----------------------------------------------------------
def cmd(label, cls, sel=False):
    inner = f'<div class="tv-frame f-{cls} cmd">{label}</div>'
    return f'<div class="tv-frame f-selected cmd-sel">{inner}</div>' if sel else inner

comp('CommandMenu', '<!-- @dsCard group="Combate" height=170 subtitle="Los cuatro mandos de 2×2; ↑ ↓ ← → mueven el anillo" -->',
     '<div class="tv tv-wrap" style="background:var(--ui-2)"><div class="cmds" id="m">'
     + cmd('LUCHAR', 'luchar') + cmd('ECO', 'eco', True) + cmd('BOLSA', 'bolsa') + cmd('HUIR', 'huir') + '</div></div>',
     """Los cuatro mandos del turno, en rejilla de 2×2 abajo a la derecha (432, 284), 100×30 cada uno.

## Qué aporta quien lo usa
- Cuál está elegido. Los mandos y sus colores son fijos: LUCHAR `cmd-fight`, ECO `cmd-eco`, BOLSA `cmd-bag`, HUIR `cmd-run`.

## Reglas
- Botón con esquina `corner-3`, luz arriba y canto oscuro abajo: se lee como una tecla.
- El elegido lleva anillo blanco de 2 px (`focus-ring`). Se mueve con flechas o WASD; Enter elige; Escape vuelve al mando anterior.
- Texto blanco con sombra `ink-1`, siempre ≥ 5,9:1.
""",
     script="""(function(){var m=document.getElementById('m');var labels=[['LUCHAR','luchar'],['ECO','eco'],['BOLSA','bolsa'],['HUIR','huir']];var f=1;
function draw(){m.innerHTML=labels.map(function(l,i){var b='<div class="tv-frame f-'+l[1]+' cmd">'+l[0]+'</div>';return i===f?'<div class="tv-frame f-selected cmd-sel">'+b+'</div>':b;}).join('');}
document.addEventListener('keydown',function(e){var k=e.key;if(k==='ArrowRight'||k==='ArrowLeft'){f^=1;}else if(k==='ArrowDown'||k==='ArrowUp'){f^=2;}else return;e.preventDefault();draw();});})();""")

# --- DialogBox -------------------------------------------------------------
comp('DialogBox', '<!-- @dsCard group="Mundo" height=230 width=1300 subtitle="Papel con marco de madera, chapa con el nombre y retrato" -->',
     f'''<div class="tv" style="padding:24px 12px 12px">
<div class="tv-frame f-textbox dialog"><span class="leaf"></span>
<div class="tv-frame f-portrait" style="padding:0"><img src="{B['portrait_coral']}" width="40" height="44" alt="Coral"></div>
<div class="lines t-paper" id="t"></div><span class="more">▼</span>
<div class="tv-frame f-tag tagname" style="border-width:8px;padding:0 2px;height:1px;line-height:1px"><span style="position:relative;top:-6px">Coral</span></div></div></div>''',
     """Caja de diálogo y de mensajes, abajo en pantalla (12, 276), 616×76.

## Qué aporta quien la usa
- Las líneas de texto (dos por caja, 15 px de interlínea), quién habla y, si lo hay, su retrato de 40×44.

## Anatomía
- Marco `f-textbox`: papel `paper`, marco de madera de 2 px `paper-edge`, esquina `corner-3`, hojita `eco` en la esquina.
- Chapa con el nombre (`f-tag`, verde `eco`) asomando sobre el borde superior.
- Retrato en su propio marco `f-portrait`.
- Texto `text-on-paper` con sombra `text-shadow-paper`. `▼` en `rust-3` cuando hay más.

## Comportamiento
- El texto se escribe letra a letra (`dur-text-char`); Enter lo completa y, con la línea entera, avanza.
""",
     script="""(function(){var L=['¡Ilan! El arroyo ya corre limpio.','Mira, volvieron las libélulas.'],t=document.getElementById('t');var all=L.join('\\n');
if(matchMedia('(prefers-reduced-motion: reduce)').matches){t.innerHTML=L.join('<br>');return;}var i=0;(function tick(){t.innerHTML=all.slice(0,i).replace('\\n','<br>');if(i++<all.length)setTimeout(tick,25);else setTimeout(function(){i=0;tick();},2500);})();})();""")

# --- LocationSign ----------------------------------------------------------
comp('LocationSign', '<!-- @dsCard group="Mundo" height=130 subtitle="Cartel de madera al entrar a una zona" -->',
     '<div class="tv tv-wrap" style="background:var(--grass-5)">'
     '<div class="tv-frame f-sign sign"><div>Valdehoja</div><div class="sub">Pueblo de las terrazas</div></div>'
     '<div class="tv-frame f-sign sign"><div>Bosque de las Cenizas</div><div class="sub">Enfermo</div></div>'
     '<div class="tv-frame f-sign sign"><div>Bosque de las Cenizas</div><div class="sub">Purificado</div></div></div>',
     """Cartel de lugar: tabla de madera arriba a la izquierda (12, 12) al entrar a una zona.

## Qué aporta quien lo usa
- Nombre de la zona y, debajo, su estado o su apodo.

## Reglas
- Marco `f-sign`: madera `wood` con clavos en las esquinas, texto `paper-5` con sombra `wood-2`.
- Entra, se queda `dur-sign` y se va. Solo para el nombre del lugar: no lleva avisos ni tutoriales.
""")

# --- Pantallas y hojas -----------------------------------------------------
def page(name, marker, body, readme):
    comp(name, marker, body, readme)

page('BattleScreen', '<!-- @dsCard group="Pantallas" height=1490 width=1300 page subtitle="Combate a 640×360: plataformas, grupo de espaldas, placas y mandos" -->',
     f'''<div class="tv tv-wrap"><img class="screen" src="{B['screen_combate_enfermo']}" alt="Combate enfermo">
<img class="screen" src="{B['screen_combate_purificado']}" alt="Combate purificado"></div>''',
     """Pantalla de combate completa, a la manera de Pokémon Negro/Blanco.

## Composición (640×360)
- Fondo por región y estado: cielo en bandas tramadas, horizonte en capas y suelo. Enfermo (incendio): cielo de humo naranja, troncos quemados, ceniza con brasas. Purificado: cielo azul, bosque y pradera con flores.
- Plataforma del monstruo a la derecha (470, 176) y del grupo a la izquierda (160, 268), elipses con borde iluminado.
- Monstruo a 1× sobre su plataforma; el grupo de espaldas a 2×, hasta tres visibles, el más cercano delante.
- `EnemyPlate` arriba a la izquierda, `PartyRow` abajo a la derecha, `DialogBox` (versión mensaje, 420×72) y `CommandMenu` en la banda inferior.
""")

page('Overworld', '<!-- @dsCard group="Pantallas" height=2220 width=1300 page subtitle="Mapa a 640×360: el bosque enfermo y purificado, y Valdehoja con diálogo" -->',
     f'''<div class="tv tv-wrap"><img class="screen" src="{B['screen_mapa_enfermo']}" alt="Mapa enfermo">
<img class="screen" src="{B['screen_mapa_purificado']}" alt="Mapa purificado">
<img class="screen" src="{B['screen_valdehoja_dialogo']}" alt="Valdehoja con diálogo"></div>''',
     """Exploración cenital, a la manera de Minish Cap y Pokémon.

## Composición
- Terreno en losetas de 16 px con transiciones redondeadas; hierba alta en parches de losetas completas.
- Objetos ordenados por profundidad (por su base), cada uno con sombra en el suelo hecha con tonos de la propia rampa.
- Ilan a 48 px; los compañeros pueden aparecer en el mapa para hablar.
- `LocationSign` al entrar y `DialogBox` con retrato al hablar.
- Enfermo y purificado son el mismo mapa: cambian paleta y objetos (árbol quemado → árbol con copa, agua turbia → agua azul, hierba seca → hierba con flores).
""")

roster = ''.join(f'''<div class="sprite-card dark"><img src="{B['m_'+k+'_corrupto']}" width="128" height="128" alt="{n} corrupto"><div class="cap t-slate">{n}</div></div>
<div class="sprite-card dark" style="background:var(--grass-5)"><img src="{B['m_'+k+'_purificado']}" width="128" height="128" alt="{p} purificado"><div class="cap t-paper">{p}</div></div>'''
                 for k, n, p in [('llama', 'Llama de la Deforestación', 'Guardián del Bosque'),
                                 ('devorador', 'Devorador de Petróleo', 'Serpiente del Arroyo'),
                                 ('golem', 'Gólem de Plástico', 'Gólem de Conchas'),
                                 ('espectro', 'Espectro del Monocultivo', 'Espíritu de la Cosecha'),
                                 ('coloso', 'Coloso del Deshielo', 'Guardián de la Cumbre'),
                                 ('sombra', 'Sombra de la Avaricia', 'Guardián del Equilibrio')])
page('MonsterRoster', '<!-- @dsCard group="Personajes" height=900 width=1300 page subtitle="Los seis monstruos: forma corrupta y forma purificada" -->',
     f'<div class="tv tv-wrap"><div class="sprites" style="max-width:600px">{roster}</div></div>',
     """Los seis monstruos de combate, 128 px, cada uno con sus dos formas.

## Reglas
- La forma corrupta lleva el material del daño (fuego y hacha, crudo irisado, plástico, maíz marchito y niebla tóxica, hielo con hollín, oro y humo) y gesto agresivo.
- La purificada conserva algo de la silueta y cambia a material sano (madera con hojas, agua, arena y conchas, cultivos variados, nieve limpia, plumas de luz) y gesto amable.
- Miran abajo a la izquierda, hacia el grupo. Se colocan sobre su plataforma alineando la base de los pies.
""")

cast = ''.join(f'''<div class="sprite-card"><img src="{B['c_'+k+'_south']}" width="48" height="48" alt="{n}"><img src="{B['c_'+k+'_east']}" width="48" height="48" alt="{n} de lado"><img src="{B['c_'+k+'_north']}" width="48" height="48" alt="{n} de espaldas"><div class="cap">{n}</div></div>'''
               for k, n in [('ilan', 'Ilan'), ('bruma', 'Bruma'), ('coral', 'Coral'), ('nix', 'Nix'), ('suri', 'Suri')] if 'c_' + k + '_south' in B)
walk = ''.join(f'<img src="{B["walk_"+d]}" width="80" height="80" alt="Ilan camina {d}">' for d in ['south', 'east', 'north', 'west'] if 'walk_' + d in B)
page('Cast', '<!-- @dsCard group="Personajes" height=420 width=1300 page subtitle="El grupo en 48 px y la caminata de Ilan" -->',
     f'<div class="tv tv-wrap"><div class="sprites">{cast}</div><div class="sprite-card">{walk}<div class="cap">Ilan camina (4 cuadros, 200 ms)</div></div></div>',
     """El grupo jugable en el mapa: lienzo de 48 px, vista cenital baja, contorno selectivo, 8 direcciones.

## Personajes
- **Ilan**: ruana ocre con franja roja y crema, pañoleta turquesa, colgante de hoja (el Fragmento del Vínculo).
- **Bruma**: guardabosques, chaqueta oliva, sombrero, pañoleta naranja.
- **Coral**: hija de pescadores, chaleco amarillo, camiseta a rayas.
- **Nix**: ingeniero, overol gris, gafas de latón, mochila de latas.
- **Suri**: agricultora, sombrero de paja, aguayo morado.

## Reglas
- Cada personaje tiene un color propio que no repite otro: ocre (Ilan), oliva (Bruma), amarillo (Coral), gris y latón (Nix), morado (Suri).
- En combate se usan de espaldas (norte-este) al doble de escala.
""")

page('Terrain', '<!-- @dsCard group="Mundo" height=520 width=1300 page subtitle="Losetas de 16 px, sanas y enfermas, y sus transiciones" -->',
     f'<div class="tv tv-wrap"><img src="{B["terrain_sheet"]}" alt="Losetas de terreno" style="width:{B.get("terrain_w", 600)}px"></div>',
     """Terreno en losetas de 16 px, hecho a mano en código con la paleta del sistema.

## Materiales
- Sano: hierba (`grass`, 4 variantes), hierba alta, tierra de camino (`dirt`), arena, agua viva (`water`).
- Enfermo (incendio): hierba seca (`drygrass`), camino de ceniza (`ash`), agua turbia.
- Transiciones en rejilla dual: borde oscuro `grass-3` en la hierba, sombra `dirt-3` bajo el borde, talud y espuma en el agua.
""")
print('ok')
