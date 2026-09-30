# Anexo — Movimiento, colisiones y transición entre zonas (parte 2)

Abierto el 2026-09-30. Hereda el contrato «Vereda»
(`2026-09-14-exploracion-top-down.md`) y sus enmiendas 1 a 5. Lo que ya está
firmado allí **no se vuelve a decidir aquí**: velocidades de 60 y 120 px/s,
diagonal por eje, movimiento sin aceleración, cámara a píxel entero, fundido de
zona de 2 × 120 ms, rótulo de lugar de 160 ms. Este anexo decide solo lo que el
contrato deja abierto.

**Estado:** fases 1 a 4 escritas. **Esperando la elección de Diego** (fase 4).

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

**Pregunta a Diego:** ¿A, B o C? Hasta su respuesta no se implementa nada.
