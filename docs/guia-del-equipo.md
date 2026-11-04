# Guía del equipo: de aquí hasta el juego terminado

Para **Diego y su compañero**. **Desde el 2026-11-02 sigue el compañero con todo lo que falta** (decisión de Diego). Se empieza por el inventario de §3.1 y por §4.0, donde está el punto exacto en que quedó el combate. Del decorado (§4.2) ya están las seis regiones, y Valdehoja tiene suelo por partes y decorado nuevos sobre su matriz de 60 × 34 (§4.3, 2026-11-03); su matriz orgánica queda para después de la presentación. Dice cómo preparar el equipo, cómo se trabaja,
en qué punto exacto está el juego y, en orden, **todo lo que falta** hasta
entregarlo. Cada tarea trae qué hacer, dónde, cómo se comprueba y cuándo está
hecha.

> **Regla número uno, para los dos: todo lo visual se hace con el sistema de
> diseño «Tierra Viva».** Está en `docs/ux/sistema-de-diseno/`. Abre
> `index.html` en el navegador y lee `project/README.md` antes de tocar nada
> que se vea. Cada componente tiene su README en `project/components/`. Si
> algo que vas a hacer no está en el sistema, o lo contradice, **se para y se
> le pregunta a Diego**: no se inventa.
>
> **Esto incluye a los personajes** (decisión de Diego, 2026-11-01): Ilan, el
> grupo, los vecinos y los monstruos se hacen con el diseño del sistema
> (componentes `Cast`, `MonsterRoster` y `Overworld`; originales de PixelLab
> en `assets/source/pixellab/`). No se dibuja ningún personaje nuevo con el
> estilo viejo de `tools/gen_world_sprites.py` ni de `gen_world_decor.py`.

Última actualización: 2026-11-01.

---

## 1. Preparar el equipo (una vez)

1. **Git** y acceso al repo `diarpicu2022-commits/ecos-de-la-tierra`.
2. **Godot 4.7.2 estándar**, no la .NET: <https://godotengine.org/download/archive/4.7.2-stable/>.
   En Windows, descomprime el zip; usa `Godot_v4.7.2-stable_win64.exe` para el
   editor y `Godot_v4.7.2-stable_win64_console.exe` para las pruebas, porque
   esta escribe la salida en la terminal.
3. **Python 3.11 o superior** con `pip install numpy pillow scipy`. Lo usan
   los generadores de arte y las comprobaciones.
4. Clona y cámbiate a la rama de trabajo:

   ```bash
   git clone https://github.com/diarpicu2022-commits/ecos-de-la-tierra.git
   cd ecos-de-la-tierra
   git checkout rediseno/terreno
   ```

5. Primera importación (crea `.godot/`, que no se versiona):

   ```bash
   GODOT="<ruta>/Godot_v4.7.2-stable_win64_console.exe"   # Windows (Git Bash)
   "$GODOT" --headless --path . --import
   ```

6. Abre el proyecto en el editor (*Importar* → `project.godot`) y pulsa
   **F5**: el juego arranca en Valdehoja (`scenes/game.tscn`). La demo de
   combates sueltos está en `scenes/main.tscn` (ábrela y pulsa F6).

### Trucos que ahorran horas

- Si Godot dice «No loader found» de una imagen nueva, la importación se
  cortó antes de llegar a ella: repite `--import` hasta que exista su
  `.import`.

- **Las pruebas que hacen capturas necesitan ventana**: sin `--headless`, o
  se quedan colgadas esperando el dibujo. En Linux, `xvfb-run -a "$GODOT" ...`.
- En Windows, a los scripts de Python que imprimen tildes o `≥` ponles
  `PYTHONIOENCODING=utf-8` delante; si no, la consola cp1252 los corta.
- Después de crear o cambiar un PNG: `"$GODOT" --headless --path . --import`.
- Si el editor reescribe `project.godot` o los `.import` de `docs/balance/`
  sin que hayas cambiado nada, descarta esos cambios
  (`git checkout -- project.godot docs/balance`).
- Si el equipo va justo de memoria, corre las pruebas de una en una.
- `--import` puede terminar con «Segmentation fault» al cerrarse. Las
  texturas quedan importadas igual: lo confirma `verify_terrain`, que compara
  la pantalla con el PNG píxel a píxel.

---

## 2. Cómo se trabaja (no se salta)

Las reglas completas están en `AGENTS.md` y en `docs/guia-de-continuacion.md`
§1. Lo esencial:

1. **El sistema de diseño manda en lo visual** (ver arriba). Los colores salen
   de `src/ui/design_tokens.gd` (rampas `TV_*`, que son las del sistema) y
   los sprites, de generadores `tools/gen_*.py` con semilla fija. Nunca se
   escribe un color, medida o duración suelto en el código.
