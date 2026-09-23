# Guía de continuación — *Ecos de la Tierra*

Redactada el 2026-09-23 para quien siga el proyecto, persona o Claude, **sin
acceso a la skill de dirección de diseño** con la que se hizo lo anterior. Todo
lo necesario para trabajar con el mismo criterio está aquí dentro. Si algo de
esta guía choca con un contrato bloqueado de `docs/ux/anexos/`, **manda el
contrato**, y el choque se avisa en vez de resolverse por cuenta propia.

Orden de lectura en cada sesión:

1. `docs/plan-de-trabajo.md` — punto de retome exacto. Siempre primero.
2. **Esta guía**, la sección de la parte que toca (§5) y las reglas de §1–§4.
3. El anexo de la pantalla en curso, **solo la sección que se necesite**.

---

## 0. Lo que ya existe y cómo se comprueba

| Pieza | Dónde | Cómo se verifica |
|---|---|---|
| Motor de combate, IA por pesos, tabla Q del jefe | `src/battle/`, `src/actors/` | `tools/console_demo.tscn` |
| Pantalla de batalla «Ceniza y Brasa» | `src/ui/battle/` | `tools/verify_usability.tscn` → **16/16** (re-ejecutado 2026-09-23) |
| Tokens de interfaz y de mundo | `src/ui/design_tokens.gd` | `python tools/verify_palette.py tokens` |
| Fuente de mapa de bits | `assets/fonts/ceniza.fnt` | `tools/verify_font.gd` |
| Sprites de monstruos y grupo | `assets/sprites/` | `python tools/verify_palette.py image <png>` → 17/17 limpios |

Ejecutar Godot sin editor (Godot 4.3+ estándar, **no** .NET):

```
<ruta>/Godot_v4.7.2-stable_win64_console.exe --headless --path . res://tools/verify_usability.tscn
```

Las capturas (`*_capture.tscn`, `*_sheet.tscn`) necesitan ventana: se lanzan
**sin** `--headless` y guardan PNG a 480×270. Ese es el medio de salida real
del juego; una captura del editor no vale como prueba.

`tools/verify_palette.py` (Python 3 + Pillow) es nuevo en esta sesión:

| Orden | Qué mide |
|---|---|
| `tokens` | Que `tools/pixel.py` y `design_tokens.gd` declaran la misma paleta |
| `image <png> [--world]` | Que todo píxel es un token; con `--world`, techo de saturación 0,22 |
| `cvd` | Separación de los acentos bajo deuteranopía, protanopía y tritanopía |
| `value <enfermo.png> <purificado.png>` | Que purificado es ≥ 1,5× más luminoso que enfermo en las 4 visiones |

---

## 1. El protocolo, en versión portable

El dueño del proyecto (Diego) trabaja con un protocolo que **no es opcional**.
Tu Claude no lo trae cargado, así que aquí está completo.

### 1.1 Las cuatro etapas, para cada pantalla o sistema nuevo

Cada parte del plan que tenga interfaz o arte abre **su propio anexo** en
`docs/ux/anexos/AAAA-MM-DD-<pantalla>.md` con estas fases, en orden:

1. **Usuarios.** Quién juega (jugador de RPG 2D, 14–30 años, género mixto,
   hispanohablante, nulo en el dominio ambiental; PC con teclado; secundario:
   el docente de Diseño de Interfaces, que evalúa criterio y no solo lógica),
   qué necesita en *esta* pantalla, qué sabe ya.
2. **Comunicación.** Qué decisión toma el jugador aquí (la «decisión
   dominante»), qué información la sostiene y en qué orden, y **qué no va**.
3. **Investigación.** Mínimo **seis fuentes, cada una con una observación
   accionable** con URL. Formato por fuente:
   `observación concreta → decisión aplicable → límite que no copiaré`.
   Fuente que no se pudo abrir: se registra con fecha y motivo. Fuente que no
   aporta nada a esta pieza **no cuenta** para las seis; citarla para llegar al
   número es peor que no citarla. **No se inventan consultas.**
4. **Direcciones y contrato.** Dos o tres direcciones **realmente distintas**
   (que cambien cómo se juega o se lee, no solo el color), **una recomendada**
   y argumentada. **Se pregunta a Diego y se espera respuesta.** La elegida se
   escribe como **contrato bloqueado** con fecha. Desde ahí se cumple: nada de
   color, tipografía, espaciado o efecto fuera del contrato. Si algo no
   funciona, se para y se dice; enmendar exige su permiso explícito y queda
   fechado como «Enmienda N».
5. **Implementación paso a paso**, nunca de una vez: tokens → componente clave
   → esqueleto → resto de componentes → pantalla completa → estados. **Al final
   de cada paso**: se muestra la captura, se cita la cláusula del contrato que
   lo respalda, se dice cuál es el siguiente y **se para a esperar visto
   bueno**.
