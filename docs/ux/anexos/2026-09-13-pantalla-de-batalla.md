# Anexo de diseño — Pantalla de batalla de *Ecos de la Tierra*

Fecha: 2026-09-13
Pantalla: combate por turnos (`scenes/battle/battle_screen.tscn`, aún inexistente).

Estado del proyecto al abrir el anexo: el motor de combate está completo y
verificado, pero **no existe ninguna capa gráfica**. `scenes/main.tscn` es un
único `Node` con `battle_demo.gd`, que escribe el combate por consola.
`assets/sprites`, `assets/tilesets`, `assets/fonts` y `assets/audio` contienen
solo `.gitkeep`.

---

## Fase 1 — Identificación de los usuarios

### Usuario primario — el jugador

- **Quién.** Jugador de RPG 2D de consola portátil, en la tradición de Pokémon,
  Final Fantasy y Golden Sun de GBA. No es «el usuario»: es alguien que ya sabe
  leer una pantalla de batalla por turnos y espera encontrar las convenciones
  del género donde siempre estuvieron.
- **Necesidad real, en sus palabras.** «Quiero saber, sin leer un tutorial, a
  quién le toca, cuánta vida le queda a cada uno, qué le pasa al monstruo y qué
  puedo hacer yo en este turno.»
- **Experiencia con la tecnología.** Intermedia. Maneja menús de videojuego con
  fluidez; no necesita que le expliquen qué es una barra de vida.
- **Edad.** 14 a 30 años. El protagonista tiene 16 y el tema ambiental apunta a
  público adolescente y joven adulto.
- **Género.** Mixto, sin sesgo. El elenco jugable ya es mixto (Ilan, Nix /
  Bruma, Coral, Suri), lo que evita que la pantalla hable a un solo público.
- **Cultura.** Hispanohablante. Toda la interfaz va en español; el código queda
  en inglés por convención del proyecto. Los PV son enteros, así que el punto
  conflictivo del separador decimal no llega a darse.
- **Nivel de habilidad en el dominio.** Alto en «jugar un RPG», **nulo en el
  dominio real del juego**: nadie llega sabiendo que a la Llama de la
  Deforestación se la ataja con una Línea Cortafuegos. Esa es la brecha que la
  interfaz tiene que cerrar, y es la razón de ser del juego.

**Condiciones reales de uso.** Sesiones largas en PC con teclado, y sesiones
cortas en Android táctil (el proyecto exporta a ambos desde el mismo código).
Pantalla de 480×270 escalada; en móvil, una mano y el pulgar sobre los
controles. Luz variable. Frecuencia alta: el jugador verá esta pantalla cientos
de veces, así que cada animación que se repita debe ser corta o poder saltarse.

### Usuario secundario — el evaluador

Docente de Diseño de Interfaces de Software. Necesita ver en pocos minutos que
hay criterio de interfaz, no solo lógica: jerarquía, estados, accesibilidad y
retroalimentación. Esto no cambia la pantalla, pero sí obliga a que **cada
estado tenga su vista** y a dejar este anexo como entregable.

### Dato que falta y se pregunta, no se inventa

Plataforma que se prioriza para la entrega (PC con teclado, Android táctil o las
dos). Cambia el tamaño mínimo de los controles: 44 px de toque es obligatorio en
táctil, y a 480×270 eso es una fracción enorme de la pantalla. Se pregunta en la
fase 4.

---

## Fase 2 — Análisis de la comunicación

| Necesidad del usuario | Qué debe comunicar la interfaz | Cómo se sabe que llegó |
|---|---|---|
| «¿A quién le toca?» | Quién actúa ahora y quién sigue | Lo identifica en menos de 1 s sin buscar |
| «¿Cuánta vida me queda?» | PV de cada miembro, y cuál está en peligro | Detecta al herido sin contar cifras |
| «¿Qué le pasa al monstruo?» | Si está purificado o sigue regenerándose | Entiende por qué el daño «no sirvió» |
| «¿Qué puedo hacer?» | Las cuatro opciones y cuáles puede pagar | Elige sin probar opciones bloqueadas |
| «¿Qué acaba de pasar?» | El resultado del último golpe | Relaciona la acción con su efecto |
| «¿Por qué pierdo?» | Que le falta la contramedida correcta | Cambia de estrategia sin que se lo digan |

### Decisión dominante

**Qué acción tomo en este turno, sabiendo si el monstruo ya está purificado o
no.** Una sola. Todo lo demás en la pantalla se subordina a esa decisión.

Esto es lo que distingue a este juego de un RPG cualquiera: el estado
`Monster.is_purified` no es un detalle de balance, es **la información que hace
que el jugador entienda el mensaje ambiental del juego**. Si el jugador no ve
que el monstruo se regenera porque no se atajó la causa, el juego falla en su
propósito, por muy bonito que se vea. El indicador de purificación no es un
adorno del HUD: es la pantalla.

### Jerarquía de la información

1. **El monstruo y su estado de purificación.** Lo más grande de la pantalla.
2. **El menú de acción del turno actual.** Donde se toma la decisión.
3. **PV y energía del grupo.** Cifra legible, no solo barra.
4. **El registro de batalla.** Última línea siempre visible; el historial, bajo
   demanda.
5. **Estados alterados y orden de turnos.** Presentes, pero subordinados.

### Qué NO va en la pantalla

- La tabla Q del jefe final en crudo. El jugador debe **notar** que el jefe se
  resiste a lo que repite, no leer un diccionario de pesos. Se comunica con la
  reacción del monstruo, no con cifras.
- Las estadísticas completas (ataque, defensa, velocidad base). Ruido durante el
  turno; van en un menú aparte.
- El contador de experiencia durante el combate. Va en la pantalla de victoria.
- El nombre técnico de los tipos ecológicos como `EcoType.FIRE`. El jugador lee
  «Fuego», que ya está resuelto en `Enums.eco_type_name()`.

---

## Fase 3 — Investigación profunda

Consultada el 2026-09-13. Una observación accionable por fuente.

### Fuentes accesibles