2. **Diseño antes que código.** Cada pantalla o sistema nuevo abre su anexo en
   `docs/ux/anexos/AAAA-MM-DD-<tema>.md` con cuatro fases:
   - usuarios;
   - comunicación;
   - investigación: al menos 6 fuentes reales con URL y lo que se saca de
     cada una, y la que no abra se registra, no se inventa;
   - 2 o 3 direcciones, con una recomendada.

   **Se le pregunta a Diego y se espera su elección.** La elegida se escribe
   como **contrato bloqueado**, y desde ahí se cumple. Cambiarlo exige su
   permiso y queda fechado como «Enmienda N». La última usada es la **14**.
3. **Paso a paso:** tokens → componente clave → esqueleto → resto →
   pantalla completa → estados. Al terminar **cada** paso hay que:
   - hacer la captura a 640 × 360;
   - citar la cláusula del contrato que lo respalda;
   - decir cuál es el siguiente;
   - **parar hasta el visto bueno de Diego**.
4. **Se verifica midiendo, no mirando:** scripts `tools/verify_*` que dan OK o
   FALLA. Se informa de lo que falla, también de los fallos propios.
5. **Git:**
   - nunca se sube directo a `master`;
   - una rama por tarea (`rediseno/...`, `parte-N/...`, `fix/...`), creada
     desde la rama de trabajo vigente;
   - commits con *Conventional Commits* en español (`feat(terreno): ...`,
     `fix(...)`, `docs(...)`, `test(...)`);
   - **sin firma de herramientas**: nada de `Co-Authored-By`, «Generated
     with…» ni enlaces a asistentes, en commits, PR, código ni documentación;
   - cada uno hace commits desde su propia cuenta.
6. **PR** con esta plantilla y capturas reales:

   ```markdown
   ## <Título del trabajo>
   📑 **Feature:** <qué se hizo, en una línea>

   ## Desarrollador
   👷 **Dev:** <tu nombre completo>

   ## Cambios (clases,archivos,etc)
   <archivos tocados y qué cambió>

   ## Pantallazos funcionalidades
   <capturas del antes y después>
   ```

7. **Al cerrar cada sesión:**
   - actualizar el «Punto de retome» de `docs/plan-de-trabajo.md` y el
     estado de `docs/traspaso.md`;
   - hacer commit y push.

   Así el otro sabe exactamente dónde seguir.
8. **Código en inglés; textos del jugador y comentarios, en español.**

### Comprobación general (antes de empezar y antes de cada PR)

```bash
PYTHONIOENCODING=utf-8 python tools/verify_palette.py tokens        # 280 tokens, sin deriva
"$GODOT" --headless --path . res://tools/verify_usability.tscn     # 16/16
"$GODOT" --headless --path . res://tools/verify_camera.tscn        # 37/37
"$GODOT" --headless --path . res://tools/verify_encounters.tscn    # 82/82
"$GODOT" --headless --path . res://tools/verify_flow.tscn          # 23/23
"$GODOT" --headless --path . res://tools/verify_party_ai.tscn      # 19/19
"$GODOT" --headless --path . res://tools/verify_movement.tscn      # 99/99
for z in valdehoja ashen_forest tar_basin broken_coast withered_plain waning_peak greed_crypt; do
  "$GODOT" --headless --path . res://tools/verify_zone.tscn -- $z  # todas en verde
done
for z in ashen_forest tar_basin broken_coast withered_plain waning_peak greed_crypt; do
  "$GODOT" --path . res://tools/verify_terrain.tscn -- $z          # 7/7, con ventana
done
# capturas con otra etiqueta y otra casilla de vista (el decorado, el hito…):
"$GODOT" --path . res://tools/verify_terrain.tscn -- ashen_forest decorado 72 30
```

---

## 3. Dónde está el juego hoy (2026-11-02)