6. **Verificación medida** (§1.5) y registro en el anexo, **incluidos los
   fallos propios**.

Fuentes de investigación para este juego (elige las que apliquen a la pieza):

- Las que Diego exige para pantallas: `styles.refero.design`,
  `motionsites.ai`, Pinterest, `mobbin.com`, `ui.aceternity.com`, Emil
  Kowalski (`emilkowal.ski`), Taste Skill (`tasteskill.dev`). Muchas son de
  web/app: **se consultan y, si no aplican al juego, se registran como «no
  aplicable» con motivo**. Así se hizo en los dos anexos existentes.
- Fuentes de dominio de juegos que sí aplican: Game UI Database
  (`gameuidatabase.com`), Interface In Game (`interfaceingame.com`), GDC Vault
  (`gdcvault.com`), devlogs en `itch.io`, Lospec (`lospec.com`), el pixelblog
  de Slynyrd (`slynyrd.com`), 80.lv, documentación de Godot.

### 1.2 Design Read — se escribe antes de construir, máximo 8 líneas

```
Registro y audiencia:
Escena de uso (luz, dispositivo, prisa, ánimo):
Tesis visual (una frase específica, no un adjetivo):
Jerarquía y decisión dominante:
Materiales: tipografía, color, imagen, retícula y movimiento:
Repertorio: cada forma que se usa y el único trabajo que hace:
Puntos de entrada: qué invita a empezar a mirar:
Riesgo que se evita: qué cliché de esta categoría no aparecerá:
```

Registros en un juego: **el HUD y los menús se juzgan como producto**
(claridad, velocidad, recuperación de errores). **El arte de título, los
créditos y los momentos de historia se juzgan como marca** (distinción,
memoria, invitación).

### 1.3 Tres reglas que más se olvidan

**Repertorio cerrado.** Cada forma tiene un solo trabajo. Una forma con dos
trabajos confunde; dos formas con el mismo trabajo, sobra una. El recurso más
característico se reserva para los momentos que lo merecen: repetido en todas
partes deja de significar. El repertorio del juego entero está en §3.

**Puntos de entrada, solo si se mira porque se quiere.** Título, créditos,
final, retratos → necesitan algo que invite a mirar (un contraste de escala, una
imagen que entra por un borde, un detalle vivo). Durante la partida — HUD,
diálogo, menú, combate — **el punto de entrada es la tarea**, y todo adorno es
ruido que cuesta errores.

**Mide antes de componer.** Antes de fijar un tamaño de texto o de caja, se
cuentan caracteres por línea y líneas por caja **contra la copia real**. Si no
cabe, se dice antes de maquetar y se propone qué cede.

### 1.4 Prohibido: el diseño de fábrica y el diseño simplón

Está prohibido lo que sale solo cuando se diseña sin criterio: degradados
violetas, esquinas redondeadas (aquí el radio es **0**), sombras difusas,
vidrio, emojis como iconos, tres columnas iguales, texto centrado sin motivo,
Inter/Roboto/Poppins por inercia, animaciones repetidas en todo, copy de
marketing. Si una paleta o una disposición aparece sola, sin un referente de la
investigación que la respalde, es la opción por defecto: se descarta.

**Tampoco vale entregar poco para no equivocarse.** El listón es senior:
jerarquía real, rejilla propia, estados terminados, un momento memorable por
pantalla, y cada decisión de peso con su referente y URL.

### 1.5 Verifica midiendo, no mirando

Lo que se puede comprobar **se comprueba ejecutando algo**: un `.gd` o un `.py`
en `tools/` que da OK o FALLA. Para este juego:

- Captura en el medio de salida: **480×270** y escalado entero a 1440×810.
- **Paleta**: `verify_palette.py image` sobre cada asset nuevo (`--world` para
  el terreno). Cero colores sueltos.
- **Contraste medido sobre el render**, no sobre los tokens: AA (4,5:1) para
  texto, 3:1 para formas que informan, AAA (7:1) para cifras con las que se
  decide.
- **Visión del color**: `verify_palette.py cvd` y `value`. Ver §2.3.
- **Teclado**: todo se alcanza, el foco nunca se pierde, Escape siempre vuelve
  atrás. Seguir el patrón de `tools/verify_usability.gd`.
- **Movimiento**: duración medida cuadro a cuadro (patrón de
  `tools/transition_sheet.gd`) y `reduced_motion` respetado.
- **Estados**: cada estado tiene su vista y se fuerza, no se espera a que salga
  jugando (patrón de `tools/states_sheet.gd`).

Lo que no se puede medir se declara **pendiente**, no se da por bueno.

### 1.6 Reglas de repositorio