| Fuente | URL | Observación accionable |
|---|---|---|
| Taste Skill | https://www.tasteskill.dev/docs | «Un solo acento en toda la página» y «un solo sistema de radio de esquina: todo agudo, todo suave o todo pastilla». Aplicado aquí: **todo agudo**, 0 px de radio en cada marco, porque el pixel art a 480×270 no puede permitirse esquinas redondeadas — una curva de 2 px se lee como un error de dibujo, no como un estilo. Y un solo acento: el verde de purificación. Prohibidos los degradados tipo *mesh blob*. |
| Emil Kowalski | https://emilkowal.ski/ui/7-practical-animation-tips | «Menos de 300 ms como regla», «`ease-out` para lo que entra», «no animes desde `scale(0)`, arranca en 0.9». Aplicado: el menú entra en 160 ms con `ease-out`; los números de daño suben y se desvanecen en 260 ms; nada supera 300 ms, porque el jugador verá esta transición cientos de veces. |
| Refero Styles | https://styles.refero.design/ | Cataloga sistemas por carácter visual («instrumento de precisión de medianoche», «editorial de miel al sol») en vez de por componente. Aplicado: las tres direcciones de la fase 4 se nombran por **carácter**, no por componente, para que la elección sea de atmósfera y no de widget. |
| Aceternity UI | https://ui.aceternity.com/components | Su catálogo de fondos por capas (Aurora, Background Lines, Noise, Grid) muestra que **el fondo puede cargar la atmósfera sin robarle legibilidad al primer plano**. Aplicado: el fondo de batalla va en tres capas con parallax mínimo y se le baja el contraste bajo los paneles de UI, para que el texto nunca compita. |
| Crítica de Final Fantasy VI (Pratt IXD) | https://ixd.prattsi.org/2018/01/design-critique-final-fantasy-vi-ios-app/ | «Third-best mapping»: el menú del grupo se ordena **en la misma configuración espacial** en que los personajes aparecen en pantalla. Y el fallo del port a iOS: botones pequeños, opciones en gris que estorban, y el pulgar tapando lo que selecciona. Aplicado: el orden del HUD del grupo espeja el orden de los sprites en el campo; las opciones sin energía **no se ocultan ni se dejan en gris mudo**: se muestran con el coste en rojo, que enseña, mientras que el gris solo frustra. |
| GDQuest — pixel art en Godot 4 | https://www.gdquest.com/library/pixel_art_setup_godot4/ | Filtro `Nearest`, `stretch/mode = viewport`, **`stretch/scale_mode = integer`** (desde 4.3) para que la escala sea 2×, 3×, 4× y nunca decimal. Verificado contra `project.godot`: el filtro ya está en `0` (Nearest) y el stretch en `viewport`, pero **falta `scale_mode = integer`**; sin eso, 480×270 escalado a 1440×810 da 3× exacto, pero cualquier ventana redimensionada por el jugador rompe la rejilla de píxeles. Corrección pendiente para el paso 1. |

### Fuentes inaccesibles — registradas, no inventadas

| Fuente | Motivo | Fecha |
|---|---|---|
| `mobbin.com` | HTTP 403. Exige sesión iniciada. | 2026-09-13 |
| `motionsites.ai` | Exige registro para ver los prompts; las miniaturas públicas no aportan duraciones ni curvas. Además cataloga plantillas de web, no movimiento de videojuego. | 2026-09-13 |
| `pinterest.com` (tablero «RPG battle UI») | HTTP 403 y redirección a dominio regional; el contenido devuelto llegó truncado. | 2026-09-13 |
| `gameuidatabase.com` (etiqueta RPG) | HTTP 403. | 2026-09-13 |

Se consultaron **6 fuentes con observación accionable**: 4 del listado
obligatorio (Taste Skill, Emil Kowalski, Refero, Aceternity) más 2 específicas
del dominio, que para una pantalla de batalla de RPG pesan más que cualquier
referente web. Las 3 obligatorias restantes quedaron fuera por bloqueo de
acceso, no por omisión.

### Nota de honestidad metodológica

Cuatro de las siete fuentes obligatorias son catálogos de **UI web y de apps
móviles**. Para una pantalla de batalla de RPG en pixel art a 480×270 su aporte
es real pero parcial: sirven para jerarquía, movimiento y criterio anti-genérico,
no para convenciones del género. Por eso se sumaron dos fuentes de dominio
(la crítica de Final Fantasy VI y la guía de pixel art de GDQuest), que son las
que gobiernan la composición. Esto se declara aquí en vez de disimularse.

---

## Fase 4 — Elección de dirección y contrato

Se presentaron tres direcciones (Ceniza y Brasa · Mediodía de Solmira ·
Herbario de Campo). El usuario eligió **Ceniza y Brasa**, plataforma **PC con
teclado**, y **pixel art generado por script** como vía de assets.

### Contrato de diseño — BLOQUEADO 2026-09-13

- **Dirección:** *Ceniza y Brasa*. El mundo está apagado en grises de ceniza y
  el único color saturado del juego es el verde de purificación; el color vuelve
  a la pantalla a medida que el jugador ataja la causa del daño.
- **Referentes que la sostienen:**
  - https://www.tasteskill.dev/docs — bloqueo de un solo acento y un solo
    sistema de radio.
  - https://emilkowal.ski/ui/7-practical-animation-tips — techo de 300 ms y
    `ease-out` para lo que entra.
  - https://ixd.prattsi.org/2018/01/design-critique-final-fantasy-vi-ios-app/ —
    *third-best mapping* entre el HUD del grupo y la posición de los sprites.
  - https://www.gdquest.com/library/pixel_art_setup_godot4/ — `Nearest`,
    `viewport`, `scale_mode = integer`.
  - https://ui.aceternity.com/components — fondo por capas que no le roba
    legibilidad al primer plano.
  - https://styles.refero.design/ — direcciones nombradas por carácter.

#### Paleta — tokens exactos

Ceniza (estructura, fondos, texto):

| Token | Hex | Uso |
|---|---|---|
| `ash_950` | `#17141c` | Fondo más profundo, bandas del viewport |
| `ash_900` | `#221d2a` | Fondo de panel |
| `ash_800` | `#2e2836` | Relleno de panel de UI |
| `ash_700` | `#3a3540` | Cielo ceniza, canal de barra |
| `ash_600` | `#4d4657` | Borde inactivo. Solo forma, nunca texto |
| `ash_400` | `#9c95a7` | Texto secundario, opción no enfocada (4,9:1 — AA). Ver enmienda 1 |
| `ash_200` | `#b8b0c4` | Barra de energía, texto de apoyo |
| `ash_050` | `#e8e4ee` | Texto primario y cifras (11,4:1 sobre `ash_800` — AAA) |

Brasa (el daño, la causa activa):

| Token | Hex | Uso |
|---|---|---|
| `ember_500` | `#e8562e` | **Solo relleno de barra y formas.** Nunca texto (3,9:1) |
| `ember_400` | `#f08a3c` | Texto de aviso (5,7:1 — AA) |
| `ember_300` | `#ffc14d` | Cursor, foco, cifras críticas (8,8:1 — AAA) |

Acento único — purificación:

