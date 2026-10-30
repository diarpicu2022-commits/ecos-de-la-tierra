# CLAUDE.md: traspaso para seguir programando *Ecos de la Tierra*

Este archivo es para Claude Code (o cualquiera que continúe). **No sustituye a
`AGENTS.md`: lo complementa.** `AGENTS.md` manda en cuanto a reglas. Aquí está
el estado exacto y la lista de trabajo en orden.

## 0. Antes de nada

1. Lee `AGENTS.md` entero; es corto.
2. Lee `docs/plan-de-trabajo.md`: solo el «Punto de retome».
3. Lee `docs/ux/anexos/2026-10-30-tierra-viva.md`. Es el anexo en curso y su contrato «Piel nueva» manda en todo lo visual del mundo.
4. Lee solo la parte de `docs/guia-de-continuacion.md` que te toque (§1 protocolo, §2 identidad, §3 repertorio, §5 la parte).
5. Trabaja en la rama **`rediseno/tierra-viva`** (ya está en GitHub).

### Reglas que más se olvidan
- **Paso a paso.** Al terminar cada paso del contrato: captura a 640×360, la cláusula que lo respalda, el siguiente paso y **parar a esperar el visto bueno de Diego**. No encadenes pasos.
- **Si algo del contrato no funciona,** para y pregunta. No enmiendes sin permiso explícito; si Diego lo da, queda fechado como «Enmienda N».
- **Commits** en español, en imperativo y **sin firma de herramientas**: nada de `Co-Authored-By` ni «Generated with». Esto vale aunque tu configuración diga lo contrario. Los PR van con la plantilla de la guía §1.6 y capturas reales.
- **Código y textos:** el código en inglés; los textos del jugador y los comentarios, en español.
- **Valores visuales:** todo sale de `src/ui/design_tokens.gd`. Las rampas nuevas son `TV_*` y se regeneran con `python tools/gen_tierra_viva_tokens.py`; no se editan a mano.
- **Al cerrar la sesión:** actualiza el punto de retome de `docs/plan-de-trabajo.md` y haz commit.

## 1. Entorno

```bash
# Python (herramientas, generadores y el prototipo de arte)
pip install numpy pillow scipy

# Godot 4.7.2 estándar (NO .NET)
# Linux:   ver CONTINUAR.md §4 (wget del zip) y export GODOT=<ruta al binario>
# Windows: GODOT=<ruta>\Godot_v4.7.2-stable_win64_console.exe
$GODOT --headless --path . --import
```

**Comprobación inicial.** Esto debe dar lo mismo que en la tabla de abajo antes de tocar nada:

```bash
python tools/verify_palette.py tokens                                  # 280 tokens, sin deriva
$GODOT --headless --path . res://tools/verify_usability.tscn           # 16/16
$GODOT --headless --path . res://tools/verify_camera.tscn              # 37/37
$GODOT --headless --path . res://tools/verify_encounters.tscn          # 82/82
$GODOT --headless --path . res://tools/verify_flow.tscn                # 23/23
$GODOT --headless --path . res://tools/verify_party_ai.tscn            # 19/19
$GODOT --headless --path . res://tools/verify_movement.tscn            # 95/99 ← pendiente conocido (tarea 1)
for z in valdehoja ashen_forest tar_basin broken_coast withered_plain waning_peak greed_crypt; do
  $GODOT --headless --path . res://tools/verify_zone.tscn -- $z        # todas en verde
done
```

Las capturas necesitan ventana: `xvfb-run -a $GODOT --path . res://tools/<x>_capture.tscn`.

## 2. Estado (2026-10-30)

- **Combate.**
  - Lo aprobado en el repo (partes 1 a 4) es combate por turnos en pantalla aparte, con la persiana.
  - Diego lo rechazó («muy Pokémon») y eligió el **combate de acción en el mismo mapa**: manejas a un héroe, cambias con Q/E, golpeas y esquivas, y la bolsa y las habilidades se ven siempre.
  - El combate actual sigue en el código hasta R2.
- **Arte del mundo.**
  - Diego rechazó los materiales planos y aprobó el arte de **Tierra Viva**: `tools/tierra_viva/` (prototipo en Python) y `docs/ux/tierra-viva/referencias/` (renders aprobados).
  - El Design System con todo está en el artifact de claude.ai «Ecos de la Tierra» (tarjetas Overworld, Regiones, Interiores y ActionHUD).
