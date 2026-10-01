# Anexo — Movimiento, colisiones y transición entre zonas (parte 2)

Abierto el 2026-09-30. Hereda el contrato «Vereda»
(`2026-09-14-exploracion-top-down.md`) y sus enmiendas 1 a 5. Lo que ya está
firmado allí **no se vuelve a decidir aquí**: velocidades de 60 y 120 px/s,
diagonal por eje, movimiento sin aceleración, cámara a píxel entero, fundido de
zona de 2 × 120 ms, rótulo de lugar de 160 ms. Este anexo decide solo lo que el
contrato deja abierto.

**Estado:** fases 1 a 4 hechas. **Dirección A, «Umbral», elegida por Diego el
2026-09-30** y bloqueada como contrato al final de este anexo. Siguiente:
fase 5, paso 1 (tokens).

---

## Fase 1 — Usuarios

- **Quién juega:** jugador de RPG 2D de 14 a 30 años, género mixto,
  hispanohablante y sin conocimientos del dominio ambiental. Juega en PC con
  teclado. Ya sabe mover un personaje en ocho direcciones: no hay que
  enseñárselo, y cualquier cosa que le obligue a pensar en moverse es un fallo.
- **Qué necesita aquí:** llegar adonde mira sin pelearse con las esquinas, saber
  por dónde se sale de la zona sin carteles y no perder el control al cruzar.
- **Secundario:** el docente de Diseño de Interfaces, que evalúa si el
  movimiento está *decidido* o solo *funciona*.
- **Accesibilidad:** con movimiento reducido no hay fundido, sino corte directo
  (ya en el contrato). Todo se hace con teclado; correr es mantener una tecla,
  no alternar un estado que haya que recordar.
- **Datos personales:** esta parte no trata ninguno. El guardado local (parte 9)
  anotará allí qué guarda y dónde.

## Fase 2 — Comunicación

- **Decisión dominante:** «¿puedo ir por ahí?». El jugador la toma cientos de
  veces por zona, siempre en periferia y nunca leyendo.
- **Qué la sostiene, en orden:**
  1. La silueta del terreno: suelo y camino se pisan; follaje y agua, no.
  2. El camino pisado (`SOIL_300`) como línea que lleva a las salidas.
  3. La respuesta del cuerpo: si choca, desliza; si roza una esquina, la dobla.
- **Qué no va:** flechas de salida, carteles «pulsa E», un minimapa en esta
  parte, zonas de colisión invisibles que contradigan el dibujo y ningún
  texto que diga por dónde ir.

## Fase 3 — Investigación

Formato: `observación → decisión aplicable → límite que no copiaré`.