| Token | Hex | Uso |
|---|---|---|
| `vital_500` | `#4ade80` | **Reservado a la purificación.** Marco, sello y sprite purificado (8,2:1 — AAA) |
| `vital_700` | `#2b9d5a` | Sombra del verde, 1 px |

**Regla de acento, no negociable:** el verde `vital_500` no aparece en ninguna
otra parte de la interfaz. Las barras de PV **no son verdes**: van de `ash_050`
(sano) a `ember_400` (herido) a `ember_500` (crítico), es decir, la vida se
drena hacia la brasa. Así el verde conserva un solo significado —«la causa se
atajó»— y el jugador lo aprende sin que nadie se lo explique.

#### Tipografía y escala

- Fuente de mapa de bits propia de 6×8 px, generada por script, con cobertura
  de español completa: `A-Z a-z 0-9`, `á é í ó ú ü ñ Ñ ¿ ¡ « » · —`.
- Escala **solo por múltiplos enteros**: 8 px (cuerpo) y 16 px (título de
  monstruo, cifras de daño). Nada intermedio: un pixel font a 1,5× se rompe.

#### Espaciado y radios

- Escala de espaciado en múltiplos de 4: `2 · 4 · 8 · 12 · 16 · 24 · 32`.
  Ningún valor fuera de esta escala sin justificarlo por escrito.
- **Radio de esquina: 0 px en todo.** Bloqueo de forma «todo agudo». A 480×270
  una curva de 2 px se lee como un error de dibujo.
- Bordes de 1 px: `ash_600` inactivo · `ember_300` enfocado · `vital_500`
  purificado.

#### Movimiento

Techo de 300 ms. Solo se animan `position`, `scale` y `modulate` (equivalentes
en Godot de `transform` y `opacity`).

| Transición | Duración | Curva |
|---|---|---|
| Cursor del menú | 90 ms | `ease-out` |
| Entrada del menú de acción | 160 ms | `ease-out`, desde `scale 0.94` |
| Barra de PV | 220 ms | `ease-out` |
| Sacudida al recibir daño | 120 ms | lineal |
| Cifra de daño (sube y desvanece) | 260 ms | `ease-out` |
| **Purificación** | 300 ms | `ease-out` |

La purificación es la única transición que llega al tope de 300 ms: es el evento
que carga el mensaje del juego y merece el momento más largo de la pantalla.
Ajuste de movimiento reducido expuesto como opción del juego, ya que Godot no
recibe `prefers-reduced-motion` del sistema.

#### Fuera de alcance de este contrato

Exploración top-down y tilemaps de mundo · diálogos y retratos · inventario
fuera de combate · guardado de partida · audio · animaciones de ataque cuadro a
cuadro (el *idle* de 2 cuadros sí entra) · menú de título · pantalla de
opciones.

### Enmiendas

**Enmienda 1 — 2026-09-13. `ash_400` aclarado de `#7a7189` a `#9c95a7`.**
Al medir los contrastes reales del paso 1 (y no estimarlos), `#7a7189` dio
**3,1:1** sobre `ash_800`: no llega al piso AA de 4,5:1 que el propio contrato
exige para texto, y estaba asignado a texto secundario. Se aclaró conservando
matiz (0,729) y saturación (0,096), quedando en **4,9:1**. El resto de cifras
de contraste de la tabla se corrigieron a los valores medidos; las anteriores
eran estimaciones mías y se desviaban hasta 0,7 puntos.
Pendiente de confirmación del usuario en el punto de control del paso 1.

Todas las cifras salen de medir la paleta con la fórmula de luminancia relativa
de WCAG 2.1 sobre `ash_800`, no de apreciación visual.

**Enmienda 2 — 2026-09-13. Composición diagonal del campo de batalla.**
Autorizada expresamente por el usuario, que juzgó la pantalla «muy plana» y
pidió la disposición de los RPG de GBA. Cambia **solo el layout**: la paleta, la
tipografía, la escala de espaciado y las duraciones del contrato siguen intactas
(la auditoría sigue dando 100 %). Se detalla en la iteración 4.


---

## Fase 5 — Registro de implementación

Un apartado por paso, con lo entregado y la cláusula que lo respalda.

### Paso 1 — Tokens · 2026-09-13

- `src/ui/design_tokens.gd`: paleta, papeles semánticos, escala de espaciado,
  forma y duraciones. Única fuente de verdad; ninguna escena escribe un color
  suelto.
- `tools/gen_font.py` → `assets/fonts/ceniza.png` + `ceniza.fnt`. Fuente de
  mapa de bits de 111 glifos, celda de 6×11 px, línea base en 9, interlineado
  12. Cobertura completa de español más `▶ ◀ ▲ ▼ ✖ ✓ ♥`.
- `project.godot`: añadido `window/stretch/scale_mode="integer"`, que faltaba.

**Cláusulas:** «Paleta — tokens exactos», «Tipografía y escala», «Espaciado y
radios», «Movimiento».

**Verificado:** `tools/verify_font.gd` confirma que Godot carga la fuente, la
mide a 6 px por carácter y no le falta ningún glifo del español.
`tools/token_sheet.tscn` renderiza el muestrario a 480×270 dentro del motor.
Contrastes medidos con la fórmula de WCAG 2.1, no estimados; de ahí salió la
enmienda 1.

**Corregido durante el paso:** la primera versión de la fuente no bajaba los
rasgos descendentes (`g j p q y`), así que «regenera» se leía «re9enera». Se
subió la celda de 6×9 a 6×11 para dar dos filas bajo la línea base.

### Paso 2 — Componente clave: el monstruo y su purificación · 2026-09-13

- `tools/pixel.py`: paleta compartida, ruido de valor determinista y lienzo con
  contorno. Base de todo el pixel art del proyecto.
- `tools/gen_sprites.py` → `assets/sprites/monsters/deforestation_flame.png` y
  `deforestation_flame_purified.png`, 48×48 px.
- `src/ui/battle/monster_view.gd`: `MonsterView`, el componente que carga la
  decisión dominante de la fase 2.

**Cláusulas:** «Regla de acento, no negociable» (el verde solo aparece al
purificar; la barra de PV va de `ash_050` a `ember_400` a `ember_500`, nunca a
verde), «Movimiento» (barra 220 ms, sacudida 120 ms, purificación 300 ms),
«Espaciado y radios» (radio 0, bordes de 1 px).

**Decisión de diseño.** La purificación no se comunica con un icono en una
esquina: cambia a la vez el **sprite** (silueta de llama → silueta de copa), el
**borde** de la ficha y el **texto** de la franja. Tres señales redundantes para
el dato del que depende que el jugador entienda el mensaje del juego. La silueta
cambia, no solo el color, para que se distinga también sin percibir el color.