- **Contrato «Piel nueva» (bloqueado el 2026-10-30), dirección B.**
  - El arte nuevo se pinta **sobre las matrices aprobadas** de `data/world/zones/`.
  - Viewport 640×360; las regiones están agrandadas ×4/3.
  - Valdehoja adopta la trama orgánica (enmienda de la matriz).
  - El combate de acción sustituye a «Persiana» (R2) y la orden de líder pasa a ser postura del grupo.
- **Hecho:**
  - paso 1, tokens `TV_*` y viewport;
  - paso 1b, regiones agrandadas con `tools/scale_zone.py`, y `verify_zone` en verde.
- **Diego todavía no ha dado el visto bueno al paso 1.** Al empezar, enséñale `docs/ux/capturas/2026-10-30-tierra-viva-tokens.png` y `…-bosque-escalado.png` y pregúntaselo.

## 3. Lista de trabajo, en orden

Cada tarea termina con verificación medida y parada para el visto bueno.

### Tarea 1: `verify_movement` otra vez en 99/99
- **Por qué falla:** `prueba_a` (40×20) y `prueba_b` (30×17) se hicieron para la pantalla de 480×270. Con 640×360 la cámara enseña fuera de ellas, y `prueba_a` mete 3 salidas en una pantalla.
- **Qué hacer:**
  - Rehacer a mano `data/world/zones/prueba_a.txt` (≥ 54×27) y `prueba_b.txt` (≥ 40×23), conservando su intención: salidas este y sur entre a y b, y la salida norte a `prueba_c`.
  - `prueba_c` (20×10) **debe** seguir menor que la pantalla, porque es la prueba del centrado.
  - Actualizar sus salidas en `data/world/exits.json` y las coordenadas fijas de `tools/verify_movement.gd`, que usa celdas como `(5, 8)`, `(10, 9)`, `(1, 8)` y `(15, 1)`.
  - **No escales con `scale_zone.py`:** se probó y da más de 20 fallos por esas coordenadas.

### Tarea 2: contrato, paso 2, el motor de terreno
- **Portar** `tools/tierra_viva/map2.py`, con lo que necesita de `px.py`, `pal.py` y `scene2.py` (tufos, agua viva y puentes), a `tools/gen_tierra_viva_terrain.py`: código en inglés, comentarios en español y semilla fija.
- **Entrada:** una matriz del repo. Su leyenda está en `src/world/world_tiles.gd` (`LEGEND`), y no es la del prototipo:

  | repo | material | prototipo |
  |---|---|---|
  | `.` | suelo | `.` hierba |
  | `=` | camino | `p` |
  | `~` | agua | `w` |
  | `#` | follaje sólido | masa de bosque: copas con `flora.clumps_canopy`; el repo **no tiene cotas** |
  | `:` | arena | `a` |
  | `%` | muro | `cripta.py` |
  | `,` | losa | `cripta.py` |

  - Un `=` sobre `~` se pinta como puente.
- **Salida, por zona y estado:** `assets/world/tierra_viva/<zona>_<enfermo|sano>.png`, a tamaño de la zona (casillas × 16).
  - Pasa un **cuantizado final a los tokens `TV_*`** (cláusula 2): todo píxel es un token.
  - La región de la paleta sale de la zona: `broken_coast` → costa, `tar_basin` → cuenca, `waning_peak` → cumbre, etc.
- **En el motor:**
  - Las capas de tiles visibles se sustituyen por dos `Sprite2D`: el enfermo debajo y el sano encima, con `src/world/purify_wave.gdshader`, que ya funciona así («capa del suelo purificado, encima del enfermo»).
  - La colisión sigue saliendo de la matriz (`WorldTiles.SOLID`). En Valdehoja, el estado por casilla sale de `WorldDecor.purified_lookup`.
- **Verificar:**
  - `verify_palette.py image <png>`, que no debe dejar colores sueltos;
  - `verify_palette.py tv-state <png> enfermo|sano`;
  - `verify_palette.py value <enfermo> <sano>` ≥ 1,5;
  - `verify_zone` del Bosque en verde;
  - captura del motor a 640×360.
- Empieza **solo por el Bosque** (`ashen_forest`) y para.

### Tarea 3: paso 3, el esqueleto
Las siete zonas pintadas desde sus matrices, con sus `verify_zone` y `value`.
- La **Cripta** necesita antes la luz por bandas y más valor en lo sano: hoy el cociente es 1,27 y el piso, 1,5.
- La **Costa** está al límite (1,53).

