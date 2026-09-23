# Anexo de diseño — Exploración top-down de *Ecos de la Tierra*

Fecha: 2026-09-14
Pantalla: mundo explorable en vista cenital (`scenes/world/`, aún inexistente).

Estado del proyecto al abrir el anexo: el combate está terminado y verificado
(motor + interfaz, dirección «Ceniza y Brasa», anexo del 2026-09-13). El mundo
**no existe**: `scenes/world/` está vacía y `assets/tilesets` no tiene un solo
tile. Hoy se entra a los seis combates desde un selector de región de
depuración (`src/ui/region_select.gd`), que es un menú, no un mundo.

**La exploración quedó expresamente fuera del contrato de la batalla**
(«Fuera de alcance: exploración top-down y tilemaps de mundo»). Por eso este
anexo abre contrato propio. Hereda la identidad visual «Ceniza y Brasa» —sería
absurdo que el mundo y el combate no se parezcan— pero las decisiones de
cámara, escala de tile, movimiento y lectura del paisaje son nuevas y se firman
aquí.

---

## Fase 1 — Identificación de los usuarios

### Usuario primario — el jugador

Es **el mismo del anexo de batalla**, y no se vuelve a levantar la ficha entera:
jugador de RPG 2D de consola portátil, 14-30 años, género mixto,
hispanohablante, experiencia intermedia con tecnología, alto en «jugar un RPG»
y **nulo en el dominio real del juego**. Plataforma confirmada en aquel
contrato: **PC con teclado**.

Lo que cambia es **la tarea**, y cambia lo suficiente como para que sea otra
pantalla:

| | En la batalla | En la exploración |
|---|---|---|
| Postura | Quieto y deliberando por turnos | En movimiento continuo, sin pausa |
| Qué decide | Qué acción tomo en este turno | A dónde voy ahora |
| Ritmo | Lo marca el juego, turno a turno | Lo marca el jugador, y puede pararse a mirar |
| Duración de la mirada | Segundos por decisión | Minutos seguidos, con la vista barriendo |
| Fracaso | Pierde el combate | **Se pierde**: no sabe a dónde ir, y abandona |

- **Necesidad real, en sus palabras.** «Quiero ver el mundo, entender a dónde
  tengo que ir y con qué puedo interactuar, sin que un cartel me lo diga.»
- **Nivel de habilidad en el dominio, precisado para esta pantalla.** Aquí está
  la observación que gobierna el anexo entero. El anexo de batalla identificó la
  brecha —nadie llega sabiendo que a la Llama de la Deforestación se la ataja
  con una Línea Cortafuegos— pero la pantalla de batalla **solo puede cerrarla a
  golpes**: el jugador descubre la causa fallando y reintentando. La exploración
  es la única superficie donde el mundo puede **enseñar la causa antes de que el
  combate la exija**. Quien atraviesa un robledal de tocones cortados y ve el
  humo antes de pelear con la Llama, llega al combate con una hipótesis. Quien
  llega por un menú, llega a ciegas.

**Condiciones reales de uso.** PC con teclado, viewport 480×270 escalado a
1440×810 (3× entero). Sesiones largas, luz variable. Frecuencia altísima: es la
pantalla donde el jugador pasa **la mayor parte del tiempo**, así que todo lo
que se repita —un paso, una transición de zona, un cuadro de diálogo— debe ser
corto o poder saltarse.

### Usuario secundario — el evaluador

Sin cambios respecto al anexo de batalla: docente de Diseño de Interfaces de
Software, que necesita ver criterio de interfaz y no solo lógica. Obliga a que
cada estado tenga su vista y a dejar este anexo como entregable.

### Datos que faltan y se preguntan, no se inventan

1. **Alcance de mundo.** Una región jugable de muestra o las cinco. Cambia si el
   mundo se dibuja a mano tile a tile o se genera por script, y cambia si hay
   mapa general entre regiones o no.
2. **Cómo se entra al combate.** Encuentros aleatorios al caminar (Pokémon) o
   enemigos visibles en el mapa a los que se decide acercarse (Chrono Trigger,
   Zelda). Es una decisión de diseño con consecuencia directa sobre el mensaje
   del juego, así que va a la fase 4 como parte de las direcciones, con
   recomendación argumentada.

Ambos se preguntan en la fase 4. No se elige por mí.

---

## Fase 2 — Análisis de la comunicación

| Necesidad del usuario | Qué debe comunicar la interfaz | Cómo se sabe que llegó |
|---|---|---|
| «¿Dónde estoy?» | Región y lugar concreto, sin abrir menú | Lo dice en voz alta al entrar a una zona nueva |
| «¿A dónde voy?» | La salida transitable, distinta del decorado | Encuentra la salida en menos de 10 s sin recorrer el borde |
| «¿Con qué puedo interactuar?» | Qué objeto responde y cuál es paisaje | Se acerca solo a lo que responde, sin probar todo |
| «¿Qué le pasó a esta tierra?» | El daño ambiental, leído en el paisaje | Nombra la causa antes de entrar al combate |
| «¿Qué he arreglado ya?» | Lo purificado no vuelve a verse enfermo | Reconoce por dónde pasó sin abrir un mapa |
| «¿Me van a atacar?» | Dónde hay peligro y si puedo evitarlo | Decide acercarse o rodear, y no se siente emboscado |

### Decisión dominante

**A dónde voy ahora, leyendo en el paisaje qué está dañado y qué ya se
purificó.** Una sola, y es doble solo en apariencia: en este juego «a dónde voy»
y «qué está dañado» son la misma pregunta, porque el daño **es** la señalización
del mundo. El humo marca el camino al Robledal Quemado igual que un cartel, pero
además enseña la causa.

Esto ata la exploración al mismo eje que la batalla. Allí la información que
carga el mensaje era `Monster.is_purified`; aquí es el **estado de purificación
de la zona**, y usa el mismo acento verde. El jugador que atraviesa una zona ya
purificada ve el único color saturado del juego y entiende, sin texto, que eso
lo hizo él.

### Jerarquía de la información

1. **El paisaje y su estado de daño.** Casi toda la pantalla. No es fondo: es el
   contenido.
2. **El personaje y hacia dónde mira.** Debe encontrarse de un vistazo sobre un
   mundo apagado.
3. **Lo interactuable, cuando está al alcance.** Aparece al acercarse, no antes.
4. **El nombre del lugar.** Al entrar, y se va solo.
5. **Todo lo demás** —menú, inventario, mapa— **bajo demanda, con la pantalla
   limpia mientras se camina.**

### Qué NO va en la pantalla

- **HUD permanente de PV y energía.** En batalla es la fila 2 de la jerarquía;
  aquí es ruido: fuera de combate no se decide nada con esa cifra. Va al menú.
- **Minimapa fijo en una esquina.** Roba una esquina de 480×270 —un 8 % de la
  pantalla— para resolver un problema que se resuelve mejor haciendo el mapa
  legible. Si el jugador necesita minimapa para no perderse, el mapa está mal
  dibujado.
- **Marcador de misión con flecha al objetivo.** Mata la decisión dominante: si
  una flecha dice a dónde ir, el jugador deja de leer el paisaje, y leer el
  paisaje es el juego.
- **Cartel de «pulsa E para interactuar» sobre cada objeto.** Repetido cientos
  de veces por sesión. Se resuelve con una señal de forma, no con texto.
- **Rejilla de tiles visible.** Convención de editor, no de jugador.

---

## Fase 3 — Investigación profunda

Consultada el 2026-09-14. Una observación accionable por fuente. Las URL son las
que se cargaron de verdad; lo que no cargó está en su tabla, con motivo y fecha.

### Nota de método, antes de la primera tabla

Seis de las siete fuentes obligatorias del protocolo son catálogos de **interfaz
web y de aplicaciones móviles**. Esta pantalla no es una interfaz: es un
**paisaje jugable de 480×270 píxeles**, y casi toda su superficie es contenido
diegético, no controles. Forzar la analogía produciría observaciones falsas
(«el tile de hierba es como una tarjeta de KPI»), así que no se fuerza.

De cada fuente web se saca **solo el principio que de verdad se transfiere**
—jerarquía, contención del acento, criterio de movimiento, consistencia de
forma— y se dice explícitamente que es un principio y no un patrón. La fuente
que no transfiere nada se marca como **no aplicable, con motivo**, en vez de
rellenarla con una frase decorativa.

El peso real de esta fase lo cargan las **nueve fuentes de dominio** del bloque
B: cámara, tile, afordancia, encuentros, paisaje dañado y transición. Son las
que van a cambiar decisiones.

---