| Fuente | Observación → decisión → límite |
|---|---|
| Godot — `PhysicsBody2D` (https://docs.godotengine.org/en/stable/classes/class_physicsbody2d.html) | `move_and_collide()` y `test_move()` llevan `safe_margin` = **0,08** para la recuperación de colisiones; `move_and_collide` **desplaza** al cuerpo para sacarlo de la pared. → Solo se usa `test_move()`, que pregunta sin mover, y la posición solo cambia en pasos de 1 px. Así no hay ninguna recuperación que deje al personaje en 0,08 px. → No se usa `CharacterBody2D.move_and_slide()`, que resuelve con fracciones. |
| Godot — `Camera2D` (https://docs.godotengine.org/en/stable/classes/class_camera2d.html) | Los `limit_*` se dan en píxeles, y «`offset` can push the view past the limit». La doc no dice qué pasa si el mapa es menor que la pantalla. → Los límites se imponen dentro de `WorldCamera`, en enteros, sin `offset`. Un mapa más estrecho que 480 px o más bajo que 270 se centra en ese eje. → No se usa `limit_smoothed`: suaviza en fracciones. |
| *Zelda-Style Top-Down Movement*, tutorial para PICO-8 de *Link's Awakening* (https://www.lexaloffle.com/bbs/?tid=153843) | El nivel 4 añade «a tuneable corner-slipping system to make it easier to avoid obstacles»: el deslizamiento en esquina es un **parámetro** del movimiento clásico, no un extra. → El deslizamiento en esquina es un token (`CORNER_SLIP`), medido y ajustable. → No copio sus cajas de colisión que cambian según hacia dónde se mira: complican la regla sin que el jugador lo note. |
| *Perfect Diagonal Movement*, PICO-8 (https://www.lexaloffle.com/bbs/?pid=163519) | Contra el «cobblestoning», «making sure you're always moving at whole pixel increments», con un acumulador por eje: a velocidad 0,5, un píxel cada dos cuadros. → El empujón de esquina también avanza en píxeles enteros: 1 px por cuadro, nunca un salto. Confirma la enmienda 4. → No normalizo la diagonal como él (la enmienda 4 ya decidió no hacerlo). |
| *The Level Design Book* — Wayfinding (https://book.leveldesignbook.com/process/blockout/wayfinding) | Jerarquía de ayudas: se empieza por la más sutil y se sube solo si las pruebas lo piden. Las líneas guía («planks that extend off the ledge», las vías del tren) marcan el paso sin interfaz. → **La salida de una zona es el camino que sale del mapa.** El camino pisado ya es la pista contratada «en cada columna» (guía §5, parte 1): se le da un trabajo más, llevar a la salida. → No uso migas de objetos recogibles: en este juego lo que se recoge ya tiene su trabajo en el catálogo. |
| Blendo Games — *Level Design: Readability* (https://blendogames.com/news/post/2026-06-xx-leveldesign_readability/) | «limited how densely packed the exits/entrances were» y una lista de «forbidden architecture» ambigua. → **Máximo dos salidas por pantalla de 480 px.** Y una arquitectura prohibida: **ningún borde de mapa pisable que no sea salida**. Todo borde que no sale se cierra con follaje o agua. → Su lista es de 3D; la mía es de tiles. |
| Stardew Valley Wiki — *Modding: Maps* (https://stardewvalleywiki.com/Modding:Maps) | Una salida es un dato: `Warp <fromX> <fromY> <toArea> <toX> <toY>`, casilla de origen → zona y casilla de destino. → Las salidas se describen en datos (`data/world/`), igual que el catálogo del paso 2a, y la prueba puede recorrerlas todas. → No copio su fundido largo ni la puerta como única salida. |

**Consultadas sin resultado utilizable** (no cuentan para las seis):

- GameDev.net, «Legend of Zelda corner-cutting»
  (https://www.gamedev.net/forums/topic/612599-legend-of-zelda-corner-cutting/):
  **403** el 2026-09-30. El extracto del buscador da un umbral de «4–6 px» para
  el empujón de *Zelda*. Se usa solo como orden de magnitud y se declara así.
- Nexus Mods, «No Transitions» para Stardew
  (https://www.nexusmods.com/stardewvalley/mods/7354): **403** el 2026-09-30.
- The Cutting Room Floor, overworld de *A Link to the Past*
  (https://tcrf.net/Development:The_Legend_of_Zelda:_A_Link_to_the_Past/Overworld):
  el 2026-09-30 devolvió contenido que no tenía que ver con el juego. No se cita.
- Game UI Database (https://www.gameuidatabase.com/): no encontré ninguna
  categoría de rótulo de lugar que añada algo a lo ya contratado.
- Las fuentes de pantalla que exige Diego (`styles.refero.design`,
  `motionsites.ai`, `ui.aceternity.com`, `tasteskill.dev`, Emil Kowalski): **no
  aplicables** a colisiones ni a salidas de un mapa de tiles. Kowalski ya está
  aplicado en el contrato (caminar no se anima). Mobbin y Pinterest siguen
  pendientes de una sesión con navegador, como en el anexo de exploración.

## Fase 4 — Direcciones

Las tres respetan «Vereda». Cambian **cómo se siente el cuerpo y cómo se cruza
de zona**, no el color.

### A · «Umbral» — recomendada

- **Caja de colisión en los pies:** 12 × 8 px, en la base del tile del
  personaje. Un paso de un tile (16 px) siempre cabe con 2 px de margen a cada
  lado, y un paso de cero tiles nunca. No hay huecos intermedios: es la «zona
  muerta métrica» de Nic Phan, ya citada en el anexo de exploración.
- **Deslizamiento en esquina de 4 px** (`CORNER_SLIP`): si el choque es contra
  una esquina y sobran 4 px o menos para librarla, el personaje avanza 1 px
  lateral por cuadro hasta librarla y sigue recto. Contra una pared plana,
  desliza por el eje libre (diagonal) o se para (recto).
- **Salidas:** solo donde el camino pisado cruza el borde del mapa. Como máximo
  dos por pantalla, y ningún borde pisable que no salga. Al cruzar: fundido de
  120 + 120 ms, se aparece un tile dentro de la zona nueva mirando en la misma
  dirección, y **si la tecla sigue pulsada se sigue andando**: el control no se
  pierde.
- **Cámara en el borde:** encerrada en los límites de la zona, en enteros. Ahí
  el personaje sí sale de la zona muerta, y la prueba lo distingue.
- **Por qué se recomienda:** es la que menos se nota. El jugador no piensa en
  esquinas ni en salidas, y cada pieza reutiliza una pista que ya existe (el
  camino) en vez de añadir una nueva.
- **Coste:** un token nuevo (`CORNER_SLIP`) y el formato de salidas en datos.

### B · «Tope» — rozamiento honesto

- La misma caja de 12 × 8 px, **sin deslizamiento en esquina**. Contra una
  esquina te paras: el mapa es exactamente lo que se dibuja.
- Salidas marcadas por un **hueco en el muro** (un tile de suelo entre follaje)
  en vez de por el camino.
- Cámara igual que en A.
- **A favor:** cero reglas ocultas. **En contra:** en un mundo de follaje
  irregular se choca a menudo con los picos de la silueta enferma («rota,
  diagonal»). El dibujo que cuenta el daño castiga al jugador por moverse, y eso
  enfrenta la lectura con el control.

### C · «Costura» — sin fundido entre zonas

- Movimiento como en A.
- **Las zonas vecinas se tocan sin cortar:** al cruzar, la cámara sigue
  deslizándose y la zona nueva ya está pintada al otro lado. La frontera entre
  una zona purificada y otra enferma se **ve en directo**, como la captura
  partida del tileset, y cruzarla es atravesar la tesis del juego.
- **Exige una enmienda:** el fundido a negro dejaría de ser «el cambio de zona»
  y quedaría solo para los cambios de plano (entrar en la Cripta, en interiores).
  También exige cargar dos zonas a la vez y resolver la cámara sobre las dos.
- **A favor:** es el momento más memorable de los tres. **En contra:** más cara
  (parte 3 entera depende de ella) y rompe una cláusula firmada.

### Design Read (dirección A)

```
Registro y audiencia: juego, lectura obligada; jugador de RPG 2D con teclado.
Escena de uso: partida larga, atención en el paisaje, el cuerpo en periferia.
Tesis visual: el camino pisado es la única flecha del juego.
Jerarquía y decisión dominante: «¿puedo ir por ahí?» → silueta, camino, cuerpo.
Materiales: sin materiales nuevos; tiles ya contratados, fundido y rótulo ya contratados.
Repertorio: camino = hacia dónde se sale; fundido = cambio de zona; rótulo = nombre al entrar.
Puntos de entrada: la tarea. Nada decorativo entre el jugador y su dirección.
Riesgo que se evita: flechas de salida, colisiones invisibles, control perdido en el fundido.
```

**Pregunta a Diego:** ¿A, B o C? — **Respuesta, 2026-09-30: A.**

---

## Contrato «Umbral» — bloqueado el 2026-09-30

**Elegido por Diego el 2026-09-30: dirección A.** Desde aquí se cumple. Nada
de valor, forma ni duración fuera de este contrato y de «Vereda».

| Cláusula | Valor | Token |
|---|---|---|
| Caja de colisión | 12 × 8 px, centrada en la base del tile del personaje | `PLAYER_HITBOX` |
| Deslizamiento en esquina | Hasta 4 px, a 1 px lateral por cuadro | `CORNER_SLIP` |
| Motor de colisión | `test_move()` por eje y en pasos de 1 px. Nunca `move_and_slide()` ni `move_and_collide()` | — |
| Pared plana | En diagonal, sigue por el eje libre; en recto, se para | — |
| Salidas | Solo donde el camino pisado cruza el borde del mapa | — |
| Densidad de salidas | Máximo 2 por pantalla de 480 px | `MAX_EXITS_PER_SCREEN` |
| Arquitectura prohibida | Ningún borde de mapa pisable que no sea salida | — |
| Datos de salida | `data/world/exits.json`: casilla de origen → zona y casilla de destino | — |
| Al cruzar | Fundido 120 + 120 ms, lineal (`DUR_ZONE_FADE`); se aparece un tile dentro, mirando igual; **con la tecla pulsada se sigue andando** | — |
| Movimiento reducido | Corte directo, sin fundido | — |
| Rótulo de lugar | Entra en 160 ms `ease-out` (`DUR_PLACE_LABEL`), panel `ASH_800`, texto 1×, arriba a la izquierda con margen `SPACE_8`, se va solo a los 2 s | `PLACE_LABEL_HOLD` |
| Cámara en el borde | Encerrada en los límites de la zona, en enteros; un mapa menor que la pantalla se centra en ese eje | — |
| Entrada | `run` = Mayús izquierda (mantener, no alternar); `interact` = `confirm` | — |
| Estado global | Autoload `GameState`: grupo, bolsa, zona y banderas | — |

**Tokens nuevos que abre el contrato:** `PLAYER_HITBOX`, `CORNER_SLIP`,
`MAX_EXITS_PER_SCREEN` y `PLACE_LABEL_HOLD`. Ningún color nuevo.

## Fase 5 — Implementación

Orden: tokens → componente clave (el cuerpo: `test_move` por eje, deslizamiento
en esquina) → esqueleto (zona de prueba con dos salidas) → resto (fundido,
rótulo, `GameState`, límites de la cámara) → pantalla completa → estados
(movimiento reducido, borde del mapa, salida pulsando la tecla). Cada paso se
cierra con captura, cláusula que lo respalda y visto bueno de Diego.

**Paso 1 — Tokens · HECHO y aprobado el 2026-09-30.**
Añadir a `src/ui/design_tokens.gd` los cuatro tokens de la tabla y a
`project.godot` la acción `run` (Mayús izquierda, `physical_keycode` 4194325,
`location` 1). **Cuidado:** abrir o ejecutar Godot reescribe `project.godot` y
borra sus comentarios; si aparece modificado sin motivo, descartar con
`git checkout project.godot` antes del commit.

Entregado (rama `parte-2/tokens`):

- `src/ui/design_tokens.gd`:
  - `PLAYER_HITBOX` = 12×8, `CORNER_SLIP` = 4 y `MAX_EXITS_PER_SCREEN` = 2,
    en una sección nueva, «Cuerpo y salidas».
  - `PLACE_LABEL_HOLD` = 2,0 s, junto a las duraciones del mundo.
  - Ningún color nuevo.
- `project.godot`: acción `run` en Mayús izquierda, tecla física. Se añadió a
  mano. `interact` no se crea: reutiliza `confirm`.

**Cláusulas:** tabla del contrato «Umbral»: caja de colisión,
deslizamiento en esquina, densidad de salidas, rótulo de lugar y entrada.

**Verificado en Godot 4.7.2** con una comprobación que carga los tokens y el
`InputMap` en el motor: **10 de 10**.

- Los cuatro valores coinciden con el contrato.
- La caja deja 2 px de margen a cada lado en un paso de 16 px, y cabe en un
  tile en alto.
- `run` existe y es Mayús **izquierda** con tecla física.
- Ninguna otra acción usa Mayús, y no existe una acción `interact` aparte.

La comprobación no se guarda como herramienta: sus reglas pasan a
`verify_movement.gd`, que las mide ya en movimiento.

Sin regresiones:

- `verify_palette.py tokens`: 24 coinciden, sin deriva.
- `verify_tileset.py`: dentro del contrato.
- `verify_usability.tscn`: 16 de 16.
- `verify_camera.tscn`: 37 de 37.

`project.godot`: Godot no lo reescribió; el diff son solo las 5 líneas de
`run`.

**Sin captura, y se dice:** ninguno de estos tokens es visible por sí solo (son
medidas de colisión, recuentos y una espera). La primera captura de la parte es
la del paso 2, el cuerpo contra paredes y esquinas.

**Pregunta abierta para Diego:** con movimiento reducido, el contrato quita el
fundido, pero no dice nada de la espera del rótulo (`PLACE_LABEL_HOLD`). Hay
dos lecturas:

- **(a)** Se mantiene en 2 s. Es una espera y no una animación, y quitarla
  dejaría al jugador sin tiempo para leer el nombre del lugar.
  **Recomendada.**
- **(b)** Pasa por `DesignTokens.duration()`, como las transiciones, y queda
  en 0.

Se decide antes del paso 4, que es cuando se implementa el rótulo.

**Visto bueno de Diego al paso 1: 2026-09-30,** por mensaje de texto a Juan
José Rueda, que fusionó el PR #4 por indicación suya. No quedó revisión en
GitHub; se anota aquí para que conste.

**Rótulo con movimiento reducido: opción (a), mantener los 2 s.** La eligió
Juan José Rueda en la sesión del 2026-09-30. **Diego la confirma en el PR del
paso 2.**

**Paso 2 — Componente clave: el cuerpo · HECHO y aprobado el 2026-09-30**
(PR #5). Diego aprobó el paso y confirmó las dos decisiones: la colisión es el
tile entero y el rótulo mantiene los 2 s con movimiento reducido. Visto bueno
comunicado a Juan José Rueda fuera de GitHub; el PR no tiene revisión escrita.

- `src/world/player_body.gd` (`PlayerBody`, hereda de `CharacterBody2D`):
  - El origen del nodo son los pies. La caja de 12×8 va justo encima, con los
    bordes en píxel entero.
  - Cada cuadro lee `move_*` y `run` y avanza 1 o 2 sub-pasos de 1 px, con
    `test_move()` por eje. Nunca `move_and_slide()`.
  - En una pared plana, en diagonal sigue por el eje libre y en recto se para.
  - En una esquina, yendo recto, se desliza hasta `CORNER_SLIP` px, a 1 px
    lateral por cuadro también corriendo. Si hay hueco igual de cerca a los dos
    lados, se para.
  - Guarda `facing`, que el paso 4 usará para aparecer mirando igual al cruzar
    una salida.
- `src/world/world_tiles.gd`: el tileset tiene capa de física. El agua y el
  follaje, enfermos y purificados, bloquean con el tile entero; el suelo y el
  camino se pisan.
- `tools/verify_movement.tscn`: la prueba de la parte, con los casos del
  cuerpo. Los pasos siguientes añaden los suyos.
- `tools/body_sheet.tscn` → `docs/ux/capturas/2026-09-30-cuerpo-{guias,limpio}.png`.

**Cláusulas:** caja de colisión, deslizamiento en esquina, motor de colisión
y pared plana del contrato «Umbral», más las velocidades y la diagonal por eje
de «Vereda» (enmienda 4).

#### Hallazgo medido: `test_move` cuenta como choque llegar a tocar

La primera versión sondaba 1 px con `test_move()` y la prueba dio **24 de 35**:

- el cuerpo se paraba a 1 px del muro;
- un paso de 16 px solo se cruzaba hasta 5 px descentrado, en vez de 6;
- cada esquina pedía 1 px más de deslizamiento, y la de 4 px ya no se rodeaba.

Se midió la causa con consultas directas al motor. El muro estaba donde
debía: el píxel 79 es muro y el 80 no. Pero `test_move()` devuelve «choca»
cuando el movimiento **acaba tocando** la pared, con margen 0, 0,001 o el de
serie, 0,08. Bajar el margen, que fue la primera hipótesis, no cambiaba nada,
y se descartó.

**Solución:** se sonda cada píxel a **0,99 px** (`PlayerBody.PROBE`) y después
se avanza el píxel entero. Tocando ya, choca; con 1 px de hueco, no; en
paralelo a la pared, no. Da lo mismo con cualquier margen. Sigue siendo
`test_move()` por eje y en pasos de 1 px, como pide el contrato.

#### Decisión — la colisión es el tile entero, no la silueta

La silueta enferma (en sierra) y la purificada (festoneada) se retiran de 1 a
3 px del borde del tile. La colisión no las sigue: seguir la sierra haría que
el cuerpo se enganchara en cada diente, que es justo el defecto por el que se
descartó la dirección B. Consecuencia visible en la captura: **entre la caja
y el borde dibujado del follaje quedan de 1 a 3 px**. En una vista cenital,
con el cuerpo pintado encima, no se lee como un hueco. Se revisa en el paso 5
con el sprite de verdad.

#### Verificado

`verify_movement.tscn`: **35 de 35**, con 2880 cuadros medidos.

- Andando, 1 px por cuadro; corriendo, 2 px; en diagonal, 1 + 1 y 2 + 2.
- Con el teclado de verdad: 1 px en el mismo cuadro de la pulsación, 0 px en
  el cuadro en que se suelta, y Mayús izquierda corre desde el primer cuadro.
- Un paso de 16 px se cruza descentrado hasta ±6 px (2 de margen + 4 de
  deslizamiento), y a ±7 no.
- Un paso de 0 px nunca se cruza, ni de follaje ni de agua, y el cuerpo se para
  tocando el muro, sin hueco.
- Una esquina a 1–4 px se rodea deslizando exactamente esos píxeles, a 1 px
  por cuadro, andando y corriendo. A 5 px se para sin deslizar.
- Con una pared plana: en diagonal sigue por el eje libre; rozándola en
  paralelo no se frena; en recto se para sin deslizar.
- Posición entera en todos los cuadros.

**La prueba se comprobó rompiéndola a propósito:**

- Sin el tope de 1 px lateral por cuadro, fallan 3 casos.
- Dejando deslizar 5 px en vez de 4, fallan 4.
- La versión que sondaba 1 px ya había dado 11 fallos.

**Captura:** tres cuerpos en la misma pantalla, a 480×270.

- A cruza un paso de un tile entrando descentrado 5 px, y se desliza 3.
- B se para contra un canto metido 5 px.
- C sube en diagonal contra el agua y sigue por el eje libre.

Las dos versiones (con y sin guías) pasan `verify_palette.py image`.

Sin regresiones:

- `verify_palette.py tokens`: sin deriva.
- `verify_tileset.py`: dentro del contrato.
- `verify_usability.tscn`: 16 de 16.
- `verify_camera.tscn`: 37 de 37.

`project.godot`: sin tocar.

**Pendiente, y se dice:**

- **El caso de hueco igual de cerca a los dos lados** no se da con tiles de
  16 px: un obstáculo de un tile ya es más ancho que la caja. Está en el
  código, pero ninguna prueba lo ejercita hasta que existan objetos menores de
  12 px.
- **El marcador tapa lo que tiene al norte** porque se pinta encima. El orden
  de dibujo por altura es del paso 5.
- **Aún no hay escena jugable.** El cuerpo se mueve con el teclado de verdad
  en la prueba, pero la zona de prueba con dos salidas es el paso 3.

**Paso 3 — Esqueleto: zona de prueba con dos salidas · HECHO el 2026-09-30.**
PR #6, fusionado por Juan José Rueda el 2026-10-01. **El PR no tiene revisión
escrita de Diego**, aunque se le pidió dejarla allí.

- `data/world/zones/prueba_a.txt` (40×20, mayor que la pantalla) y
  `prueba_b.txt` (30×17): mapas de texto con la leyenda de `WorldTiles`.
  **Son solo zonas de prueba.** El formato de mapa de las zonas de verdad
  (texto o pintado en el editor) lo sigue decidiendo Diego en la parte 3.
- `data/world/exits.json`, como pide el contrato: casilla de origen → zona y
  casilla de destino. Cuatro salidas, dos por zona.
- `src/world/zone_rules.gd` (`ZoneRules`): carga las zonas y las salidas, y
  comprueba las reglas del contrato:
  - cada salida es camino y está en el borde;
  - ningún borde pisable deja de ser salida;
  - hay como mucho `MAX_EXITS_PER_SCREEN` salidas en cualquier ventana de
    30×17 tiles;
  - cada salida lleva a una casilla pisable junto a una salida de vuelta.
  La prueba de cada zona de la parte 3 podrá reutilizarla.
- `src/world/world_root.gd` (`WorldRoot`) y la escena jugable
  `scenes/world/test_zone.tscn`, que se puede abrir y jugar con el teclado:
  - pinta la zona y monta el cuerpo y la cámara;
  - cuando el centro de la caja sale del mapa por una salida, carga la zona de
    destino con un **corte directo** y pone los pies en `to_cell`, un tile
    dentro, sin tocar hacia dónde mira;
  - como el cuerpo lee el teclado en cada cuadro, con la tecla pulsada se
    sigue andando.
- `src/world/player_body.gd`: un **marcador provisional**, 16×24 con contorno
  `ASH_050` (la firma de «persona» del catálogo), para que el cuerpo se vea
  hasta que exista su sprite en el paso 5.
- `tools/zone_sheet.tscn` → `docs/ux/capturas/2026-09-30-esqueleto-{antes,llegada,despues}.png`.

**Cláusulas:** salidas, densidad de salidas, arquitectura prohibida, datos de
salida y «al cruzar» del contrato «Umbral». Esto último en parte: el
fundido es del paso 4.

#### Verificado

`verify_movement.tscn`: **58 de 58**. A los 35 casos del paso 2 se suman:

- `prueba_a` y `prueba_b` cumplen las reglas de salida.
- Cada regla detecta su incumplimiento en un mapa o en unas salidas
  estropeados a propósito: un borde abierto, una salida que no es camino,
  tres salidas en una pantalla, una llegada al agua y una salida sin vuelta.
- Las cuatro salidas, cruzadas con el teclado de verdad:
  - se llega a la zona de destino;
  - en el cuadro del cambio, los pies están **exactamente** en `to_cell`;
  - se mira igual que al salir;
  - y, con la tecla pulsada, se sigue andando 1 px en cada uno de los 20
    cuadros siguientes, sin uno parado.
- Posición entera en 3187 cuadros.

**La prueba se comprobó rompiéndola a propósito:**

- Sin control tras cargar la zona fallan 15 casos. Esa rotura quita el control
  desde el arranque, no solo al cruzar, así que es más burda que el caso real.
- Apareciendo un tile desplazado fallan 6.

Sin regresiones:

- `verify_palette.py tokens`: sin deriva.
- `verify_tileset.py`: dentro del contrato.
- `verify_usability.tscn`: 16 de 16.
- `verify_camera.tscn`: 37 de 37.
- `test_zone.tscn`: arranca sin errores.
- `project.godot`: sin tocar.

#### FALLA medido, y se dice: la cámara enseña el vacío junto a las salidas

`verify_palette.py image` sobre las tres capturas encuentra `#4c4c4c`, el
fondo sin mapa, en **51 840, 59 112 y 52 704 px**: entre el 40 % y el 46 % de
la pantalla. Las salidas están por definición en el borde, y la cámara todavía
no tiene límites. Es la cláusula «Cámara en el borde», que el orden de la
fase 5 pone en el paso 4. La captura demuestra que ese paso es imprescindible
antes de enseñar el juego a nadie.

**Pendiente, y se dice:**

- El cambio de zona es un corte directo. Faltan el fundido, el rótulo,
  `GameState` y los límites de la cámara (paso 4).
- En la captura «después» los pies avanzaron 19 px en 20 cuadros: la hoja
  congela el cuerpo un cuadro para capturar la llegada. Es un efecto de la
  herramienta, no del juego: `verify_movement` mide 1 px en cada cuadro.
- Una salida hacia el oeste o el norte aparece en `to_cell` con el cuerpo de
  espaldas a la zona nueva, porque sigue mirando hacia donde iba. Es lo que
  pide el contrato («mirando igual»).

**Paso 4 — Resto: límites de la cámara, fundido, rótulo y `GameState` ·
HECHO el 2026-10-01, pendiente del visto bueno de Diego.** Rama
`parte-2/transicion`.

- `src/world/world_camera.gd`: `limits` y `visible_rect()`. El centro se
  encierra en la zona, en enteros, al final de cada `advance()` y en
  `snap_to_target()`. Un eje en el que el mapa no llena la pantalla queda
  centrado. Sin `limits`, la cámara se comporta igual que antes, así que
  `verify_camera` sigue en 37 de 37.
- `src/world/world_root.gd`: el fundido. Son dos medios fundidos lineales de
  `DUR_ZONE_FADE`, contados en cuadros de física: 120 ms son **7 cuadros a
  60 Hz, 117 ms**. La zona cambia con la pantalla cubierta. Con movimiento
  reducido, corte directo en el mismo cuadro.
- `src/world/place_label.gd` (`PlaceLabel`): el rótulo de lugar.
  - Panel `PANEL_FILL` con borde `BORDER_IDLE` de 1 px, como pide el
    repertorio de la guía §3.1, y texto 1× en `TEXT_PRIMARY`.
  - Relleno `SPACE_4`, como el HUD de la batalla.
  - Arriba a la izquierda, con margen `SPACE_8`.
  - Entra en `DUR_PLACE_LABEL`, **10 cuadros (167 ms)**, con la curva de
    salida de la batalla (`EASE_OUT_TRANS`, cúbica). Se queda
    `PLACE_LABEL_HOLD` (120 cuadros) y se va solo en otros 10.
  - Con movimiento reducido entra y se va de golpe, pero la espera de 2 s se
    mantiene.
- `src/core/game_state.gd`: autoload `GameState`, registrado a mano en
  `project.godot`. Guarda la zona, hacia dónde se mira, el grupo, la bolsa
  (`Inventory`) y las banderas. En esta parte solo escribe el mundo.
- `data/world/zones.json`: el nombre visible de cada zona («Claro de prueba»,
  «Ribera de prueba»).
- `tools/umbral_sheet.tscn` → `docs/ux/capturas/2026-10-01-umbral-{antes,fundido,llegada,esquina}.png`.
- `tools/zone_sheet.tscn`, la hoja del paso 3, se fija en movimiento reducido
  para que siga reproduciendo el corte directo de entonces. Sus capturas
  históricas no se tocan.

**Cláusulas:** «Al cruzar», «Movimiento reducido», «Rótulo de lugar»,
«Cámara en el borde» y «Estado global» del contrato «Umbral», más las
duraciones de «Vereda».

#### Decisiones que el contrato no fijaba, tomadas con tokens existentes

Las cuatro se señalan en el PR para que Diego las confirme:

1. **Color del fundido: `ASH_950`.** El contrato dice «fundido a negro», pero
   no hay token negro. `ASH_950` es el fondo más profundo de la paleta, y no
   se añade ningún color.
2. **El cuerpo se detiene durante el fundido de salida** (6 cuadros, después
   del paso que cruza) y vuelve a leer el teclado al cambiar de zona. Con la
   tecla pulsada sigue andando durante el fundido de entrada sin soltarla.
   Seguir andando durante la salida lo llevaría fuera del mapa, ya sin
   cámara que lo siga.
3. **El rótulo se anima solo con opacidad,** y va **por debajo de la
   cortina**: aparece con la zona nueva, no encima del negro.
4. **Fundido y rótulo se cuentan en cuadros de física,** no con un `Tween`, para
   poder medirlos cuadro a cuadro. Al redondear a cuadros enteros, 120 ms se
   quedan en 117 ms y 160 ms suben a 167 ms.

#### Verificado

`verify_movement.tscn`: **81 de 81**. A los 58 casos anteriores se suman:

- **Límites:**
  - Un mapa de 320×160 se centra en (160, 80) y no se mueve.
  - En 1280 cuadros corriendo hacia las cuatro esquinas de las dos zonas, la
    pantalla nunca sale de la zona.
  - Junto al borde el cuerpo sí sale de la zona muerta, como admite el
    contrato.
- **Fundido:**
  - El cambio llega 7 cuadros después de cruzar, con opacidades exactas 1/7 …
    7/7 (lineal) y la pantalla cubierta.
  - La entrada dura 7 cuadros.
  - El cuerpo se queda quieto durante la salida y anda en cada cuadro de la
    entrada sin soltar la tecla.
  - Al acabar, la cortina queda transparente.
  - La pantalla nunca enseña fuera de la zona al cruzar.
- **Movimiento reducido:** la zona cambia en el mismo cuadro de cruzar, sin
  ningún cuadro de cortina.
- **`GameState`:** sabe la zona de destino y que se mira al este.
- **Rótulo:**
  - Dice «Ribera de prueba», en (8, 8).
  - Entra en 10 cuadros con curva de salida: el primer cuadro sube más que el
    último.
  - Se queda 120 cuadros y se va en 10.
  - Con movimiento reducido no se anima, y la espera sigue siendo de 120
    cuadros.

**La prueba se comprobó rompiéndola a propósito:**

- Sin límites de cámara fallan 5 casos.
- Con un fundido curvo falla 1.
- Aplicando el movimiento reducido a la espera del rótulo falla 1.

**Corregido durante el paso, en la prueba:**

1. Contaba como cuadro de fundido el mismo cuadro del cruce, en el que el
   cuerpo sí avanza.
2. La comprobación «el cuerpo sale de la zona muerta» pasaba también **sin**
   límites, así que no medía nada. La zona muerta de `WorldCamera` cuenta sus
   dos bordes como dentro y `Rect2i.has_point` excluye el final. Corregida, y
   ahora falla sin límites.
3. Una variable con el mismo nombre que la del bucle impedía cargar la prueba
   (`zone`). Se renombró.

**Capturas:**

- `antes`, `llegada` y `esquina` pasan `verify_palette.py image`: **todo
  píxel es un token**. El vacío del paso 3 desaparece: era el 40–46 % de la
  pantalla, y ahora es 0.
- `fundido` no pasa, y es lo que se espera: la cortina mezcla con opacidad,
  igual que el velo de la pantalla de desenlace de la batalla.

Sin regresiones:

- `verify_palette.py tokens`: sin deriva.
- `verify_tileset.py`: dentro del contrato.
- `verify_usability.tscn`: 16 de 16.
- `verify_camera.tscn`: 37 de 37.
- `test_zone.tscn` y `main.tscn` arrancan sin errores con el autoload.
- `project.godot`: solo las 4 líneas de `[autoload]`.

**Pendiente, y se dice:**

- **Paso 5 (pantalla completa):** el sprite del personaje en lugar del
  marcador, el orden de dibujo por altura y revisar el hueco de 1–3 px entre
  la caja y el borde dibujado.
- **Paso 6 (estados):** el fundido es la única transición del mundo que se
  mide cuadro a cuadro. Faltan los estados forzados en una hoja
  (`states_sheet`) y comprobar con la cámara en movimiento sobre zona
  purificada la nota de Diego sobre el follaje.
- **El rótulo del arranque** se ve todavía en la captura `antes`, porque el
  cuerpo llega a la salida antes de los 2 s. Es lo que dice el contrato (el
  rótulo sale al entrar en una zona); se señala por si en la parte 10 la
  primera entrada debe tratarse distinto.

**Verificación de la parte** (`tools/verify_movement.gd`): posición entera en
cada cuadro; 1 y 2 px por cuadro y eje; cero cuadros de aceleración; un pasillo
de 16 px siempre se cruza y uno de 0 nunca; una esquina a 4 px o menos se
rodea y a 5 px no; duración del fundido medida; la tecla pulsada sigue andando
tras cruzar; y, en el borde del mapa, la cámara nunca enseña fuera de la zona.