- Código en inglés (`PascalCase` con `class_name`, archivos en `snake_case`);
  textos de jugador y comentarios en español.
- La interfaz se construye **en GDScript**, no montada a mano en `.tscn`.
- Ningún color, espaciado ni duración se escribe suelto: **todo sale de
  `DesignTokens`**. Si falta un valor, el contrato no lo contempla: se pregunta.
- Assets de arte generados por script en `tools/gen_*.py` con semilla fija,
  usando la paleta de `tools/pixel.py`.
- **Sin firma de herramientas en nada**: ni `Co-Authored-By: Claude`, ni
  «Generated with Claude Code», ni enlaces a claude.ai, en commits, PR, código
  ni documentación.
- Cada sesión **se cierra actualizando `docs/plan-de-trabajo.md` y con un
  commit**.
- Plantilla de PR obligatoria:

  ```markdown
  ## <Título del trabajo>
  📑 **Feature:** <qué se hizo, en una línea>

  ## Desarrollador
  👷 **Dev:** <tu nombre completo>

  ## Cambios (clases,archivos,etc)
  <archivos tocados y descripción de los cambios>

  ## Pantallazos funcionalidades
  <capturas del antes/después; no son opcionales>
  ```

---

## 2. La identidad, en lo que no se toca

### 2.1 Decisiones cerradas (resumen; el detalle está en el plan)

- Godot 4 + GDScript. PC con teclado primero.
- Viewport **480×270**, escalado **entero**, filtro `Nearest`, ajuste a píxel
  activado en `project.godot`.
- Identidad **«Ceniza y Brasa»**: el mundo está apagado en grises violáceos;
  **la brasa** (`EMBER_*`) es la causa activa del daño; **el verde**
  (`VITAL_*`) significa **solo** «la causa se atajó». Ni una barra de vida, ni
  un botón, ni una hoja decorativa en verde.
- Dirección del mundo **«Vereda»**: mundo contiguo, cámara viva con zona muerta
  28×48 px, cámara a píxel entero, **caminar no se anima**, 60 px/s andar y
  120 px/s correr (1 y 2 px por cuadro). Encuentros visibles. La purificación
  **abre paso y devuelve fauna**.
- Paleta de mundo: tres rampas `SOIL_*`, `WATER_*`, `FLORA_*`, **saturación
  ≤ 0,22**. El follaje enfermo es oliva, **no verde**.
- Radio de esquina 0. Borde 1 px. Fuente de mapa de bits en 11 px (1×) y 22 px
  (2×), sin tamaños intermedios. Espaciado en la escala 2/4/8/12/16/24/32.
- Techo de 300 ms para eventos de interfaz; solo se animan posición, escala y
  opacidad (`modulate`); `DesignTokens.duration()` respeta el movimiento
  reducido.

### 2.2 Lenguaje del entorno — no se contradice nunca

| | Terreno enfermo | Terreno purificado |
|---|---|---|
| Valor | Bajo, hundido | Alto, levantado |
| Silueta | Rota, diagonal, puntiaguda | Limpia, redonda, borde continuo |
| Fauna | Ausente | Presente |

| | Responde al jugador | Es decorado |
|---|---|---|
| Contorno | Sólido, `ASH_050` | Sin contorno |
| Valor | Más claro que su fondo | Más oscuro |

**Regla de negación:** si una clase de objeto responde, **no existe ningún
ejemplar decorativo de esa clase en todo el juego**. Si un tocón se replanta,
no hay tocones de adorno. Nada de carteles «pulsa E».

### 2.3 Hallazgo nuevo, medido el 2026-09-23: el verde y la brasa colapsan con daltonismo

`verify_palette.py cvd` da:

| Par | Normal | Deuteranopía | Protanopía |
|---|---|---|---|
| `VITAL_500` / `EMBER_400` | dE 95,7 · 1,43:1 | dE 28,8 · **1,22:1** | dE 22,0 · 1,85:1 |
| `VITAL_500` / `EMBER_300` | dE 76,7 · **1,08:1** | dE 34,7 · 1,21:1 | dE 22,6 · 1,11:1 |

El verde y la brasa se separan **casi solo por matiz**, y con la ceguera al rojo
y al verde (en torno al 8 % de los varones, sumando sus variantes) el matiz se va. Conclusión, que ya pedía el contrato y
ahora está medida: **«purificado» frente a «causa activa» nunca puede depender
solo del color**. Siempre va acompañado de valor, silueta, fauna o movimiento.
Toda pieza nueva que use los dos acentos pasa `verify_palette.py value` con
cociente ≥ 1,5 **en las cuatro visiones**, y en el anexo se dice qué señal no
cromática la acompaña.

La batalla ya cumple (tres señales redundantes: sprite, marco y franja de
texto). El mundo tiene que cumplirlo desde el primer tile.