**Verificado:** `tools/component_sheet.tscn` renderiza los cuatro estados
(intacto, purificado, herido, crítico) a 480×270 en el motor.
`tools/transition_sheet.tscn` captura la purificación cuadro a cuadro y
confirma la duración de 300 ms y el fundido real entre los dos sprites.

**Corregido durante el paso:** el nombre del monstruo y el tipo ecológico se
solapaban en fichas estrechas («Deforestaci**Fuego**»). El tipo se movió a la
franja de purificación, que además es su sitio lógico: responde a la misma
pregunta. Se añadió recorte con puntos suspensivos para nombres que no quepan.

**Pendiente, y se dice:** solo existe el sprite de la Llama de la
Deforestación. Los otros cuatro monstruos de región y el jefe final entran en
el paso 4, junto al resto de componentes.

### Paso 3 — Esqueleto del layout · 2026-09-13

- `src/ui/battle/battle_screen.gd`: `BattleScreen`, con las bandas, los anclajes
  del grupo y los huecos marcados de lo que aún no existe.
- `tools/layout_sheet.tscn`: renderiza el esqueleto con guías y sin ellas.

**Reparto vertical de los 270 px**

| Banda | Rango | Alto | Jerarquía de la fase 2 |
|---|---|---|---|
| A · Campo de batalla | 0-170 | 170 | 1 (monstruo) |
| B · HUD del grupo | 170-210 | 40 | 3 (PV y energía) |
| C · Menú y mensaje | 210-270 | 60 | 2 (la decisión) y 4 (registro) |

Dentro del campo: monstruo en `y 8..112` (sprite 48 + ficha 52), horizonte en
`y 112`, grupo apoyado en `y 122..170`.

**Cláusulas:** «Espaciado y radios» (todas las bandas y los huecos salen de la
escala de múltiplos de 4; radio 0 y bordes de 1 px).

#### Decisión 1 — el HUD va debajo de su personaje, no en una lista

La pantalla se divide en **cinco columnas de 96 px**. El sprite de cada
personaje se planta en el centro de su columna y su columna del HUD queda
exactamente debajo. Es el *third-best mapping* de la crítica de Final Fantasy VI
recogida en la fase 3: los controles y la información se ordenan en la misma
configuración espacial que los objetos que representan. Con una lista vertical a
un lado, el jugador tendría que emparejar mentalmente cada fila con un muñeco
del campo, y eso es trabajo que la interfaz puede ahorrarle gratis.

#### Decisión 2 — el registro no tiene banda propia

La jerarquía de la fase 2 pedía cinco niveles, y una lectura literal daba una
banda por nivel. Al montarlo no cabía: el campo necesita 170 px para que la
ficha del monstruo (que termina en `y 112`) no tape a un grupo que ocupa
`y 122..170`. Con una banda de registro de 22 px, el campo se quedaba en 148 y
la ficha se comía la fila del grupo. Se comprobó en la primera captura del paso.

En lugar de encoger la ficha del monstruo —que es la decisión dominante y no
debe perder peso— el registro **comparte sitio** con la descripción de la opción
enfocada, en la mitad derecha de la banda C. Los dos textos nunca hacen falta a
la vez: mientras el jugador elige lee la descripción, y mientras se resuelve el
turno lee el registro. La jerarquía se respeta; lo que cambia es que los niveles
2 y 4 comparten región en momentos distintos.

**Verificado:** `tools/layout_sheet.tscn` renderiza la pantalla a 480×270 en el
motor, con guías y limpia. Sin solapes entre bandas ni entre componentes. La
alineación de cada columna del HUD con su sprite se comprueba en la captura.

**Pendiente, y se dice:** el fondo del campo son dos bandas planas de ceniza con
una línea de horizonte. El fondo ilustrado por regiones y el parallax de tres
capas registrado en la fase 3 entran en el paso 5, al ensamblar la pantalla.

### Paso 4 — Resto de componentes · 2026-09-13

- `tools/gen_sprites.py`: los seis monstruos, cada uno en sus dos variantes.
- `tools/gen_characters.py` → `assets/sprites/party/`: los cinco personajes
  jugables, 32×48 px, de espaldas.
- `src/ui/battle/action_menu.gd`: `ActionMenu`, con cursor, foco y teclado.
- `src/ui/battle/party_member_hud.gd`: `PartyMemberHud`, la columna de 96×40.

**Cláusulas:** «Regla de acento, no negociable», «Movimiento» (cursor 90 ms,
entrada del menú 160 ms desde `scale 0.94`, barras 220 ms), «Espaciado y
radios», «Tipografía y escala».

#### Decisión 1 — una sola gramática de color para los seis monstruos

Todos los monstruos sin purificar llevan sus marcas en **brasa**, y al
purificarse esas mismas marcas pasan a **verde**. Da igual que el daño sea
fuego, petróleo, plástico, monocultivo o deshielo: el color dice «la causa sigue
activa», no «esto es fuego». El jugador aprende el código una vez, en el Bosque
de las Cenizas, y le sirve hasta la Cripta de la Avaricia.

En el Coloso del Deshielo la coincidencia es literal: sus grietas incandescentes
son calor, que es exactamente la causa del daño que encarna.

#### Decisión 2 — purificar cambia la silueta, no solo el color

Cada variante purificada cambia de forma, no de tinte:

| Monstruo | Sin purificar | Purificado |
|---|---|---|
| Llama de la Deforestación | árbol ardiendo | copa que rebrota |
| Devorador de Petróleo | bulto viscoso y goteante | charco bajo y en calma |
| Gólem de Plástico | bloques revueltos y encajados | bloques separados y apilados |
| Espectro del Monocultivo | surco de tallos idénticos | surco irregular y diverso |
| Coloso del Deshielo | mermado, agrietado, chorreando | glaciar entero y de borde limpio |
| Sombra de la Avaricia | sombra deshilachada | sombra atravesada por la luz |

Así la purificación se percibe **también sin distinguir bien el color**, que es
un mínimo de accesibilidad y además hace la lectura más rápida para todos.

#### Decisión 3 — el grupo va en ceniza, sin color propio

El contrato reserva el verde a la purificación y la brasa al daño activo, así
que darle a cada personaje su color saturado rompería las dos reglas. La
diferencia se juega donde el pixel art la juega de verdad: **silueta** (el
Fragmento de Ilan, la capucha de Bruma, la trenza de Coral, la mochila de Nix,
el sombrero de Suri) y **valor** (cada uno en una franja distinta de la rampa).
El nombre lo pone su columna del HUD, justo debajo.

#### Decisión 4 — el menú es uno solo, no tres

