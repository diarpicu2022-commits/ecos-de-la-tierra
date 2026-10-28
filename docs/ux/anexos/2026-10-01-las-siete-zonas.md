# Anexo — Las siete zonas (parte 3)

Abierto el 2026-10-01 por Juan José Rueda. Hereda «Vereda» (exploración, con
sus enmiendas 1 a 5) y «Umbral» (movimiento y zonas). Lo que ya está firmado
allí **no se vuelve a decidir aquí**:

- el tileset y su paleta;
- la colisión del tile entero;
- las salidas en el borde, como mucho 2 por pantalla;
- el fundido y el rótulo;
- la cámara encerrada en la zona;
- el catálogo de lo que responde y la regla de negación;
- el paso cerrado que la purificación abre.

Este anexo decide **cómo se compone cada zona**.

**Estado:** fases 1 a 4 cerradas. **Las dos pruebas con personas quedan
aplazadas por decisión de Diego** (2026-10-01; ver «Pruebas aplazadas»), y la
fase 4 se planteó con la hipótesis prudente. **Diego eligió el 2026-10-28:
dirección A «Rastro», mapas en texto, hipótesis prudente confirmada.** Contrato
«Rastro» escrito y **valores aprobados por Diego el 2026-10-28**. Abierta la
fase 5 con Valdehoja: paso 1 entregado.

**Subdivisión (guía §5): una zona por sesión,** en este orden: Valdehoja →
Bosque de las Cenizas → Cuenca de Alquitrán → Costa Quebrada → Llanura
Marchita → Cumbre Menguante → Cripta de la Avaricia. Las fases 1 a 4 de este
anexo valen para las siete; la fase 5 abre un apartado por zona.

---

## Fase 1 — Usuarios

- **Quién juega:** el mismo jugador de los anexos anteriores. Juega a RPG 2D,
  tiene de 14 a 30 años, es hispanohablante y usa PC con teclado. **No sabe
  nada del dominio ambiental:** nadie llega sabiendo que a un incendio se le
  ataja con una línea cortafuegos.
- **Qué necesita en una zona,** en sus palabras:
  - «¿Dónde estoy y qué le pasó a este sitio?»
  - «¿Hacia dónde sigo?»
  - «¿Qué cambió cuando lo arreglé?»
- **Lo que ya sabe hacer** (partes 1 y 2):
  - moverse sin pensar en ello;
  - leer el camino como la salida;
  - distinguir lo que responde (contorno claro) del decorado.
  No hay que enseñárselo otra vez.
- **Lo que esta parte tiene que enseñarle, y ninguna otra puede:** **la causa
  del daño, antes del combate.** El anexo de batalla dejó sin verificar si el
  jugador deduce en combate que hay que atajar la causa (fila «¿Por qué
  pierdo?»). El anexo de exploración ya señalaba la consecuencia: la zona es la
  única superficie que puede enseñar la causa **antes** de que el combate la
  exija. Quien cruza un robledal de tocones y ve el humo llega a la Llama con
  una hipótesis.
- **Secundario:** el docente de Diseño de Interfaces, que evalúa si el
  paisaje está **decidido** (cada forma con un trabajo) o solo **dibujado**.
- **Volumen de contenido:** siete zonas dibujadas tile a tile son la parte más
  cara del juego en autoría. El método de autoría (texto o editor) pesa tanto
  como el diseño.

## Fase 2 — Comunicación

- **Decisión dominante:** **«¿hacia dónde sigo?»**, leída en el mismo paisaje
  que dice **qué le pasó a esta tierra**. En este juego son la misma pregunta,
  porque el daño señaliza (anexo de exploración, fase 2): el humo lleva al
  Robledal igual que un cartel, y además enseña la causa.
- **Qué la sostiene, en orden de lectura:**
  1. **El hito:** una silueta única de la zona, visible desde lejos (el árbol
     quemado mayor, la torre de la refinería, la montaña de basura, el silo,
     el glaciar partido). Dice dónde estás y hacia dónde está la fuente.
  2. **El gradiente de daño:** más roto y oscuro cuanto más cerca de la
     fuente. Dice si vas hacia ella o te alejas.
  3. **El camino pisado:** lleva a las salidas. Ya es la pista contratada en
     cada columna de 480 px.
  4. **El paso cerrado:** se ve que hay un «más allá» y que ahora no se pasa.
     Dice que falta algo.
  5. **La fauna,** solo tras purificar: dice que eso lo hiciste tú.
- **Qué no va:**
  - carteles o flechas de dirección;
  - texto que explique la causa (el paisaje la enseña, o no hay causa);
  - un minimapa;
  - decorado que se parezca a algo del catálogo de lo que responde;
  - un segundo hito que compita con el primero;
  - verde de adorno en una zona enferma.

### El vocabulario de la zona, con Kevin Lynch

Lynch (fase 3, fuente 1) describe cómo se lee una ciudad con cinco elementos.
Cada uno tiene ya una forma en este juego, y **cada forma tiene un solo
trabajo** (repertorio de la guía §3.1):

| Elemento de Lynch | En una zona de *Ecos* | Forma ya contratada |
|---|---|---|
| Camino (*path*) | Por dónde se va | Camino pisado, `SOIL_300` |
| Borde (*edge*) | Por dónde no se va | Follaje y agua, sólidos (colisión del tile entero) |
| Distrito (*district*) | Cuánto daño hay aquí | Gradiente: franjas de daño que se aclaran al alejarse de la fuente |
| Nodo (*node*) | Donde pasa algo | Claro con persona, semillero o paso cerrado |
| Hito (*landmark*) | Dónde estoy y dónde está la fuente | **Nuevo:** una silueta grande y única por zona, sin entrar en ella |

El hito es la **única forma nueva** que pide la parte 3. Entra en el
repertorio solo si la fase 4 lo contrata.