| Rama | Qué tiene | Estado |
|---|---|---|
| `master` | Partes 1 a 4: mundo en estilo plano, combate por turnos con persiana | Estable |
| `rediseno/tierra-viva` | Contrato «Piel nueva», paso 1: rampas `TV_*`, pantalla de 640 × 360, regiones ×4/3; el juego arranca en el mundo | Fusionada (PR #20) |
| `rediseno/terreno` | Lo anterior, más el suelo Tierra Viva de las seis regiones, el sistema de diseño en `docs/ux/sistema-de-diseno/`, el decorado del Bosque, Ilan y los monstruos de PixelLab y la escena del combate a 640 × 360 (ver el inventario §3.1) | **Rama de trabajo** |
| `parte-5/anexo` | Parte 5 (diálogos y retratos), pasos 1 a 5, hecha para 480 × 270 | Respaldo, sin PR; en espera |

**Decisiones de Diego que ya no se discuten:**
- el arte es Tierra Viva;
- el combate pasa a ser **de acción en el mismo mapa**, como en Minish Cap
  (no por turnos): manejas a un héroe, Q/E cambian de héroe, Z ataca,
  X esquiva, C usa la habilidad eco y V el objeto;
- pantalla de 640 × 360;
- las regiones van agrandadas ×4/3;
- Valdehoja pasa a la trama orgánica;
- **enmienda 14:** las masas de cada región sustituyen al relleno de árboles.

**Documentos que manda leer cada tarea:**
- `docs/traspaso.md`: estado y tareas del rediseño;
- `docs/ux/anexos/2026-10-30-tierra-viva.md`: anexo y contrato «Piel
  nueva», con el registro de cada paso;
- `docs/guia-de-continuacion.md`: protocolo, identidad, IA y una sección
  por parte;
- `docs/plan-de-trabajo.md`: punto de retome y decisiones cerradas;
- `docs/ux/sistema-de-diseno/`: **el sistema de diseño**.

### 3.1 Inventario: lo que todavía se ve con el diseño viejo (2026-11-02)

Diego, 2026-11-02: «ya debes empezar a cambiar todo como en el sistema de
diseño, que el viejo diseño aún está y se ve horrible». **La prioridad es que
no quede nada viejo a la vista.** Esta tabla es la lista de trabajo. Al
terminar una fila, se marca HECHO con la fecha y el commit.

| # | Pieza | Código de hoy | Qué pide el sistema (`docs/ux/sistema-de-diseno/project/`) | Estado |
|---|---|---|---|---|
| 1 | Suelo de las seis regiones | `tools/gen_tierra_viva_terrain.py` | `components/Terrain`, `Regiones` | HECHO 2026-11-01 |
| 2 | Ilan en el mapa (48 px, caminata de 4 cuadros) | `src/world/player_body.gd`, `tools/gen_tierra_viva_cast.py` | `components/Cast` | HECHO 2026-11-01 |
| 3 | Monstruos de mapa | `src/world/map_monster.gd` | `MonsterRoster`, `referencias/combate_accion.png` | HECHO 2026-11-01 |
| 4 | Decorado del Bosque | `tools/gen_tierra_viva_decor.py` | README §Mundo, `Overworld` | HECHO 2026-11-01 |
| 5 | Escena del combate (fondo, monstruo, grupo de espaldas) | `src/ui/battle/battle_screen.gd`, `tools/gen_tierra_viva_battle.py` | `assets/img/combate_enfermo.png`, `combate_purificado.png` | HECHO 2026-11-02 |
| 6 | Tipografía Brote | `DesignTokens.FONT_PATH` → `assets/fonts/brote.fnt` | README §Tipografía | HECHO 2026-11-02 (falta el titular de 22 px) |
| 7 | Placa del monstruo | `monster_view.gd` (`_draw_panel`) | `components/EnemyPlate` (10, 10), 184 px, pizarra | HECHO 2026-11-03 |
| 8 | Filas del grupo | `party_member_hud.gd` | `components/PartyRow` (456, 196), 176 px, 27 px | HECHO 2026-11-02 |
| 9 | Menú del turno | `action_menu.gd` | `components/CommandMenu`: 2 × 2 en (432, 284), 100 × 30, LUCHAR / ECO / BOLSA / HUIR | ver §4.0 |
| 10 | Mensaje del combate | `battle_screen.gd` (`_draw_message`) | `components/DialogBox`: papel con marco de madera | HECHO 2026-11-03 |
| 11 | Chapas de tipo y estado | (no existen) | `components/TypeBadge` | ver §4.0 |
| 12 | Cola de turnos | `turn_order_strip.gd` | **No está en el sistema**: se pregunta a Diego si se quita | pendiente de decisión |
| 13 | Cifras de daño | `damage_numbers.gd` | README §Movimiento: doble tamaño, `~` si se rehace | ver §4.0 |
| 14 | Pantalla de resultado | `result_overlay.gd` | pizarra o papel del sistema, titular de 22 px | ver §4.0 |
| 15 | Cartel de lugar | `src/world/place_label.gd` | `components/LocationSign`: madera con clavos | HECHO 2026-11-03 (contraste 3,22:1, pendiente de Diego) |
| 16 | Selector de región | `src/ui/region_select.gd` | `components/Regiones` | §4.12 |
| 17 | Decorado de las seis regiones y de Valdehoja: HECHO (regiones 2026-11-02, PR #21, #22, #23, #25 y #26; Valdehoja 2026-11-03, sobre la matriz actual) | `tools/gen_world_decor.py` (viejo) | README §Mundo; añadir su función al `CATALOG` de `gen_tierra_viva_decor.py` | §4.2, el compañero |
| 18 | Fauna y animales | `tools/gen_tierra_viva_decor.py` (`village()`) | sistema: «aparecen flores y fauna» | HECHO 2026-11-03 (Yara sigue vieja: falta en PixelLab) |
| 19 | Valdehoja orgánica, edificios de PixelLab y vecinos | `data/world/zones/valdehoja.*` | `components/Overworld`, `assets/source/pixellab/bld`, `npc` | §4.3 y §4.6 |
| 20 | Caminata de Bruma, Coral, Nix y Suri, y las diagonales | `assets/source/pixellab/<nombre>/` (solo rotaciones) | `Cast`: 8 rotaciones y 4 cuadros | generar en PixelLab y correr `gen_tierra_viva_cast.py` |
| 21 | HUD del mapa | (no existe) | `components/ActionHUD` | §4.6 (R3) |
| 22 | Diálogos y retratos | rama `parte-5/anexo` | `components/DialogBox`; manda el sistema, no el contrato «Columna» | §4.7 |
| 23 | Interiores | (no existen) | `components/Interiores`, `referencias/int_*.png` | §4.6 |
| 24 | Título y créditos | (no existen) | `referencias/titulo_*.png`, `creditos_*.png` | §4.12 y §4.14 |

**Regla para cerrar una fila:**
- se mide con la herramienta que corresponda: `verify_palette.py`, la
  prueba del paso y una captura a 640 × 360 con `tools/battle_capture.tscn`
  o `tools/verify_terrain.tscn`;
- la captura se compara con la referencia del sistema;
- se anota en el anexo `docs/ux/anexos/2026-10-30-tierra-viva.md`.

---

## 4. Todo lo que falta, en orden

Cada bloque termina con su verificación y con la parada para el visto bueno
de Diego. **Con cada uno se abre el README del sistema de diseño que se
indica.**

### 4.0 Combate y tipografía con el sistema (filas 6 a 14 del inventario)

Lo que más se ve después del mapa. Va por pasos, cada uno con su captura
(`"$GODOT" --path . res://tools/battle_capture.tscn -- <zona> <etiqueta> [purificado]`):

1. **Escena:** HECHO el 2026-11-02 (`58e3e63`).
2. **Tipografía Brote:** HECHO el 2026-11-02 (`8153c2c`). Cubre todos los
   caracteres de la fuente vieja; las pruebas siguen en verde.
3. **Marcos del combate.** Las herramientas ya están:
   - **`src/ui/tv_frame.gd` (`TvFrame`):** dibuja los marcos del sistema
     (`assets/ui/marcos/*.png`, nueve partes con bordes de 8 px, todos
     tokens), el texto con sombra sobre pizarra o papel, las chapas
     `TypeBadge` (`badge`, `type_fill`) y las barras (`bar`, `hp_fill`).
   - **`PartyRow`:** HECHO. `party_member_hud.gd` usa `TvFrame`; se ven tres
     filas alrededor de quien tiene el turno (`BattleScreen._layout_huds`).
     Captura: `docs/ux/capturas/2026-11-02-combate-filas-waning_peak.png`.
   - **`EnemyPlate`:** HECHO el 2026-11-03. `MonsterView._draw_panel` usa
     `TvFrame.PLATE` de 184 × 44 en (10, 10), con el nombre, las chapas de
     tipo y de estado (CORRUPTO o PURIFICADO) y «PV» con su barra de 5 px y
     la cifra. Captura: `docs/ux/capturas/2026-11-03-placa-*.png`.
   - **`CommandMenu`:** rejilla de 2 × 2 en (432, 284), 100 × 30, con los
     marcos `cmd-luchar`, `cmd-eco`, `cmd-bolsa` y `cmd-huir`, y
     `cmd-selected` para el elegido. Está en `action_menu.gd`, el menú raíz.
     **Antes, Diego decide** si se quedan las cuatro entradas del sistema
     (recomendado: ECO abre las habilidades y ORDEN pasa a Tab) o las cinco
     de hoy. `verify_party_ai` comprueba la fila de ORDEN y habrá que
     adaptarla.
   - **El aviso de papel:** HECHO el 2026-11-03. `BattleScreen._draw_message`
     dibuja `TvFrame.TEXTBOX` en `MESSAGE_RECT` (6, 282, 420 × 72), con el
     texto en papel a 15 px de interlínea y `▼` en `TV_RUST_2`. Los tonos del
     registro pasan al papel con `_paper_tone`. Captura:
     `docs/ux/capturas/2026-11-03-aviso-*.png`. **Lo siguiente es el
     `CommandMenu`**, que espera la decisión de Diego (cuatro o cinco
     entradas).
   - Los submenús (habilidades, bolsa, objetivo) no están en el sistema:
     se usa `TvFrame.PLATE` como marco de lista, y se avisa a Diego.
   - **Aviso para Diego:** las barras de PV del sistema son verdes
     (`hp-high`). Eso choca con la regla vieja de «el verde solo significa
     purificado». Manda el sistema, pero hay que anotarlo como enmienda
     fechada en el anexo.
4. **Estados:** chapas `TypeBadge`, barras `hp-high/mid/low`, cifras a doble
   tamaño con `~`, pantalla de resultado y la cola de turnos (decide Diego).

### 4.1 Paso 4a: masas de región · HECHO el 2026-11-01 (visto bueno de Diego el 2026-11-01)

Sistema de diseño: `project/README.md` §Mundo, `components/Regiones/README.md`
y `components/Terrain/README.md`.

1. Corre `verify_zone` en Cuenca, Costa, Llanura, Cumbre y Cripta. Es lo
   único sin medir del 4a, porque la pasada se cortó por falta de memoria.
2. En `tools/gen_tierra_viva_terrain.py`, añadir lo que pide el sistema por
   región, en lo enfermo:
   - **Llanura:** manchas de `sludge` (lodo) sobre la hierba seca. Calcula el
     ruido siempre y píntalo solo en lo enfermo, para no desalinear la
     semilla entre estados.
   - **Cumbre:** «hollín sobre `ice`», manchas de ceniza tramadas en lo
     enfermo.
   - **Cripta:** `smog`, jirones finos y tramados en lo enfermo. Poco: es una
     rampa clara y baja el valor.
3. `python tools/gen_tierra_viva_terrain.py` (unos 2 minutos), importa y
   mide:
   - `verify_palette.py image` y `tv-state` en cada PNG;
   - `verify_palette.py value <enfermo> <sano>` **≥ 1,5 en las cuatro
     visiones**;
   - `verify_terrain` y `verify_zone` en las seis.
4. Capturas a 640 × 360. `verify_terrain` las escribe en
   `docs/ux/capturas/<fecha del día>-terreno-<zona>-*.png`.
5. Registra el resultado en el anexo, para y pide el visto bueno.

### 4.2 Paso 4b: el decorado del catálogo

**Estado (2026-11-01):**
- **Bosque hecho:** `tools/gen_tierra_viva_decor.py ashen_forest` escribe 23
  sprites en `assets/sprites/world/tierra_viva/` (`<id>_<zona>_<estado>.png`)
  y `WorldDecor` los busca ahí antes que en el decorado viejo.
- **PixelLab movido** a `assets/source/pixellab/` (con README) y excepción de
  paleta hecha: `verify_palette.py image <png> --source <original>`.
- **Cuenca hecha (2026-11-02):** `basin()` escribe 25 sprites; falta el
  visto bueno de Diego y decidir si el Devorador se mueve, porque tapa la
  torre del hito (anexo de Tierra Viva, «Paso 4b — El decorado de la
  Cuenca»).
- **Costa hecha (2026-11-02):** `coast()` escribe 19 sprites (anexo de
  Tierra Viva, «Paso 4b — El decorado de la Costa»).
- **Permiso de Diego (2026-11-02):** fusionar lo necesario para la
  presentación del miércoles; cada región entra en `rediseno/terreno` al
  pasar sus medidas.
- **Llanura hecha (2026-11-02):** `plain()` escribe 28 sprites. El
  monstruo de mapa tapa el silo del hito; pasa también, en parte, en la
  Cuenca y la Costa (anexo de Tierra Viva).
- **Cumbre hecha (2026-11-02):** `peak()` escribe 22 sprites. El Coloso
  de mapa tapa el glaciar.
- **Cripta hecha (2026-11-02):** `crypt()` escribe 20 sprites. Con eso
  están las seis regiones.
- **Falta:**
  - Valdehoja, con su matriz nueva (paso 5, §4.3): se añade su función
    al `CATALOG` del generador, igual que `forest()`;
  - ~~el monstruo de mapa~~: hecho el 2026-11-01 (punto 5).

Sistema de diseño: `project/README.md` §Mundo y §Activos,
`assets/Mundo/README.md` y las imágenes de `project/assets/img/`
(`arbol@2x`, `arbol_quemado@2x`, `burnt_tree_*`, `log_pile_*`, `grass_*`,
`flower_*`, `crop_row_*`, `ghost_net_*`, `boat_*`, `casa@2x`).

1. Nuevo `tools/gen_tierra_viva_decor.py` que genere, con el estilo del
   prototipo (`tools/tierra_viva/flora.py`, `burnt.py`, `zones.py` y
   `cripta.py`), los sprites de cada id del catálogo de los `*.deco.txt`:
   - viñetas, hitos, pasos cerrados y monstruos de mapa;
   - lo que hay en el suelo: ceniza, crudo, basura, rocas, hierba alta,
     surcos, sal, grietas, monedas;
   - fauna y animales.

   La lista de ids actual está en `assets/sprites/world/decor/`, que es el
   estilo viejo (`tools/gen_world_decor.py`). **Mismos ids y nombres de
   archivo** (`<id>_pure.png`, `<id>_sick.png`, `<id>_<zona>_*.png`), para
   que `src/world/world_decor.gd` los cargue sin cambios. Empieza **solo por
   el Bosque** y para.
2. Reglas del sistema:
   - contorno del tono más oscuro de **su propia rampa** (`ASH_050` solo en
     lo que responde al jugador);
   - el árbol quemado es el mismo árbol sin copa, con hollín al pie;
   - en lo enfermo todo se asienta en el daño: la madera, carbonizada; casas
     y vallas, hacia la ceniza;
   - las piezas van agrupadas por uso, nunca repartidas al azar.
3. **PixelLab** (edificios y vecinos):
   - se mueven de `tools/tierra_viva/pl/` a `assets/source/pixellab/`, con un
     README (nombre y uso de cada uno);
   - en `tools/verify_palette.py` se añade la excepción «tinta de personaje o
     edificio» (como `CHARACTER_INKS`), aceptada solo dentro de esos sprites.
4. Verificación: `verify_palette.py image` y `tv-state` en cada sprite
   nuevo, `verify_zone` de la zona y capturas con `verify_terrain` (etiqueta
   `decorado` y una casilla que encuadre el hito).
5. **Monstruos de mapa (hecho, 2026-11-01):** `tools/gen_tierra_viva_cast.py`
   recorta los seis de PixelLab (`assets/source/pixellab/monsters/`) y los
   escribe en `assets/sprites/world/cast/monster_<zona>_{sick,pure}.png`.
   Van a su tamaño, unos 110 px, como en la maqueta del sistema
   `referencias/combate_accion.png`. `MapMonster` los usa en las tres
   posturas, y la alerta la dicen las bandas.

### 4.3 Paso 5: Valdehoja orgánica

**Estado (2026-11-03):** hecha la primera parte, la piel nueva sobre la
matriz aprobada de 60 × 34 (decisión de Juan José Rueda por la
presentación; **falta que Diego la confirme**):
- el suelo por partes, con `part_mask.gdshader` (punto 3 de abajo, hecho);
- el decorado de `village()`, con casas dibujadas en código a la escala de
  3 × 3.

**Falta** la matriz orgánica (puntos 1, 2 y 4), con los edificios de PixelLab
a su tamaño. Detalle en el anexo, «Paso 5, primera parte».

Sistema de diseño: `components/Overworld/README.md` (está entera la Valdehoja
de 90 × 60) y `referencias/valdehoja_*.png`, `v_*.png`.

1. Escribir la matriz nueva `data/world/zones/valdehoja.txt` (y su `.deco.txt`
   y `.parts.txt`) desde `tools/tierra_viva/village5.py`.
2. Se conservan:
   - la plaza del Árbol del Vínculo (hito);
   - la bocamina tapiada 2 × 2 (enmienda 12);
   - las cinco salidas a las regiones;
   - las seis partes de purificación;
   - el jardín de Yara.
3. Valdehoja va **por partes** (cada parte sigue a su región). El suelo
   necesita un sprite por parte, o una máscara por parte para el shader de
   la ola. Hoy `WorldRoot._mount_terrain` solo sabe de zonas enteras.
4. Verificación: `verify_zone valdehoja` en verde (adaptado a la matriz
   nueva) y capturas.

### 4.4 Paso 6: los estados, que cierran R1

**Estado (2026-11-03):** hechos los puntos 1 a 3. El agua viva alterna
`<zona>_sano.png` y `_sano_1.png` (`WorldAmbient.set_terrain`), las partes de
Valdehoja se ven por casilla y la fauna sigue solo en lo purificado. Falta el
punto 4, el PR de R1.

1. Enfermo y sano por partes en Valdehoja, con la ola de 900 ms en Bayer
   4 × 4 (ya existe: `src/world/purify_wave.gdshader`).
2. **Agua viva:** con el suelo en sprite, el segundo cuadro del agua
   (enmienda 8) ya no se ve. Genera un segundo PNG sano con el agua en
   `frame = 1` y alterna los dos cada `DUR_AMBIENT_WATER` (`WorldAmbient`).
3. Fauna solo en lo purificado y animales siempre (enmienda 8). Hoy funciona;
   comprueba que siga.
4. Abrir el **PR de R1** (rediseño del mundo) contra `master`.

### 4.5 R2: el combate de acción en el mapa (anexo nuevo)

Sistema de diseño: `components/ActionHUD/README.md`,
`components/EnemyPlate/README.md`, `components/TypeBadge/README.md`,
`components/BattleScreen/README.md`, `assets/Monstruos/README.md` (dos formas
por monstruo) y `referencias/combate_accion.png` y `combate_purifica.png`.
Prototipo: `tools/tierra_viva/combat_mock.py` y `hud.py`.

1. Anexo nuevo con las cuatro fases y 2 o 3 direcciones; **preguntar a
   Diego**.
2. Ideas ya argumentadas en el anexo de Tierra Viva (fuentes 4 a 7):
   - la contramedida de 2 rondas pasa a ser una ventana de aturdimiento;
   - la orden de líder (IA-5) pasa a ser la postura del grupo;
   - el cambio con Q/E es instantáneo;
   - cada héroe se distingue por lo que hace.
3. Reglas del sistema:
   - golpear sin la causa correcta hace que el monstruo **se rehaga** (aviso
     en papel: «La llama se rehace. Su causa es FUEGO»);
   - la habilidad eco del héroe adecuado lo purifica: cambian forma, paleta
     y expresión, y sale la ola.
4. Al implementar:
   - se sustituye la persiana (`src/world/battle_blinds.gd`) y la pantalla
     de batalla (`src/ui/battle/`), esta solo cuando el combate nuevo pase
     sus pruebas;
   - se reescriben `verify_flow` y `verify_encounters` para el combate en el
     mapa;
   - se vuelve a pasar `tools/balance_bot.tscn`.
5. **Deudas de equilibrado que hay que cerrar aquí:**
   - el Gólem de la Costa no presiona;
   - la fuerza bruta gana demasiado en la Llanura (100 %), la Cuenca (64 %)
     y el Bosque (41 %).

### 4.6 R3: HUD siempre visible, interiores, vecinos y personajes

Sistema de diseño: `components/ActionHUD`, `PartyRow`, `LocationSign`,
`Interiores`, `Cast` y `assets/Personajes/README.md`.

1. **HUD de acción** siempre a la vista y sin pausar:
   - tarjeta del héroe arriba a la izquierda, con el relevo debajo;
   - bolsa abajo a la izquierda, con teclas 1–4;
   - mandos en rombo abajo a la derecha;
   - pizarra `slate`;
   - tipografía **Brote**: `project/fonts/Brote.woff2` (pásala a TTF o BMFont
     para Godot; `tools/tierra_viva/font.py` la genera).
2. **Cartel de lugar** de madera con clavos (sustituye a `PlaceLabel`).
3. **Personajes de 48 px en 8 direcciones**, con caminata de 4 cuadros a
   200 ms. **Ilan hecho (2026-11-01):** `tools/gen_tierra_viva_cast.py` saca
   de PixelLab la hoja `assets/sprites/world/cast/ilan.png`, con celdas de
   48 px, de pie más 4 cuadros por orientación, y `PlayerBody` cambia de
   cuadro cada 12 px (200 ms andando). Bruma, Coral, Nix y Suri ya tienen su
   hoja, pero **sin caminata**: PixelLab solo dio la de Ilan, así que hay que
   generar `walk_<dir>.gif` de cada uno y volver a correr el script. Faltan
   las 4 diagonales del sistema (8 rotaciones). Al pasarlos al juego se mide con
   `verify_palette.py image <png> --source assets/source/pixellab/<nombre>`.
4. **Interiores** (posada, tienda, casa): `referencias/int_*.png` y
   `tools/tierra_viva/interiors.py`.
5. **Vecinos:** 6 con nombre y variantes por región (`ZONE_NPC` en
   `tools/tierra_viva/zones.py`).
6. Los mínimos de accesibilidad: contraste ≥ 4,5:1 en el texto (se mide
   sobre el render), foco visible y teclado completo.

### 4.7 Parte 5: diálogos y retratos

Rama `parte-5/anexo`: caja de diálogo, retratos de las siete voces,
conversación con Yara, Rasgo en brasa o ceniza y Yara por el ave. **Antes de
seguir hay que resolver un choque con el sistema de diseño:**

- el sistema pide la caja `DialogBox`: papel con marco de madera, hoja `eco`,
  chapa con el nombre y fuente Brote (`components/DialogBox/README.md`);
- la parte 5 hizo el contrato «Columna»: panel de ceniza a 480 × 270.

**Se le pregunta a Diego cuál manda.** Lo esperable es que mande el sistema:
se enmienda «Columna», se remide a 640 × 360 y se conserva lo que no choca
(textos en datos, máquina de escribir, retratos, lado de quien habla). Luego:

- **IA-3:** pistas de Yara por el ave, con modelo del jugador por monstruo y
  tres niveles; prueba `tools/verify_hints.gd`.
- **IA-6:** memoria de Rasgo, con cinco actos, 32 combinaciones y tres
  desenlaces; prueba `tools/verify_rasgo.gd`. Detalle en
  `docs/guia-de-continuacion.md` §3.3.

### 4.8 Parte 6: progresión

Guía de continuación, parte 6.
- Los compañeros se unen tras su región: Bruma (Bosque), Coral (Cuenca),
  Nix (Costa) y Suri (Llanura).
- Las banderas de `GameState` son la única fuente de verdad: región
  purificada, compañero unido y habilidades.
- Sin barras de experiencia en el mundo.

### 4.9 Parte 7: puzzles ambientales, uno por región

Guía de continuación, parte 7. **El puzzle es el ensayo de la contramedida**:
- Bosque: cortafuegos;
- Cuenca: barreras absorbentes;
- Costa: fardos al contenedor;
- Llanura: rotar cultivos;
- Cumbre: manto sobre la roca.

Sin textos de instrucción. Si el jugador falla tres veces, la pista llega
**en diálogo**.

### 4.10 Parte 8: menú fuera de combate («cuaderno de campo»)

Pestañas Grupo · Bolsa · Habilidades · Ecos. En el sistema de diseño, la
pizarra y el papel (`project/README.md` §Interfaz). Cada estado con su vista
propia: bolsa vacía, sin energía y región no visitada.

### 4.11 Parte 9: guardado

- Se guarda en un **brote** (punto purificado; el primero, en el jardín de
  Yara).
- JSON en `user://save.json` con versión del formato, y autoguardado al
  cambiar de zona.
- Archivo corrupto: aviso y partida nueva, **nunca** un cierre.
- Prueba: guardar → cargar → comparar `GameState` campo a campo.

### 4.12 Parte 10: título y opciones

Concepto: `docs/ux/tierra-viva/titulo-y-creditos.md` y `referencias/titulo_*`.
Es la dirección A del anexo.
- El título es **Valdehoja real en el estado de la partida**, y
  `scenes/main.tscn` pasa a abrirlo.
- Opciones obligatorias: movimiento reducido, velocidad del texto, volumen
  por bus, reasignación de teclas y escala de ventana entera.
- La demo de combates queda como herramienta de depuración.

### 4.13 Parte 11: audio

**Estado (2026-11-03):** sonido provisional generado por código para la
presentación (`tools/gen_audio.py`, `GameAudio`, `verify_audio`). Falta el anexo
de la parte y que Diego lo vea; detalle en el anexo de Tierra Viva.

- Lo enfermo suena apagado (bus Ambiente con filtro de paso bajo) y se abre
  al ritmo de la ola.
- Buses: Música, Ambiente, Efectos, Interfaz.
- **Solo audio con licencia libre registrada** en `docs/licencias-audio.md`.
- Ningún sonido lleva información que no tenga también una señal visual.

### 4.14 Parte 12: final y créditos

Concepto en `titulo-y-creditos.md` y `referencias/creditos_*`:
- tras purificar la Sombra, una última ola por el mundo;
- los créditos son un recorrido por las siete zonas sanas.

**Pendiente de Diego:** los nombres completos del equipo y `LICENCIAS.md`
(fuentes, audio y PixelLab).

### 4.15 Entrega

1. Exportar el `.exe`: en Godot, *Editor → Administrar plantillas de
   exportación* (descarga de unos 1,3 GB), luego *Proyecto → Exportar →
   Windows Desktop*.
   - **Hecho el 2026-11-03 desde `master` (`1afe0b0`).** Se probó que arranca
     y carga Valdehoja; falta jugarlo entero con el ejecutable.
   - **`export_presets.cfg` no se versiona** (`.gitignore`), así que cada uno
     crea el suyo. Tiene que llevar:
     - **Recursos a incluir:** `data/*`. El juego lee sus mapas como `.txt` y
       `.json` con `FileAccess`, y Godot no los exporta por defecto: sin esto,
       el `.exe` arranca sin mapas.
     - **Recursos a excluir:** `docs/*,tools/*`.
     - **Incrustar el PCK** (`binary_format/embed_pck`), para que sea un solo
       archivo.
   - **Por consola:** `"$GODOT" --headless --path . --export-release "Windows
     Desktop" <ruta>.exe`. Puede cerrarse con «Segmentation fault», como
     `--import`: mira el código de salida y la fecha del `.exe`, porque si
     falla no lo reescribe.
   - **Entrega:** junto al `.exe` va `docs/legal/privacidad.md`.
2. **Privacidad**, desde el diseño (regla de Diego): el juego no recoge
   datos de nadie.
   - **Hecho el 2026-11-03:** el aviso breve está en
     `docs/legal/privacidad.md`. Se comprobó en `src/` que no hay red ni
     escritura de archivos; hoy solo escribe el motor (registros en `user://`).
   - **Falta:** enseñarlo dentro del juego, en las opciones (§4.12) o en los
     créditos (§4.14), y actualizar su apartado de la partida con el guardado
     (§4.11). Si algún día hay red, cuentas o analítica, entra la política
     completa.
3. Fusionar los PR pendientes cuando Diego lo diga, empezando por el #20.

### Deudas que no se olvidan

- **Prueba con personas** de «¿Por qué pierdo?» (hoja lista en
  `docs/ux/pruebas/2026-10-01-hoja-de-pruebas.md`). Con el combate nuevo
  (R2) hay que rehacerla.
- **IA-2:** la fauna en bandada (*boids*), con su prueba `verify_fauna.gd`.
- **Mobbin y Pinterest** sin consultar en el anexo de exploración.
- **Aviso de anclajes** de `src/world/battle_blinds.gd` al arrancar. Se va
  sola cuando R2 retire la persiana.

---

## 5. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| **Sistema de diseño** (manda en lo visual) | `docs/ux/sistema-de-diseno/` (`index.html`, `project/README.md`) |
| Reglas del repo | `AGENTS.md` |
| Estado y tareas del rediseño | `docs/traspaso.md` |
| Punto de retome | `docs/plan-de-trabajo.md` |
| Protocolo, identidad, IA e instrucciones por parte | `docs/guia-de-continuacion.md` |
| Anexo y contrato en curso | `docs/ux/anexos/2026-10-30-tierra-viva.md` |
| Prototipo de arte aprobado | `tools/tierra_viva/` (con su README) |
| Generador del suelo | `tools/gen_tierra_viva_terrain.py` |
| Tokens | `src/ui/design_tokens.gd` y `tools/pixel.py` (las rampas `TV_*` se regeneran con `tools/gen_tierra_viva_tokens.py`) |
| Comprobaciones | `tools/verify_*.py`, `tools/verify_*.tscn` |
| Capturas | `docs/ux/capturas/` |