### A. Fuentes del protocolo

#### A.1 — Accesibles, con observación accionable

| Fuente | URL | Observación accionable |
|---|---|---|
| Taste Skill | https://www.tasteskill.dev/docs | Dos bloqueos que ya rigen en batalla y que aquí se ponen a prueba de verdad: **«un acento en toda la página»** («a warm-grey site does not suddenly get a blue CTA in section 7») y **«un solo sistema de radio: todo agudo, todo suave o todo pastilla, con la excepción documentada cuando se mezcle»**. Transferencia literal: el verde `vital_500` no puede aparecer en el mundo salvo en zona purificada — ni en un arbusto sano de decorado, ni en un cartel, ni en el marcador del personaje. Un mundo top-down tiene mucha más superficie que una pantalla de batalla, así que el riesgo de fuga del acento es mucho mayor y hay que auditarlo por conteo de píxeles, no por vista. |
| Emil Kowalski — *Great animations* | https://emilkowal.ski/ui/great-animations | Regla que **cambia una decisión concreta de esta pantalla**: «never animate keyboard initiated actions. These actions are repeated sometimes hundreds of times a day, an animation would make them feel slow». Caminar es exactamente eso: una acción de teclado repetida miles de veces por sesión. Consecuencia: el **paso del personaje y el seguimiento de cámara no llevan curva de entrada**; el techo de 300 ms del contrato de batalla es un techo para eventos, no un permiso para amortiguar el movimiento continuo. Se conserva de la misma fuente el `ease-out` para lo que entra, la interrumpibilidad y el límite a `transform`/`opacity`. |
| Emil Kowalski — *Animations on the Web* (temario) | https://animations.dev/ | El módulo 4 separa «buena» de «excelente» por **orquestación**: no la duración de cada pieza, sino el orden en que entran. Transferible al único momento largo de esta pantalla, la purificación de una zona: si el verde vuelve de golpe en toda la pantalla, es un cambio de paleta; si vuelve escalonado desde un origen, es un acontecimiento. Queda como material para la fase 4, no como decisión. |
| Refero Styles | https://styles.refero.design/ | Clasifica sistemas por **metáfora atmosférica** y no por componente: «midnight precision instrument» (Linear), «white room with a single blue» (Apple), «clinical blueprint on frosted paper», «sunlit honey editorial». Aplicado igual que en el anexo de batalla: las direcciones de la fase 4 se nombrarán por **carácter del paisaje**, no por mecánica ni por widget, para que la elección sea de atmósfera. Nota: «a white room with a single blue» es, descrita en otro idioma, la misma estrategia que «Ceniza y Brasa» — base neutra y un solo saturado. Refuerza que la herencia del contrato de batalla no es un capricho local. |
| Aceternity UI | https://ui.aceternity.com/components | Dos familias que sí tienen equivalente aquí, y una que no. **Sirve:** los fondos por capas (*Aurora*, *Cloud Shader*, *Noise*, *Scales*) confirman que la atmósfera se carga en una capa aparte que no compite con el primer plano — en un mapa top-down eso es una capa de niebla o humo por encima del tilemap y por debajo de las entidades, con su propio nivel de contraste. **Sirve más:** *Card Spotlight* y *Canvas Reveal Effect* son **revelado por proximidad**: la información aparece cuando el cursor se acerca, no antes. Es exactamente el patrón que la fase 2 pide para lo interactuable («aparece al acercarse, no antes»), y confirma que la señal debe vivir en el objeto, no en un HUD fijo. **No sirve:** *Meteors*, *Sparkles*, *Shooting Stars* — movimiento ambiental continuo que a 480×270 y con paleta cerrada sería ruido. |

#### A.2 — Accesible, pero no aplicable

| Fuente | URL | Motivo | Fecha |
|---|---|---|---|
| `motionsites.ai` | https://motionsites.ai/ | La página **sí cargó** y el catálogo es público (Veyra Electric, Urban Jungle, Liquid Glass Agency, Pulse 3D…), pero es un banco de *prompts* para generar landings con IA. No expone duraciones, curvas ni criterios de movimiento, y su vocabulario —*liquid glass*, fondos animados, 3D— es incompatible por definición con pixel art de paleta cerrada a escala entera. **No se le fuerza una observación.** Se marca no aplicable y el criterio de movimiento lo cubre Kowalski, que sí es aplicable. | 2026-09-14 |

#### A.3 — Inaccesibles

| Fuente | Motivo | Fecha |
|---|---|---|
| `mobbin.com` | Exige sesión iniciada y el acceso previsto es vía Chrome. **La extensión de Chrome no está conectada** en esta sesión (`Browser extension is not connected`), así que no hubo forma de abrirla. No se consultó. | 2026-09-14 |
| `pinterest.com` | Mismo motivo: el acceso previsto es la sesión del usuario en Chrome, y la extensión no respondió. Sin sesión, Pinterest devuelve 403 al acceso directo, tal como ya se registró el 2026-09-13. | 2026-09-14 |

**Balance honesto del bloque A:** de las siete fuentes obligatorias, **cuatro
dieron observación accionable** (Taste Skill, Kowalski en dos páginas, Refero,
Aceternity), **una se descartó por no aplicable** con motivo escrito y **dos
quedaron bloqueadas por falta de sesión de navegador**. No se llega a seis
dentro de este bloque, y no se disimula. El mínimo de seis se cumple contando
el bloque B, que es donde el protocolo permite —y aquí, exige— fuentes propias
del medio.

---

### B. Fuentes de dominio

Nueve fuentes, tratadas con el mismo rigor: URL exacta y observación accionable.

#### B.1 — Cámara en RPG 2D top-down

| Fuente | URL | Observación accionable |
|---|---|---|
| Godot — `Camera2D` (documentación de clase) | https://docs.godotengine.org/en/stable/classes/class_camera2d.html | Los nombres y los valores por defecto, para no inventarlos: `position_smoothing_enabled` = **`false`**, `position_smoothing_speed` = **`5.0`** (píxeles por segundo), `drag_horizontal_enabled` y `drag_vertical_enabled` = **`false`**, `drag_left/right/top/bottom_margin` = **`0.2`** (fracción del semiviewport), `limit_enabled` = `true` con límites en ±10 000 000, `limit_smoothed` = `false`. **Dato decisivo: `Camera2D` no tiene ninguna propiedad de ajuste a píxel.** Nada en la cámara redondea su propia posición. Quien crea que «Godot ya lo hace» se equivoca, y ahí nace el problema de la rejilla rota. |
| Blobsmith — cuatro causas de costuras entre tiles en Godot 4 | https://blobsmith.itch.io/blobsmith-lite/devlog/1631794/thin-lines-between-tiles-in-godot-4-paste-your-projectgodot-and-find-which-of-the-four-causes-is-yours | La solución concreta que sustituye al «Enable Pixel Snap» de Godot 3, que **ya no existe** y que sigue apareciendo en tutoriales viejos: `rendering/2d/snap/snap_2d_transforms_to_pixel` y `rendering/2d/snap/snap_2d_vertices_to_pixel`, **ambas apagadas por defecto**. Tercera causa: `TileSetAtlasSource.use_texture_padding`, que viene en `true` y se solapa con los márgenes dibujados a mano en el atlas. Cuarta: la costura pintada dentro del propio arte, que ninguna configuración arregla. |
| Demo de cámara suave con píxel perfecto en Godot 4 (voithos) | https://github.com/voithos/godot-smooth-pixel-camera-demo | La técnica completa, por si se quiere suavizado **sin** romper la rejilla: se renderiza el mundo en un `SubViewport` **un píxel más grande que el viewport visible** (322×182 para mostrar 320×180), la cámara mantiene una posición «virtual» decimal, su `global_position` real se ajusta a entero, y **el resto decimal se aplica como desplazamiento al `Sprite2D` que muestra el `ViewportTexture`**. Con `Snap 2D Vertices to Pixel` activo, filtro `Nearest` e interpolación de física con `physics_jitter_fix = 0`. Limitaciones declaradas por el propio autor: todos los hijos del `SubViewport` se ajustan a entero, el parallax suave exige un `SubViewport` por capa, y la escala tiene que ser múltiplo entero. |
| Foro de Godot — «Smooth camera in pixel perfect game» | https://forum.godotengine.org/t/smooth-camera-in-pixel-perfect-game/112586 | La frase que zanja el debate y que conviene tener escrita antes de la fase 4: **«If your camera or parallax is moving in subpixels then your game isn't pixel perfect anyway.»** El hilo **no llega a consenso**: quien quiere movimiento suave acepta subpíxel, y quien quiere rejilla intacta acepta que la cámara avance a saltos de un píxel. No hay tercera vía gratis. Es una disyuntiva de dirección, no un problema técnico por resolver. |
| Bitdecay Games — devlog de cámara de *Odd Verdure* | https://bitdecaygames.itch.io/odd-verdure-jam/devlog/481096/cameras | Cifras reales de zona muerta en un juego 2D de baja resolución, no teoría: **20 px de ancho × 28 px de alto** en la versión de jam, ampliada a **48 px de alto** en la versión final «para dar holgura sin descentrar al jugador», con **sesgo hacia abajo** para que se vea más terreno por delante. Anticipación: la zona muerta se desplaza hasta **30 px** según la velocidad, interpolada, y vuelve a neutro a **30 px/s** cuando el personaje se para. Un *raycast* hacia abajo suprime la anticipación en caídas cortas, porque si no la cámara «rebota» en cada escalón. |