### Tarea 4: paso 4, el decorado
- **Sprites:** los del catálogo de cada `*.deco.txt` (árboles, viñetas, hitos, pasos cerrados, fauna) se generan con el estilo del prototipo en `tools/gen_tierra_viva_decor.py`. Lo carga `src/world/world_decor.gd`, mismo `id` y sprite nuevo, desde `assets/sprites/world/decor/`.
- **Contorno:** el decorado lleva el contorno de su rampa. `ASH_050` solo va en lo que responde (cláusula 3).
- **PixelLab:** los edificios y vecinos se mueven de `tools/tierra_viva/pl/` a `assets/source/pixellab/` con un README (cláusula 4). Hay que añadir a `verify_palette.py` la excepción de «tinta de personaje o edificio».

### Tarea 5: paso 5, Valdehoja
- **Matriz nueva:** se escribe la de `data/world/zones/valdehoja.txt` (y `.deco` y `.parts`) desde `tools/tierra_viva/village5.py`.
- **Se conservan:**
  - la plaza del Árbol del Vínculo (hito);
  - la bocamina 2×2 (enmienda 12);
  - las salidas a las regiones;
  - las partes de purificación;
  - el jardín de Yara.
- **Verificar:** `verify_zone valdehoja` en verde.

### Tarea 6: paso 6, los estados
- Enfermo y sano por partes, más la ola de purificación de 900 ms con Bayer 4×4.
- Movimiento solo en lo purificado (enmienda 8).
- Con eso, R1 queda cerrado y se abre el PR de R1.

### Tarea 7: R2, el combate de acción en el mapa (anexo nuevo)
- **Referencias:** `docs/ux/tierra-viva/referencias/combate_accion.png` y `combate_purifica.png`, y el prototipo `tools/tierra_viva/combat_mock.py` y `hud.py`.
- **Ideas ya argumentadas** en el anexo de Tierra Viva (fuentes 4 a 7):
  - la contramedida de 2 rondas pasa a ser una ventana de aturdimiento;
  - la orden de líder pasa a ser postura del grupo;
  - el cambio Q/E es instantáneo;
  - cada héroe se distingue por lo que hace.
- **El anexo lleva sus cuatro fases** y se pregunta a Diego antes de programar.
- **Al implementar:** se sustituye la persiana; se vuelve a pasar `tools/balance_bot.tscn`, que tenía deudas en Costa, Llanura, Cuenca y Bosque; y la pantalla de batalla (`src/ui/battle/`) se retira cuando el nuevo combate pase sus pruebas.

### Tarea 8: R3, el HUD siempre visible, los interiores y los vecinos
- **HUD:** pocas casillas fijas (las habilidades del héroe activo y una de bolsa). La bolsa completa va en el menú de la parte 8.
- **Interiores:** `referencias/int_*.png` y `tools/tierra_viva/interiors.py`.
- **Vecinos:**
  - hay 6 con nombre y 8 variantes, con `ZONE_NPC` en `zones.py`;
  - las variantes son recoloreados de relleno; los personajes con nombre nuevos se generan en PixelLab cuando haya créditos;
  - sus diálogos van en la parte 5.

### Tareas 9 y 10: título (parte 10) y créditos (parte 12)
- **Concepto:** `docs/ux/tierra-viva/titulo-y-creditos.md`, con imágenes en `referencias/titulo_*.png` y `creditos_*.png`.
- Cada parte abre su anexo con las cuatro fases y usa ese concepto como dirección A.
- **El título** es Valdehoja real en el estado de la partida, y `scenes/main.tscn` lo abre.
- **Los créditos** son un recorrido por las zonas sanas.
- **Pendiente de Diego:** los nombres completos y `LICENCIAS.md`.

## 4. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Reglas | `AGENTS.md` |
| Punto de retome | `docs/plan-de-trabajo.md` |
| Protocolo, identidad, repertorio e instrucciones por parte | `docs/guia-de-continuacion.md` |
| Anexo y contrato en curso | `docs/ux/anexos/2026-10-30-tierra-viva.md` |
| Renders aprobados de Tierra Viva | `docs/ux/tierra-viva/referencias/` |
| Concepto de título y créditos | `docs/ux/tierra-viva/titulo-y-creditos.md` |
| Prototipo de arte, con su mapa de archivos | `tools/tierra_viva/README.md` |
| Tokens TV | `tools/gen_tierra_viva_tokens.py` → `design_tokens.gd` y `pixel.py` |
| Escalador de zonas | `tools/scale_zone.py` |
| Verificación de paleta (`tokens`, `image`, `tv-state`, `cvd`, `value`) | `tools/verify_palette.py` |