`ActionMenu` recibe una lista de entradas y no sabe si son las cuatro opciones
de la raíz, las Habilidades Ecológicas o los objetos de la Bolsa. Un solo
componente, un solo comportamiento que aprender.

Las entradas que no se pueden pagar **no se ocultan ni se apagan en gris mudo**:
se muestran con el coste en rojo, y el cursor puede pararse en ellas. Es la
corrección directa al fallo del port de Final Fantasy VI registrado en la fase 3
(«opciones en gris que estorban y no explican nada»): el gris frustra, mientras
que ver el coste enseña cuánta energía falta.

**Verificado:** `tools/components4_sheet.tscn` renderiza a 480×270 en el motor
los cinco sprites sobre sus columnas, el HUD en cinco estados distintos (turno
activo, sano, herido, crítico con estado alterado, fuera de combate) y el menú
en sus dos usos.

**Corregido durante el paso:**
1. Los cinco personajes salieron en tonos `ash_800`-`ash_950`, que sobre el
   suelo `ash_900` del campo los habría hecho invisibles. Se subieron todas las
   rampas conservando las diferencias relativas de valor.
2. El Espectro del Monocultivo purificado se quedaba **sin cuerpo**: los ojos
   flotaban sobre un campo vacío. Purificar apacigua al espíritu, no lo borra.
3. El Coloso del Deshielo purificado era casi idéntico al corrupto. Ahora
   recupera masa y borde limpio, y la diferencia se ve en la silueta.
4. Tres variantes purificadas colapsaban en la misma mancha verde. Se
   diferenciaron por forma, según la tabla de la decisión 2.
5. El Fragmento del Vínculo de Ilan era invisible sobre su túnica, la más clara
   del grupo. Ahora lleva borde oscuro.
6. En el HUD, un personaje con dos estados alterados mostraba «Aturdimiento.»
   con el contador cortado. Ahora se sacrifica el «+N» antes que el nombre del
   estado.

### Paso 5 — Pantalla completa · 2026-09-13

- `src/ui/battle/battle_screen.gd`: la pantalla ensamblada y conectada al
  `BattleManager` por señales.
- `src/demo/battle_intro.gd` + `scenes/main.tscn`: **F5 abre el combate del
  Bosque de las Cenizas con gráficos.** La prueba por consola se conserva en
  `tools/console_demo.tscn`.
- `tools/play_capture.tscn`: juega el combate real inyectando pulsaciones.

**Cláusulas:** todas las del contrato. El fondo de tres capas viene de la
observación de Aceternity UI de la fase 3: atmósfera sin robarle legibilidad al
primer plano, con el contraste bajando hacia el horizonte.

#### Decisión 1 — el combate se reproduce, no se vuelca

`BattleManager` resuelve la ronda entera de forma **síncrona**: cuando
`submit_action()` devuelve el control, los enemigos ya actuaron y los PV ya son
los finales. Volcar eso en pantalla de golpe habría vaciado las barras mientras
el registro narraba todavía el primer golpe.

La pantalla encola los eventos y los reproduce uno a uno. Las vistas quedan en
**pausa** todo el combate y solo avanzan cuando la reproducción las vuelca, de
modo que lo que se lee y lo que se ve van juntos. `confirm` adelanta el paso
para quien ya lo haya leído, y un `▼` avisa de que queda registro por delante:
sin él, no habría forma de distinguir una pausa de un cuelgue.

Esto obligó a un cambio en `MonsterView` y `PartyMemberHud`: las cifras de PV se
leen ahora del **valor animado**, no del real. Antes la barra se movía mientras
el número ya mostraba el resultado final, y se contradecían.

#### Decisión 2 — el grupo se centra, no se apelotona

Las columnas conservan siempre sus 96 px, pero el bloque entero se centra según
cuántos personajes haya. Con dos, el grupo queda en medio del campo en vez de
pegado a la izquierda con tres huecos vacíos a la derecha, y la correspondencia
entre cada sprite y su columna del HUD se conserva intacta.

#### Decisión 3 — con varios enemigos, la ficha sigue al cursor

Tres fichas de 176 px no caben en 480. Con más de un enemigo, todos muestran su
sprite pero **solo el que está en el punto de mira enseña la ficha completa**, y
la ficha cambia al recorrer el menú de objetivos. El jugador ve de quién está
hablando antes de confirmar.

#### Decisión 4 — el menú de objetivos es el mismo menú

Elegir a quién atacar usa `ActionMenu`, igual que elegir acción, habilidad u
objeto. Y si solo hay un objetivo vivo, el paso se salta: preguntar entre una
sola opción es hacer trabajar al jugador para nada.

**Verificado:** `tools/play_capture.tscn` juega el combate real inyectando
pulsaciones, espera a que la pantalla pida decisión (en vez de pulsar a ciegas)
y captura la purificación cuadro a cuadro. Queda comprobado en el juego, no en
una maqueta: el menú responde al teclado, el registro avanza, el árbol cambia de
llama a copa, el marco pasa a verde y la línea del registro se tiñe.

**Pendiente, y se dice:** no hay cifras de daño flotando sobre el objetivo. El
`BattleManager` comunica el resultado como texto ya compuesto, y sacar el número
de la frase sería frágil. Hacerlo bien pide una señal con datos
(`damage_dealt(target, amount, eco_type)`), que toca las reglas y no la
interfaz. Queda anotado como trabajo para después de la fase 6.

### Paso 6 — Estados · 2026-09-13

- `src/ui/battle/result_overlay.gd`: `ResultOverlay`, la vista de cierre.
- `src/actors/character.gd`: nuevo `get_known_skills()`.
- `project.godot`: ajuste `game/accessibility/reduced_motion`.

#### Vistas de estado, una por desenlace

| Estado | Qué se ve |
|---|---|
| Victoria | Titular verde y «La causa del daño quedó atajada» |
| Derrota | Titular brasa y **cuántas veces se rehizo el monstruo** |
| Retirada | Titular ceniza y la misma prueba |
| Sin energía | La habilidad sigue listada, con el coste en rojo |
| Fuera de combate | Columna en gris, barra apagada, «✖ FUERA» |
| Enemigo caído | El sprite se queda tenue, no desaparece |

En la derrota **no se da un consejo, se enseña el hecho**: «El monstruo se
rehízo 4 veces: la causa seguía activa». La fase 2 pide que el jugador cambie de
estrategia «sin que se lo digan», así que la pantalla aporta la prueba y le deja
la conclusión.

#### La capa de desenlace es un nodo aparte, y por una razón

En Godot los hijos se pintan **después** del padre. Dibujar el desenlace dentro
de `BattleScreen` hacía que la ficha del monstruo le pasara por encima y le
cortara el titular. Como capa añadida en último lugar, queda garantizado que va
arriba. Se descubrió mirando la captura, no razonándolo.