**Cotejo contra el proyecto, hecho y no supuesto.** Se leyó `project.godot`
(2026-09-14). Están puestos `window/stretch/mode="viewport"`,
`window/stretch/scale_mode="integer"`,
`rendering/textures/canvas_textures/default_texture_filter=0` (Nearest) y
`window/size` 480×270 con anulación de ventana a 1440×810. **Faltan las dos
claves de ajuste a píxel**: no existe ninguna entrada
`rendering/2d/snap/snap_2d_transforms_to_pixel` ni
`snap_2d_vertices_to_pixel`. En la batalla no se notó porque nada se desplazaba
en subpíxel; con cámara en movimiento y un tilemap, sí se va a notar. Se deja
registrado como hallazgo técnico, no como decisión: qué se hace con él depende
de la disyuntiva del hilo de Godot, y esa la resuelve la fase 4.

#### B.2 — Escala de tile y densidad de detalle a 480×270

| Fuente | URL | Observación accionable |
|---|---|---|
| SLYNYRD — *Pixelblog 20: Top Down Tiles* | https://www.slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles | Cuatro reglas con número. **Tamaño:** 16×16 px es el estándar y «anything over 32×32px seems like overkill». **Color por tile:** pocos colores; «too many colors and the texture will become blurry», y el contraste fuerte dentro de un patrón «may result in displeasing noise». **Equilibrio:** repartir el peso visual de forma homogénea dentro del tile y hacer que los grupos de píxeles crucen el borde y envuelvan, que es lo que oculta la costura. **Vecindad:** «a busy texture next to another busy texture may exhaust the eyes» — nunca dos texturas cargadas juntas; se alterna zona texturada con **espacio negativo**, y la monotonía de un único tile de hierba se rompe con variantes ocasionales, no con más detalle en el tile base. **Lo que esta fuente NO cubre, y se dice:** ni alturas, ni acantilados, ni distinción de transitable frente a bloqueado. Eso lo cubre B.3. |
| Búsqueda sobre tiles de GBA (nivel de extracto, ver aviso) | https://www.pokecommunity.com/threads/times-extensive-tiling-tutorial.345695/ · https://gbadev.net/forum-archive/thread/9/4097.html | Dato de hardware que conviene tener presente: en GBA el tile nativo es de **8×8 px**, y el «tile» de 16×16 de Pokémon Rubí/Zafiro y Fire Red es en realidad un **metatile de cuatro tiles de 8×8**. Consecuencia práctica: la unidad de composición del arte puede ser 16, pero la unidad de **variación** que aquellos juegos manejaban era 8, y de ahí sale su riqueza sin ruido. **Aviso de honestidad:** la página de PokéCommunity devolvió **HTTP 403** al intentar cargarla; este dato procede de los extractos del buscador, no de la página completa, y se marca como tal. |

**Cuenta que sale de aquí, y que hay que mirar de frente.** A 480×270 con tiles
de 16 px caben **30 × 16,875 tiles** — no 17 enteros: la última fila queda
cortada a 14 px. Un mapa que se diseñe pensando en «17 filas» tendrá siempre
una fila mutilada arriba o abajo. Con la regla de SLYNYRD de alternar textura y
espacio negativo, 30×17 tiles es un lienzo **pequeño**: una habitación de
interior cabe entera, pero un claro de bosque legible se come media pantalla.
Es un dato de encuadre para la fase 4, no una decisión.

#### B.3 — «Esto es interactuable» sin poner un cartel

| Fuente | URL | Observación accionable |
|---|---|---|
| Emilia Schatz (Naughty Dog) — *Defining Environment Language for Video Games*, en 80.lv | https://80.lv/articles/defining-environment-language-for-video-games | Tres recursos, en orden de potencia. **Uno, forma:** «round shapes evoke safety and well-being» y carecen de afordancia; «rectangular shapes are solid, stationary and powerful» y sí la sugieren; lo diagonal y puntiagudo la niega evocando peligro. **Dos, aislamiento:** el objeto interactuable se destaca siendo *el único* de su forma en su vecindad — «the object that affords climbing up is highlighted by making it the only rectangular shape in close vicinity». **Tres, y es la más útil aquí, negar la afordancia a propósito:** al decorado se le quita contraste, se le ensucia la silueta y se le dan bordes irregulares, para que el jugador **no** intente interactuar. La clave del apartado es que casi todo el trabajo está en negar, no en señalar. |
| Nic Phan — *Affordances in Game Level Design* | https://www.nicphan.com/post/affordances-in-game-level-design | El concepto de **zona muerta métrica** («metric buffering»): en vez de permitir superficies caminables de 0° a 35° y no caminables de 35° en adelante, se deja un hueco vacío — caminable por debajo de 30°, no caminable por encima de 40°, y **nada entre 30 y 40**. La ambigüedad se elimina prohibiéndose a uno mismo los casos limítrofes. Y el ejemplo de *Uncharted*: los asideros horizontales son **la única textura horizontal** de toda la roca. Traducido a un tilemap: si un tocón es interactuable, ningún tocón decorativo puede existir en el juego. La consistencia no es una virtud opcional; es el mecanismo entero. |
| Sandro Maglione — guía de diseño de nivel en pixel art | https://www.sandromaglione.com/articles/pixel-art-platformer-level-design-full-guide | La receta concreta de separación de capas en píxeles, no en abstracto. **Capa principal (lo que responde):** contorno sólido de alto contraste, colores más claros y **menos saturados**, más detalle, animación y partículas. **Fondo cercano (decorado):** **sin contorno** —precisamente para que no se confunda con un muro colisionable—, menos contraste, colores más oscuros y **más saturados**, menos detalle. **Fondo lejano:** a veces un solo color de silueta. Es un platformer y aquí es cenital, pero la gramática —contorno, contraste, saturación y detalle como cuatro diales de «esto responde»— se transfiere entera. Ojo a la inversión: **más saturado = más lejos y menos importante**, al revés del instinto. |
| Aceternity UI (ya citada en A.1) | https://ui.aceternity.com/components | *Card Spotlight* y *Canvas Reveal Effect*: la información se revela **por proximidad del cursor**, no de forma permanente. Equivalente diegético directo del «aparece al acercarse, no antes» de la fase 2. |

#### B.4 — Encuentros visibles en el mapa frente a encuentros aleatorios

Este apartado se levanta con más detalle que los demás porque es el que alimenta
las direcciones de la fase 4, y porque **las dos posturas tienen defensores
serios**. No se recomienda ninguna aquí.

| Fuente | URL | Qué aporta |
|---|---|---|
| RPG Maker Web — *Random Encounters vs On-Map Encounters* | https://forums.rpgmakerweb.com/threads/random-encounters-vs-on-map-encounters.35973/ | El inventario más completo de ventajas, costes y **soluciones híbridas**. |
| RPG Maker Web — *To use random encounters or not?* | https://forums.rpgmakerweb.com/threads/to-use-random-encounters-or-not.144861/ | Cifras y mitigaciones concretas: separación mínima entre combates, zonas designadas, reducción posterior al jefe. |
| Final Boss Blues — *Enemy Encounters: What You're Doing Wrong* | https://finalbossblues.com/enemy-encounters/ | Los errores de diseño, y la regla de no mezclar sistemas. |
| Bulbapedia — *Tall grass* | https://bulbapedia.bulbagarden.net/wiki/Tall_grass | El caso híbrido histórico y su abandono progresivo. |

**Argumentos a favor de los encuentros aleatorios**

1. **Tensión por incertidumbre.** No saber cuántos combates quedan hasta el
   próximo punto de guardado, ni si los PV aguantarán, produce una presión de
   recursos que desaparece en cuanto los enemigos son contables sobre el mapa.
   Es el argumento central de quien los defiende: el peligro difuso es un
   recurso dramático, y ponerlo en el mapa lo desactiva.
