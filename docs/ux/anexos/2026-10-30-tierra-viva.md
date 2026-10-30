# Anexo de diseño — Rediseño «Tierra Viva»: arte del mundo y combate en el mapa

Fecha: 2026-10-30 · Rama: `rediseno/tierra-viva` · Estado: **fases 1 a 4 escritas;
pendiente de la elección de Diego.** No se ha tocado código ni assets del juego.

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

## Fase 4 — Direcciones (pendiente de elección de Diego)

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

Hasta tener respuesta no se escribe contrato ni código.