---

## 3. Subida de listón: la tesis del juego entero

Hasta ahora cada pantalla tenía su tesis. Falta la que las une, y es la que
convierte un RPG correcto en uno que se recuerda:

> **En Solmira el color no se pinta: se devuelve. Y vuelve con tres cosas —
> verde, vida y sonido—. Eso es un eco.**

El título del juego deja de ser un nombre y pasa a ser la mecánica. Cada
purificación devuelve las tres a la vez: el verde en el terreno, la fauna que
se mueve y el sonido que se abre (§5, partes 1, 3 y 11). Esto no contradice
ningún contrato. Da un criterio para decidir cuando dudes: **¿esto hace que
purificar se note más como un retorno?** Si no, sobra.

### 3.1 Repertorio del juego — lista cerrada, un trabajo por forma

| Forma | Su único trabajo | Dónde **no** aparece nunca |
|---|---|---|
| Verde `VITAL_*` | Lo purificado | Barras, botones, decorado, texto que no sea de purificación |
| Brasa `EMBER_500/400` | La causa activa y el aviso | Adorno |
| `EMBER_300` | Foco y cursor (ya contratado en batalla) | Relleno de zonas grandes |
| Contorno `ASH_050` 1 px | «Esto responde» | Decorado, marcos de UI del mundo |
| **Tramado ordenado 4×4** (enmienda 3) | **Solo** el avance de la purificación | Transiciones, sombras, fondos |
| Fundido a negro 2×120 ms | Solo el cambio de zona | Combate, diálogo |
| Persiana horizontal (propuesta, parte 4) | Solo la entrada al combate | Cualquier otra transición |
| Panel `ASH_800` + borde `ASH_600` 1 px | Todo texto que se lee (diálogo, menú, rótulo) | El mundo en sí |
| Fauna animada | Solo zona purificada | Zonas enfermas (negación) |
| Rótulo de lugar | Solo el nombre de la zona al entrar | Avisos, tutoriales |

Si al revisar una pantalla ves una forma haciendo el trabajo de otra, o una
forma nueva que no está en la tabla, **para y pregunta**.

### 3.2 Enmiendas aprobadas por Diego el 2026-09-23

Nacieron como propuestas P1 y P2 de esta guía. **Ya son contrato**: enmiendas 3
y 4 del anexo de exploración, con sus tokens en `design_tokens.gd`
(`DUR_ZONE_PURIFY`, `PURIFY_DITHER_STEPS`, `BAYER_4X4`, `DIAGONAL_NORMALIZED`).