2. **Ambiente.** Una cueva oscura donde el ataque llega sin verse venir es
   coherente con la ficción de la cueva. En determinados lugares, la emboscada
   *es* el sitio.
3. **Rejugabilidad.** La variación entre partidas surge sola, sin diseñar
   colocaciones distintas.
4. **Coste de producción, y aquí sí es un argumento legítimo.** No hacen falta
   sprites de enemigo sobre el mapa, ni comportamiento de persecución, ni
   reglas de reaparición. En un proyecto de asignatura con el mundo aún sin
   dibujar, esto pesa — pero se declara como restricción de producción, **no**
   como argumento de diseño (regla de la vista de cliente).
5. **Subir de nivel es voluntario y trivial.** Quien quiera más combates,
   camina. No hay que diseñar un sitio para eso.

**Argumentos en contra de los encuentros aleatorios**

1. **Castigan explorar,** que es exactamente lo que el mapa pide hacer. El
   hallazgo formulado con más claridad: los combates aleatorios «actively
   punish exploration, which usually works directly against how JRPG maps are
   designed». Para esta pantalla el choque es frontal: la decisión dominante es
   *leer el paisaje*, y un sistema que interrumpe la lectura cada pocos pasos
   milita contra la decisión dominante.
2. **El combate encadenado.** Un combate un paso después del anterior es la
   queja más repetida, y desespera.
3. **Rehacer camino se vuelve un peaje.** Volver por una zona ya recorrida
   cuesta combates ya ganados, con los mismos enemigos y la misma recompensa.
4. **Interrumpen puzles y conversación.** Cortan cualquier tarea que exija
   sostener la atención en el mapa.
5. **Quitan control al diseñador.** «You can fine tune the game with far more
   freedom when you control how many encounters a dungeon has»: sin saber
   cuántos combates hará el jugador antes del jefe, el ajuste de dificultad es
   una apuesta.

**Argumentos a favor de los enemigos visibles en el mapa**

1. **Preparación.** Se ve venir el combate, se decide con qué grupo y con qué
   objetos se llega.
2. **Agencia real:** rodear, esperar, o ir a por él. Esquivar y perseguir son
   jugabilidad añadida en el mapa, no solo en el combate.
3. **Los jefes se distinguen** de la tropa por su presencia física, sin
   necesidad de anunciarlos.
4. **Sirven de cierre.** Un enemigo plantado en un paso es una puerta que se
   entiende sin texto.
5. **Ambientan el lugar** cuando el tipo de enemigo concuerda con el sitio: el
   propio monstruo se convierte en información sobre la zona. **Este punto es
   el que más pesa en este juego concreto**, porque aquí el monstruo *es* la
   causa del daño ambiental, y verlo en el paisaje es literalmente leer el
   paisaje.
6. **Permiten integrar mecánica de acercamiento:** primer golpe por la espalda,
   emboscada si te alcanzan por detrás. Final Boss Blues lo señala como el
   error más común de quien pone enemigos visibles y no los aprovecha.

**Argumentos en contra de los enemigos visibles**

1. **Esquivar puede ser más molesto que combatir.** En un juego por turnos, ir
   sorteando sprites por un pasillo estrecho cansa más que un combate que
   simplemente ocurre.
2. **Ansiedad de nivel.** Sin saber cuánta experiencia «debería» llevar, el
   jugador duda en cada enemigo entre esquivar y pelear, y esa duda repetida
   desgasta.
3. **Riesgo de quedarse corto de nivel** si se esquiva casi todo, y llegar al
   jefe sin poder ganarlo.
4. **Coste de producción alto:** un sprite cenital por enemigo, comportamiento
   de patrulla o persecución, reglas de reaparición, y evitar que dos o tres
   persiguiendo a la vez arrinconen al jugador.
5. **Mapas artificiales.** Para que no se esquive todo hay que estrechar
   pasillos y poner obstáculos, y el mapa empieza a diseñarse para el sistema
   de encuentros en vez de para el paisaje.

**Soluciones híbridas documentadas** — el material más útil para construir una
tercera dirección en la fase 4:

| Híbrido | Cómo funciona | Fuente |
|---|---|---|
| **Terreno que da permiso** | Los combates aleatorios solo ocurren dentro de un terreno **visualmente marcado**. La hierba alta de Pokémon: se distingue del suelo normal por sprite, el combate solo se dispara al pisarla, y hay tramos donde se puede rodear. El jugador no elige el momento, pero **sí elige entrar**. | Bulbapedia · RPG Maker Web |
| **Medidor de encuentros** | Un contador que se agota con cada combate; agotado, la zona queda limpia. Convierte el peaje en progreso visible. | RPG Maker Web |
| **Separación mínima por pasos** | Impedir por regla dos combates seguidos: se cita una holgura del orden de **40-50 pasos** entre uno y otro. Mata el combate encadenado sin tocar el sistema. | RPG Maker Web |
| **Reducción tras el jefe** | Bajar o anular la frecuencia en la zona ya superada, para que rehacer camino no sea un castigo. Encaja de forma natural con una zona purificada. | RPG Maker Web |
| **Objetos de control** | Repelentes que bajan la frecuencia y cebos que la suben: le devuelven al jugador el mando sin quitar la incertidumbre. | Final Boss Blues · RPG Maker Web |
| **Aprovechar el acercamiento** | Con enemigos visibles, tocarlos por la espalda concede primer golpe; ser alcanzado por detrás concede emboscada. Convierte la aproximación en jugabilidad en vez de en un peaje. | Final Boss Blues |

**Dos advertencias que las fuentes repiten y conviene no perder:**

- **No mezclar los dos sistemas en el mismo juego** sin una regla que el jugador
  pueda aprender: la inconsistencia confunde más que cualquiera de los dos
  sistemas por separado (Final Boss Blues).
- **La evolución del propio género es unidireccional.** Pokémon pasó de combate
  aleatorio en hierba (generaciones 1-7) a encuentros visibles en *Let's Go*, a
  ambos a la vez en *Espada/Escudo*, y en *Legends: Arceus* **eliminó el
  encuentro aleatorio en hierba**, dejando a los Pokémon a la vista y
  reconvirtiendo la hierba en sigilo. El caso híbrido canónico lo abandonó su
  propio autor (Bulbapedia). Es un dato, no un veredicto: la nostalgia por la
  hierba alta también está documentada en esos mismos foros.

#### B.5 — Cómo se lee «daño ambiental» en un paisaje pixel art

| Fuente | URL | Observación accionable |
|---|---|---|
| Emilia Schatz — *Defining Environment Language* (ya citada) | https://80.lv/articles/defining-environment-language-for-video-games | Aplicada al daño en vez de a la afordancia, la gramática de forma se invierte y da el vocabulario que hacía falta: **lo puntiagudo y diagonal evoca peligro** y niega la invitación a acercarse. Un tocón astillado, una rama quebrada y una grieta son formas diagonales; un árbol vivo y una copa redonda son formas redondas. La zona enferma se puede componer entera **por silueta**, sin tocar el color — lo que en una paleta desaturada de grises es la única palanca que queda de verdad. |
| Sandro Maglione (ya citada) | https://www.sandromaglione.com/articles/pixel-art-platformer-level-design-full-guide | El dial de **saturación como distancia** («background: more saturation, darker colors; main layer: brighter, less saturated») da la contrapartida técnica: en un mundo desaturado, un elemento **desaturado y oscuro se lee como fondo**. Por tanto el paisaje enfermo no se comunica bajando saturación —ya está toda baja— sino **bajando el valor y ensuciando la silueta**, y la zona purificada se comunica subiendo el valor y limpiando el borde. Coincide con lo que ya se hizo en batalla («el Coloso purificado recupera masa y borde limpio»). |
| Debate sobre restauración del entorno (nivel de extracto, ver aviso) | https://www.resetera.com/threads/games-where-beating-an-area-cleanses-it-returns-it-to-its-natural-state.327503/ · https://okami.fandom.com/wiki/Bloom · https://okami.neoseeker.com/wiki/Cursed_Zone | El precedente directo del mecanismo de este juego, con cuatro implementaciones del mismo gesto: **Ōkami** (zona maldita gris y marchita; florecer el Árbol Guardián devuelve el color a la región entera, y además **revela caminos y recursos** que antes no se veían), **de Blob** (ciudad gris que recupera color, vegetación, población y música por zonas), **The Saboteur** (el barrio liberado pasa de blanco y negro a color) y **Soul Blazer** (los pueblos se reconstruyen según se completan mazmorras). Tres observaciones accionables: *(a)* el cambio se aplica **por región completa, no por objeto**, para que se perciba; *(b)* en Ōkami la restauración **abre paso**, es decir, purificar no es solo estética, cambia la topología del mapa y por tanto la decisión dominante «a dónde voy»; *(c)* de Blob y Ōkami añaden vida —fauna, sonido— y no solo color: **la ausencia de bichos es un marcador de daño tan legible como el humo**, y barata en pixel art. **Aviso de honestidad:** el hilo de ResetEra devolvió **403** y las dos wikis de Ōkami devolvieron **403** y **402**; este material procede de extractos de buscador, no de páginas cargadas, y se marca como tal. |

