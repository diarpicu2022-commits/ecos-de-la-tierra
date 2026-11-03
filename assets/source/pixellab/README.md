# Fuentes de PixelLab

Originales de personajes, monstruos y edificios del sistema de diseño «Tierra
Viva» (`docs/ux/sistema-de-diseno/project/README.md` §Activos: «Personajes y
monstruos generados con PixelLab a partir de descripciones de este sistema»).
Antes vivían en `tools/tierra_viva/pl/`. Se movieron aquí en el paso 4b (guía
del equipo §4.2) porque son la fuente de los sprites del juego, no un
prototipo.

La carpeta `assets/source/` lleva `.gdignore`: Godot no importa nada de aquí.
Los sprites que usa el juego se sacan de estas fuentes con un `tools/gen_*.py`
y se escriben en `assets/sprites/`.

**Regla:** no se dibuja a mano encima ni se sustituye un original por otro de
otra fuente. Si hace falta un personaje o edificio nuevo, se genera en
PixelLab con la descripción del sistema (componentes `Cast`, `Overworld`,
`Interiores`, `MonsterRoster`) y se guarda aquí con su nombre.

## Contenido

| Carpeta | Qué es | Tamaño | Lo usa |
|---|---|---|---|
| `ilan/`, `bruma/`, `coral/`, `nix/`, `suri/` | El grupo jugable, 8 direcciones (`south`, `south-east`, `east`, `north-east`, `north`, `north-west`, `west`, `south-west`). Ilan trae además la caminata `walk_<dir>.gif` | lienzo de 48 × 48 | componente `Cast`; R3 (guía §4.6) |
| `npc/<nombre>/` | Vecinos con nombre de Valdehoja (Doña Rosa, la abuela Toña, Don Aurelio, Tito, el padre Julián, Mariela), 8 direcciones | 48 × 48 | `Overworld`, `Interiores`; `tools/tierra_viva/village5.py` |
| `npc_var/<nombre>/` | **Derivados, no originales:** variantes de aldeano (campesina, pescador, petrolero…) con otro tono de ropa y piel, hechas por `tools/tierra_viva/npc_vars.py` desde `npc/` | 48 × 48 | aldeanos sin nombre de las regiones |
| `monsters/` | Los seis monstruos de historia en sus dos formas, `<nombre>_corrupto.png` y `<nombre>_purificado.png`: llama, devorador, golem, espectro, coloso, sombra | 128 × 128 | `MonsterRoster`, `BattleScreen`; `tools/tierra_viva/zones.py`, `combat_mock.py` |
| `mon/` | Salidas originales de PixelLab de los monstruos, con el nombre en inglés que se usó al pedirlas (de aquí salen los de `monsters/`) | 128 × 128 | referencia |
| `m_flame/` | Primeras pruebas de la Llama de la Deforestación (`corrupt.png`, `img0.png`) | 128 × 128 | referencia |
| `bld/` | Edificios únicos de Valdehoja en vista frontal con volumen: alcaldía, posada (cuatro versiones), almacén, molino, taller, cabaña, capilla, escuela, panadería, granero, herrería, torre, casas | variable (p. ej. posada 104 × 120) | `Overworld`; `tools/tierra_viva/village5.py`, `scene2.py` |
| `obj/`, `obj2/` | Árbol sano y árbol quemado (`tree_clean.png`, `burnt_clean.png`, ya sin la base isométrica) y sus salidas originales | 128 × 128 | tarjetas `arbol` y `arbol_quemado` del sistema; `mapscene.py`, `scene2.py` |
| `obj3/` | Casa de adobe de Valdehoja (`house.png`) y su salida original | 102 × 118 | `village.py`, `scene2.py` |
| `obj4/` | Capilla (`chapel.png`) | 128 × 128 | referencia de `bld/capilla_0.png` |

## Paleta

Estos sprites traen colores propios de PixelLab que no son tokens `TV_*`. En
`tools/verify_palette.py`, la orden `image --source pixellab` acepta esa
«tinta de personaje o edificio» **solo** dentro de un sprite que salga de
aquí. Cualquier otra pieza del mundo tiene que ser toda tokens.
