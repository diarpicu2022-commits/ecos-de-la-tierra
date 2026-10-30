# Prototipo Tierra Viva

El generador de arte con el que se hizo el rediseño «Tierra Viva» (del
2026-10-28 al 2026-10-30) y que Diego aprobó al verlo. **Es la referencia del
contrato «Piel nueva»**
(`docs/ux/anexos/2026-10-30-tierra-viva.md`). Todavía no está integrado en el
juego. Portarlo es el paso 2 del contrato y está explicado en `CLAUDE.md`.

Python 3 con `numpy`, `pillow` y `scipy`. Se ejecuta **desde esta carpeta**,
porque las rutas son relativas (`pl/`, `final/`, `final7/`, `out2/`):

```bash
cd tools/tierra_viva
pip install numpy pillow scipy
python zones.py                 # costa, cuenca, llanura y cumbre, enfermo y sano → out2/z_*.png
python zones.py costa           # solo una
python cripta.py                # Cripta de la Avaricia → out2/z_cripta_*.png
python interiors.py             # posada, tienda y casa → out2/int_*.png
python npc_vars.py              # variantes de vecinos → pl/npc_var/ y out2/npc_vars.png
python title_credits.py         # concepto del título y de los créditos → out2/titulo_*, creditos_*
python village5.py              # Valdehoja orgánica entera (tarda)
```

`out2/` no se versiona; lo aprobado está copiado en
`docs/ux/tierra-viva/referencias/`. El archivo `.gdignore` impide que Godot
importe esta carpeta.

## Mapa de archivos

| Archivo | Qué hace |
|---|---|
| `pal.py` | Paleta: rampas `R` (hex) y `P` (RGBA). Es la que pasó a `TV_*` en `design_tokens.gd` (`tools/gen_tierra_viva_tokens.py`) |
| `px.py` | Primitivas: `new`, `col`, `blit`, `outline`, `shade`, `ellipse`, `save` |
| `map2.py` | **Motor de terreno.** De la matriz de casillas a máscaras suavizadas por material (`rounded`), agua con profundidad, orillas y playa, cotas de borde natural (`organic_top`, `paint_level`), caminos, plazas ovaladas y cultivos. `palette(state, region)` da las variantes de cada región |
| `maps2.py` | `Builder`: escribe matrices (`run`, `high`) con los caracteres `. p w B S t f c u a` |
| `scene2.py` | La escena: tufos, agua viva, puentes, objetos ordenados por la base con sombra, calcos de suelo; validador de árboles (`tree_ok`, `solve_trees`), versión enferma (`ashen`, `char`), edificios de PixelLab (`BLD_PL`, `load_overrides`) |
| `flora.py`, `burnt.py` | Copas por racimos, arbustos, rocas; el árbol quemado sale del mismo tronco sano |
| `roofix.py` | Repara tejados cortados de los sprites de PixelLab |
| `buildings.py` | Edificios y props procedurales (farol, fuente, pozo, banco, puesto) |
| `village5.py` | **Valdehoja orgánica**: calles en curva (`srow`), casas a distinta altura, plazas ovaladas, patios, vecinos. Es la matriz que enmienda la de `data/world/zones/valdehoja.txt` (cláusula 6) |
| `zones.py` | Costa, Cuenca, Llanura y Cumbre: matrices, props propios (palma, mangle, palafito, balancín, tubería, frailejón, espantapájaros) y vecinos por zona (`ZONE_NPC`) |
| `dress.py` | Vestido por racimos sin pisar caminos, agua ni objetos; árboles en los bordes |
| `cripta.py` | La sala de la Cripta, con su luz. **Pendiente:** cuantizar la luz en bandas y subir el valor de lo sano (cociente 1,27 < 1,5) |
| `interiors.py` | Interiores: sala con pared de frente y suelo en planta, muebles |
| `npc_vars.py` | Variantes de vecinos por recoloreado (ropa y piel), 8 direcciones |
| `title_credits.py` | Concepto del título (Valdehoja en el estado de la partida) y de los créditos (recorrido por las zonas sanas) |
| `hud.py`, `combat_mock.py` | Concepto del combate de acción en el mapa y su HUD (base de R2) |
| `font.py` | Fuente «Brote» (BMFont, TTF y render en PIL) |
| `unpack.py`, `unpack_npc.py` | Importan los lotes descargados de PixelLab |
| `maps.py`, `village.py`, `village_views.py`, `terrain.py`, `mapscene.py`, `battle.py`, `ds_*.py` | Versiones anteriores y la construcción del Design System; se conservan como historia |

## Recursos

- `pl/`: sprites de PixelLab.
  - Edificios (`bld/`), Ilan y el grupo (`ilan/`, `suri/`, `nix/`, `bruma/`, `coral/`), vecinos (`npc/`, 8 direcciones), variantes (`npc_var/`), monstruos y objetos.
  - Al portar se mueven a `assets/source/pixellab/` (cláusula 4).
- `final/`: personajes y monstruos recortados, marcos de interfaz, fuente Brote y pantallas de combate.
- `final7/`: Valdehoja entera sana y enferma, más cinco vistas. El título las usa.