#### B.6 — Transición entre zonas

| Fuente | URL | Observación accionable |
|---|---|---|
| Bugnet — *How to Implement Screen Transitions That Feel Good* | https://bugnet.io/blog/how-to-implement-screen-transitions-that-feel-good | La transición cumple **dos** funciones a la vez: suaviza el corte y **esconde la carga** — el momento en que se carga la escena siguiente es el que queda tapado por el fundido. Y el error nombrado como el más frecuente es exactamente el riesgo de esta pantalla: «a long, elaborate transition that the player sits through every single time becomes tedious fast, especially on transitions that happen frequently». Segunda regla: **coherencia** — mezclar estilos de transición se percibe como descuido, no como variedad; fundido rápido para lo rutinario, algo más elaborado reservado al momento importante. La fuente **no da milisegundos**; solo «quick enough to feel smooth without becoming a wait». El número tendrá que salir del techo de 300 ms que ya fija el contrato de batalla, no de esta fuente. |
| Búsqueda sobre desplazamiento y transición en mapas 2D (nivel de extracto, ver aviso) | https://gamedev.net/forums/topic/525538-2d-screens-vs-continuous-scrolling/4407786/ · https://gamedev.net/forums/topic/668452-how-to-do-rpg-interiors | Las tres familias, con su ámbito: **desplazamiento (paneo)** cuando el destino está en el mismo plano —la cámara queda encerrada en los límites de la sala y se desplaza al cruzar la puerta, como en Castlevania, donde se ve al personaje atravesar el vano—; **fundido** cuando hay cambio de plano, como bajar unas escaleras; **corte seco**, que la comparación con *8 Eyes* señala como notablemente más brusco que el desplazamiento de Castlevania. Y una cuarta vía que **evita la transición por completo**: el interior «mezclado» o de techo que desaparece, que mantiene la mirada pegada al personaje y no corta nunca. **Aviso de honestidad:** ambos hilos de GameDev.net devolvieron **403** al cargarlos; procede de extractos del buscador. |

#### B.7 — Inaccesibles del bloque de dominio

| Fuente | Motivo | Fecha |
|---|---|---|
| `rpgcodex.net` — *Random vs Fixed vs Visible Enemies* | HTTP 403. | 2026-09-14 |
| `resetera.com` — *Random Battles vs Visible Enemies in JRPGs* | HTTP 403. | 2026-09-14 |
| `resetera.com` — *Games where beating an area cleanses it* | HTTP 403. Usado solo a nivel de extracto, marcado en B.5. | 2026-09-14 |
| Medium — *Great Game UX: Encounter Design in Chrono Trigger* | HTTP 403. Era la fuente prevista para el análisis de Chrono Trigger; **no se cita lo que diría**. | 2026-09-14 |
| `pokecommunity.com` — tutorial extenso de tiling de GBA | HTTP 403. Usado solo a nivel de extracto, marcado en B.2. | 2026-09-14 |
| `rpgmaker.net` — *Random or On map encounters?* | HTTP 403. | 2026-09-14 |
| `gamedesignskills.com` — narrativa ambiental | HTTP 403. | 2026-09-14 |
| `gamedev.net` — dos hilos de transición y de scroll 2D | HTTP 403. Usados solo a nivel de extracto, marcado en B.6. | 2026-09-14 |
| Wikis de Ōkami (`fandom`, `neoseeker`) | HTTP 402 y 403. Usadas solo a nivel de extracto, marcado en B.5. | 2026-09-14 |
| PC Gamer — *Why I love restoring nature in Okami* | Cargó, pero el cuerpo del artículo llegó truncado: solo se obtuvo la navegación del sitio. **No se cita.** | 2026-09-14 |

---

### C. Recuento de la fase

| | Cantidad |
|---|---|
| Fuentes del protocolo con observación accionable | 4 (Taste Skill, Kowalski en dos páginas, Refero, Aceternity) |
| Fuentes del protocolo descartadas por no aplicables | 1 (`motionsites.ai`, con motivo) |
| Fuentes del protocolo inaccesibles | 2 (Mobbin, Pinterest — extensión de Chrome sin conectar) |
| Fuentes de dominio cargadas por completo, con observación accionable | 9 |
| Fuentes usadas solo a nivel de extracto del buscador, marcadas como tales | 4 |
| Fuentes registradas como inaccesibles, con motivo y fecha | 12 |

**Total de fuentes con observación accionable cargadas de verdad: 13.** El
mínimo de seis se cumple, pero no dentro del listado obligatorio, y eso se dice
en A.3 en vez de disimularse.

### D. Tensiones que quedan abiertas para la fase 4

Se enumeran **sin recomendar ninguna**: la elección es del usuario.

1. **Cámara suave frente a rejilla intacta.** El hilo de Godot deja claro que no
   hay tercera vía gratis, salvo pagar la complejidad del `SubViewport` de
   voithos. Tres posturas posibles: cámara a saltos de un píxel entero, cámara
   suave aceptando subpíxel, o cámara por salas sin seguimiento continuo.
2. **Cómo se entra al combate.** Pregunta ya abierta en la fase 1. El material
   de B.4 da los dos lados y seis híbridos documentados.
3. **Cuánto mundo cabe.** 30×17 tiles de 16 px es un lienzo pequeño, y la
   última fila queda cortada a 14 px. Condiciona si las zonas son salas
   cerradas o mapa continuo.
4. **Qué hace la purificación además de cambiar el color.** En Ōkami **abre
   paso**. Si aquí solo repinta, el verde es una recompensa estética; si abre
   paso, entra en la decisión dominante.
5. **Transición entre zonas.** Fundido, paneo o sin transición. La regla de
   Bugnet y la de Kowalski apuntan en la misma dirección —lo que se repite
   cientos de veces tiene que ser corto o inexistente— pero la elección entre
   las tres familias es de dirección, no de técnica.
6. **Alcance de mundo:** una región de muestra o las cinco. Sigue sin
   responderse desde la fase 1.

**Hallazgo técnico que no espera a la fase 4, porque es un hecho y no una
opinión:** a `project.godot` le faltan
`rendering/2d/snap/snap_2d_transforms_to_pixel` y
`rendering/2d/snap/snap_2d_vertices_to_pixel`. Qué valor llevan depende de la
tensión 1.

---

## Fase 4 — Elección de dirección y contrato

Se presentaron tres direcciones excluyentes, separadas por **cómo mira el
jugador**, que es el eje de la decisión dominante: *Estampa* (sala fija sin
scroll), *Vereda* (mundo contiguo con cámara viva) y *Casilla* (avance por
rejilla). La recomendación fue *Estampa*, por control del encuadre y porque
elimina el problema del subpíxel.

**El usuario eligió *Vereda*.** Además: encuentros **visibles en el mapa** y
purificación que **abre paso y devuelve fauna**. Se acata, y se acata entero.

### Lo que cuesta la elección, dicho antes de empezar

Con cámara libre **el encuadre lo decide el jugador**, no el diseño. Eso tira
abajo el recurso más fuerte de *Estampa*: colocar el daño dentro del cuadro para
que dirija la mirada a la salida. Aquí no hay cuadro.

No es motivo para revisar la elección; es una restricción que la dirección
asume y compensa, y por eso sube a cláusula del contrato en vez de quedar como
nota al pie: **la señalización del daño debe leerse en cualquier recorte**. Se
diseña por columnas verticales de paisaje —cada franja de ancho de pantalla
tiene que contener por sí sola una pista de hacia dónde sigue el camino—, no por
composiciones cerradas. Una pista que solo funciona viendo la sala entera está
mal puesta.

### Contrato de diseño — BLOQUEADO 2026-09-14

- **Dirección:** *Vereda*. Mundo contiguo recorrido con cámara viva, bajo la
  identidad «Ceniza y Brasa» heredada del contrato del 2026-09-13. El mundo está
  apagado; el color saturado solo aparece donde la causa ya se atajó.
