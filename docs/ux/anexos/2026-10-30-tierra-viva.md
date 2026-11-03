# Anexo de diseño — Rediseño «Tierra Viva»: arte del mundo y combate en el mapa

Fecha: 2026-10-30 · Rama: `rediseno/tierra-viva` · Estado: **dirección B elegida;
contrato «Piel nueva» bloqueado el 2026-10-30.** Paso 1 (tokens) en curso.

## Por qué existe este anexo

Entre el 2026-10-28 y el 2026-10-30, fuera del repositorio, Diego dirigió un
rediseño visual completo con referentes de GBA y 16 bits (Zelda: The Minish
Cap y Link's Awakening, CrossCode, Moonlighter, Pokémon Blanco y Negro). El
resultado vive en el Design System «Ecos de la Tierra» (tarjetas Overworld,
Regiones, Interiores, ActionHUD) e incluye:

- Valdehoja con trama orgánica.
- Las cinco regiones y el bosque, en enfermo y sano.
- Tres interiores.
- Doce personajes con 8 direcciones.
- Un combate de acción en el mismo mapa.

Diego lo pidió explícitamente: el combate por turnos le parecía «muy
Pokémon», y el mapa con materiales planos, «horrible».

Ese trabajo **choca con contratos bloqueados**. AGENTS.md no deja integrarlo
sin anexo ni sin permiso. Este anexo hace tres cosas:

1. Mide los choques.
2. Propone tres maneras de integrarlo.
3. Espera la elección de Diego.

## Fase 1 — Usuarios

- **Jugador** (guía §1.1): RPG 2D, 14–30 años, PC con teclado.
  - Lo que cambia para él: **el combate deja de ser una pantalla aparte**. Pelea donde explora y con las mismas teclas de mover.
  - Necesita leer de un vistazo el héroe activo, su vida, la bolsa y las habilidades, sin abrir menú. Diego pidió que la bolsa y las habilidades se vean siempre en pantalla.
- **Docente de Diseño de Interfaces**: evalúa criterio.
  - Para él, un rediseño a mitad de proyecto **es un riesgo y una oportunidad**: o se documenta como decisión con causa y con medición, o parece un capricho que tira cuatro partes aprobadas.
- **El equipo** (Juan José Rueda y quien continúe): necesita saber qué contratos siguen vigentes. Si no, cada sesión discute lo mismo.

## Fase 2 — Comunicación

**Decisión dominante del jugador en el mundo nuevo:** *¿ataco, esquivo o
cambio de héroe ahora?* Se toma en menos de un segundo y sin pausa.

La información que la sostiene, en este orden:

1. Dónde está el enemigo y hacia dónde mira; se lee por la silueta, no por el color.
2. Cuánta vida tiene el héroe activo.
3. Qué héroe es el siguiente con Q/E y qué habilidad tiene lista.
4. La bolsa.

**Lo que no va:** números de daño flotando en cada golpe, minimapa o cualquier HUD que tape el borde superior del mapa (donde están las cotas), y textos de tutorial en el mundo. La regla «nada de carteles "pulsa E"» de la guía §2.2 sigue valiendo.

**Lo que se conserva del lenguaje del entorno** (guía §2.2), y es la razón de
que este rediseño no sea solo un cambio de gusto:

| | Enfermo | Sano |
|---|---|---|
| Valor | Bajo, hundido | Alto |
| Silueta | Rota: árbol quemado sin copa, palma caída, frailejón seco | Llena: copa, roseta |
| Fauna | Ausente | Presente |

Tierra Viva **ya cumple** estas tres filas en las seis zonas.

## Fase 3 — Investigación

Formato: observación → decisión aplicable → límite que no copiaré.

1. **Godot, «Multiple resolutions»** — https://docs.godotengine.org/es/4.4/_sources/tutorials/rendering/multiple_resolutions.rst.txt (en la versión en inglés de 4.3 solo cargó la navegación).
   - **Observación:** la guía oficial llama a 640×360 «a good baseline» para pixel art, porque escala con factor entero a 1280×720, 1920×1080, 2560×1440 y 3840×2160 sin barras. Recomienda el modo de estiramiento `viewport` y el escalado `integer`.
   - **Decisión:** 640×360 es una opción respaldada, no un gusto. 480×270 también escala entero a 1920×1080 (×4), pero no a 1280×720.
   - **Límite:** no se toca el estiramiento `viewport` ni el filtro `Nearest`, que ya son contrato.
2. **Slynyrd, Pixelblog 20: Top Down Tiles** — https://www.slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles
   - **Observación:** recomienda repartir el peso visual de forma homogénea, mezclar zonas planas con zonas de vegetación de distinta densidad («monotonous» si se repite un solo tile) y trabajar a 16×16.
   - **Decisión:** se mantiene la casilla de 16 px del repo. Las texturas de Tierra Viva se generan sobre esa rejilla, así que **los mapas aprobados no cambian de tamaño**.
   - **Límite:** no se adopta la proyección 3/4 en los muros del mundo abierto; las caras de cota ya tienen su altura fija.
3. **Slynyrd, Pixelblog 43: Top Down Tiles part 2** — https://slynyrd.com/blog/2023/3/26/pixelblog-43-top-down-tiles-part-2
   - **Observación:** sombras proyectadas ligeras, en una o dos caras, nunca más largas que un tile y del mismo largo sea cual sea la altura del muro. Agua hecha de manchas unidas por líneas de 1 px, con brillos y sombras desplazadas, y animada a dos cuadros.
   - **Decisión:** las sombras de muro de la Cripta se quedan en 10 px (menos de un tile) y el agua viva anima a dos cuadros, que encaja con la enmienda 8.
   - **Límite:** no se copia su textura de arena en «S», que él mismo avisa que puede quedar como «ramen noodle».
4. **CrossCode (Wikipedia)** — https://en.wikipedia.org/wiki/CrossCode
   - **Observación:** se explora un mundo en el que se pelea o se resuelven puzles; no hay pantalla de batalla aparte. Las acciones son golpe cuerpo a cuerpo, disparo a distancia, esquiva o bloqueo, y cambio instantáneo de elemento.
   - **Decisión:** el combate en el mapa se apoya en un referente de 16 bits consolidado. El cambio instantáneo de elemento es el modelo del cambio de héroe con Q/E: sin pausa y sin menú.
   - **Límite:** no se copian el sistema de rangos ni la sobrecarga elemental. Son capas de profundidad que no caben en el alcance de un proyecto de curso.
5. **GamingBolt, «CrossCode: Deciphering the Pillars…»** — https://gamingbolt.com/crosscode-deciphering-the-pillars-of-an-action-rpg-classic/amp
   - **Observación:** muchos enemigos tienen fases de aturdimiento que se interrumpen con un disparo cargado. Poner a los compañeros en postura defensiva atrae los ataques y prepara combos.
   - **Decisión:** la contramedida de cada monstruo (contrato «Persiana», 2 rondas en regiones) se traduce a **una ventana de aturdimiento**. La «orden de líder» de IA-5 se traduce a **una postura del grupo**, así que la sintonía no se pierde.
   - **Límite:** sin parkour ni saltos; el mundo del repo no tiene alturas transitables.
6. **Game-Wisdom, análisis de Moonlighter** — https://game-wisdom.com/analysis/moonlighter
   - **Observación:** critica que cada tipo de arma tenga un solo ataque especial y que mejorarlas no cambie cómo se juega, de modo que el combate «se vuelve repetitivo». También, que el mismo enemigo es letal en una cornisa estrecha y trivial en campo abierto.
   - **Decisión:** cada héroe se diferencia por **lo que hace**, no por cifras: el cambio Q/E tiene que cambiar la táctica. Los encuentros se colocan pensando en el terreno.
   - **Límite:** no se adopta el bucle de tienda y mazmorra de Moonlighter.
7. **Zelda Wiki, «Items Screen»** — https://zelda.fandom.com/wiki/Items_Screen
   - **Observación:** en Link's Awakening, Link lleva **como máximo dos objetos equipados** a la vez y los elige en una subpantalla aparte. En Minish Cap la subpantalla tiene 12 casillas fijas.
   - **Decisión:** el HUD siempre visible muestra **pocas casillas fijas** (las habilidades del héroe activo y una de bolsa). La bolsa completa sigue en el menú de la parte 8.
   - **Límite:** no se pone todo el inventario en pantalla; taparía el mapa.

**Fuentes que no se pudieron abrir** (2026-10-30):
- https://zeldawiki.wiki/wiki/HUD: error del sitio, no se recuperó nada.
- La página inglesa de Godot 4.3 «multiple_resolutions»: solo devolvió la navegación.

**Fuentes de la lista de Diego para pantallas:** `styles.refero.design`,
`mobbin.com`, `ui.aceternity.com` y `tasteskill.dev`. No aplican a un mapa
de juego en pixel art, igual que en los anexos anteriores.

### Medición de los choques (hecha el 2026-10-30 sobre los renders de Tierra Viva)

Saturación de los cinco renders de región en estado enfermo, a 640×368:

| Región | Mediana de saturación | Píxeles por encima de 0,22 | Colores distintos |
|---|---|---|---|
| Costa | 0,45 | 84 % | 259 |
| Cuenca | 0,50 | 82 % | 179 |
| Llanura | 0,42 | 90 % | 280 |
| Cumbre | 0,40 | 72 % | 1 259 |
| Cripta | 0,30 | 84 % | **6 076** |

Lectura:

- **Techo de saturación.** El techo de 0,22 de «Vereda» lo superan entre el 72 % y el 90 % de los píxeles. No es una deriva: Tierra Viva tiene **otra paleta**.
- **La Cripta.** Su luz de antorchas es un degradado continuo y genera más de 6 000 colores, algo que `verify_palette.py` («cero colores sueltos») rechazaría. **Se cuantiza o se rehace la luz por bandas.**
- **Lo que no se ha medido.** Falta `verify_palette.py cvd` y `value` sobre estos renders. Queda **pendiente**: no se dan por buenos.

### Contratos y reglas que Tierra Viva contradice

| Regla vigente | Dónde | Qué hace Tierra Viva |
|---|---|---|
| Viewport 480×270 | `project.godot`, guía §2.1 | Compone a 640×360 |
| Saturación del mundo ≤ 0,22, rampas `SOIL/WATER/FLORA` | «Vereda», enmienda 6 | Paleta propia (`art/pal.py`): mediana 0,40–0,50 en lo enfermo |
| Contorno `ASH_050` = «responde»; decorado sin contorno | Guía §2.2 | Todo prop lleva contorno oscuro |
| Combate en pantalla aparte con persiana de 300 ms | «Persiana» | Combate de acción en el mismo mapa |
| El jugador maneja solo a Ilan y da órdenes al grupo | «Orden de líder» (IA-5) | El jugador **cambia** de héroe con Q/E |
| Assets generados por `tools/gen_*.py` con la paleta de `tools/pixel.py` | Guía §1.6 | Pipeline propio en Python fuera del repo, más sprites de PixelLab (edificios y NPC) |
| Verde `VITAL_*` solo en lo purificado | Guía §2.1 y §3.1 | **Cumple**: lo sano es lo purificado y en lo enfermo no hay verde |
| Fauna solo en lo purificado | Enmienda 7 | **Cumple** |

## Fase 4 — Direcciones (Diego eligió B el 2026-10-30)

### A · «Trasplante» — todo de una vez

Tierra Viva sustituye la identidad visual y el combate a la vez:

- Viewport a 640×360.
- La paleta de `art/pal.py` pasa a `design_tokens.gd` y a `pixel.py`.
- Las zonas se rehacen con las trazas nuevas.
- El combate de acción sustituye a «Persiana» y a la pantalla de batalla.

- **A favor:** es exactamente lo que Diego vio y aprobó. Es la entrega más rápida de explicar.
- **En contra:**
  - Tira o reescribe los contratos «Vereda», «Rastro», «Persiana» y «Orden de líder» en un solo paso, sin poder comparar.
  - Deja obsoletas las verificaciones medidas (`verify_zone`, `verify_squint`, `balance_bot`) hasta que se rehagan.
  - Las trazas nuevas de las zonas no tienen los puzles, las viñetas ni las bóvedas aprobados en la parte 3.
- **Riesgo para la nota:** el docente ve cuatro partes aprobadas descartadas sin una comparación.

### B · «Piel nueva, mismo mundo» — recomendada

Se integra por capas y **los mapas aprobados se conservan**:

1. **R1, el mundo.**
   - El motor de Tierra Viva (máscaras suavizadas, cotas de borde natural, árboles validados) pinta **las mismas matrices** de `data/world/zones/*.txt`. Los puzles, viñetas, bóvedas, encuentros y la bocamina siguen donde Diego los aprobó.
   - Viewport a 640×360 (fuente 1).
   - Paleta nueva como **enmienda 13**, con las reglas semánticas intactas: verde solo en lo purificado, brasa para la causa activa, valor y silueta redundantes.
   - El contorno se reasigna: **el contorno de 1 px en `ASH_050` sigue marcando «responde»**. El decorado lleva un contorno de su propia rampa, más oscuro, que no compite con él (se mide con `value`).
   - El pipeline entra en el repo como `tools/gen_tierra_viva_*.py` con semilla fija. Los sprites de PixelLab entran como assets fuente versionados.
2. **R2, el combate en el mapa.**
   - Anexo propio.
   - Sustituye «Persiana» por un contrato nuevo:
     - golpe, esquiva y cambio Q/E;
     - la contramedida pasa a ventana de aturdimiento (fuente 5);
     - la orden de líder pasa a postura del grupo, para que la sintonía de IA-5 no se pierda.
   - Se vuelve a pasar el bot de equilibrado.
3. **R3, HUD siempre visible, interiores y NPC.** HUD con pocas casillas fijas (fuente 7), las tres salas interiores y los vecinos con sus diálogos de la parte 5.

- **A favor:**
  - Cada capa se compara con lo anterior y se aprueba por separado (§1.1, paso a paso).
  - El trabajo de diseño de las partes 2 a 4 se conserva.
  - El docente ve un rediseño **motivado, medido y por fases**.
- **En contra:**
  - Es más lento que A.
  - Las trazas nuevas de Valdehoja (calles curvas, casas a distinta altura) **no entran tal cual**: el pueblo tendría que rehacerse sobre su matriz aprobada o enmendar esa matriz.

### C · «Vitrina» — Tierra Viva como prueba aparte

El juego sigue como está. Tierra Viva entra como **una escena de
demostración** (Valdehoja y el combate de acción) que se juega aparte para
compararla con la versión actual. Con esa prueba se decide después.

- **A favor:** riesgo cero para lo aprobado; sirve de prueba con usuarios (pendiente desde la parte 1).
- **En contra:** no cumple lo que Diego pidió (cambiar el combate y el mapa del juego). Duplica trabajo y deja el juego real con el arte que Diego ya rechazó.

### Recomendación: B

Es la única que cambia lo que Diego pidió sin perder lo aprobado:

- Los mapas del repo **ya son matrices de caracteres**, igual que las que pinta el motor de Tierra Viva. Por eso la piel nueva cabe en el mundo aprobado sin redibujar su diseño.
- La paleta cambia, pero el **significado** del color se mantiene, y ese significado es lo que el contrato protegía: el verde vuelve al purificar.

### Preguntas para Diego

1. **Dirección:** A, B o C.
2. **Viewport:** 640×360 (recomendado por Godot y por cómo se compuso el arte) o mantener 480×270.
3. **Valdehoja:** con B, ¿se conserva la matriz aprobada del pueblo o se enmienda para adoptar la trama orgánica nueva?
4. **Combate:** confirmar que el contrato nuevo de R2 sustituye a «Persiana» y adapta «Orden de líder» (postura del grupo en vez de orden por ronda).

**Respuestas de Diego (2026-10-30):** B · 640×360 · enmendar la matriz de
Valdehoja · el combate de acción sustituye a «Persiana» y la orden de líder
pasa a postura del grupo.

### Medición previa al contrato: valor enfermo frente a purificado

`python tools/verify_palette.py value <enfermo> <sano>` sobre los renders de Tierra Viva (2026-10-30):

| Zona | Normal | Deuteranopía | Protanopía | Tritanopía |
|---|---|---|---|---|
| Valdehoja | 2,09 | 2,03 | 2,17 | 2,07 |
| Cuenca | 1,96 | 1,91 | 2,04 | 1,95 |
| Llanura | 1,91 | 1,87 | 1,97 | 1,89 |
| Cumbre | 1,74 | 1,69 | 1,81 | 1,74 |
| Costa | 1,59 | 1,53 | 1,69 | 1,59 |
| **Cripta** | **1,27 FALLA** | **1,25** | **1,30** | **1,27** |

La regla del entorno («enfermo = valor bajo») se cumple en cinco de seis zonas
con la paleta nueva. **Excepciones:**
- **Cripta (falla):** el oro enfermo brilla. Hay que corregirla antes de aprobar su zona.
- **Costa (al límite):** queda a 0,03 del piso en deuteranopía.

## Contrato «Piel nueva» — BLOQUEADO 2026-10-30

Alcance: **R1, el mundo.** R2 (combate en el mapa) y R3 (HUD, interiores y
NPC) abren su propio anexo.

### 1. Resolución
- Viewport **640×360**; estiramiento `viewport`, escalado `integer`, filtro `Nearest`, ajuste a píxel.
- Ventana por defecto **1280×720** (×2). 1440×810 deja de ser entero.
- La casilla sigue en **16 px**. Una pantalla muestra 40×22,5 casillas.
- `MAX_EXITS_PER_SCREEN` se mide sobre 640 px.

### 2. Paleta (enmienda 13)
- **Rampas `TV_*`.** Se añaden a `design_tokens.gd` y `tools/pixel.py`, generadas por `tools/gen_tierra_viva_tokens.py` desde una tabla única. Son las del arte aprobado: tierra, piedra, hierba, hoja, arena, agua, madera, tejados, muro, flor, hierba seca, hoja muerta, ceniza, crudo, lodo, plástico, óxido, oro, hielo, fuego y las variantes regionales.
- **El techo de 0,22 deja de aplicarse a las rampas `TV_*`.** La paleta pasa a regirse por el significado:
  - **Solo en celdas purificadas:** `TV_GRASS`, `TV_LEAF`, `TV_FLOWER` y `TV_WATER` (agua viva).
  - **Solo en celdas enfermas:** `TV_DRYGRASS`, `TV_DEADLEAF`, `TV_OIL*`, `TV_SLUDGE*`, `TV_PLASTIC*`, `TV_TURBID`, `TV_SMOG`.
  - **Neutras:** el resto.
- **Se conserva.** `VITAL_*` sigue con su único significado en la interfaz. `EMBER_*` sigue siendo la causa activa y el aviso. La UI sigue en `ASH_*`.
- **Valor:** `verify_palette.py value` ≥ 1,5 en las cuatro visiones para cada zona. La Cripta se corrige antes de aprobar su zona.
- **Cero colores sueltos.** El terreno y el decorado generados pasan un **cuantizado final a los tokens `TV_*`**. La luz se hace en bandas de la rampa, nunca en degradado continuo.

### 3. Contorno
- **El contorno de 1 px en `ASH_050` sigue reservado a lo que responde.**
- El decorado lleva un contorno **de su propia rampa**, el tono más oscuro (índice 0 o 1), nunca `ASH_050`.
- La regla de negación de la guía §2.2 no cambia.

### 4. Assets externos
- **Edificios y personajes de PixelLab.** Entran como fuente versionada en `assets/source/pixellab/` con su README (nombre y uso).
- **Su paleta no se cuantiza.** Se registra como «tinta de personaje o edificio», igual que `CHARACTER_INKS`, y `verify_palette.py` acepta sus colores solo dentro de esos sprites.

### 5. Pipeline
- **Ubicación.** El generador de Tierra Viva entra en `tools/tierra_viva/` (código en inglés y comentarios en español), con semilla fija.
- **Pinta las matrices de `data/world/zones/*.txt`.** Los caracteres del repo se traducen a los materiales del motor: suelo, camino, agua, puente, escalera, cota, arena, muro y losa.
- **Salida:** un atlas por zona y estado, más las capas de decorado que `WorldDecor` ya sabe colocar.

### 6. Valdehoja (enmienda de la matriz)
- **Trazado nuevo.** Se adopta el pueblo orgánico de Tierra Viva: calles en curva, casas a distinta altura y plazas ovaladas.
- **Lo que se conserva** se marca en la matriz nueva antes de pintar: la plaza del Árbol del Vínculo, la bocamina tapiada de 2×2 (enmienda 12), las salidas a las regiones y las partes de purificación (`valdehoja.parts.txt`).
- `verify_zone` se adapta a la matriz nueva y sigue en verde.

### 7. Lo que no cambia
- **Movimiento y cámara:** el movimiento («Umbral», «Vereda»), la cámara con zona muerta y la diagonal sin normalizar.
- **Purificación de zona:** la ola de 900 ms con tramado Bayer 4×4.
- **Fauna:** la fauna solo en lo purificado y los animales domésticos siempre.
- **Interfaz:** el radio 0, el borde de 1 px y la tipografía de mapa de bits.

### Orden de implementación
1. **Tokens:** rampas `TV_*`, viewport y ventana.
2. **Componente clave:** el motor de terreno en `tools/tierra_viva/`, pintando el Bosque desde su matriz.
3. **Esqueleto:** las siete zonas pintadas desde sus matrices, con verify_zone en verde.
4. **Resto:** el decorado y los edificios de PixelLab colocados por `WorldDecor`.
5. **Pantalla completa:** Valdehoja con su matriz enmendada.
6. **Estados:** enfermo y sano con la ola de purificación por partes.

Al final de cada paso: captura, cláusula y espera del visto bueno de Diego.

### Registro

#### Paso 1 — Tokens y viewport · 2026-10-30

**Hecho:**
- `tools/gen_tierra_viva_tokens.py` escribe las **39 rampas `TV_*`** (233 tokens) desde una sola tabla en los bloques marcados de `design_tokens.gd` y `pixel.py`.
  - Es idempotente: ejecutarlo dos veces no duplica nada.
  - También escribe `TV_PURIFIED_ONLY` y `TV_SICK_ONLY` (cláusula 2).
- `verify_palette.py`:
  - las rampas `tv_` quedan fuera del techo de 0,22 (cláusula 2);
  - orden nueva `tv-state <png> enfermo|sano`. Un color compartido entre una rampa de solo-purificado y otra de otro grupo cuenta como neutro; por ejemplo, el blanco de nieve, flor y plástico.
- `project.godot`: viewport 640×360 y ventana 1280×720 (cláusula 1).
- `zone_rules.gd`: `SCREEN_TILES` pasa a 40×23.
- Lámina: `docs/ux/capturas/2026-10-30-tierra-viva-tokens.png`. «+» marca solo-purificado (texto en verde); «−», solo-enfermo (texto en brasa).

**Medido:**

```
python tools/verify_palette.py tokens        → 280 tokens coinciden. Sin deriva.
verify_usability    16/16     (antes 16/16)
verify_camera       37/37     (antes 37/37)
verify_encounters   82/82     verify_flow 23/23     verify_party_ai 19/19
verify_movement     95/99     (antes 99/99)
verify_zone         valdehoja 55/55 · ashen_forest 44/46 · tar_basin 44/45
                    broken_coast 44/46 · withered_plain 43/45
                    waning_peak 43/45 · greed_crypt 46/48   (antes, todas en verde)
```

**Lo que falla y por qué.** No son errores de código: son consecuencia
directa de ver un 78 % más de mapa por pantalla.

1. **`verify_movement`: 4 fallos de las zonas de prueba.**
   - `prueba_b` (30×17) y `prueba_c` (20×10) son más pequeñas que la pantalla nueva, así que la cámara enseña fuera de la zona.
   - `prueba_a` mete 3 salidas en una pantalla de 640 px.
   - Son zonas de prueba hechas a la medida de 480×270. Se arreglan agrandándolas, sin tocar el contrato «Umbral».
2. **`verify_zone`: el ritmo del contrato «Rastro».**
   - **Viñetas:** con 40 casillas de ancho, dos viñetas caben en la misma pantalla en cinco de las siete zonas.
   - **Hito:** el hito asoma antes del 25 % del camino en el Bosque, la Llanura y la Cripta.
   - **Follaje:** en la Costa, la Llanura y la Cumbre el follaje ya no tapa la fuente antes de llegar.
   - Las matrices aprobadas se diseñaron para enseñar 30×17 casillas.

**Decisión que hace falta (se para aquí):**
- (a) **Agrandar las matrices** de las seis regiones en proporción (~×1,33), conservando el orden de viñetas, hito y fuente. Es coherente con Tierra Viva, cuyas zonas ya son mayores.
- (b) **Mantener las matrices** y enmendar las reglas de ritmo de «Rastro» a la pantalla nueva.
- (c) **Volver a 480×270.**

Recomendado: (a). Conserva el ritmo que se aprobó, que es lo que «Rastro» protege, y la piel nueva gana espacio para el decorado agrupado.

**Decisión de Diego (2026-10-30): (a) agrandar las matrices.**

#### Paso 1b — Las seis regiones a ×4/3 · 2026-10-30

`tools/scale_zone.py` agranda la matriz de una zona y su capa de decorado, y
reescribe sus salidas. El orden importa:

1. **Terreno:** vecino más próximo.
2. **Salidas:** cada salida sigue en el borde y sobre el camino. La llegada queda un tile dentro, junto a la salida de vuelta (contrato «Umbral»).
3. **Borde:** el camino que ganó ancho se cierra en el borde, salvo la casilla de salida.
4. **Decorado:**
   - Cada pieza conserva su tamaño y busca, junto a su esquina escalada, el mismo suelo bajo cada casilla.
   - Las viñetas mantienen, casilla a casilla, su distancia al **camino principal** tal como lo recorre `verify_zone`.
   - La fuente sigue tocando el camino en cruz.
   - El hito queda a ≤ 3 tiles de la fuente.
   - El paso cerrado tapa el camino de lado a lado.

| Zona | Antes | Ahora | `verify_zone` |
|---|---|---|---|
| Bosque de las Cenizas | 100×34 | 134×46 | 46/46 |
| Cuenca de Alquitrán | 80×52 | 107×70 | 45/45 |
| Costa Quebrada | 96×40 | 128×54 | 47/47 |
| Llanura Marchita | 90×40 | 120×54 | 45/45 |
| Cumbre Menguante | 72×52 | 96×70 | 46/46 |
| Cripta de la Avaricia | 60×66 | 80×88 | 50/50 |
| Valdehoja (sin tocar; se rehace en el paso 5) | 60×34 | 60×34 | 55/55 |

- **Las cifras cambian de 46 a 47 o de 48 a 50** porque algunas comprobaciones son una por salida o una por paso cerrado. Los pasos cerrados ahora ocupan el camino de lado a lado, así que hay más.
- **`verify_zone.gd`:** la franja de «pista» mide `ZoneRules.SCREEN_TILES.x`, no 30 fijo.
- **`AGENTS.md`:** capturas a 640×360.
- **Captura:** `docs/ux/capturas/2026-10-30-tierra-viva-bosque-escalado.png`.
  - Arriba, el Bosque aprobado; abajo, el agrandado.
  - El marco blanco es una pantalla: 30×17 antes, 40×23 ahora.
  - Colores: viñetas en rojo, hito en amarillo, fuente en blanco, paso cerrado en magenta y llegada en cian.

**Pendiente, medido y no arreglado:** `verify_movement` sigue en **95/99**.
- Sus zonas de prueba (`prueba_a` 40×20, `prueba_b` 30×17) se hicieron a la medida de 480×270 y ahora son menores que la pantalla.
- Escalarlas no sirve: la prueba lleva coordenadas fijas de esas zonas y probarlo dio más de 20 fallos.
- Se rehacen a 54×27 y 40×23 junto con sus coordenadas, en el paso 2, antes de tocar el motor de terreno.

**Visto bueno de Diego al paso 1 y al 1b: 2026-10-30.**

#### Tarea 1 — Las zonas de prueba a la pantalla nueva · 2026-10-30

- **Crecen hacia la derecha y hacia abajo**, sin mover nada de lo que ya
  había. Así siguen valiendo casi todas las coordenadas fijas de
  `verify_movement.gd`. A mano, sin `scale_zone.py`.
  - `prueba_a`: 40×20 → **54×27**. El camino este llega al nuevo borde
    (53, 9) y el camino sur, a (12, 26). En la parte nueva hay un bloque
    sólido y un charco, para que no sea un llano vacío.
  - `prueba_b`: 30×17 → **40×23**. Mide justo una pantalla: así la prueba
    de «tres salidas en una pantalla» sigue cayendo en una ventana de 40
    casillas.
  - `prueba_c`: 20×10, **sin tocar**. Sigue siendo menor que la pantalla
    para la prueba del centrado.
- **Ninguna pantalla de 40×23 ve las tres salidas de `prueba_a`:** entre la
  sur (x = 12) y la este (x = 53) hay 42 casillas, y entre la norte (y = 0)
  y la sur (y = 26), 27.
- **`exits.json`:** se mueven las salidas este y sur de `prueba_a` y las
  llegadas de vuelta desde `prueba_b`, (52, 9) y (12, 25). El `_doc` dice
  640 px.
- **`verify_movement.gd`:** solo cambian las coordenadas ligadas a esas dos
  salidas. Los puntos de partida quedan a la misma distancia de la salida
  que antes.
- **Medido:** `verify_movement` **99/99** (antes 95/99). La comprobación
  inicial entera, en verde: 280 tokens sin deriva, `verify_usability`
  16/16, `verify_camera` 37/37, `verify_encounters` 82/82, `verify_flow`
  23/23, `verify_party_ai` 19/19 y `verify_zone` en las siete zonas.
- **Un fallo mío al capturar, y se dice:** la primera toma de `prueba_b`
  puso a Ilan sobre el agua, porque elegí a mano una casilla del charco.
  `enter_zone` no comprueba si se pisa. Se repitió en tierra.
- **Capturas a 640×360:** `docs/ux/capturas/2026-10-30-tierra-viva-prueba-a.png`
  y `-prueba-b.png`. El suelo todavía es el plano de antes: el motor de
  terreno es el paso 2.

**Siguiente:** paso 2, el motor de terreno, empezando solo por el Bosque.

**Visto bueno de Diego a la tarea 1: 2026-10-31.** Entra en el PR #20 con el
paso 1 y el 1b.

#### Paso 2 — Componente clave: el motor de terreno, en el Bosque · 2026-10-31

**Generador:** `tools/gen_tierra_viva_terrain.py` (cláusula 5). Es el port de
`tools/tierra_viva/map2.py` y de lo que hace falta de `scene2.py`. Código en
inglés, comentarios en español y semilla fija: dos ejecuciones dan los mismos
bytes (comprobado con `md5sum`).

- **Entrada:** la matriz aprobada de `data/world/zones/ashen_forest.txt`, con
  la leyenda del repo.
  - `.` → hierba con matas en V sobre rejilla con desfase.
  - `=` → camino con rodadas, centro gastado, bordillo de piedrecitas y
    briznas en el borde. El alisado del camino bajó de 9 a 5: con 9, un
    camino de una casilla quedaba en 10 px y no cubría su casilla.
  - `~` → agua hundida: profundidad por distancia a la orilla, cara de tierra
    al norte, talud en los lados y destellos en el agua abierta.
  - `=` con agua a los dos lados → puente de tablas con barandillas.
  - `#` → **masa de copas por racimos** (`flora.clumps_canopy`), recortada a
    sus casillas. Los racimos asoman como mucho 4 px (`OVERHANG`, menos de un
    cuarto de casilla), en festón. Con el borde recortado en recto se leía
    como un muro, así que se cambió. Contorno del tono más oscuro de su rampa
    (cláusula 3) y sombra al sur.
  - Vida del agua (de `scene2.py`): juncos y nenúfares solo en lo sano;
    piedras que asoman en los dos estados.
- **Mismo dibujo, otro material:** los dos estados usan la misma semilla y
  los mismos índices de rampa, y solo cambia la rampa.
  - Hierba → `TV_DRY_GRASS`.
  - Copas → `TV_DEAD_LEAF`.
  - Agua → `TV_TURBID`.
  - Tierra → `TV_SICK_SOIL`.
  - Así la ola descubre el mismo dibujo, que pasa de enfermo a sano.
- **Cuantizado final** (cláusula 2): todo píxel pasa al token `TV_*`
  permitido más cercano de su estado. Hoy no mueve ninguno, porque todo sale
  ya de las rampas; queda como garantía.
- **Salida:** `assets/world/tierra_viva/ashen_forest_{enfermo,sano}.png`,
  de 2144 × 736 (134 × 46 casillas).

**En el motor** (`src/world/world_root.gd`):

- Si la zona tiene su par enfermo y sano, `_mount_terrain` pone dos `Sprite2D`
  en el origen, el enfermo debajo y el sano encima. El sano solo se ve si la
  zona está purificada.
- **La capa de tiles queda oculta** y solo da la colisión, que sigue saliendo
  de la matriz (`WorldTiles.SOLID`).
- **La ola usa el mismo shader** (`purify_wave.gdshader`) sobre una copia del
  sprite sano. Sin el par, todo sigue como antes: Valdehoja y las otras cinco
  zonas no cambian.

**Medido:**

```
verify_palette image  ashen_forest_enfermo.png   todo píxel es un token
verify_palette image  ashen_forest_sano.png      todo píxel es un token
verify_palette tv-state enfermo / sano           ningún color del otro estado
verify_palette value  purificado / enfermo       1,71 normal · 1,61 deuteranopía
                                                 1,85 protanopía · 1,69 tritanopía (piso 1,5)
verify_terrain (nuevo, 640×360)                  7/7
```

- `tools/verify_terrain.tscn` comprueba:
  - los dos sprites miden la zona, están en el origen y la capa de tiles está
    oculta;
  - empujando contra el follaje 60 cuadros, Ilan no pisa ninguna casilla
    sólida;
  - **con el decorado e Ilan ocultos, el 100 % de la pantalla es exactamente
    el píxel del PNG** en esa posición del mundo: sin filtro, escala ni
    desfase. Pasa enferma, purificada y a mitad de la ola, donde cada píxel
    es enfermo o sano (125 443 sano y 103 411 enfermo) y nunca mezcla.
- **Un fallo mío en la prueba, y se dice:** la primera versión pedía un 90 %
  con todo visible y falló (83 %). El decorado viejo tapa el 17 % de la
  pantalla. Era un mal umbral, no un fallo del motor, y se pasó a medir el
  suelo solo.
- **Capturas a 640 × 360:**
  `docs/ux/capturas/2026-10-31-terreno-ashen_forest-enfermo.png`, `-ola.png`
  y `-sano.png`.

**Lo que se ve y todavía no es de este paso:** los árboles sueltos, la fuente
y los pasos cerrados son el decorado viejo de «Rastro»; se rehacen en el paso
4. El agua no se anima: con la capa de tiles oculta, el segundo cuadro del
agua viva (enmienda 8) no se ve, y vuelve en el paso 6, el de los estados.

**Siguiente:** paso 3, el esqueleto: las otras cinco regiones pintadas
desde sus matrices (Cuenca, Costa, Llanura, Cumbre y Cripta). La Cripta
necesita antes su luz por bandas (cociente 1,27 < 1,5) y la Costa está al
límite (1,53).

**Visto bueno de Diego al paso 2: 2026-10-31.**

#### Paso 3 — Esqueleto: las seis regiones desde sus matrices · 2026-10-31

El mismo generador pinta ya las seis regiones (`REGION` en
`tools/gen_tierra_viva_terrain.py`). El motor no cambia: `_mount_terrain`
monta cualquier zona que tenga su par enfermo y sano. Valdehoja sigue con
los tiles hasta el paso 5.

- **Paletas de región** (las de `map2.palette`, ya como tokens):

  | Región | Sano | Enfermo |
  |---|---|---|
  | Bosque y Llanura | hierba, hoja, agua | hierba seca, hoja muerta, agua turbia, tierra enferma |
  | Cuenca | ídem | **agua de crudo**, hierba de lodo, ceniza en el camino |
  | Costa | ídem, con arena | **agua con plástico**, hierba seca, arena gris |
  | Cumbre | **páramo, nieve, puyas** | páramo seco, pedregal, hoja muerta |
  | Cripta | piedra con musgo y **luz por bandas** | ceniza en penumbra, oro derramado |

- **Arena** (`:`, la Costa): portada de `map2.render`, con grano, borde de
  1 px y franja oscura. Donde el agua toca la playa no hay talud, sino bajío
  claro y espuma en ondas.
- **La Cripta tiene pintor propio** (`render_crypt`, de `cripta.py`, a la
  matriz del repo):
  - losas de 32 × 24 en hileras desplazadas, con bisel y junta;
  - el muro visto desde arriba: corona de sillares y, donde da al suelo, su
    cara de 8 px con hiladas;
  - la alfombra en ajedrezado rojo con ribete de oro.
- **La luz de la Cripta, por bandas** (cláusula 2, pendiente desde el
  anexo): haces diagonales que suben uno o dos tonos de la rampa, con borde
  tramado de 2 px, nunca en degradado. Solo en lo sano.

**El valor, medido, y lo que se tuvo que cambiar para llegar al piso.** Se
dice entero, porque son tres ajustes de paleta sobre el prototipo:

1. **Costa, 1,34 → 1,75.** Con la arena gris en su sitio, la playa pesaba
   casi igual sana que enferma, y la arena es un tercio de la zona.
   - Bajar la arena un tono la dejó en 1,50 en deuteranopía, por debajo del
     piso.
   - Igualar la hierba seca a la del Bosque no movió nada: en la Costa casi
     no hay hierba suelta.
   - **Quedó la arena dos tonos más oscura que la sana.**
2. **Cripta, 1,42 → 1,77.** Con la piedra en el mismo tono en los dos
   estados, la luz sola no llegaba. **La enferma baja un tono toda la losa**
   (penumbra), y así lo pide su descripción: el oro tapa las grietas del
   techo.
3. **Cripta, el oro:** con una pieza cada 140 px de suelo parecía confeti.
   Se dejó en una cada 280.

```
value purificado / enfermo   normal  deuter.  protan.  tritan.   (piso 1,5)
Bosque de las Cenizas         1,71    1,61     1,85     1,69
Cuenca de Alquitrán           1,71    1,62     1,85     1,69
Costa Quebrada                1,75    1,72     1,80     1,75
Llanura Marchita              2,03    1,92     2,22     2,02
Cumbre Menguante              1,83    1,75     1,94     1,82
Cripta de la Avaricia         1,77    1,76     1,78     1,77
```

- **En las doce imágenes:** `verify_palette image` dice que todo píxel es un
  token, y `tv-state` no encuentra ningún color del otro estado.
- **`verify_terrain`, ahora genérico:** mira desde la casilla de llegada y
  empuja contra la primera casilla de follaje o muro con suelo debajo. Da
  **7/7 en las seis regiones**; en cada una, el 100 % de la pantalla es el
  PNG enfermo, el sano o, a mitad de la ola, uno de los dos sin mezcla.
- **Reproducible:** dos ejecuciones dan los mismos 12 archivos, byte a byte.
- **Capturas a 640 × 360:**
  `docs/ux/capturas/2026-10-31-terreno-<zona>-{enfermo,ola,sano}.png`, 18
  en total.

**Sigue sin ser de este paso:** el decorado (árboles sueltos, rocas, pinos,
fuente, columnas de la Cripta) es el viejo y se rehace en el paso 4.

**Siguiente:** paso 4, el decorado:
- los sprites del catálogo de cada `*.deco.txt`, con el estilo del
  prototipo y el contorno de su rampa;
- los edificios y vecinos de PixelLab, a `assets/source/pixellab/`.

**Visto bueno de Diego al paso 3: 2026-10-31.**

#### Corrección contra el sistema de diseño · 2026-11-01

Diego descargó el sistema de diseño «Tierra Viva» y ahora está en el repo, en
`docs/ux/sistema-de-diseno/`. Al cotejar los pasos 2 y 3 con él salieron
diferencias, y Diego aprobó corregirlas (2026-10-31):

- **Bosque enfermo = incendio** (`ash` + `fire`): árboles quemados sin copa,
  con hollín al pie y brasas. Antes eran copas de hoja muerta.
- **Los bosques se cierran con muros de árboles solapados**, con troncos;
  antes eran una alfombra de copas.
- **Arbustos enfermos = ramitas secas**, no manchas oscuras.
- **Rasgos de región pendientes:** `sludge` en la Llanura enferma, hollín
  sobre `ice` en la Cumbre y `smog` en la Cripta.
- **Para otras partes:** la caja de diálogo (papel con marco de madera)
  choca con el contrato «Columna» de la parte 5; el cartel de lugar, el HUD
  de acción y los personajes de 48 px son de R2 y R3.

#### Enmienda 14 — La masa sustituye al relleno · autorizada por Diego el 2026-10-31

- En una zona con suelo de Tierra Viva, las piezas `tree`, `tree_b`,
  `burnt_tree`, `bush`, `pine` y `boulder` que caen **enteras dentro del
  follaje sólido** no se montan: ni sprite ni cuerpo. La colisión ya sale de
  la matriz. Antes eran unas 4.400 piezas en las seis regiones.
  - `WorldDecor.FILL`, `has_terrain()` e `is_fill()`.
  - `verify_zone` cuenta con la misma regla.
  - El Bosque pasa de unos 680 sprites de decorado a 82.
- **Cada región tiene su masa** en el generador (`MASS` en
  `gen_tierra_viva_terrain.py`), colocada en los mismos sitios en los dos
  estados:

  | Región | Sano | Enfermo |
  |---|---|---|
  | Bosque | muro de árboles solapados | árboles quemados con brasas; el borde entero y uno de cada tres dentro |
  | Cuenca | muro de árboles | árboles quemados sin brasas |
  | Costa y Llanura | arbustos | ramitas secas |
  | Cumbre | frailejones | frailejones secos |

**Paso 4a, estado al 2026-11-01 (parcial, subido para que el equipo siga):**

- **Medido en verde:**
  - `verify_palette image` y `tv-state` en las doce imágenes;
  - `value`: Bosque 1,63–1,79, Cuenca 1,54–1,67, Costa 1,54–1,60,
    Llanura 1,83–2,09 y Cumbre 2,35–2,53;
  - `verify_terrain` 7/7 en las seis regiones;
  - `verify_usability` 16/16, `verify_camera` 37/37, `verify_encounters`
    82/82, `verify_flow` 23/23, `verify_party_ai` 19/19 y
    `verify_movement` 99/99;
  - `verify_zone`: Bosque 46/46 y Valdehoja 55/55.
- **Sin medir:** `verify_zone` en Cuenca, Costa, Llanura, Cumbre y Cripta.
  La pasada se cortó porque el equipo se quedó sin memoria, no por un
  fallo. Es lo primero que hay que correr.
- **Falta:**
  - el `sludge` de la Llanura, el hollín sobre `ice` de la Cumbre y el
    `smog` de la Cripta;
  - repasar las capturas a 640 × 360: `verify_terrain` ya las regeneró con
    las masas nuevas (`2026-10-31-terreno-<zona>-*.png`), pero falta
    rehacerlas con los rasgos de región;
  - el visto bueno de Diego.
- **El paso a paso desde aquí** está en `docs/guia-del-equipo.md`.

#### Paso 4a — Cierre: rasgos de región · 2026-11-01

- **`verify_zone` en las cinco zonas que faltaban, en verde:** Cuenca 45/45,
  Costa 47/47, Llanura 45/45, Cumbre 46/46 y Cripta 50/50.
- **`paint_blight`**, el daño propio de cada región sobre el suelo libre.
  El ruido se calcula en los dos estados, para que la semilla no se
  desalinee, y solo se pinta en lo enfermo:
  - **Llanura:** charcos de lodo (`sludge`) en el tono más bajo de la
    rampa, con grumos y borde de hierba seca.
  - **Cumbre:** hollín tramado en los dos tonos más oscuros de la ceniza.
- **Cripta:** jirones de `smog` finos y escasos donde en lo sano entra la
  luz.
- **Dos fallos propios, y se dicen:**
  1. **El lodo salió verde lima** con el tono medio de su rampa. En este
     juego el verde dice «purificado», así que se bajó al tono más oscuro y
     a manchas más pequeñas. El hollín se leía como charcos azulados: se
     oscureció igual.
  2. **El frailejón sano llevaba la falda en `dead_leaf`,** que es solo de
     lo enfermo. El cuantizado lo tapaba moviendo 111 494 px en la Cumbre
     sana, y se vio por su contador. Ahora la falda es madera (neutra) y
     **las doce imágenes salen con 0 píxeles movidos**: todo nace en su
     token.
- **Medido:**
  - `verify_palette image` y `tv-state` en verde;
  - `value`: Llanura 1,84–2,10, Cumbre 2,42–2,61 y Cripta 1,76–1,78; las
    demás, como en la entrada anterior;
  - `verify_terrain` 7/7 en las seis regiones.
- **Capturas a 640 × 360:**
  `docs/ux/capturas/2026-10-31-terreno-<zona>-{enfermo,ola,sano}.png`.

**Siguiente:** paso 4b, los sprites del catálogo, empezando por el Bosque
(guía del equipo, §4.2).

#### Paso 4b — El decorado del Bosque · 2026-11-01

**Decisión de Diego (2026-11-01):** «ya todo debe regirse al nuevo sistema de
diseño, en lo que se refiere en diseño de personajes y todo lo demás». Queda
escrito en la regla número uno de la guía del equipo. No es una enmienda,
porque el contrato ya decía que el sistema manda en lo visual: es la
confirmación de que los personajes también entran.

- **`tools/gen_tierra_viva_decor.py`** dibuja el catálogo del Bosque con el
  vocabulario de la masa del suelo, `piece`, `clumps` y `outlined` de
  `gen_tierra_viva_terrain.py`. Así un árbol suelto del borde se lee igual
  que los del muro. Hace 23 sprites:
  - árbol, segunda copa y árbol del gradiente;
  - el roble del hito;
  - tocón, tronco talado y troncos apilados;
  - ceniza, hierba alta (con su cuadro de mecerse), roca, semillero y paso
    cerrado.
- **Reglas del sistema que cumple:**
  - el árbol quemado es el mismo árbol sin copa, en la misma posición;
  - en lo enfermo, cerco de ceniza al pie y madera carbonizada; en lo sano,
    sombra sobre hierba y un brote en el tocón;
  - contorno del tono más oscuro de la rampa de cada pieza, salvo el
    semillero, que responde al jugador y lleva `ash_050`;
  - la ceniza purificada da flores.
- **Carga:**
  - los sprites van en `assets/sprites/world/tierra_viva/<id>_<zona>_<estado>.png`;
  - `WorldDecor._texture` y el segundo cuadro de lo que se mece miran ahí
    primero, y después el decorado viejo;
  - así las regiones que faltan siguen como estaban hasta que les toque.
- **Fallos propios, vistos en las capturas y corregidos:**
  1. La ceniza enferma, con núcleo claro, se leía como guijarros blancos.
     Ahora es una mancha tramada que deja ver el suelo.
  2. La hierba alta y la ceniza enfermas casi no se veían: subieron un tono.
  3. El roble del hito, a 48 × 64, se perdía en el muro de árboles. Ahora
     mide 64 × 80 y desborda su huella de 3 × 4 casillas, que sigue siendo
     la de la colisión.
- **PixelLab:**
  - `tools/tierra_viva/pl/` pasó a `assets/source/pixellab/` con su README
    (qué es y quién usa cada carpeta);
  - lleva `.gdignore` en `assets/source/` para que Godot no lo importe;
  - los scripts del prototipo apuntan a la ruta nueva.
- **Excepción de paleta** «tinta de personaje o edificio»:
  - se usa como `verify_palette.py image <png> --source <original>`;
  - un color suelto vale solo si está en ese original;
  - el original tiene que estar dentro de `assets/source/pixellab/`.
  - Probado: Ilan contra su original pasa, contra el de Coral falla, y una
    ruta fuera de `pixellab/` se rechaza.
- **Medido:**
  - los 23 sprites pasan `image` y `tv-state` sin un píxel movido;
  - `verify_zone ashen_forest` da 46/46;
  - `verify_terrain` da 7/7 con las vistas nuevas (`72 30` para el hito,
    `8 14` para la tala).
- **Capturas a 640 × 360:**
  `docs/ux/capturas/2026-11-01-decorado{,-puente,-tala}-ashen_forest-{enfermo,ola,sano}.png`.
- **Pendiente:**
  - las otras regiones;
  - el monstruo de mapa. En el sistema es un personaje de 48 px y Ilan
    sigue a 16 × 24, así que entran juntos. Lo decide Diego.

#### Personajes del sistema en el mapa: Ilan y los monstruos · 2026-11-01

Diego, a mitad del 4b: «sigues corriendo con los diseños viejos, ya necesito
los nuevos». Se adelanta lo que más se ve, que son los personajes.

- **Hallazgo:** las tarjetas `*@4x` de monstruos y de decorado del sistema
  (`deforestation_flame@4x`, `burnt_tree_*@4x`, `log_pile_*@4x`…) son los
  sprites **viejos** del juego ampliados: coinciden píxel a píxel. El diseño
  de verdad del sistema está en `arbol@2x`, `arbol_quemado@2x`, en los
  personajes y monstruos de PixelLab y en las referencias. Esas tarjetas no
  sirven de modelo.
- **`tools/gen_tierra_viva_cast.py`:**
  - copia sin repintar los originales de `assets/source/pixellab/` en
    `assets/sprites/world/cast/`;
  - hace las hojas de Ilan, Bruma, Coral, Nix y Suri (celdas de 48 px, de
    pie más 4 cuadros de caminata por orientación);
  - recorta los seis monstruos de historia en sus dos formas.
- **Ilan:**
  - `PlayerBody` usa la hoja nueva;
  - el cuadro cambia por distancia, cada 12 px: andando a 60 px/s son los
    200 ms de `dur-walk-frame`, y la regla «para justo cuando el cuerpo se
    para» se mantiene;
  - `verify_movement` da 100/100, con la comprobación nueva de que la
    caminata pasa por sus 4 cuadros.
- **Monstruo de mapa:**
  - el de PixelLab a su tamaño (unos 110 px), como en
    `referencias/combate_accion.png`;
  - mira a la izquierda, así que el volteo va al revés que con el viejo;
  - `verify_encounters` da 82/82.
- **Paleta:**
  - cada hoja pasa `verify_palette.py image <png> --source assets/source/pixellab/<nombre>`;
  - `source_inks` lee también los cuadros de los GIF.
- **Batería:**
  - `verify_zone` en verde en las siete zonas;
  - usability 16, camera 37, flow 23, party_ai 19.
- **Captura:** `docs/ux/capturas/2026-11-01-personajes-ashen_forest-enfermo.png`.
- **Sigue viejo:**
  - el decorado de las otras cinco regiones y de Valdehoja;
  - la pantalla de combate, que usa los monstruos viejos de 48 px y los
    retratos del grupo;
  - el HUD, el diálogo y el título;
  - la caminata de Bruma, Coral, Nix y Suri, que PixelLab solo dio para
    Ilan;
  - las diagonales.

#### Paso 4b — El decorado de la Cuenca · 2026-11-02

Cláusulas: 2 (paleta y cuantizado), 3 (contorno de la propia rampa) y la
regla del sistema «en lo enfermo todo se asienta en el daño»
(`project/README.md` §Mundo; `components/Regiones/README.md`: «ciénaga de
crudo, balancines, tubería, barriles, árboles quemados» / «laguna limpia con
juncos y bosque alrededor»).

- **`basin()` en `tools/gen_tierra_viva_decor.py`**, igual que `forest()`.
  Hace 25 sprites del catálogo de `tar_basin.deco.txt`:
  - árbol y segunda copa: la misma pieza que la masa de la Cuenca (sano y
    quemado sin brasas, `MASS["cuenca"]`);
  - el hito, la torre de la refinería: 56 × 84, desborda su huella de
    3 × 4 hacia arriba como el roble del Bosque. Enferma, con la llama de la
    antorcha (`fire`, la causa activa), óxido a manchas y crudo que chorrea;
    purificada, apagada y con enredadera y flores al pie;
  - las viñetas: barril volcado (bidón `roof_blue`, como en
    `referencias/z_cuenca_enfermo.png`), mancha de crudo, tubería partida
    (purificada, empalmada con un collar), barca varada (casco negro hasta
    el charco) y red rota (purificada, remendada y con flotadores);
  - juncos (purificados, con espadañas y su cuadro de mecerse), hierba alta,
    arbusto (enfermo, ramitas secas, regla de Regiones), roca, semillero y
    paso cerrado (tuberías retorcidas en el crudo).
- **El daño de la Cuenca es el crudo, no la ceniza.** `foot()` toma el cerco
  de `P["stain"]` si la región lo da; la Cuenca le pasa la rampa `oil`, con
  reflejos de `sheen`. El Bosque no cambia: regenerado, da los mismos bytes.
- **Lo que se limpia con la ola** (crudo, barriles y paso cerrado) solo tiene
  sprite enfermo: `WorldDecor.VANISH_WHEN_PURE` no lo monta purificado.
- **Fallos propios, vistos en las capturas y corregidos:**
  1. La barca, una elipse plana, se leía como un disco. Ahora tiene popa
     recta, proa en punta y bancadas.
  2. La red en gris medio no se veía sobre la hierba de lodo. Ahora la
     cuerda es clara (`stone_5`; purificada, `wood_5`).
- **Medido:**
  - los 25 sprites pasan `verify_palette.py image` y `tv-state`, con 0 px
    llevados a su token;
  - `verify_zone tar_basin` da 45/45;
  - `verify_terrain tar_basin` da 7/7 en las cuatro vistas.
- **Capturas a 640 × 360:**
  `docs/ux/capturas/2026-11-02-decorado{,-v1,-v2,-v3}-tar_basin-{enfermo,ola,sano}.png`
  (hito `49 44`; viñetas `64 12`, `19 35` y `81 59`).
- **Pendiente, para que lo decida Diego:** en lo enfermo, el Devorador de
  mapa (PixelLab, unos 110 px, en `(50, 47)`) tapa casi entera la torre del
  hito, que está justo detrás. Con el monstruo viejo de 48 px no pasaba.
  Opciones: mover el monstruo unas casillas al sur o al este en
  `tar_basin.deco.txt`, o aceptar que el hito se descubre al purificar.
- **Siguiente:** la Costa (`broken_coast`), cuando Diego dé el visto bueno.

#### Combate con el sistema de diseño, paso 1: la escena · 2026-11-02

Diego: «sigue» (después de ver a Ilan y los monstruos de mapa).

- **Qué combate se hace.** El componente `BattleScreen` del sistema describe
  el combate de acción en el mapa (R2, guía §4.5). Pero `EnemyPlate`,
  `PartyRow`, `CommandMenu`, `TypeBadge` y la imagen `combate_enfermo.png`
  describen, con medidas exactas, la pantalla por turnos, que es la que
  tiene el juego. Se rediseña esa; R2 sigue en su sitio.
- **Fallo propio, encontrado al medir:** el combate seguía a 480 × 270 desde
  antes de «Piel nueva». En el juego, a 640 × 360, ocupaba solo la esquina
  de arriba a la izquierda y dejaba una franja gris. El grupo, además, salía
  con siluetas grises provisionales. Captura del antes:
  `2026-11-02-combate-antes-ashen_forest.png`.
- **Tokens:**
  - `gen_tierra_viva_tokens.py` añade las rampas de interfaz del sistema
    (`ui`, `paper`, `hp`) y las del cielo del combate del prototipo
    (`dusk` y `dusk_hill`, solo-enfermo; `sky` y `far_hill`, solo-purificado);
  - también los papeles semánticos de `components/tokens.css`
    (`TV_SLATE`, `TV_PAPER`, `TV_CMD_FIGHT`, `TV_HP_HIGH`…);
  - el generador ahora reescribe los grupos de estado de `pixel.py` aunque
    ya existan, porque antes se quedaban viejos;
  - en total, 320 tokens sin deriva.
- **`tools/gen_tierra_viva_battle.py`:**
  - porta `battle.py` del prototipo y hace los fondos de 640 × 360 por región
    y estado, con las dos plataformas;
  - el Bosque es el del sistema;
  - **las otras cinco son derivadas**, porque el sistema no las dibuja: la
    misma estructura con la paleta aprobada de cada región. Cuenca con
    torres de bombeo, Costa con mar, Llanura con silo y cerca, Cumbre con
    picos y Cripta como interior de sillares y columnas.
- **`gen_tierra_viva_cast.py`** añade dos cosas:
  - el grupo de espaldas: la rotación norte-este de PixelLab al doble
    (`battle-back: 96px`);
  - los seis monstruos de combate, con la clave de su script.
- **Pantalla:**
  - `SCREEN` pasa a 640 × 360;
  - el fondo es la imagen de la región: enfermo mientras quede un monstruo
    sin purificar y sano cuando todos lo están;
  - el monstruo se planta en sus pies (470, 184), sobre su plataforma, a su
    tamaño;
  - el grupo va de espaldas con los pies en (150, 276): el primero delante a
    la izquierda y el resto 8 px más atrás;
  - con más de tres miembros el paso se encoge para que nadie se salga, que
    con cinco se salía Ilan.
- **Medido:**
  - usability 16/16, party_ai 19/19, flow 23/23, encounters 82/82 y wave 7/7;
  - la paleta de los 12 fondos (`image` y `tv-state`), de las 5 espaldas y
    de los 12 monstruos (`--source`) sin fallos.
- **Capturas:**
  - `2026-11-02-combate-escena-ashen_forest.png`;
  - `…-escena-purificado-ashen_forest.png`;
  - `…-escena-tar_basin.png` y `…-escena-waning_peak.png`.
- **Lo que queda para los pasos siguientes:**
  - **Paso 2:** la placa del enemigo y las filas del grupo con sus marcos
    `f-plate` y `f-row`. Con cinco miembros, las filas no caben a 27 px
    sobre los mandos: hay que decidir cómo.
  - **Paso 3:** los mandos en rejilla de 2 × 2 y el aviso de papel. El juego
    tiene cinco entradas (ATACAR, HABILIDADES, BOLSA, HUIR, ORDEN) y el
    sistema, cuatro (LUCHAR, ECO, BOLSA, HUIR). Lo decide Diego.
  - **Paso 4:** los estados, la cola de turnos (que no está en el sistema)
    y las cifras.