#### Movimiento reducido, expuesto de verdad

El contrato lo exigía y hasta ahora era una variable que nadie podía cambiar.
Ahora es `game/accessibility/reduced_motion` en `project.godot`, editable desde
el editor, desde la línea de órdenes o desde una futura pantalla de opciones.
Con `true`, toda transición salta al estado final.

---

## Fase 6 — Pruebas de usabilidad

### Con qué se verificó, y con qué no

**Playwright no aplica.** El contrato y las preferencias del proyecto lo piden
por defecto, pero es una herramienta de navegador y esto es un juego de
escritorio en Godot: no hay DOM, ni viewport de CSS, ni consola web. Se dice
aquí en vez de simular una verificación que no existió.

Lo que sí se hizo, **contra el juego en ejecución**:

| Prueba | Herramienta | Resultado |
|---|---|---|
| Recorrido por teclado | `tools/verify_usability.tscn` | 8 de 8 |
| Opciones no pagables | `tools/verify_usability.tscn` | 4 de 4 |
| Escalado entero | `tools/verify_usability.tscn` | 4 de 4 |
| Paleta renderizada | auditoría de píxeles | 100 % dentro del contrato |
| Contraste en pantalla | auditoría de píxeles | sin fallos |
| Consola | arranque en modo headless | limpia |

### Equivalente de los tres anchos de pantalla

El requisito de capturar a 390, 768 y 1440 px es de web. Aquí el lienzo es fijo
a 480×270 y lo que varía es el factor de escala, así que el equivalente honesto
es comprobar que la rejilla de píxeles sobrevive a cualquier tamaño de ventana:

| Ventana | Escala | Entera |
|---|---|---|
| 480×270 | 1,000 | sí |
| 960×540 | 2,000 | sí |
| 1103×621 (tamaño arbitrario) | 2,000 | sí |
| 1440×810 | 3,000 | sí |

El tamaño arbitrario es el que importa: sin `scale_mode=integer` habría dado
2,3 y roto la rejilla.

### Contraste medido sobre píxeles reales

No son estimaciones de la paleta: se localiza cada píxel de texto en la captura
y se mide contra la superficie que tiene al lado.

| Texto | Sobre | Ratio | Nivel |
|---|---|---|---|
| `ash_050` (nombres y cifras) | `ash_900` | 13,1:1 | AAA |
| `ember_300` (foco y cifras críticas) | `ash_900` | 10,2:1 | AAA |
| `vital_500` (purificado) | `ash_900` | 9,4:1 | AAA |
| `ember_400` (sin purificar) | `ash_900` | 6,6:1 | AA |
| `ash_400` (texto secundario) | `ash_900` | 5,7:1 | AA |
| `ash_400` (opciones sin foco) | `ash_800` | 4,9:1 | AA |

Todas las cifras que el jugador lee para decidir (PV, energía, costes) están en
AAA. Piso AA cumplido en todo lo demás.

### Auditoría de paleta

Se cuenta cada color de la captura y se compara con los tokens del contrato.

- Pantalla de juego: **100 % de los píxeles dentro del contrato**, 11-12 colores
  distintos en total.
- Vista de desenlace: 59 %. El 41 % restante es el **velo de `ash_950` al 78 %**
  sobre el campo, la única mezcla con transparencia de toda la interfaz.
  Es deliberada y queda anotada como la excepción.

La primera pasada dio 94 %: las bandas de cielo usaban `lerp` entre `ash_800` y
`ash_700` y generaban cuatro tonos intermedios que no eran tokens. Se
sustituyeron por escalones discretos, que además es el lenguaje correcto del
pixel art. **El incumplimiento lo encontró la auditoría, no la vista.**

### Cierre de la tabla de la fase 2

Por cada fila, según su propio criterio de «cómo se sabe que llegó».

| Necesidad | Criterio | Veredicto |
|---|---|---|
| «¿A quién le toca?» | Lo identifica en menos de 1 s sin buscar | **Llegó** (cerrada en la iteración 1). La columna del personaje activo se enciende con borde y nombre en brasa, justo bajo su sprite, y la cola de la esquina superior izquierda enseña quién va después hasta el fin de la ronda. |
| «¿Cuánta vida me queda?» | Detecta al herido sin contar cifras | **Llegó.** La barra cambia de hueso a naranja al 55 % y a rojo al 25 %, y la cifra se tiñe en crítico. Se distingue por color y por longitud. |
| «¿Qué le pasa al monstruo?» | Entiende por qué el daño «no sirvió» | **Llegó.** Tres señales redundantes: sprite, marco y franja de texto. Más el destello al regenerarse y la línea del registro teñida. |
| «¿Qué puedo hacer?» | Elige sin probar opciones bloqueadas | **Llegó, tras corregir un fallo.** La verificación destapó que `get_usable_skills()` filtraba por energía, así que las habilidades impagables **desaparecían del menú**: exactamente el fallo de Final Fantasy VI que el contrato dice evitar. Se separó «saber una habilidad» de «poder pagarla». |
| «¿Qué acaba de pasar?» | Relaciona la acción con su efecto | **Llegó** (cerrada en la iteración 2). El registro narra línea a línea, las barras se mueven al mismo ritmo y la cifra aparece **sobre el sprite del objetivo**, así que con varios enemigos ya no hace falta leer el nombre en la frase. |
| «¿Por qué pierdo?» | Cambia de estrategia sin que se lo digan | **No verificado.** La pantalla aporta todo lo que puede: la franja «sin purificar», el destello de regeneración, la línea teñida y el recuento en la derrota. Pero si un jugador real deduce por su cuenta que hay que atajar la causa **no se puede saber sin sentar a alguien delante**, y eso no se ha hecho. Es la única fila que depende de una prueba con personas. |

### Lo que queda pendiente, sin maquillar

*(Las dos primeras entradas se cerraron en las iteraciones 1 y 2.)*

1. **Prueba con personas.** Ninguna fila que dependa de lo que deduce un jugador
   puede darse por cerrada sin ella. Es lo primero que haría falta antes de dar
   la pantalla por terminada.
2. ~~**Cinco personajes a la vez.**~~ Cerrado en la iteración 3.

---

## Iteración 1 — Cola de turnos · 2026-09-13

La fase 6 es iterativa y puede devolver a la fase 5. Esta iteración existe
porque el cierre de la tabla dejó la primera fila a medias: la pantalla decía a
quién le tocaba, pero no quién venía después.

- `src/ui/battle/turn_order_strip.gd`: `TurnOrderStrip`.
- `src/battle/battle_manager.gd`: nuevo `get_pending_turns()`, solo lectura.