- **Referentes que la sostienen:**
  - https://emilkowal.ski/ui/great-animations — no se anima lo que se repite
    cientos de veces por sesión.
  - https://docs.godotengine.org/en/stable/classes/class_camera2d.html —
    `Camera2D` no tiene ajuste a píxel; el ajuste vive en dos claves de proyecto.
  - https://bitdecaygames.itch.io/odd-verdure-jam/devlog/481096/cameras — zona
    muerta medida, no estimada: 48 px de alto, sesgo al borde inferior.
  - https://www.sandromaglione.com/articles/pixel-art-platformer-level-design-full-guide
    — contorno, valor y saturación como lenguaje de «esto responde».
  - https://www.nicphan.com/post/affordances-in-game-level-design — la afordancia
    se construye negando casos limítrofes, no señalándolos.
  - https://80.lv/articles/defining-environment-language-for-video-games — el
    lenguaje del entorno se declara una vez y no se contradice nunca.
  - https://www.slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles — rejilla
    y legibilidad de terreno cenital.

#### Cámara

Seguimiento con **zona muerta de 28 px de ancho por 48 px de alto**, con el
personaje sesgado hacia el borde inferior de la zona: en vista cenital importa
más ver hacia dónde se va que de dónde se viene.

**La cámara se ajusta a píxel entero.** Se descarta el `SubViewport` de un píxel
extra: su coste declarado es un `SubViewport` por capa de parallax, y aquí no
hace falta pagarlo, porque el problema que resuelve se evita eligiendo bien la
velocidad. Con la cámara redondeada a entero, el tirón solo se ve si el
personaje avanza fracciones de píxel por cuadro; si avanza un número entero, no
hay nada que redondear y el movimiento es exacto.

Por eso las velocidades **no son un número de gusto, son parte del contrato**:

| | Velocidad | A 60 Hz |
|---|---|---|
| Caminar | 60 px/s | **1 px por cuadro** |
| Correr | 120 px/s | **2 px por cuadro** |

Física fijada a 60 Hz. Cualquier velocidad futura debe ser múltiplo entero de
60 px/s, o rompe el trato.

En `project.godot`, ambas en `true`:
`rendering/2d/snap/snap_2d_transforms_to_pixel` y `snap_2d_vertices_to_pixel`.

#### Movimiento del personaje

Ocho direcciones, **sin aceleración, sin inercia y sin amortiguación**. Se
mueve en el cuadro en que se pulsa y se para en el cuadro en que se suelta.
Caminar es la acción de teclado más repetida del juego, y animarla la vuelve
lenta.

El techo de 300 ms del contrato de batalla **es para eventos** —purificar, entrar
a un combate, abrir un diálogo—, no un permiso para amortiguar movimiento
continuo. Queda dicho aquí porque es el malentendido más fácil de cometer.

#### Rejilla y tile

Tile de **16 px**. El mapa es mayor que el viewport, así que los tiles cortados
en el borde de pantalla son el comportamiento normal del scroll y no un defecto:
la aritmética de 30 × 16,875 solo era un problema en la dirección de sala fija,
y **se abandona con ella** la idea de reservar los 14 px sobrantes como franja
fija. Con cámara viva, la franja del nombre del lugar es una capa que aparece y
se va, no un recorte permanente del mundo.

#### Lenguaje del entorno — se declara una vez y no se contradice

| | Terreno enfermo | Terreno purificado |
|---|---|---|
| Valor | Bajo, hundido | Alto, levantado |
| Silueta | Sucia, rota, irregular | Limpia, de borde continuo |
| Fauna | Ausente | Presente |

En una paleta ya desaturada, **el daño no se comunica quitando saturación**,
porque no queda de dónde quitar. Se comunica bajando el valor y ensuciando la
silueta. Es el mismo recurso que ya funcionó con el Coloso del Deshielo.

| | Responde | Es decorado |
|---|---|---|
| Contorno | Sólido, de alto contraste | Sin contorno |
| Valor | Más claro que su fondo | Más oscuro |

**Regla de negación, no negociable.** Si una clase de objeto responde, **ningún
ejemplar decorativo de esa clase existe en el juego**. Si un tocón se puede
replantar, no hay tocones de adorno. Nada de carteles de «pulsa E»: la
afordancia se construye prohibiendo el caso limítrofe, no rotulándolo.

#### Encuentros

Monstruos **visibles en el mapa**, con la contrapartida documentada asumida y
acotada: el mapa **no se estrecha** para impedir que se esquive el combate. El
jugador que rodea, rodea. El nivel se sostiene con los combates de historia, que
no se esquivan.

Coherencia con el mundo: el monstruo **es** la causa del daño de su región, así
que verlo en el paisaje forma parte de leer el paisaje, y su sola presencia
explica el estado del terreno que lo rodea.

#### Purificación

Al modo de *Ōkami*: purificar **retira un obstáculo y revela paso o recurso**, y
**devuelve la fauna** a la zona. Queda dentro de la decisión dominante en vez de
ser un premio estético. Consecuencia asumida para la parte 3 del plan: **cada
zona se traza con un paso cerrado** que la purificación abre.

#### Movimiento (duraciones)

Se heredan las del contrato de batalla. Las propias del mundo:

| Transición | Duración | Curva |
|---|---|---|
| Caminar y correr | **0 ms. No se anima** | — |
| Rótulo del lugar (entra y se va) | 160 ms | `ease-out` |
| Cambio de zona (fundido a negro y vuelta) | 2 × 120 ms | lineal |
| Purificación de zona | 300 ms | `ease-out` |

#### Alcance

**Las cinco regiones, juego completo.** Decidido el 2026-09-14; anula la nota de
recorte de `CONTEXTO.md`. Siete zonas: Valdehoja, las cinco regiones y la Cripta
de la Avaricia. Resuelve la tensión 6 de la fase 3 y el dato pendiente 1 de la
fase 1.

#### Fuera de alcance de este contrato

Diálogos y retratos · menú fuera de combate · guardado · audio · pantalla de
título · puzzles ambientales (parte 7 del plan, contrato propio) · combate, que
ya tiene el suyo.

### Enmiendas

**Enmienda 1 — 2026-09-14. Tres rampas de material para el terreno.**
Autorizada expresamente por el usuario. La paleta de «Ceniza y Brasa» tiene
ocho grises de un mismo violeta apagado, pensados para paneles de interfaz. En
vista cenital, suelo, agua y follaje pintados con ellos colapsan en una sola
masa: el hallazgo de Maglione es que separar materiales necesita contorno,
valor **y** saturación, y saturación no hay.

Se añaden nueve tokens en tres rampas, con **techo de saturación 0,22** en HSV
—frente a 0,80 de `ember_500` y 0,70 de `vital_500`—, así que el mundo sigue
apagado y la regla del acento único queda intacta.

| Token | Hex | Token | Hex | Token | Hex |
|---|---|---|---|---|---|
| `soil_700` | `#403732` | `water_700` | `#1e2426` | `flora_700` | `#434536` |
| `soil_500` | `#594d46` | `water_500` | `#364145` | `flora_500` | `#575946` |
| `soil_300` | `#73645a` | `water_300` | `#4e5e63` | `flora_300` | `#6a6e56` |

Matices: suelo 24°, agua 196°, follaje 68°. El follaje **no es verde**: es oliva
sucio. El verde de este juego tiene un solo significado y no se gasta en
decorado.

Los valores no se eligieron a ojo. Salen de una búsqueda que exige a la vez:
saturación ≤ 0,22; el verde de purificación y la brasa legibles sobre
**cualquier** terreno con 3:1, el mínimo gráfico de WCAG 1.4.11; separación
perceptual ≥ 7 de dE dentro de una misma rampa, que es sombreado del mismo
material; y ≥ 8 de dE contra los grises de panel.

**Lo que no se consiguió, y no se maquilla.** La separación entre materiales
distintos queda en **dE 9,2**, no en los 12 que me había fijado como margen. Se
midió que el techo de saturación no era la causa —subirlo a 0,26 y a 0,30 no
mejoraba nada— sino que nueve tonos no caben con esa holgura en un rango de
valor tan estrecho; y al exigir que el verde se lea sobre el follaje hubo que
oscurecerlo, lo que apretó todavía más. Los dos criterios tiran en direcciones
opuestas y se priorizó el verde, que es el que carga el mensaje del juego.