| # | Propuesta | Qué enmienda | Argumento |
|---|---|---|---|
| **P1** | **La ola de purificación.** Al purificar una zona, el verde no aparece de golpe: avanza desde el lugar del combate en un tramado ordenado de 4×4 (Bayer), en 8 pasos, **900 ms**, y la fauna entra detrás de la ola. | Tabla de duraciones de «Vereda»: la purificación de zona pasa de 300 a 900 ms. | El techo de 300 ms existe porque la batalla se ve cientos de veces. La purificación de zona ocurre **siete veces en toda la partida**: es el momento más raro y más importante del juego. Kowalski lo dice: lo que se ve pocas veces puede ser más expresivo (https://emilkowal.ski/ui/great-animations). El tramado es la técnica propia del pixel art para fundir dos estados sin inventar colores intermedios (https://en.wikipedia.org/wiki/Ordered_dithering): **no añade ni un token**. Con movimiento reducido: salto directo al estado final. |
| **P2** | **Diagonal sin normalizar.** En diagonal, 1 px en X **y** 1 px en Y por cuadro al andar (2+2 al correr). | Aclara «Movimiento del personaje»: la velocidad múltiplo de 60 px/s se cumple **por eje**. | Normalizar la diagonal da 42,4 px/s por eje, que son 0,707 px por cuadro: **fracciones de píxel**, justo lo que el contrato prohíbe porque produce tirones con la cámara a píxel entero. La diagonal un 41 % más rápida es la solución clásica de los juegos de 16 bits y es invisible jugando. |

La purificación del **monstruo** en batalla no cambia: sigue en 300 ms. Con
movimiento reducido, la ola salta directamente al estado final.

---

## 4. Deudas que no están en la tabla de partes

Se atienden cuando su parte lo permita; no se olvidan.

| Deuda | Qué hacer | Cuándo |
|---|---|---|
| **Prueba con personas** de «¿Por qué pierdo?» (anexo de batalla, fila **No verificado**) | Sentar a 3 personas que no conozcan el juego delante del combate del Bosque. No explicar nada. Anotar si deducen que hay que atajar la causa, en cuántos turnos, qué dicen en voz alta. Registrar en el anexo de batalla, con fecha. | **Antes de la parte 3.** Si falla, cambia cómo se diseñan las siete zonas. |
| Fondo de batalla por región + parallax de 3 capas | Pendiente desde el paso 5 del anexo de batalla. Hoy son dos bandas planas. Reutilizar las **mismas rampas** del tileset de la región (coherencia mundo↔combate) y bajar su contraste bajo los paneles. | Parte 4, al conectar mundo y combate. |
| Mobbin y Pinterest sin consultar en el anexo de exploración | Consultar con navegador; si no aportan a un juego, registrarlas como «no aplicable» con motivo. | Primera sesión con navegador. |
| F5 abre el selector de región de pruebas | Mantener `region_select.gd` como herramienta de depuración, no como escena principal. | Parte 10. |
| Numeración de enmiendas del anexo de exploración | Corregida en esta sesión: si la separación dE 9,2 no basta, la siguiente libre es la **5** (la 3 y la 4 son P1 y P2). | Hecho. |

---

## 5. Instrucciones por parte

Formato de cada parte: **para quién y para qué** → contrato → dirección
recomendada → pasos con puntos de control → verificación → hecho cuando.
Las «direcciones recomendadas» de las partes 5 a 12 son **semillas para la
fase 4 del anexo de esa parte**: se presentan a Diego junto con otras una o
dos alternativas reales, y **él elige**. Las referencias marcadas «a verificar»
no se han abierto en esta sesión: se abren y se citan de verdad en la fase 3, o
no se citan.

### Parte 1 — Tokens de mundo, tileset y cámara · EN CURSO

**Estado:** tokens hechos y **aprobados por Diego el 2026-09-23**. `pixel.py` ya
tiene las tres rampas de mundo.

**Para quién y para qué:** el jugador tiene que leer, en cualquier recorte de
pantalla, dónde está el daño y hacia dónde sigue el camino, sin carteles.

**Contrato:** «Vereda» (`docs/ux/anexos/2026-09-14-exploracion-top-down.md`).

**Paso 2a — Catálogo de lo que responde · HECHO 2026-09-23, pendiente de visto
bueno.** Está en el anexo de exploración (fase 5, paso 2a) y, legible por
máquina, en `data/world/interactables.json`. Lo esencial para dibujar:

- **Dos verbos:** usar y empujar. **Hueco de tamaño:** se recoge ≤ 8×8 px, se
  usa o empuja ≥ 16×16 px, nada entre medias.
- Lo que responde es **rectangular** con contorno `ASH_050`; el decorado
  enfermo, **diagonal**; el purificado, **redondo**.
- Clases globales: persona, semillero, hatillo, monstruo, paso cerrado.
- Una clase por región, que es el ensayo de su contramedida: maleza seca
  (Bosque), barrera absorbente (Cuenca), fardo + contenedor (Costa), parcela
  cercada (Llanura), manto reflectante (Cumbre).
- **Los tocones son decorado**, no clase: son la mejor señal de la tala.
- Lo resuelto **desaparece o se transforma**; nunca se queda como adorno.

**Paso 2b — Tileset (componente clave) · EN CURSO.** Ya empezado: el estado,
las mediciones, las iteraciones descartadas y los cuatro pendientes están en el
anexo de exploración, fase 5, paso 2b. **Empieza por ahí, no desde cero.** Lo
que sigue es la especificación original, que ya está implementada:

- Generador nuevo `tools/gen_tiles.py` → `assets/tilesets/world.png`, con
  semilla fija y la paleta de `tools/pixel.py`. Tile de 16 px.
- Por material (suelo, agua, follaje): variante **enferma** y **purificada**, y
  transiciones de borde con el esquema de terreno de Godot 4 «Match Sides»
  (16 piezas por par de materiales): suficiente y mucho más barato que el de
  47.
- Enfermo: rampa `*_700/_500`, siluetas **diagonales y rotas**, sin contorno.
  Purificado: sube un escalón de valor, siluetas **redondas y continuas**;
  follaje y agua purificados en `VITAL_900/700/500`.
- Los objetos del catálogo del paso 2a llevan contorno `ASH_050` y son más
  claros que su fondo.
- **Pista en cada columna:** el camino pisado (`SOIL_300`) y el gradiente de
  daño hacia la fuente (más roto y oscuro cuanto más cerca del monstruo) son
  las dos pistas que se deben poder poner en cualquier franja de 480 px.

**Verificación del paso 2b:**

```
python tools/verify_palette.py image assets/tilesets/world.png --world
python tools/verify_palette.py value <tile_enfermo.png> <tile_purificado.png>   # por material
```

Y una escena `tools/tileset_sheet.tscn` que pinte un mapa de prueba de
30×17 tiles con los tres materiales en los dos estados y capture a 480×270.
Sobre esa captura se decide la decisión abierta: **si dE 9,2 entre materiales
basta o hace falta la enmienda 5.** Criterio medido: tres personas nombran el
material de 10 recortes de 64×64 sin error, o no basta.
**Punto de control con Diego.**

**Paso 3 — Esqueleto: cámara.** `Camera2D` con `drag_*_margin` equivalentes a
28×48 px, sesgo inferior `CAMERA_BIAS_DOWN`, anticipación `CAMERA_LOOKAHEAD`,
posición redondeada a entero. Prueba `tools/verify_camera.gd`: mueve al
personaje 600 cuadros en las 8 direcciones y **falla** si en algún cuadro la
posición de la cámara o la del personaje no es entera, o si el personaje sale
de la zona muerta.

**Hecho cuando:** tileset aprobado, capturas en el anexo, `verify_camera` en
verde, dE resuelto, plan actualizado y commit.

### Parte 2 — Movimiento, colisiones y transición entre zonas

**Para qué:** moverse no debe costar pensamiento. Se pulsa y se mueve, se suelta
y se para.

**Contrato:** «Vereda» + enmienda 4 (diagonal sin normalizar).

- Acciones de entrada nuevas en `project.godot`: `run` (Mayús izquierda) e
  `interact` (reutiliza `confirm`). Nada de teclas nuevas para lo que ya existe.
- **Sin** `move_and_slide` con velocidades libres: mover píxel a píxel con
  `test_move` por eje, para que la posición siga entera al deslizar contra una
  pared. Deslizar en esquinas: si la diagonal choca en un eje, sigue en el otro.
- Transición de zona: fundido a negro 120 ms + 120 ms, lineal
  (`DUR_ZONE_FADE`); rótulo del lugar 160 ms `ease-out` (`DUR_PLACE_LABEL`),
  panel `ASH_800`, texto 1×, arriba a la izquierda con margen `SPACE_8`, se va
  solo a los 2 s. Con movimiento reducido: sin fundido, corte directo.
- Estado global en un autoload `GameState` (grupo, bolsa, zona, banderas de
  purificación): lo necesita la parte 4 y la 9.

**Verificación:** `tools/verify_movement.gd` → posición entera en cada cuadro,
velocidad por eje de 1/2 px por cuadro, cero cuadros de aceleración (se mueve
en el mismo cuadro de la pulsación), duración del fundido medida.

### Parte 3 — Las siete zonas

**Para qué:** que el paisaje cuente el problema ambiental antes que cualquier
texto, y que el jugador sepa siempre hacia dónde seguir.

**Subdividir: una zona por sesión**, en este orden: Valdehoja → Bosque de las
Cenizas → Cuenca de Alquitrán → Costa Quebrada → Llanura Marchita → Cumbre
Menguante → Cripta de la Avaricia. Anotar la subdivisión en el plan.

**Mapas como texto.** Se recomienda escribir cada zona como mapa ASCII en
`data/maps/<zona>.txt` (un carácter por tile, leyenda en cabecera) que un
script convierte en `TileMapLayer`. Así se puede leer, auditar y comparar en un
diff. La alternativa es pintar en el editor de Godot; decidirlo con Diego en la
primera zona.

**Dirección recomendada para las zonas:**

- **Valdehoja arranca gris salvo una cosa: el jardín de Yara**, el único verde
  del mundo al empezar. El jugador aprende qué significa el verde **antes** del
  primer combate, sin un solo texto. Semilla a verificar en fase 3: *Gris*, de
  Nomada Studio, donde el color que vuelve es la progresión
  (https://store.steampowered.com/app/683320/GRIS/).
- **Valdehoja es el marcador de progreso.** Cada región purificada devuelve
  verde y fauna también a una parte del pueblo. Volver a casa enseña cuánto se
  lleva hecho, sin barra de progreso.
- Cada zona tiene: la **fuente del daño** (donde vive el monstruo, lo más roto y
  oscuro), un **gradiente** que se aclara al alejarse, **un paso cerrado** que
  la purificación abre (contrato) y **un único hito visual** reconocible
  desde lejos: la silueta del árbol quemado mayor, la torre de la refinería, la
  montaña de basura, el silo, el glaciar partido.
- Diseño **por columnas**: cada franja de 480 px contiene al menos una pista.

**Verificación por zona** (`tools/verify_zone.gd <zona>`):
1. Búsqueda en anchura desde la entrada: la salida es **inalcanzable** con la
   zona enferma y **alcanzable** tras purificar.
2. Cada franja vertical de 480 px contiene ≥ 1 tile con dato `clue = true`
   (camino pisado, gradiente o hito).
3. Ningún tile decorativo pertenece a una clase del catálogo de la parte 1.
4. `verify_palette.py image --world` sobre la captura completa de la zona.

### Parte 4 — Encuentros y paso mundo ↔ combate

**Para qué:** que el jugador **decida** si pelea, y que la pelea continúe el
mundo sin romperlo.

- El monstruo patrulla **dentro de su zona de daño**; su sola presencia explica
  el terreno que lo rodea. Contacto → combate.
- **Entrada al combate** (dirección recomendada, a contratar): persiana
  horizontal en franjas de 8 px que se cierra desde la fila del monstruo,
  ≤ 300 ms. Otra familia distinta del fundido y del tramado (§3.1).
- El combate usa el **fondo de la región** (deuda de §4) con las mismas rampas
  del tileset.
- `GameState` entra al combate y sale actualizado: PV, energía, bolsa,
  estados. Huir devuelve al mapa con el monstruo aún ahí y **1 s de gracia**
  sin nuevo contacto, para que no se encadene el combate.
- Victoria → vuelta al mapa → **ola de purificación** (P1) desde el punto del
  combate → se abre el paso.

**Verificación:** prueba que entra, gana y sale, y compara el estado del grupo
antes y después (idéntico al resultado del combate); prueba de huida con los
tiempos de gracia; transición medida.

### Parte 5 — Diálogos y retratos

**Anexo nuevo.** **Registro:** lectura obligada, así que se juzga como producto.

**Medido para esta sesión, a confirmar con `verify_font`:** la fuente mide
6 px por carácter. Con un panel a ancho completo, margen `SPACE_8`, relleno
`SPACE_8` y retrato de 48 px + `SPACE_8` de separación, quedan **392 px de
texto = 65 caracteres por línea**. Con 3 líneas de 12 px, nombre y relleno, el
panel mide **64 px de alto** (24 % de la pantalla). **Regla medible: ninguna
caja de diálogo supera 3 líneas de 65 caracteres.** Script
`tools/verify_dialogue.py` que la comprueba sobre todos los textos.

- Textos en datos (`data/dialogue/*.json`), nunca escritos en el código.
- Efecto de máquina de escribir rápido y opcional; `confirm` completa la línea
  y un segundo `confirm` avanza. Con movimiento reducido: texto completo
  directo.
- Retratos 48×48 generados por script con la paleta, **2 expresiones** por
  personaje (neutra y la que defina su arco), no más.
- **Momento memorable recomendado:** la etiqueta del nombre del Comandante Rasgo
  va en **brasa** mientras sirve a la Compañía Áurea, porque la brasa significa
  «causa activa». En su redención, la etiqueta pasa a ceniza. Es un cambio de
  un solo token que cuenta su arco sin una línea de texto.

### Parte 6 — Progresión

**Para qué:** que el jugador sepa qué ha ganado y qué le falta.

- Según la propuesta (§3.4), el Conocimiento Ambiental desbloquea las
  habilidades ecológicas. Los compañeros se unen **tras** su región: Bruma
  (Bosque), Coral (Cuenca), Nix (Costa), Suri (Llanura).
- Banderas en `GameState`: región purificada, compañero unido, habilidades
  desbloqueadas. Una sola fuente de verdad que leen el mundo, el menú, el
  guardado y el título.
- **Sin barras de experiencia nuevas en el mundo.** El progreso se lee en
  Valdehoja (parte 3) y en el cuaderno (parte 8).

### Parte 7 — Puzzles ambientales

**Anexo nuevo.** Esta es la parte que más puede arreglar la deuda de la prueba
con personas.

**Dirección recomendada: el puzzle es el ensayo de la contramedida.** El puzzle
de cada región es **la misma idea que la habilidad ecológica que vence al jefe,
pero en el mundo y sin presión**: en el Bosque se desbrozan haces de maleza
seca para abrir una línea cortafuegos que el fuego no cruza; en la Cuenca se
empujan barreras absorbentes hasta cerrar el canal; en la Costa se empujan los
fardos a su contenedor; en la Llanura se rotan los cultivos de las parcelas
cercadas; en la Cumbre se despliega el manto sobre la roca oscura. Las clases y
sus reglas ya están fijadas en el catálogo (parte 1, paso 2a). Resolverlo **es** el Conocimiento Ambiental que desbloquea la
habilidad. Así, cuando el jugador llega al combate, ya ha hecho con las manos lo
que el combate le pide, y «¿por qué pierdo?» tiene una respuesta que ya conoce.
Semilla a verificar en fase 3: el esquema de introducir, practicar, complicar y
rematar una mecánica que Nintendo usa en sus niveles (buscar el análisis de Game
Maker's Toolkit sobre *Super Mario 3D World*).

- Solo con objetos del catálogo de la parte 1 (regla de negación).
- Sin textos de instrucción: se enseña por disposición.
- Cada puzzle tiene un estado **atascado** reconocible y una salida: si el
  jugador falla tres veces, Yara o el compañero de la región dan una pista
  **en diálogo**, no en un cartel.

### Parte 8 — Menú fuera de combate

**Anexo nuevo.** **Registro:** producto.

- **Dirección recomendada: «cuaderno de campo».** Pestañas Grupo · Bolsa ·
  Habilidades · **Ecos**. Ecos es el registro de lo devuelto: por región, qué
  fauna volvió y qué se purificó. Refuerza la tesis sin añadir mecánica.
- Reutilizar el menú genérico de la batalla (`action_menu.gd`) y su recorrido
  por teclado. Mismos tokens, mismo cursor `EMBER_300`.
- **Estados con vista propia:** bolsa vacía, habilidad sin energía (se lista,
  no desaparece: lección ya aprendida en la batalla), región no visitada en
  Ecos (silueta en `ASH_600`, sin nombre).
- Verificación: extender el patrón de `verify_usability.gd` al menú.

### Parte 9 — Guardado

**Para qué:** que el jugador pueda irse sin miedo a perder progreso.

- **Dirección recomendada: el punto de guardado es un brote**, un tile
  purificado diminuto. Es coherente con la regla del verde: guardar ocurre en
  tierra ya curada. El primero está en el jardín de Yara.
- JSON en `user://save.json` + autoguardado al cambiar de zona. Versión del
  formato dentro del archivo.
- **Estados:** guardado correcto (rótulo 160 ms), archivo corrupto (mensaje y
  opción de empezar de nuevo, **nunca** un cierre del juego), sin partida.
- Verificación: ida y vuelta guardar → cargar → comparar `GameState` campo a
  campo; archivo corrupto a propósito → no se cierra el juego.

### Parte 10 — Título y opciones

**Anexo nuevo. Registro: marca** en el título, **producto** en opciones.

- **Dirección recomendada para el título:** una vista viva de Valdehoja en su
  estado de la partida guardada. En partida nueva, todo gris salvo el jardín de
  Yara. Con tres regiones purificadas, el título muestra ese verde. **La
  pantalla de título cambia a medida que el jugador devuelve el mundo.** Nombre
  del juego en la fuente a 2×, con un solo punto de entrada claro. Menú: Continuar
  · Nueva partida · Opciones · Salir.
- **Opciones (accesibilidad, obligatorias):** movimiento reducido (hoy solo
  existe en `project.godot`), velocidad del texto, volumen por bus (música,
  ambiente, efectos), reasignación de teclas, escala de ventana entera.
- `scenes/main.tscn` pasa a abrir el título. El selector de región queda como
  herramienta de depuración.
- Punto de entrada comprobable: en la captura del título, lo más contrastado
  de la pantalla es el nombre del juego o el verde; se mide sobre el render.

### Parte 11 — Audio

**Anexo nuevo.**

- **Dirección recomendada: el sonido también es un eco.** El ambiente de una
  zona enferma suena **apagado**: bus «Ambiente» con
  `AudioEffectLowPassFilter` cerrado (~700 Hz, a ajustar de oído y dejar
  anotado). Al purificar, el filtro se abre **al ritmo de la ola** (P1) y
  entran los sonidos de fauna. Referencia técnica:
  https://docs.godotengine.org/en/stable/classes/class_audioeffectlowpassfilter.html
- Buses: Música, Ambiente, Efectos, Interfaz. Sonidos de interfaz cortos
  (< 80 ms): cursor, confirmar, cancelar, sin energía.
- Solo audio con licencia libre y **registrada**: `docs/licencias-audio.md` con
  autor, URL y licencia de cada archivo. Sin licencia clara, no entra.
- Ningún sonido lleva información que no tenga también una señal visual.

### Parte 12 — Final y créditos

**Registro: marca.** Es la pieza que se mira porque se quiere.

- **Dirección recomendada:** tras purificar a la Sombra de la Avaricia, una
  última ola recorre el mundo entero. Los créditos son **un recorrido de cámara
  por las siete zonas ya verdes y con fauna**, con los nombres encima en
  paneles. Los créditos enseñan lo que el jugador devolvió.
- En los créditos, el equipo con sus nombres reales y las licencias de audio y
  fuentes de terceros. Sin firmas de herramientas.

---

## 6. Cómo se cierra cada sesión

1. Verificación de la parte ejecutada y su salida pegada en el anexo.
2. `python tools/verify_palette.py tokens` en verde.
3. `verify_usability.tscn` sigue en 16/16 (no se rompió la batalla).
4. `docs/plan-de-trabajo.md`: parte marcada, punto de retome movido, lo que
   quedó a medias anotado.
5. Commit en español, en imperativo, **sin firma de herramientas**.
6. Si hay PR: plantilla de §1.6 con capturas reales.