**Cláusulas:** «Paleta» (ningún color nuevo), «Espaciado y radios», «Tipografía
y escala».

### Decisión 1 — no se inventa el futuro

`TurnManager` recalcula el orden **en cada ronda** con la velocidad efectiva del
momento, así que un estado de lentitud puede darle la vuelta entera. La cola
muestra solo lo que ya está decidido y se cierra con «fin de ronda». Prolongarla
a rondas futuras sería enseñar una predicción que el propio motor no garantiza.

Cerrar la lista importa por sí mismo: sin ese pie, no se distingue «aquí acaba
la ronda» de «aquí acaba lo que cabía en pantalla».

### Decisión 2 — el bando se marca con la gramática que ya existe

Cada ficha lleva una barra de 2 px a la izquierda: ceniza clara para el grupo,
brasa para el enemigo. **No se introduce ningún color nuevo.** La brasa ya
significa «causa activa» en todo el juego, y un enemigo en la cola es
exactamente eso. La auditoría de paleta sigue dando 100 %.

### Decisión 3 — nombres de una palabra

«Llama de la Deforestación» no cabe en 76 px. La ficha muestra la primera
palabra —«Llama», «Espectro», «Devorador»— que basta para reconocerlo cuando su
sprite está en pantalla justo al lado. Los clones del Espectro se llaman «Eco
del Monocultivo», así que tampoco se confunden con el original.

### Decisión 4 — la cola viaja con cada evento

Como la reproducción del registro va por detrás de las reglas, una cola leída
«en vivo» mostraría el final de la ronda mientras el texto narra todavía el
principio. Cada evento encolado lleva la cola del instante en que ocurrió, y la
reproducción la restituye al mostrarlo.

### Corregido durante la iteración

Reservar margen izquierdo para la cola descentraba al enemigo cuando solo había
uno: quedaba a la derecha de su propia ficha. El margen se aplica ahora solo con
dos o más enemigos, que es cuando de verdad se repartirían encima de la franja.

### Verificado

- `tools/verify_usability.tscn`: **16 de 16**, sin regresiones.
- Auditoría de paleta: **100 % dentro del contrato** en pantalla de juego.
- Capturas del combate real con la cola en sus tres estados: turno del grupo,
  turno del enemigo por delante y última ficha de la ronda.

---

## Iteración 2 — Cifras de daño · 2026-09-13

Cierra la fila «¿qué acaba de pasar?». Es la primera iteración que **toca la
capa de reglas**, y por eso se explica aquí con detalle.

- `src/actors/combatant.gd`: señales `damage_taken` y `healing_received`, más
  `get_resistance_for()` en la clase base.
- `src/ui/battle/damage_numbers.gd`: `DamageNumbers`, la capa que las escribe.

**Cláusulas:** «Movimiento» (`DUR_DAMAGE_NUMBER`, 260 ms), «Paleta» (ningún
color nuevo), «Tipografía y escala».

### Decisión 1 — el dato lo emite el motor, no lo adivina la interfaz

Hasta ahora el único aviso de un golpe era la frase ya compuesta del registro
(«Bruma pierde 14 PV»). Sacar el número de ahí exigiría analizar texto, que se
rompe en cuanto alguien reescribe una frase.

`Combatant.take_damage()` ya calculaba el daño real: ahora además lo **emite**.
La señal viaja con el tipo ecológico y con un indicador de si el objetivo lo
resistió. Son doce líneas en el motor y ninguna regla cambia: la demo por
consola sigue dando los mismos resultados en los cuatro escenarios.

### Decisión 2 — la cifra enseña la regla del juego

Es lo que hace que valga la pena, más allá del adorno:

| Caso | Cómo se ve |
|---|---|
| Golpe que el monstruo resiste | `~3` en ceniza apagada |
| Golpe que hace mella | `12` en brasa viva |
| Daño recibido por el grupo | cifra en brasa de aviso |
| Curación | `+18` en hueso |

El mismo ataque básico da `~3` antes de purificar y `12` después. El jugador ve
la diferencia entre «no le hice nada» y «ahora sí» **sin leer una sola
explicación**, que es exactamente lo que pide el criterio de la fase 2.

### Decisión 3 — la curación no puede ir en verde

El verde `vital_500` significa una sola cosa en todo el juego: «la causa se
atajó». Una curación en verde lo diluiría. Va en `ash_050`, el hueso de lo que
está sano, que además es el color de la barra de PV llena.

### Decisión 4 — el apagado va por escalones de rampa, no por transparencia

La cifra se desvanece bajando un escalón de la rampa (`ember_300` →
`ember_400`, `ash_050` → `ash_400`) en lugar de fundirse con alfa. Mezclar
transparencia generaría colores intermedios que no son tokens, y la auditoría
de paleta los marcaría como incumplimiento. El escalón, además, es el lenguaje
propio del pixel art.

### Decisión 5 — las cifras se sueltan al ritmo del registro

Igual que las barras: se acumulan mientras las reglas resuelven y se sueltan en
cada volcado, de modo que la cifra aparece con la línea que la narra y no tres
segundos antes.

### Corregido durante la iteración

El marcador `~` de daño resistido **no existía en la fuente** y salía como
glifo vacío. Se añadió a `gen_font.py` a la altura del centro de las cifras, no
a la de las minúsculas. La fuente pasa de 111 a 112 glifos.

### Verificado

- `tools/numbers_capture.tscn`: captura los dos casos en el combate real, a
  intervalos de 50 ms para atrapar una animación de 260 ms.
- `tools/verify_usability.tscn`: **16 de 16**, sin regresiones.
- `tools/console_demo.tscn`: los cuatro escenarios de reglas dan el mismo
  resultado que antes de tocar `Combatant`.
- Auditoría de paleta: **100 % dentro del contrato**.

---

## Iteración 3 — Los seis combates · 2026-09-13

Hasta aquí solo se jugaba el Bosque de las Cenizas, con un grupo de dos y un
enemigo. Quedaban sin probar en pantalla el reparto de cinco columnas y el único
caso con varios enemigos.

- `src/demo/encounters.gd`: catálogo de los seis combates.
- `src/ui/region_select.gd`: pantalla de elección de región.
- `src/demo/game_root.gd` + `scenes/main.tscn`: selector ↔ combate.

### Decisión 1 — el selector no inventa un lenguaje nuevo

La lista de regiones es el **mismo `ActionMenu`** del combate: mismo cursor,
mismos tokens, mismo teclado. Quien sabe moverse por el menú de batalla sabe
moverse por aquí sin aprender nada. La ficha de la derecha repite la estructura
de la ficha del monstruo, adelantada: elegir región y elegir acción son la misma
clase de decisión y se presentan igual.