dE 9,2 sigue siendo unas cuatro veces el mínimo perceptible y basta para áreas
planas contiguas, pero **el color no puede cargar solo con distinguir
materiales**: el contorno y la silueta declarados en el contrato tienen que
acompañar. Si en la verificación se ve que no basta, sale una enmienda nueva
(la siguiente libre, hoy la **5**: la 2 ya se usó para el ajuste a píxel y la
3 y la 4 para P1 y P2; numeración corregida el 2026-09-23).

Peor caso medido del verde sobre terreno: **3,03:1**. De la brasa: **3,27:1**.

**Enmienda 2 — 2026-09-14. Ajuste a píxel en `project.godot`.**
No es cuestión de gusto: Godot 4 retiró el «Enable Pixel Snap» de la 3.x y lo
partió en `rendering/2d/snap/snap_2d_transforms_to_pixel` y
`snap_2d_vertices_to_pixel`, ambas apagadas por defecto, y `Camera2D` no tiene
ajuste a píxel propio. Se activan las dos. En la batalla no se notaba porque
nada se movía en subpíxel.

**Enmienda 3 — 2026-09-23. La ola de purificación (P1).**
Autorizada expresamente por Diego el 2026-09-23. Propuesta en
`docs/guia-de-continuacion.md`, §3.2.

La purificación de **zona** deja de ser un cambio de 300 ms en bloque y pasa a
ser una **ola**: el verde avanza desde el lugar donde se ganó el combate, en un
tramado ordenado de 4×4 (Bayer), en **8 pasos**, durante **900 ms**, y la fauna
entra detrás del frente de la ola.

| Transición | Antes | Ahora |
|---|---|---|
| Purificación de zona | 300 ms, `ease-out` | **900 ms, 8 pasos de tramado, lineal por paso** |

Por qué no rompe el techo de 300 ms: ese techo existe porque la batalla se ve
cientos de veces por sesión. La purificación de zona ocurre **siete veces en toda
la partida**; es el momento más raro y el que carga el mensaje. El tramado es el
recurso propio del pixel art para fundir dos estados sin fabricar colores
intermedios, así que **no añade ni un token**: cada píxel es enfermo o
purificado, nunca una mezcla.

**Repertorio:** el tramado ordenado queda reservado **solo** para el avance de la
purificación. No se usa en transiciones, sombras ni fondos.
**Movimiento reducido:** salto directo al estado final, sin ola.
La purificación del **monstruo** en batalla no cambia: sigue en 300 ms.

**Enmienda 4 — 2026-09-23. Diagonal sin normalizar (P2).**
Autorizada expresamente por Diego el 2026-09-23.

En diagonal, el personaje avanza **1 px en X y 1 px en Y por cuadro** al andar,
y 2 + 2 al correr. La regla de velocidades se lee **por eje**: cada eje se mueve
un número entero de píxeles por cuadro.

Por qué: normalizar el vector da 60 / √2 = 42,4 px/s por eje, que son 0,707 px
por cuadro. Son fracciones de píxel, justo lo que la cláusula «Cámara» prohíbe
porque, con la cámara ajustada a entero, producen tirones. La diagonal queda un
41 % más rápida en distancia recorrida, la solución habitual de los juegos de
16 bits, y jugando no se nota.

---

## Fase 5 — Implementación

### Paso 1 — Tokens · 2026-09-14, aprobado 2026-09-23

- `src/ui/design_tokens.gd`: rampas `SOIL_*`, `WATER_*`, `FLORA_*`, techo
  `WORLD_SATURATION_CEILING`, lenguaje del entorno, rejilla, cámara,
  velocidades y duraciones del mundo.
- `project.godot`: ajuste a píxel (enmienda 2).

**Cláusulas:** «Enmienda 1», «Cámara», «Movimiento del personaje»,
«Movimiento (duraciones)».

**Visto bueno de Diego: 2026-09-23.**

**Añadido en la misma revisión:**

- `tools/pixel.py` recibe las nueve tintas de mundo: sin ellas, el generador del
  tileset no podía usar los tokens aprobados.
- `tools/verify_palette.py` detectó **deriva**: `EMBER_700` y `VITAL_900` se
  usaban en los sprites desde el 2026-09-13 sin estar en `design_tokens.gd`. Se
  declaran allí; no son colores nuevos. Resultado: 24 tokens coinciden y los 17
  sprites pasan con todos sus píxeles dentro del contrato.
- Medido con `verify_palette.py cvd`: `VITAL_500` frente a `EMBER_300` da 1,08:1
  de contraste en visión normal, y `VITAL_500` frente a `EMBER_400` baja a
  1,22:1 con deuteranopía. El verde y la brasa se separan casi solo por matiz.
  Confirma, ahora con cifras, la cláusula del lenguaje del entorno: **el estado
  se lee por valor y silueta, no por color.** El tileset tendrá que pasar
  `verify_palette.py value` con cociente ≥ 1,5 en las cuatro visiones.

**Siguiente:** paso 2a, catálogo de lo que responde; después, paso 2b,
tileset. Instrucciones en `docs/guia-de-continuacion.md`, §5, parte 1.

### Paso 2a — Catálogo de lo que responde · 2026-09-23

Va antes que el tileset porque **la regla de negación decide qué tiles pueden
existir**. Dibujar primero y catalogar después obliga a redibujar.

**Cláusulas:** «Lenguaje del entorno» (tabla responde/decorado y regla de
negación), «Purificación» (paso cerrado que se abre), «Encuentros»; enmiendas 3
y 4.
**Referentes, ya en el contrato:** Schatz (forma rectangular = afordancia,
diagonal = peligro, redonda = seguridad; el objeto que responde es *la única*
forma rectangular de su vecindad), Phan (hueco métrico: se prohíben los casos
limítrofes) y Maglione (contorno y valor como diales de «esto responde»).

#### Cuatro reglas que salen de los referentes

1. **Dos verbos en todo el juego.** **Usar** (`confirm` mirando al objeto, a un
   tile de distancia) y **Empujar** (caminar contra el objeto). Hablar es usar
   sobre una persona. No hay tercer verbo: cada verbo nuevo es otra cosa que el
   jugador tiene que descubrir sin cartel.
2. **Gramática de forma.** Lo que responde es **rectangular**, lleva contorno
   `ASH_050` y es más claro que su fondo. El decorado enfermo es **diagonal y
   roto**; el purificado, **redondo**. Ningún decorado del juego tiene silueta
   rectangular sólida ni contorno.
3. **Hueco métrico de tamaño** (Phan). Lo que se recoge mide **≤ 8×8 px**. Lo
   que se empuja o se usa mide **≥ 16×16 px**. **Nada mide entre 9 y 15 px**:
   el tamaño dice el verbo antes de probarlo.
4. **Resuelto no es decorado.** Un objeto resuelto deja de responder, así que no
   puede quedarse en el mapa tal cual: sería un ejemplar decorativo de una
   clase que responde. **Desaparece o se transforma en una silueta de otra
   familia.** Cada clase declara su forma resuelta.

#### Clases globales

| Id | Clase | Verbo | Firma visual | Resuelto | Consecuencia de la negación |
|---|---|---|---|---|---|
| `person` | Persona | Usar (hablar) | 16×24, contorno | — | **No hay personas de fondo.** Todo humano del mundo habla; nada de multitudes decorativas. |
| `seedbed` | Semillero (guardar) | Usar | Cajón de madera 16×16 con un brote `VITAL`: tierra ya curada | — | No hay cajones ni macetas de adorno. El primero está en el jardín de Yara. |
| `bundle` | Hatillo (objeto o material) | Usar (recoger) | Fardo atado de 8×8, contorno | Desaparece | Todo bulto pequeño se recoge. No hay sacos ni cajas de atrezo. |
| `monster` | Monstruo | Contacto → combate | Brasa, en movimiento | Purificado; ola (enmienda 3) | Ya contratado. |
| `blocker` | Paso cerrado | **Ninguno**: lo abre la purificación | Diagonal, puntiagudo, **sin contorno**, valor bajo | Desaparece con la ola | No responde al jugador y **no existe como decorado**: cada ejemplar es un paso que se abrirá. |

**Lo que nunca responde:** la fauna. No lleva contorno y solo aparece en zona
purificada. Nada vivo responde salvo personas y monstruos. El ave mensajera de
Yara llega en escenas, nunca como objeto del mapa.

#### Clases regionales — una por región, y es el ensayo de su contramedida

Cada una es la habilidad ecológica del jefe, hecha con las manos y sin presión
(guía, parte 7). Resolverla es el Conocimiento Ambiental que desbloquea la
habilidad.