## Fase 3 — Investigación

Consultada el 2026-10-01. Formato: `observación → decisión aplicable → límite
que no copiaré`. Solo cuentan las fuentes cargadas de verdad.

### A. Fuentes de dominio

| # | Fuente | Observación → decisión → límite |
|---|---|---|
| 1 | Kevin Lynch, *The Image of the City* (resumen en Wikipedia: https://en.wikipedia.org/wiki/The_Image_of_the_City) | Cinco elementos con los que se lee una ciudad; el hito es un punto de referencia **en el que no se entra** y que es único en su contexto, y el mejor nodo es el que es único e «intensifica» lo que lo rodea. → Cada zona se compone con los cinco, y cada uno con su forma ya contratada (tabla de la fase 2). **El hito no se pisa ni responde**: es decorado grande, y por tanto sin contorno. → No copio su escala urbana: una zona tiene un solo hito, no varios. |
| 2 | Don Carson, *Environmental Storytelling* (Game Developer: https://www.gamedeveloper.com/design/environmental-storytelling-creating-immersive-3d-worlds-using-lessons-learned-from-the-theme-park-industry) | Tres técnicas aplicables: **viñetas de causa y efecto** («doors that have been broken open, traces of a recent explosion»); «save your most decorative elements for areas you wish to draw your audience to»; y responder a «¿dónde estoy?» en unos 15 s. → **Cada zona lleva viñetas de causa y efecto en el camino hacia la fuente.** Son la respuesta del paisaje a «¿por qué pierdo?»: tocones con el corte limpio (tala) antes que árboles quemados (fuego). El detalle se concentra cerca de la fuente; el resto queda en espacio negativo. → No copio su ritmo de parque temático, que es lineal: el mapa aquí lo recorre el jugador a su manera. |
| 3 | Harvey Smith y Matthias Worch, *What Happened Here? Environmental Storytelling* (GDC 2010, resumen: https://www.gdcvault.com/play/1012647; crónica en Nieman Storyboard: https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/) | El jugador **tira** de la información (*pull*), no se la empujan; la ley de cierre («what's important is what happens between the panels»); y «it has to be possible to miss some things to make finding them meaningful». → La causa se enseña con **dos elementos que el jugador une**, no con uno que lo diga todo: el tocón y, más allá, la mancha de ceniza; el barril volcado y el agua negra. Ninguna viñeta es obligatoria salvo el gradiente. → Se escribió para FPS en 3D; de ella solo tomo la composición de la viñeta, no su densidad de objetos. |
| 4 | Scott Rogers, *Everything I learned about level design I learned from Disneyland* (GDC 2009; apuntes: https://craphound.com/disneylandleveldesign.txt) | Los *weenies* son hitos que **atraen**; al llegar a un cruce «more weenies open up […] prompting the player to choose where to go»; y la «squint test»: entrecerrando los ojos, lo más luminoso tiene que marcar el camino. → **Prueba de entrecerrar sobre cada zona:** con la captura emborronada, lo más luminoso es el camino o la zona purificada, nunca un decorado. Se puede medir con un desenfoque y un umbral. El hito de una zona puede asomar en el borde de la anterior. → No copio el radio de un centro con radios: el mapa es de zonas contiguas con salidas, no de un centro. |
| 5 | *Various Uses of Landmarks in Level Design* (https://tancoque.design.blog/) | Tres usos: orientar («a centrally-located landmark»), recordar el objetivo, y **marcar el progreso con negación y recompensa**: el hito se tapa al girar o cruzar y reaparece más cerca, y así «the player's progress […] become[s] more tangible». Cita *Journey*. → El hito de cada zona está **en la fuente del daño**: acercarse a él es acercarse al monstruo. La cámara encerrada y las masas de follaje hacen de negación; el camino que se abre a un claro, de recompensa. → Un hito «visible desde lejos» en 480×270 cenital es un hito de pocos tiles: no hay horizonte. |
| 6 | *The Level Design Book*, Wayfinding (https://book.leveldesignbook.com/process/blockout/wayfinding) | «Players look in the direction they are moving» y «Players focus on contrast (in color, shape, lighting, and movement)». → El hito y las viñetas se colocan **por delante en la dirección del camino** (que es lo que ya enseña la anticipación de la cámara, enmienda 5), y se distinguen por **forma** antes que por color, que en esta paleta casi no hay. → Sus porcentajes de certeza son orientativos; no se toman como cifras de diseño. |
| 7 | SLYNYRD, *Pixelblog 20: Top Down Tiles* (https://www.slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles) | A escala de mapa: «mix in spaces of flat green with textured areas of differing vegetation density, which can create visually pleasing gradations» y «the negative space helps reduce noise». → **El gradiente de daño se dibuja por densidad**, no con tiles nuevos: más decorado roto y más junto cerca de la fuente, y más espacio negativo lejos. Con los tiles ya aprobados más un juego pequeño de decorado. → El artículo trata del tile; la composición de zona la pone este anexo. |
| 8 | Craig Reynolds, *Boids* (https://www.red3d.com/cwr/boids/) | Tres reglas (separación, alineación y cohesión), con vecindad «characterized by a distance […] and an angle», más evitar obstáculos. → **IA-2 (guía §3.3):** la fauna usa las tres reglas, más evitar al jugador y no salir de la zona purificada, con vecindad limitada para que el coste no crezca con el cuadrado de la bandada. → No copio su vuelo en 3D: aquí la posición avanza en píxeles enteros con un acumulador por eje (anexo de la parte 2, fase 3). |

**Fuente prevista que no aporta lo que se suponía.** *Gris*, en la ficha de
Steam (https://store.steampowered.com/app/683320/GRIS/), describe una «faded
reality» y que el progreso va «revealing new paths to explore», pero **no dice
que vuelva el color**, que es lo que la guía (§5, parte 3) quería verificar.
Confirma que el progreso abre caminos, que ya está contratado, y nada más. No
cuenta para las seis.

### B. Fuentes de pantalla que exige Diego

| Fuente | Resultado, 2026-10-01 |
|---|---|
| Taste Skill (https://www.tasteskill.dev/docs) | Carga. Dos bloqueos que pasan a escala de mapa: «one accent across the whole page» (el verde solo en lo purificado, también en el decorado de las siete zonas) y un solo sistema de formas (lo enfermo, diagonal; lo purificado, redondo; lo que responde, rectangular). Ya rigen; aquí se aplican a toda la autoría de decorado. |
| Emil Kowalski, *Great animations* (https://emilkowal.ski/ui/great-animations) | Carga. «It's easy to start adding animations everywhere […] animations lose their impact». → La fauna es el único movimiento ambiental del mundo y solo existe en zona purificada. Nada más se mueve solo: ni agua, ni hojas, ni humo animado. Que el humo se anime o no se decide en la fase 4, y es justo esta tensión. |
| Refero Styles (https://styles.refero.design/) | Carga. Cataloga sistemas de diseño de webs y productos. **No aplica** a componer un mapa de tiles. |
| Aceternity UI (https://ui.aceternity.com/components) | Carga. Componentes de React y Tailwind. **No aplica.** |
| `motionsites.ai` | No reabierta. Ya se registró como no aplicable el 2026-09-14 (anexo de exploración, A.2): es un banco de *prompts* para landings, sin criterios de movimiento. |
| Mobbin, Pinterest | No consultadas: exigen sesión iniciada, y no se inicia sesión en servicios de terceros desde esta herramienta. Siguen como deuda en la guía §4. |

**Recuento:** **8 fuentes de dominio** con observación accionable y cargadas
de verdad, más 2 del listado obligatorio que aportan una regla. Se supera el
mínimo de seis sin contar las no aplicables.


## Pruebas aplazadas — decisión de Diego, 2026-10-01

Diego decidió **aplazar las dos pruebas con personas** «para agilizar», y se
lo comunicó en persona a Juan José Rueda, que lo trasladó a la sesión del
2026-10-01. No hay registro escrito suyo en GitHub. Se anota aquí, con fecha y
con sus consecuencias:

- **«¿Por qué pierdo?»:** sin resultado. **La fase 4 se diseña con la
  hipótesis prudente: que no llega.** Es decir, que el combate no enseña solo
  que hay que atajar la causa, y por tanto **la zona tiene que enseñarla
  antes**. Si algún día la prueba dice que sí llega, el paisaje solo
  refuerza lo que el combate ya enseña: se pierde poco. Lo contrario, suponer
  que llega y equivocarse, dejaría siete zonas mudas. Diego confirma esta
  hipótesis al elegir la dirección.
- **Materiales:** sin resultado. La separación dE 9,2 sigue sin comprobar con
  personas, así que **la parte 1 sigue abierta** solo por esto. Las zonas se
  dibujan sobre el tileset aprobado y, si la prueba falla más adelante, la
  enmienda 9 (antes reservada como 6) cambia tintas y no mapas: los mapas son de material, no de color.
- **Las dos siguen como deuda** en la guía §4 y en el plan, con la hoja lista
  en `docs/ux/pruebas/2026-10-01-hoja-de-pruebas.md`.

## Fase 4 — Direcciones

Las tres respetan «Vereda» y «Umbral»: el tileset, la colisión, las salidas en
el camino, la cámara, el catálogo y el paso cerrado que la purificación abre.
**No cambian la paleta.** Cambian **cómo se recorre una zona y en qué orden
aparece la causa**.

Las tres comparten estas piezas:

- **Un hito por zona**, la única forma nueva. Es una silueta de varios tiles
  en la capa de entidades, ordenada por altura, que no se pisa ni responde y
  por tanto va sin contorno (Lynch, fuente 1).
- **El gradiente de daño por densidad de decorado** (SLYNYRD, fuente 7).
- **La fauna con *boids*, solo tras purificar** (IA-2, fuente 8).
- **Las reglas medidas de la parte 2.**

### A · «Rastro» — la zona es el camino hacia la causa · recomendada

- **Cómo se recorre:** un camino pisado principal lleva desde la entrada
  hasta la **fuente del daño**, donde está el monstruo. A lo largo del camino
  hay **tres viñetas de causa y efecto encadenadas**, cada una más cerca de la
  causa y más dañada que la anterior (Carson, fuente 2: «following
  Saknussemm»; Smith y Worch, fuente 3: dos objetos que el jugador une). En el
  Bosque, por ejemplo:
  1. tocones con el corte limpio (tala);
  2. troncos apilados junto a un claro sin árboles;
  3. el primer árbol quemado, con la ceniza todavía en diagonal hacia la
     fuente.
- **El hito** está en la fuente. Se ve por primera vez a media zona y se
  pierde detrás del follaje antes de reaparecer más cerca: negación y
  recompensa (fuente 5).
- **El paso cerrado** está **al otro lado de la fuente**: para seguir hay que
  pasar por el monstruo de la fuente. No contradice «el mapa no se estrecha»:
  ese monstruo es **combate de historia**, y «Vereda» ya dice que los combates
  de historia no se esquivan. Los encuentros comunes (IA-1, parte 4) patrullan
  fuera del camino principal, y se pueden rodear. Purificar abre el paso y
  devuelve la fauna detrás de la ola.
- **Caminos secundarios:** cortos, con espacio negativo y alguna persona o
  algún semillero. Ninguna viñeta de causa fuera del camino principal.
- **Por qué se recomienda:** es la única de las tres que **garantiza** que
  todo jugador ve la causa antes de pelear, sin depender de un texto. Responde
  directamente a la hipótesis prudente. Y el camino ya es la pista contratada
  en cada columna, así que **no añade ninguna forma más que el hito**.
- **Coste:** medio. Tres viñetas por zona salen de un juego pequeño de
  decorado por región, que ya está catalogado como «decorado del daño» en el
  paso 2a.
- **Riesgo:** linealidad. Se mitiga con caminos secundarios, pero la zona es,
  en esencia, un recorrido.

### B · «Claro» — la zona gira alrededor de un centro

- **Cómo se recorre:** la entrada da a un **claro central** (el nodo de
  Lynch) del que salen tres o cuatro ramales. Uno lleva a la fuente; los
  otros, a personas, semilleros, objetos y el puzzle (parte 7). Es el
  esquema de centro y radios de Disneyland (Rogers, fuente 4): desde el centro
  se ven varios hitos menores y el jugador **elige**.
- **La causa** se concentra en el claro. Es un pueblo o un campamento afectado,
  con **una persona que la nombra** en diálogo (parte 5) y las viñetas
  alrededor.
- **El hito** se ve desde el claro y marca el ramal de la fuente.
- **A favor:** la más exploratoria; casa con el puzzle de cada región, que
  está en un ramal.
- **En contra:** **la causa depende en parte de un texto**, y la fase 2 dice
  «texto que explique la causa: no va». Además, un jugador que vaya derecho al
  monstruo puede no pasar por las viñetas. Con la hipótesis prudente, esto es
  justo lo que hay que evitar. Y adelanta trabajo de la parte 5.

### C · «Antes y después» — la zona son dos mapas

- **Cómo se recorre:** la zona enferma es **estrecha**, un único corredor
  denso de daño hasta la fuente. Al purificar no solo se abre el paso:
  **cambia la topología**. Se abren dos o tres pasos a la vez, aparece una ruta
  que antes no existía y, por ella, la vuelta corta a Valdehoja. El
  mapa purificado es otro mapa.
- **La causa** está en el corredor, y es imposible no verla.
- **El hito** es el propio paso cerrado, enorme y visible desde la entrada:
  lo que no deja pasar.
- **A favor:** la más memorable, y la que más hace sentir la tesis de que el
  color se devuelve y vuelve con caminos (guía §3).
- **En contra:**
  - **dobla el coste de autoría**, con dos estados de mapa por zona y siete
    zonas;
  - **choca con «el mapa no se estrecha»** («Vereda», encuentros visibles): un
    corredor obliga al combate. Con encuentros visibles, eso exige una
    enmienda.
  - tensa la regla de máximo 2 salidas por pantalla en el estado purificado.

### Design Read (dirección A)

```
Registro y audiencia: juego, exploración con lectura obligada; jugador sin dominio ambiental.
Escena de uso: partida larga, el jugador avanza por el camino y mira hacia donde va.
Tesis visual: el camino lleva a la causa, y la causa se ve antes de tocarla.
Jerarquía y decisión dominante: «¿hacia dónde sigo?» → hito, gradiente, camino, viñeta, paso cerrado.
Materiales: tiles aprobados; decorado del daño por región; un hito por zona; ningún color nuevo.
Repertorio: hito = dónde está la fuente; viñeta = qué la causó; camino = por dónde; paso cerrado = qué falta.
Puntos de entrada: la tarea; el hito asoma por delante en la dirección del camino.
Riesgo que se evita: la zona-decorado que no explica nada, y el cartel que lo explica todo.
```

### Segunda decisión: el formato de los mapas

| | Texto (`data/world/zones/<zona>.txt`) · **recomendado** | Pintado en el editor de Godot |
|---|---|---|
| Qué hay hoy | Las tres zonas de prueba ya son texto. `ZoneRules` las valida, y `verify_movement` las recorre. | Nada. Habría que guardar el `TileMapLayer` en una escena por zona. |
| Revisar un cambio | Se lee en el diff del PR, carácter a carácter. | El diff de un `.tscn` es binario en la práctica: no se puede revisar. |
| Pintar | Hay que escribir los caracteres a mano. Una leyenda ampliada (decorado y viñetas) lo hace más largo de escribir. | Más cómodo y visual. |
| Riesgo con «Vereda» | Ninguno. | El editor reescribe archivos al guardar, igual que pasa ya con `project.godot`. |

La recomendación es **texto**, por coherencia con lo que ya existe y porque el
criterio de la asignatura se evalúa leyendo. El decorado y el hito pueden ir
en una segunda capa de texto por zona (`<zona>.deco.txt`) con su propia
leyenda, para que el mapa de materiales siga siendo legible.

### Pregunta a Diego

1. **¿Dirección A, B o C?** Recomendada: **A, «Rastro»**.
2. **¿Mapas en texto o en el editor?** Recomendado: **texto**.
3. **¿Confirmas la hipótesis prudente** de que, sin la prueba, las zonas
   enseñan la causa antes del combate?

**Respuesta de Diego, 2026-10-28** (en la sesión, al retomar el proyecto; el
PR #11 se fusionó sin comentario y por eso se le preguntó):

1. **Dirección A, «Rastro».**
2. **Mapas en texto.**
3. **Sí, confirma la hipótesis prudente:** las zonas enseñan la causa antes
   del combate.

## Contrato «Rastro» — bloqueado el 2026-10-28

**Elegido por Diego el 2026-10-28: dirección A, mapas en texto.** Hereda
«Vereda» (con las enmiendas 1 a 5) y «Umbral» sin tocarlos. Desde aquí se
cumple: nada de forma, densidad ni movimiento fuera de este contrato. **No
abre ningún color, tipografía ni duración nueva.**

**Los valores de la tabla los propone esta sesión** a partir de la dirección A
y de las fuentes de la fase 3; el visto bueno de Diego a esos valores es el
punto de control antes de Valdehoja. Si alguno no le sirve, se cambia antes de
dibujar, no después.

**Visto bueno de Diego a los valores: 2026-10-28**, sin cambios.

### Composición de una zona regional (Bosque, Cuenca, Costa, Llanura, Cumbre)

| Cláusula | Valor | Respaldo |
|---|---|---|
| Camino principal | Un camino pisado continuo de la entrada a la **fuente del daño**. Es el único camino que llega a la fuente | Dirección A; Lynch (fuente 1) |
| Viñetas de causa y efecto | **Exactamente 3**, todas **junto al camino principal** (a ≤ 2 tiles de él), en orden de daño creciente hacia la fuente. Cada una son **dos elementos que el jugador une** (causa y consecuencia), nunca uno que lo diga todo | Carson (2), Smith y Worch (3) |
| Viñetas fuera del camino | **Ninguna.** Los caminos secundarios llevan personas, semilleros o espacio negativo | Dirección A |
| Separación entre viñetas | Dos viñetas nunca caben en la misma pantalla de 480 × 270: se leen una a una | Smith y Worch (3): el cierre ocurre entre viñetas |
| Fuente del daño | Al final del camino principal. La ocupa el **monstruo de historia** de la región, que no se esquiva («Vereda») | Dirección A |
| Paso cerrado | Uno o más `blocker` **al otro lado de la fuente**, nunca antes de ella. La ola de purificación (enmienda 3) los retira | Catálogo 2a; «Vereda» |
| Salida tras purificar | Solo es alcanzable después de purificar. Sin purificar, la única salida alcanzable es la de entrada | Guía §5, parte 3 |
| Encuentros comunes | Fuera del camino principal y rodeables. El mapa no se estrecha para forzarlos (parte 4, IA-1) | «Vereda» |
| Hito | **Uno por zona**, en la fuente. Silueta de **entre 2 × 3 y 4 × 4 tiles** (32 × 48 a 64 × 64 px), en la capa de entidades ordenada por altura, **sin contorno**, no se pisa ni responde. Forma de la familia del daño de la región (diagonal y rota) | Lynch (1); catálogo 2a, regla 2 |
| Primera vista del hito | Entra en pantalla por primera vez **a media zona**, por delante en la dirección del camino; follaje lo tapa al menos una vez antes de la fuente | Tancoque (5); *Level Design Book* (6) |
| Gradiente de daño | **Por densidad de decorado del daño**, en tres franjas: cerca de la fuente, media y lejana. La franja lejana es la que más espacio negativo tiene. Ningún tile nuevo: decorado del catálogo 2a, tabla «decorado permitido» | SLYNYRD (7) |
| Pista por columna | Cada franja vertical de 480 px tiene al menos un tile de pista (camino, viñeta o hito) | Guía §5, parte 3 |
| Prueba de entrecerrar | Con la captura de la zona desenfocada, lo más luminoso es el camino o lo purificado; **nunca un decorado** | Rogers (4) |
| Movimiento ambiental | ~~Solo la fauna, y solo tras purificar~~. **Enmienda 8 (2026-10-28):** se mueve solo lo purificado: agua, flores, hierba, fauna y animales. Lo enfermo (humo, ceniza, agua muerta) es estático | Kowalski (fase 3, B); Diego |
| Animales domésticos | **Enmienda 7 (2026-10-28):** en Valdehoja desde el principio, sin responder. La fauna silvestre, solo dentro de una parte purificada | Diego |
| Paleta | **Enmienda 6 (2026-10-28):** madera y tejado bajo el techo de 0,22; agua viva, flores y prado por encima, solo en lo purificado | Diego; guía §3.2 bis |
| Verde en zona enferma | Ninguno, ni de adorno. Lo purificado lleva siempre valor, silueta o fauna además del verde | Guía §2.3 |
| Texto | Ningún cartel, flecha ni texto que explique la causa | Fase 2 |

### Las dos zonas que no son regionales

No tienen una forma propia en la fase 4. Se fija aquí lo que hereda cada una, y
lo que falta se pregunta a Diego **al abrir su apartado de la fase 5**, no
antes:

- **Valdehoja** (guía §5): empieza gris salvo **el jardín de Yara**, el único
  verde del mundo al empezar, con el primer `seedbed`. No tiene monstruo ni
  viñetas de causa. El camino principal lleva al jardín, y el jardín es su
  hito. Es el **marcador de progreso**: cada región purificada devuelve verde
  y fauna a una parte del pueblo. *Se pregunta al abrirla:* cuántas partes
  tiene el pueblo y qué parte devuelve cada región.
- **Cripta de la Avaricia:** las cinco clases regionales juntas (catálogo 2a).
  *Se pregunta al abrirla:* si sus viñetas son las cinco causas o una sola.

### Formato de los mapas

| Cláusula | Valor |
|---|---|
| Materiales | `data/world/zones/<zona>.txt`, un carácter por tile con la leyenda de `WorldTiles.LEGEND` (`.` suelo, `=` camino, `~` agua, `#` follaje). Sin cambios |
| Decorado, hito y entidades | Segunda capa por zona, `data/world/zones/<zona>.deco.txt`, **del mismo tamaño** que la de materiales, con su leyenda en cabecera (`; X = tipo, id, sólido|pisable[, AxB]`). Un espacio = nada |
| Partes (solo Valdehoja) | Tercera capa, `<zona>.parts.txt`, un carácter por parte. Añadida el 2026-10-28: con rectángulos, lo purificado acababa en cantos rectos |
| Validación | `ZoneRules.check()` sobre la capa de materiales, como hoy; `tools/verify_zone.gd <zona>` sobre las dos capas |
| Nombres | Identificador en inglés y `snake_case` (`ashen_forest`, como en `interactables.json`); el nombre del jugador, en `zones.json` |

### Verificación de cada zona (`tools/verify_zone.gd`, por escribir en Valdehoja)

1. Búsqueda en anchura desde la entrada: la salida es **inalcanzable** en
   enfermo y **alcanzable** tras retirar los `blocker`.
2. La fuente es alcanzable solo por el camino principal.
3. Hay **3 viñetas**, todas a ≤ 2 tiles del camino principal, ninguna en la
   misma pantalla que otra.
4. Hay **un hito**, del tamaño del contrato, y ningún `blocker` entre la
   entrada y la fuente.
5. Cada franja de 480 px tiene al menos una pista.
6. Ningún decorado pertenece a una clase de `interactables.json`.
7. `verify_palette.py image --world` sobre la captura completa, y la prueba de
   entrecerrar sobre la misma captura.

Valdehoja y la Cripta adaptan los puntos 2 a 4 a lo que se decida al abrirlas;
el resto se cumple igual.

**Tokens nuevos que abre el contrato:** ninguno. Los de la enmienda 6 se
abren con ella: `WOOD_*`, `ROOF_*`, `AQUA_*`, `BLOOM_*`, `VITAL_300`,
`VITAL_400` y `VITAL_600`. Las cifras de composición
(3 viñetas, tamaño del hito, 2 tiles de distancia) son reglas de autoría y
viven en `verify_zone.gd`, no en `DesignTokens`, porque no se dibujan.

### Fase 5 — orden de trabajo

Una zona por sesión, en el orden de la guía. Cada zona sigue el paso a paso del
protocolo, con su propio apartado aquí:

1. **Mapa en texto** (materiales y decorado) y `verify_zone.gd` en verde.
2. **Decorado del daño** de la región con `tools/gen_*.py`, y su hito.
3. **Zona montada** en el motor, con captura a 480 × 270.
4. **Estados:** enferma, purificada y la ola entre las dos.

Al final de cada paso: captura, cláusula que lo respalda, siguiente paso y
visto bueno de Diego.

## Tensiones que recogió la fase 3 (resueltas en la fase 4 y el contrato)

Se enumeran **sin recomendar ninguna**: las direcciones se plantean cuando
estén los resultados.

1. **«¿Por qué pierdo?» (prueba A).**
   - **Si llega**, las zonas pueden ser sutiles: el paisaje refuerza una
     causa que el combate ya enseña.
   - **Si no llega**, cada zona tiene que **enseñar la causa antes del
     combate**: viñetas de causa y efecto en el camino a la fuente (fuentes 2
     y 3), y quizá un nodo con una persona que la nombre (parte 5). Es una
     dirección distinta, más densa.
2. **Los materiales (prueba B):** si la separación dE 9,2 no basta, hace falta
   la enmienda 9 (antes reservada como 6) antes de dibujar siete zonas sobre el tileset.
3. **Formato de mapa: texto o editor.** Lo decide Diego en la primera zona
   (guía §5). Las zonas de prueba de la parte 2 ya son texto, y `ZoneRules`
   las valida: es lo que existe hoy.
4. **El hito, como forma nueva:** cómo se dibuja (sprite de varios tiles en
   la capa de entidades, ordenado por altura) y si su silueta puede asomar
   desde la zona anterior.
5. **El humo y otros elementos ambientales:** animados o quietos. Kowalski
   (B) y el repertorio (la fauna es el único movimiento) empujan a quietos.
6. **Valdehoja como marcador de progreso** (guía §5): qué parte del pueblo
   devuelve cada región purificada, en datos (`GameState`) y en el mapa.
7. **Prueba de entrecerrar** (fuente 4): medirla en `verify_zone`, además de
   las cuatro reglas de la guía.

**Lo que ya está medido y obliga** (partes 1 y 2), sin depender de las
pruebas:

- cada franja vertical de 480 px lleva al menos una pista (`clue`);
- como mucho 2 salidas por pantalla, y ningún borde pisable sin salida;
- con la zona enferma, la salida queda **inalcanzable**, y alcanzable tras
  purificar (búsqueda en anchura, guía §5);
- ningún decorado de una clase que responde;
- el verde solo en lo purificado.

## Fase 5 · Valdehoja — abierta el 2026-10-28

### Las dos preguntas de Valdehoja, respondidas por Diego el 2026-10-28

1. **Cinco partes, una por región**, además del jardín de Yara, que es verde
   desde el principio. La Cripta no devuelve ninguna: su final cambia el mundo
   entero.
2. **Cada parte está ligada al daño de su región**, para que el pueblo repita
   la causa que el jugador ya aprendió:

| Región purificada | Parte de Valdehoja que vuelve | Id en `zones.json` |
|---|---|---|
| Bosque de las Cenizas | La arboleda del pueblo (sureste) | `ashen_forest` |
| Cuenca de Alquitrán | El río (este) | `tar_basin` |
| Costa Quebrada | La era y sus caminos, sin basura (centro) | `broken_coast` |
| Llanura Marchita | Las terrazas de cultivo (noroeste) | `withered_plain` |
| Cumbre Menguante | La acequia que baja del deshielo y riega las terrazas | `waning_peak` |
| — (desde el principio) | El jardín de Yara, con el primer semillero y el hito | `yara_garden` |

### Paso 1 — Mapa en texto y `verify_zone.gd` · ENTREGADO el 2026-10-28

Primera entrega: el mapa de materiales, sin decorado. **Diego la juzgó
«horrible, desabrida»:** faltaban árboles, animales y detalle, y pidió el nivel
de los juegos 2D de GBA (Zelda, Pokémon) y de Final Fantasy. De esa revisión
salieron las enmiendas 6, 7 y 8 (guía §3.2 bis) y el paso 2 se hizo a
continuación, en la misma sesión.

**Referentes.** Los tutoriales que se buscaron (itch.io, slynyrd.com) no se
pudieron abrir: están fuera de la red permitida en la sesión en la nube. **No
cuentan como fuentes.** Lo que se tomó de los juegos que nombra Diego es
observación propia, y se declara así:

- copas de árbol sueltas y solapadas en el borde del bosque, nunca una masa
  plana;
- el tejado domina la casa y es lo que se lee de lejos;
- el suelo lleva cobertura menuda (matas, piedras, flores) con espacio
  negativo;
- el agua y la hierba se mueven;
- cuatro o cinco tonos por material.

### Paso 2 — Decorado, casas, hito y animales · ENTREGADO, espera visto bueno

**Cláusulas:** contrato «Rastro» (hito, gradiente por densidad, formato de
mapas); catálogo 2a (gramática de forma, hueco métrico, regla de negación);
enmiendas 6, 7 y 8.

**Entregado:**

- `tools/gen_world_decor.py` → `assets/sprites/world/decor/`: 34 piezas, cada
  una con su variante enferma y purificada cuando la tiene:
  - el árbol, con dos copas (enfermo: ralo, roto y con ramas desnudas;
    purificado: redondo);
  - el arbusto, la hierba alta, el matojo, las flores (mustias en lo enfermo),
    la hilera de cultivo (enferma: monocultivo seco; purificada: cereal y
    legumbre alternos), el tocón (purificado: con brote) y la basura suelta
    (desaparece al purificar);
  - lo que no cambia al purificar: la casa de madera y la de piedra (tejado a
    cuatro aguas, 3×3 tiles), el pozo, la roca y las piedrecitas;
  - el hito: el árbol de Yara, de 48×64 y en flor;
  - lo que responde, con contorno `ASH_050`: el semillero y Yara;
  - los animales domésticos (gallina de 8×8, perro y cabra de 16×16) y la
    fauna silvestre (pájaro y mariposa de 8×8, con dos cuadros cada uno).
- `tools/gen_tiles.py`, enmienda 6:
  - el agua purificada pasa a `AQUA_700` con rizos `AQUA_900`;
  - la tierra purificada pasa a prado (`VITAL_600`, con briznas `VITAL_700` y
    `VITAL_400`);
  - la **fila 7** nueva del atlas es el borde del prado: festón redondo
    contra la tierra enferma.
- `src/world/world_tiles.gd`: `purified_mask()` y el uso de la fila 7 en
  `paint()`.
- `data/world/zones/valdehoja.deco.txt`:
  - seis casas, cada una con su camino delante de la puerta, y el pozo en la
    era;
  - árboles en todo el borde del bosque y una arboleda de árboles sueltos;
  - cobertura de suelo con espacio negativo y las terrazas de monocultivo;
  - el jardín de Yara, con flores, mariposas y pájaros;
  - gallinas junto a la casa de Ilan, el perro en la era y cabras en los
    prados.
- `data/world/zones/valdehoja.parts.txt`: las seis partes como capa de texto
  con formas que siguen orillas, setos y caminos. Sustituye a los rectángulos
  de `zones.json`; así se resuelve lo que se planteó en el paso 1 sobre los
  cantos rectos (opción a).
- `ZoneRules.load_deco()` lee el tamaño de cada pieza, y
  `ZoneRules.load_parts()` lee la capa de partes.
- `tools/verify_zone.gd` comprueba además:
  - que las piezas estén enteras;
  - que los árboles puedan ir sobre el follaje y la fauna sobre el agua;
  - que cada casa tenga camino delante de la puerta;
  - que la fauna silvestre esté dentro de una parte.
- `tools/zone_preview.py`: pinta el decorado ordenado por altura, cada pieza en
  el estado de la parte en la que apoya, y la pantalla de 480 × 270 con Ilan.

**Capturas** (`zone_preview.py`, a 1×):

- `docs/ux/capturas/2026-10-28-valdehoja-inicio.png`: la zona entera al
  empezar la partida.
- `docs/ux/capturas/2026-10-28-valdehoja-cinco-regiones.png`: con las cinco
  partes devueltas.
- `docs/ux/capturas/2026-10-28-valdehoja-pantalla-casa.png`: 480 × 270 en la
  aparición, con Ilan.
- `docs/ux/capturas/2026-10-28-valdehoja-pantalla-jardin.png`: el jardín de
  Yara, el primer verde del juego.
- `docs/ux/capturas/2026-10-28-valdehoja-pantalla-era-purificada.png`: la era
  y la arboleda ya devueltas.

#### Verificado

- `python tools/verify_palette.py tokens`: **47 tokens, sin deriva**.
- `python tools/verify_tileset.py`: **dentro del contrato**.
  - Prado frente a tierra enferma: valor 4,37 en visión normal (piso 1,5).
  - Prado frente a follaje: dE 17,3. Agua purificada frente a follaje: dE 58,7.
  - Contorno `ASH_050` sobre el agua viva: 4,19:1.
- `verify_palette.py image --world` sobre las cinco capturas: **todo píxel es
  un token** en cuatro de ellas. En la quinta falla, y se dice abajo.
- Comprobaciones de `verify_zone.gd` pasadas en el espejo en Python: **28 de
  28**, más las seis puertas de las casas.

#### FALLA medido, y se dice

- **El sprite de Ilan no pasa `--world`:** su contorno `ash_950` (72 px) y sus
  ojos `ash_900` (2 px) superan el techo de 0,22. Es el sprite aprobado en la
  parte 2, paso 5, y el contorno oscuro es una decisión de ese paso. **No se ha
  tocado.** Se decide si `ash_950` y `ash_900` cuentan como tinta de
  personaje, igual que las de la interfaz, o si se cambian.
- **Tres intentos fallidos en esta sesión, corregidos antes de entregar:**
  - el agua purificada clara (`AQUA_500`) dejaba el contorno `ASH_050` a
    1,10:1;
  - oscurecer el follaje purificado para separarlo del prado bajaba su valor a
    1,34 (piso 1,5);
  - un prado de base `VITAL_700` quedaba a dE 1,2 del follaje.

  Los tres se midieron, se revirtieron y la solución final es la de arriba.
- **`ash_900` en ventanas y ojos del decorado** superaba el techo: se cambió
  por `water_700`.

#### Pendiente, y se dice

- **Nada de esto se ha ejecutado en Godot.** En la nube no hubo permiso para
  lanzar el binario. Faltan `verify_zone`, `verify_movement` y
  `verify_usability`. La fila 7 del atlas obliga a que Godot reimporte
  `world.png`.
- **La colisión del decorado sólido** (casas, árboles, pozo) no existe todavía
  en el motor: `verify_zone` la usa para el recorrido, pero `WorldRoot` aún no
  monta la capa de decorado. Es el paso 3.
- **Enmienda 8, el movimiento:** los sprites de fauna y gallina tienen dos
  cuadros, pero el brillo del agua y el vaivén de la hierba no tienen cuadros
  todavía. Es el paso 4 (estados).
- **Prueba de entrecerrar:** con la captura del motor, en el paso 3.
- **La salida al Bosque** lleva a una zona aún sin dibujar.

**Visto bueno de Diego al paso 2: 2026-10-28** («sí, dale»).

### Paso 3 — Valdehoja en el motor · HECHO, espera visto bueno

**Cláusulas:** «Umbral» (colisión del tile entero, capa de entidades ordenada
por altura); contrato «Rastro» (formato de los mapas); enmiendas 6 y 7.

**Entregado:**

- `src/world/world_decor.gd` (`WorldDecor`) recorre la capa de decorado:
  - cada pieza es un `Sprite2D` en `WorldRoot.entities`, con la posición en
    su pie, así que el orden por altura la pone delante o detrás de Ilan;
  - cada pieza sólida lleva un `StaticBody2D` del tamaño entero de la pieza,
    en tiles, igual que el terreno y que el recorrido de `verify_zone`;
  - el estado de cada pieza sale de la casilla de su pie, y la fauna
    silvestre solo se monta en lo purificado.
- `WorldDecor.purified_lookup()` da el estado por casilla:
  - en una zona sin partes, la bandera `purified_<zona>` como antes;
  - en Valdehoja, cada parte sigue a la bandera de su región, el jardín está
    purificado siempre y el resto sigue a la bandera de Valdehoja (el final).
- `WorldRoot.enter_zone()` pinta con ese estado por casilla, monta el decorado
  y retira el de la zona anterior. Las zonas de prueba, sin capa de decorado,
  se pintan igual que antes.
- `tools/verify_zone.gd` gana una sección «En el motor»:
  - un sprite por pieza y un cuerpo por pieza sólida;
  - andando hacia la puerta de una casa, Ilan se para fuera;
  - el jardín está purificado al empezar y la arboleda no;
  - con `purified_ashen_forest`, vuelven la arboleda y sus pájaros.
- `tools/valdehoja_capture.tscn`: las capturas del motor a 480 × 270 (casa,
  jardín, era con la Costa purificada y con todo purificado).
- `tools/valdehoja_play.tscn`: para pasear por Valdehoja con el teclado.

#### Verificado en Godot 4.7.2 (2026-10-28, con permiso de Diego en la sesión)

- `--import`: limpio; `project.godot` no se reescribió.
- `verify_zone.tscn -- valdehoja`: **41 de 41**, más 2 pendientes declarados
  (la salida al Bosque sin dibujar y la prueba de entrecerrar). En el motor:
  - 377 sprites ordenados por altura y 146 cuerpos sólidos;
  - andando hacia la puerta de una casa, Ilan se para fuera;
  - el jardín está purificado al empezar y la arboleda no;
  - con el Bosque purificado, vuelven la arboleda y su fauna.
- `verify_movement`: **99 de 99**. `verify_usability`: **16 de 16**.
  `verify_camera`: **37 de 37**. Las zonas de prueba no cambian.
- **Dos fallos que la prueba cazó en la primera pasada, y se corrigieron:**
  - Al volver a entrar en la zona, el decorado viejo seguía en el árbol hasta
    el final del cuadro y Godot renombraba el nuevo. Ahora `WorldRoot` lo
    saca del árbol antes de liberarlo.
  - **La arboleda no tenía fauna:** el pájaro previsto caía bajo un árbol y
    el generador lo descartó. Se añadió una en (36, 23). Era un defecto de
    contenido, no de la prueba.
- **Capturas del motor**, a 480 × 270: `docs/ux/capturas/2026-10-28-valdehoja-motor-casa.png`,
  `-jardin.png`, `-era.png` (con la Costa purificada) y `-todo.png`. Salen
  iguales a las de `zone_preview.py`.
- `verify_palette.py image --world` sobre las cuatro: **FALLA solo por el
  sprite de Ilan** (`ash_950`, 72 px; `ash_900`, 2 px), el hallazgo ya anotado
  en el paso 2. Todo el decorado y el terreno son tokens dentro del contrato.

#### Pendiente, y se dice

- **Prueba de entrecerrar**: no tiene todavía una medida automática; se
  propone escribirla en el paso 4.
- **El juego principal (`scenes/main.tscn`) todavía no lleva al mundo**: sigue
  abriendo la demo de batalla. El paso del mundo al combate es la parte 4.
- **Enmienda 8 (movimiento):** paso 4, estados.
- **El sprite de Ilan frente a `--world`:** lo decide Diego.

**Siguiente:** paso 4, estados: la ola por partes, el agua y la hierba que se
mueven y los animales que andan (enmienda 8), y la prueba de entrecerrar.