Se eligió selector en vez de campaña encadenada por una razón práctica: para
revisar el juego no se puede exigir ganar cinco combates seguidos antes de ver
la Cripta de la Avaricia.

### Decisión 2 — cada contramedida vive en una persona

| Región | Monstruo | Grupo | Quien ataja |
|---|---|---|---|
| Bosque de las Cenizas | Llama de la Deforestación | 2 | Bruma (fuego) |
| Cuenca de Alquitrán | Devorador de Petróleo | 3 | Coral (petróleo) |
| Costa Quebrada | Gólem de Plástico | 4 | Nix (plástico) |
| Llanura Marchita | Espectro del Monocultivo | 5 | Suri (monocultivo) |
| Cumbre Menguante | Coloso del Deshielo | 5 | Ilan (deshielo) |
| Cripta de la Avaricia | Sombra de la Avaricia | 5 | los cinco |

El grupo crece de dos a cinco, que es lo que ejercita el reparto de columnas. Y
el jefe final exige exactamente a los cinco porque cada contramedida vive en una
persona distinta: la idea del juego, traducida a reparto.

### Decisión 3 — las opciones apagadas dicen por qué

En el Bosque, Ilan solo conoce el Escudo de Albedo, que es de deshielo: su menú
de Habilidades está legítimamente vacío. Antes la opción aparecía apagada y
muda. Ahora su descripción dice «Ilan aún no conoce ninguna Habilidad Ecológica.
Otro del grupo sí», que además enseña que el grupo se complementa. Lo mismo con
la Bolsa vacía.

### Corregido durante la iteración

1. **El tipo de daño y el estado se tocaban** en la ficha del monstruo con
   nombres largos («Monocultivo»), y el jefe mostraba «Neutro», que no le dice
   nada al jugador. La franja pasó a ser una frase: «Monocultivo · se regenera»,
   y para el jefe «aprende de lo que repites».
2. **Las etiquetas del menú desbordaban.** «Espectro del Monocultivo» en el menú
   de objetivos se salía de sus 128 px y se montaba sobre el mensaje de al lado.
   `ActionMenu` recorta ahora a lo que queda entre el cursor y el coste.
3. **Los tres bancos de prueba se rompieron** al meter el selector: cargaban
   `main.tscn` esperando un combate. Ahora entran por el selector, como el
   jugador.
4. **Un falso positivo en la propia verificación.** La prueba de habilidades
   comprobaba solo que el menú tuviera entradas, así que cuando la opción estaba
   apagada seguía contando las cuatro de la raíz y daba por buena una
   comprobación que nunca ocurrió. Ahora exige que las entradas sean de tipo
   `skill`, y avanza turnos hasta llegar a alguien que tenga habilidades.

### Verificado

- `tools/regions_capture.tscn`: selector y apertura de los seis combates, con
  grupos de 2, 3, 4, 5, 5 y 5.
- `tools/clones_capture.tscn`: el Espectro con sus dos clones. Tres enemigos
  repartidos por el campo sin pisar la cola de turnos, cola con «+1 mas», y la
  **ficha completa siguiendo al cursor** por el menú de objetivos
  (199/200 → 70/70).
- `tools/verify_usability.tscn`: **16 de 16**, ahora con la prueba corregida.
- Auditoría de paleta: **100 % dentro del contrato**.

---

## Iteración 4 — Composición diagonal del campo · 2026-09-13

Petición directa del usuario: la pantalla se veía plana y quería la disposición
de los RPG de Game Boy Advance, con los enemigos a la derecha y el grupo a la
izquierda.

### Diagnóstico: por qué estaba plana

No era cuestión de gusto, había tres causas concretas:

1. **Todo paralelo al borde.** Enemigo centrado arriba, grupo en fila recta
   abajo, bandas de fondo horizontales. Ni una diagonal en toda la pantalla.
2. **Sin solapamiento.** Los cinco del grupo a la misma altura y sin tocarse:
   una fila de fichas, no un grupo de personas.
3. **Sin sombras ni suelo.** Los sprites flotaban sobre una franja de color.

Y una cuarta, de fondo: los dos bandos no se miraban. No había confrontación
porque no había eje entre ellos.

### La composición nueva

Grupo escalonado **abajo a la izquierda**, enemigos escalonados **arriba a la
derecha**, y el hueco entre ambos es el campo. La profundidad sale de tres
recursos, ninguno de los cuales escala el sprite (una fuente y unos sprites de
píxel solo admiten escalas enteras):

| Recurso | Cómo se aplica |
|---|---|
| Altura en pantalla | Más arriba es más lejos. El horizonte está en `y 104` |
| Solapamiento | Quien está delante se dibuja encima y tapa al de atrás |
| Sombra y plataforma | Más grandes y marcadas cuanto más cerca |

### Las fichas van en la esquina contraria a sus sprites

Ficha del enemigo **arriba a la izquierda**, ventana del grupo **abajo a la
derecha**. Es la convención de los RPG de consola portátil y resuelve un
problema real: ningún panel tapa a quien describe.

### El mapeo se conserva, girado

La ventana del grupo lista a sus miembros **en el mismo orden vertical** en que
están en el campo: quien está más abajo en la diagonal está más abajo en la
lista. El *third-best mapping* de la fase 3 sigue vigente; lo que cambia es que
antes era horizontal (una columna bajo cada sprite) y ahora es vertical.

La cola de turnos pasó de columna lateral a franja horizontal en el borde
superior, porque la esquina que ocupaba es ahora el sitio de la ficha enemiga.

### Corregido durante la iteración

1. **Los enemigos 2 y 3 desaparecían.** Les puse `z_index` negativo para que el
   más cercano quedara encima, y en Godot un hijo con z negativo se va por
   **detrás del fondo que pinta el propio padre**. Se cambió a valores
   positivos descendentes.
2. **Una sola plataforma no servía para los enemigos.** Escalonados en diagonal
   ocupan 48 px de altura entre el primero y el último, y sobre una elipse plana
   los de atrás flotaban. Cada enemigo tiene ahora su plataforma y su sombra,
   encogidas según la distancia.
3. **Acentos perdidos** al reescribir las descripciones del menú («rehara»,
   «Ecologicas», «vacia»). Restituidos.

### Verificado

- `tools/regions_capture.tscn`: los seis combates con grupos de 2 a 5.
- `tools/clones_capture.tscn`: tres enemigos escalonados, cada uno con su
  plataforma, y la ficha siguiendo al cursor.
- `tools/verify_usability.tscn`: **16 de 16**, sin regresiones.
- Auditoría de paleta: **100 % dentro del contrato**. El cambio es de
  composición, no de color.