| Región | Id | Clase | Verbo | Qué ensaya | Firma visual | Resuelto |
|---|---|---|---|---|---|---|
| Valdehoja | — | *Solo clases globales* | — | Andar, hablar, guardar | — | — |
| Bosque de las Cenizas | `dry_brush` | Haz de maleza seca | Usar (desbrozar) | **Línea Cortafuegos**: abrir un hueco para que el frente de fuego no pase | Bloque 16×16 de ramas atadas | Desaparece: queda suelo pisado |
| Cuenca de Alquitrán | `boom` | Barrera absorbente | Empujar sobre el agua | **Barrera Absorbente**: cerrar un canal para contener la mancha | Rollo flotante 32×16 | Anclada: se funde con la orilla como tile de borde |
| Costa Quebrada | `waste_bale` | Fardo de residuos | Empujar | **Separación en la Fuente** | Fardo 16×16. El material se lee **por silueta**: botellas (trazos verticales), red (cuadrícula), latas (círculos) | Entra en su contenedor y desaparece |
| Costa Quebrada | `sorting_bin` | Contenedor | Recibe un fardo | Ídem | 16×24 con **la misma silueta** del material en el frente. **Nunca por color** (medición del paso 1) | Lleno: tapa cerrada y sin contorno, otra familia de forma |
| Llanura Marchita | `plot` | Parcela cercada | Usar (cambiar cultivo) | **Rotación de Cultivos**: que dos parcelas vecinas nunca repitan cultivo | 16×16 con cerca de 1 px. Cultivo por silueta: cereal (trazos verticales), legumbre (puntos redondos), barbecho (tierra lisa) | Crece en follaje redondo purificado |
| Cumbre Menguante | `albedo_cover` | Manto reflectante | Usar (desplegar) | **Escudo de Albedo**: cubrir la roca oscura que derrite el puente de hielo | Lona doblada 16×16 | Desplegado: pasa a ser superficie de puente, tile de suelo |
| Cripta de la Avaricia | — | *Las cinco clases juntas* | — | La combinación, como el jefe | — | — |

#### Lo que cambia respecto a la semilla de la guía

- **El Bosque no usa el tocón: usa la maleza.** El tocón es la señal más clara
  de la tala. Si respondiera, la regla de negación lo prohibiría como decorado
  en todo el juego y la región perdería su mejor señal de daño. Además la
  maleza ensaya mejor la Línea Cortafuegos, que consiste en quitar combustible,
  no en plantar. **Los tocones quedan libres como decorado**, diagonales y
  rotos.
- **La Costa tiene dos clases.** La separación necesita origen y destino. Es la
  única región con dos, y se acepta porque el contenedor no se mueve: el verbo
  sigue siendo uno, empujar.

#### Lo que queda libre para contar el daño (decorado permitido)

| Región | Decorado del daño (diagonal, roto, sin contorno) |
|---|---|
| Bosque | Tocones, troncos caídos, árboles calcinados, ceniza |
| Cuenca | Manchas de crudo, barriles volcados, tuberías partidas |
| Costa | Basura **suelta y dispersa**, nunca atada ni en fardos. Arena con puntos de microplástico |
| Llanura | Hileras interminables de un solo cultivo, **sin cerca**. Las terrazas de Valdehoja se dibujan como franjas escalonadas largas, nunca como parcelas cuadradas cercadas |
| Cumbre | Roca oscura expuesta, grietas, agua de deshielo |

#### Riesgo que se declara, no se esconde

**Cumbre Menguante y la regla «más claro que su fondo».** Si el suelo
purificado de la Cumbre es nieve clara, el manto reflectante deja de ser más
claro que su fondo. No afecta al puzzle, que ocurre con la zona enferma (roca
oscura), pero sí a cualquier manto que siguiera visible tras purificar. Por eso
el manto **se transforma** al resolverse (regla 4) y no queda ninguno a la
vista después de la ola. El contraste del contorno contra cada fondo de la
región **se mide sobre el render** en el paso 2b; si falla, se para y se avisa.

#### Resolución de una tensión interna del anexo

La fase 2 dice que lo interactuable «aparece al acercarse, no antes», y el
contrato pide contorno `ASH_050` en todo lo que responde. **Manda el
contrato**: el contorno es permanente porque es la firma de la clase y lo que
permite leer el paisaje de lejos. «Al alcance» no añade marca ni efecto: si el
jugador está a un tile mirando al objeto, **usar funciona**, y eso es todo. No
entra ninguna forma nueva en el repertorio.

#### Datos para la verificación

`data/world/interactables.json` recoge este catálogo en formato legible por
máquina. La prueba `verify_zone.gd` de la parte 3 lo lee para comprobar que
ningún tile decorativo pertenece a una clase que responde y que ningún objeto
mide entre 9 y 15 px.

**Punto de control.** Pendiente del visto bueno de Diego antes del paso 2b.

**Visto bueno de Diego al catálogo: 2026-09-23.**

### Paso 2b — Tileset · EN CURSO desde el 2026-09-23 (lo termina otra persona del equipo)

**Lo que ya existe:**

- `tools/gen_tiles.py` → `assets/tilesets/world.png` (atlas de 16×7 tiles). Base
  plana con pocas formas contadas. Enfermo: diagonal y roto. Purificado:
  redondo. Columnas 0-15 = máscara de vecinos N1 E2 S4 O8.
- `src/world/world_tiles.gd` (`WorldTiles`): construye el `TileSet`, calcula la
  máscara y pinta un mapa de texto (`.` suelo, `=` camino, `~` agua,
  `#` follaje).
- `tools/tileset_sheet.tscn`: captura enfermo, purificado y partido a 480×270.
  Capturas en `docs/ux/capturas/2026-09-23-tileset-*.png`.
- `tools/verify_tileset.py`: valor en cuatro visiones, dE entre materiales,
  contorno `ASH_050` y acentos contra el terreno.

**Iteraciones ya descartadas, para no repetirlas:** ruido umbralizado píxel a
píxel (se leía como letras); rizos del agua en arco junto a un punto (se leían
como caras); guijarros en cruz (se leían como destellos); dos matas verdes por
tile (confeti); parches que cruzan el borde del tile (salen partidos en
astillas).

**Medición actual (`python tools/verify_tileset.py`):**

| Regla | Resultado |
|---|---|
| Todo píxel es token, saturación ≤ 0,22 | OK |
| Valor purificado/enfermo ≥ 1,5 en 4 visiones | Suelo 1,56–1,59 OK · Agua 2,25–2,31 OK · Follaje 1,92–2,20 OK · **Camino 1,48–1,49 FALLA** |
| dE entre materiales ≥ 9 | OK, mínimo 9,1 (suelo/camino enfermos) |
| Contorno `ASH_050` sobre el terreno ≥ 3:1 | OK, peor caso 4,21:1 |
| `VITAL_500` / `EMBER_300` sobre el terreno ≥ 3:1 | OK, 3,03 y 3,27 |
| `EMBER_500` sobre el terreno | **AVISO** 1,46:1 → requisito para la parte 4 |

**Pendiente, en este orden:**

1. **Decisión de Diego sobre el camino (1,48 frente a 1,5).** Con nueve tintas de
   mundo, las dos reglas medidas chocan: oscurecer el camino enfermo lo acerca al
   suelo enfermo (dE < 9), y el camino purificado ya está en `SOIL_300`, la
   tinta más clara. Opciones: **(a)** aceptar 1,48 para el camino, porque su
   estado lo cargan también la silueta del borde (sierra frente a festón) y la
   textura (grietas frente a liso); el piso de 1,5 lo fijé yo, y el contrato
   pide «valor bajo/alto» sin cifra. Es la recomendada. **(b)** Enmienda 5: un
   token nuevo `SOIL_200` para el camino purificado. Da margen, pero añade una
   décima tinta y acerca el camino al contorno `ASH_050` de lo que responde.
2. **Revisar el follaje purificado.** Es la masa más cargada de la pantalla.
   Medido, cumple; a ojo, sus copas repetidas tienden a papel pintado. Enseñar
   la captura a Diego y preguntar si se calma (menos copas y más base
   `VITAL_700`) o si se acepta como la recompensa de la zona.
3. **Prueba con personas de los materiales** (decisión abierta de la enmienda 1):
   tres personas nombran el material de 10 recortes de 64×64 de las capturas. Si
   fallan, sale la enmienda 5 (o la 6, si la 5 se usó para el camino).
4. **Punto de control con Diego** con las tres capturas y la salida de
   `verify_tileset.py`. Sin su visto bueno no se pasa al paso 3 (cámara).

**Requisito que se arrastra a la parte 4:** un monstruo en el mapa lleva
siempre borde `EMBER_300` o contorno. `EMBER_500` solo mide 1,46:1 sobre el
follaje enfermo.

