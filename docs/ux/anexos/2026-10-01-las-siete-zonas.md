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

**Estado:** fases 1 a 4 escritas. **Las dos pruebas con personas quedan
aplazadas por decisión de Diego** (2026-10-01; ver «Pruebas aplazadas»), y la
fase 4 se plantea con la hipótesis prudente. **Falta que Diego elija la
dirección y el formato de mapa.**

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
  enmienda 6 cambia tintas y no mapas: los mapas son de material, no de color.
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

**Respuesta:** pendiente.

## Tensiones que recogió la fase 3 (resueltas en la fase 4)

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
   la enmienda 6 antes de dibujar siete zonas sobre el tileset.
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
