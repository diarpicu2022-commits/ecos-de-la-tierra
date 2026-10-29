# Plan de trabajo — *Ecos de la Tierra*

Última actualización: 2026-10-28 (sesión 8; cierre de la parte 4)

**Este archivo se lee primero al abrir una sesión nueva.** Dice qué está hecho,
qué toca ahora y qué decisiones ya están tomadas, para no volver a discutirlas
ni volver a leer el proyecto entero.

**Lo segundo es `docs/guia-de-continuacion.md`**: el protocolo de diseño
completo, el repertorio del juego y las instrucciones de cada parte. Está
escrita para que cualquiera del equipo, con o sin la skill de dirección de
diseño, siga con el mismo criterio.

---

## Cómo se trabaja: una parte por sesión

El juego completo no se hace en un día y no se intenta. El trabajo va **por
partes, y las partes van por sesiones**, por dos motivos distintos y los dos
válidos:

1. **De diseño.** Al terminar cada parte se muestra lo hecho y se para a esperar
   visto bueno. Un desvío corregido al final de una parte es un daño pequeño; el
   mismo desvío descubierto con el juego entero montado obliga a rehacer.
2. **De coste.** Una sesión que abarca demasiado se queda sin contexto a mitad,
   y lo que sigue se hace peor y más caro en tokens. Una parte por sesión —dos
   si salen cortas— mantiene la sesión con contexto de sobra.

### Reglas de sesión

- **Se abre leyendo este archivo**, no explorando el repositorio. Aquí está el
  punto de retome exacto.
- **Se cierra actualizando este archivo** —marcar la parte, mover el punto de
  retome, anotar lo que quedó a medias— **y commiteando**. Una sesión que
  termina sin commit obliga a la siguiente a reconstruir qué pasó.
- **No se abre la parte siguiente sin cerrar la actual.** Si sobra sesión, se
  pule lo hecho o se verifica; no se adelanta trabajo a medio hacer.
- **No se releen los anexos enteros** salvo que la parte los necesite. Para
  saber qué se decidió basta la sección «Decisiones cerradas» de aquí abajo.

---

## Punto de retome

> **Parte 4 — Encuentros y paso mundo ↔ combate. CERRADA el 2026-10-28.**
> Anexo `docs/ux/anexos/2026-10-28-encuentros.md`. Lo siguiente es abrir la
> **parte 5** (diálogos y retratos) con su anexo.
>
> - Contrato «Persiana»:
>   - IA-1 en el mapa: patrulla, alerta, persecución y rendición;
>   - ventaja por la espalda;
>   - persiana de 300 ms y fondo regional en tres capas;
>   - el grupo vive en `GameState`;
>   - huida con 1 s de gracia;
>   - la ola de purificación pieza a pieza.
> - Enmienda 1: señal de alerta en brasa, con la Cripta como excepción.
> - IA-4: `tools/balance_bot.gd`.
> - IA-5, contrato «Orden de líder»:
>   - el jugador maneja solo a Ilan y da una orden de grupo;
>   - la orden se juzga (enmienda 1);
>   - la sintonía manda (enmienda 2).
> - Reglas nuevas de combate:
>   - en las regiones, la contramedida se sostiene 2 rondas;
>   - la Sombra exige combinar en la misma ronda.
> - **Deudas de equilibrado:**
>   - el Gólem de la Costa no presiona;
>   - la fuerza bruta gana demasiado en la Llanura (100 %), la Cuenca (64 %)
>     y el Bosque (41 %).
> - Pendientes: la fauna en bandada (IA-2, parte 3) y arrancar el juego en el
>   mundo con `GameFlow` (parte 10).
>
> **Parte 3 — Las siete zonas. CERRADA el 2026-10-28.**
>
> **Parte 3, historial:**
> Anexo `docs/ux/anexos/2026-10-01-las-siete-zonas.md`.
>
> **Bosque de las Cenizas: aprobado por Diego** (2026-10-28). Prueba de
> entrecerrar en lo enfermo: opción (b), el camino se lee por silueta y no por
> luz.
>
> **Cuenca de Alquitrán: aprobada** (2026-10-28, PR #14).
>
> **Costa Quebrada: aprobada** (2026-10-28). Trae la enmienda 9, la arena.
>
> **Llanura Marchita: aprobada** (2026-10-28, PR #15).
>
> **Cumbre Menguante: aprobada** (2026-10-28, PR #16).
>
> **Cripta de la Avaricia: aprobada** (2026-10-28), con la enmienda 12.
> - Cinco bóvedas, una por región (Diego): lo que la Compañía se llevó de
>   cada región junto a su oro.
> - Enmienda 10, la piedra: muro `%` y losa `,`, sin color nuevo.
> - Hito: la estatua de oro del Barón Cendral; fuente: la Sombra de la
>   Avaricia. Al purificar, el oro desaparece.
> - **Enmienda 12** (Diego): detrás de la Sombra, un túnel y un pozo con
>   reja de oro suben a Valdehoja; allí llegan a una bocamina tapiada de 2×2
>   que se abre al purificar la Cripta.
> - `verify_zone`: Cripta **48/48** y Valdehoja **55/55**; las siete zonas en verde.
>
> **Valdehoja, hecho en la sesión 7** (pasos 1 a 4, todos con visto bueno de
> Diego):
> - el contrato «Rastro»;
> - las enmiendas 6, 7 y 8 (paleta rica con color al purificar, animales,
>   movimiento en lo purificado);
> - 38 piezas de decorado y el atlas con el prado, su borde y el agua viva;
> - `WorldDecor` y `WorldAmbient` en el motor, `verify_zone` 49/49 y
>   `verify_squint` en verde.
>
> Quedan dos cosas que dependen de otras partes: **la ola de purificación por
> partes** (con el combate, parte 4) y **la llegada al Bosque** (se fija al
> dibujarlo).
>
> **Godot en la nube:** se descarga como dice `CONTINUAR.md` §4 en
> `/home/user/godot/` y hace falta que Diego permita ejecutar el binario. Con
> eso se pasan todas las pruebas y las capturas con `xvfb-run`.
>
> **Parte 2 — Movimiento, colisiones y transición entre zonas. CERRADA el
> 2026-10-01.** Contrato «Umbral», seis pasos, PR #4 a #9; `verify_movement`
> da **99 de 99**. Los PR #6 a #9 los fusionó Juan José Rueda con permiso de
> Diego, sin revisión escrita en GitHub. Queda para Diego juzgar el GIF del
> follaje purificado en movimiento (anexo de la parte 2, paso 6).
>
> **Módulo de IA ampliado** (2026-09-30): seis piezas nuevas, IA-1 a IA-6, en
> la guía §3.3. Cada una entra en su parte; ninguna toca la parte 2.
>
> ---
>
> **Parte 1 — Tokens de mundo, tileset y cámara.** Todo hecho y aprobado salvo
> **la prueba con tres personas** de los recortes. Sigue abierta por eso.
>
> Hecho: fases 1 a 4 del anexo de exploración (contrato «Vereda» bloqueado) y
> el **paso 1 de la fase 5, los tokens, aprobados por Diego el 2026-09-23**.
> En la sesión 3 también se cerró la deriva de paleta entre `pixel.py` y
> `design_tokens.gd` y se añadió `tools/verify_palette.py`.
>
> **Paso 2a — catálogo: hecho y aprobado** (2026-09-23).
>
> **Paso 2b — tileset: EN CURSO.** Sesión 4 (2026-09-29): camino aceptado en
> 1,48 (opción a), follaje purificado calmado a dos copas por tile y
> `verify_tileset.py` **en verde**, capturas del motor rehechas
> (`docs/ux/capturas/2026-09-29-*`). Punto de control con Diego
> **hecho** (2026-09-30, PR #1): aprueba camino y follaje. Queda la prueba con
> tres personas usando los recortes de `docs/ux/prueba-materiales/`.
> Detalle en el anexo de exploración, fase 5, paso 2b, «Sesión del
> 2026-09-29».
>
> **Paso 3 — cámara: HECHO y aprobado** (2026-09-30, rama
> `parte-1/camara`). `WorldCamera` en `src/world/world_camera.gd`,
> `verify_camera.tscn` **37 de 37**, capturas `docs/ux/capturas/2026-09-30-camara-*`.
> Enmienda 5: ritmo de la anticipación. Detalle en el anexo de exploración,
> fase 5, paso 3.
>
> **Para cerrar la parte 1 falta solo** la prueba con tres personas de los
> recortes (dE entre materiales). La parte 2, ya abierta, revisa también el
> descentrado de la cámara al parar (anexo de exploración, paso 3).
>
> A partir de aquí **lo continúa otra persona del equipo** siguiendo
> `docs/guia-de-continuacion.md`.

---

## Las doce partes

Van en este orden porque cada una se apoya en la anterior: no hay diálogo sin
zonas, ni progresión sin encuentros.

| # | Parte | Estado |
|---|---|---|
| — | Motor de combate por turnos, IA por pesos, tabla Q del jefe | **Hecho**, verificado por consola |
| — | Pantalla de batalla «Ceniza y Brasa» | **Hecho**, 16/16 en usabilidad |
| 1 | Tokens de mundo, tileset y cámara | **En curso** — tokens, catálogo y tileset aprobados; cámara aprobada 2026-09-30; falta la prueba con personas |
| 2 | Movimiento, colisiones y transición entre zonas | **Hecha** (2026-10-01) — contrato «Umbral», `verify_movement` 99/99 |
| 3 | Las siete zonas: Valdehoja + cinco regiones + Cripta de la Avaricia | **Cerrada** 2026-10-28 — contrato «Rastro»; enmiendas 6-10 y 12. Las siete zonas aprobadas, `verify_zone` en verde |
| 4 | Encuentros y paso mundo ↔ combate conservando el estado del grupo | **Cerrada** 2026-10-28 — contratos «Persiana» y «Orden de líder» (IA-1, IA-4, IA-5); deudas de equilibrado en el anexo |
| 5 | Diálogos y retratos: Yara, los cuatro compañeros, Rasgo | |
| 6 | Progresión: quién se une dónde, qué habilidad trae, qué región quedó purificada | |
| 7 | Puzzles ambientales, uno por región | |
| 8 | Menú fuera de combate: grupo, bolsa, habilidades | |
| 9 | Guardado de partida | |
| 10 | Pantalla de título y opciones | |
| 11 | Audio | |
| 12 | Final y créditos | |

Las partes 3, 5 y 7 son las caras, y no por código sino por **contenido**: siete
zonas dibujadas tile a tile, cinco personajes con arco y cinco puzzles distintos
son trabajo de autoría. Es previsible que cada una ocupe varias sesiones y se
subdivida —una zona por sesión, por ejemplo—. Cuando eso pase, se anota aquí la
subdivisión en vez de dejar la parte abierta indefinidamente.

---

## Decisiones cerradas — no se vuelven a discutir

Salvo información nueva. Si alguna se enmienda, se anota con fecha.

- **Alcance: el juego completo, las cinco regiones.** Decidido por el usuario el
  2026-09-14. **Anula** la nota de recorte de `CONTEXTO.md`, que permitía
  quitar Llanura Marchita y Cumbre Menguante si apretaba el tiempo. No hay
  versión de muestra: se entrega el juego entero.
- **Motor y lenguaje:** Godot 4, GDScript. Nada de C#: su exportación a Android
  es experimental.
- **Plataforma priorizada:** PC con teclado. Fijado en el contrato de la batalla.
- **Identidad visual:** «Ceniza y Brasa», contrato bloqueado el 2026-09-13 en
  `docs/ux/anexos/2026-09-13-pantalla-de-batalla.md`. El mundo la hereda; lo
  suyo propio se firma en el anexo de exploración.
- **Resolución:** viewport 480×270 escalado por múltiplos enteros. Filtro
  `Nearest`, `stretch/scale_mode = integer`.
- **El verde `vital_500` es solo purificación.** En todo el juego, no solo en la
  batalla. Regla de acento único, no negociable.
- **Radio de esquina 0 px** en toda la interfaz.
- **Código en inglés, textos de jugador en español.** Clases en `PascalCase` con
  `class_name`, archivos en `snake_case`.
- **La interfaz se construye en GDScript**, no en escenas `.tscn` montadas a
  mano: es el patrón que ya sigue `src/ui/`, y mantiene el diseño en un sitio
  donde se puede leer y auditar.
- **Sin firma de herramientas** en commits, código ni documentación.
- **Dirección del mundo: «Vereda»** (2026-09-14). Mundo contiguo con cámara
  viva, zona muerta de 28×48 px y cámara ajustada a píxel entero. Contrato en
  `docs/ux/anexos/2026-09-14-exploracion-top-down.md`.
- **Caminar no se anima.** Velocidades atadas a la rejilla: 60 px/s al andar y
  120 al correr, que a 60 Hz son 1 y 2 píxeles por cuadro exactos. Cualquier
  velocidad nueva debe ser múltiplo de 60 px/s.
- **Encuentros visibles en el mapa**, y el mapa **no se estrecha** para impedir
  que se esquive el combate.
- **Purificar abre paso y devuelve fauna**, no solo repinta. Cada zona se traza
  con un paso cerrado que la purificación abre.
- **Paleta de mundo: tres rampas de material** (suelo, agua, follaje) con techo
  de saturación 0,22. Enmienda 1 del contrato de exploración, autorizada.
- **La ola de purificación** (2026-09-23): la purificación de zona avanza en
  tramado ordenado 4×4, 8 pasos, 900 ms. El tramado es exclusivo de ese
  momento. Enmienda 3.
- **Diagonal sin normalizar** (2026-09-23): 1 + 1 px por cuadro; las
  velocidades se cumplen por eje. Enmienda 4.
- **Camino en 1,48 de valor** (2026-09-29, aprobado por Diego el 2026-09-30):
  se acepta sin token nuevo, porque su estado lo cargan también la silueta del
  borde y la textura. Piso propio de 1,47 en `verify_tileset.py`.
- **Follaje purificado con dos copas por tile** (2026-09-29, aprobado por Diego el
  2026-09-30): con tres se leía como papel pintado y con una salía una
  retícula de lunares.
- **Cámara** (2026-09-30, enmienda 5): la anticipación abre a 60 px/s y vuelve
  a 30 px/s, por eje. Zona muerta 12 px bajo el centro de la pantalla. Con
  movimiento reducido, sin anticipación.
- **Enmiendas 6, 7 y 8** (2026-10-28, Diego, al ver Valdehoja «desabrida»):
  paleta rica con color al purificar (madera, tejado, agua viva, flores,
  prado); animales domésticos siempre y fauna silvestre al purificar;
  movimiento ambiental solo en lo purificado. Detalle en la guía §3.2 bis.
- **Enmienda 9, la arena** (2026-10-28, Diego): material nuevo (`:`) para la
  Costa, sin color nuevo; piso propio de dE 6 entre arena y camino
  purificados (medido 6,9). La reserva para el dE entre materiales pasa a la
  siguiente enmienda libre.
- **Cripta: cinco bóvedas, una por región, y enmienda 10, la piedra**
  (2026-10-28, Diego): 5 viñetas solo en la Cripta; muro `%` y losa `,` sin
  color nuevo, que no conviven con los otros materiales. La reserva para el
  dE entre materiales pasa a la enmienda 11.
- **Enmienda 12, la salida de la Cripta** (2026-10-28, Diego): detrás de la
  Sombra, un túnel y un pozo, cerrados con reja de oro, suben a Valdehoja. Allí
  llegan a una bocamina tapiada (2×2, parte `greed_crypt` del pueblo) que se
  abre al purificar la Cripta. Valdehoja admite ese único paso cerrado.
- **Entrecerrar en lo enfermo** (2026-10-28, Diego, opción b): el camino
  enfermo se lee por silueta y textura, no por luz; `verify_squint` mide que no
  mande el decorado.
- **El mundo va en cadena** (2026-10-28, Diego): Valdehoja → Bosque → Cuenca →
  Costa → Llanura → Cumbre → Ciudad Dorada; el paso cerrado de cada fuente
  abre la región siguiente.
- **Tinta de personaje** (2026-10-28, Diego): `ash_950` y `ash_900` se aceptan
  en `verify_palette --world` solo como contorno y ojos de personaje; el
  decorado y el terreno se miden con `--strict`.
- **Partes de Valdehoja como capa de texto** (`valdehoja.parts.txt`), no como
  rectángulos (2026-10-28).
- **Zonas: «Rastro»** (2026-10-28, elegido por Diego): un camino principal
  lleva a la fuente del daño pasando por 3 viñetas de causa y efecto; hito en
  la fuente; paso cerrado detrás del monstruo de historia. **Mapas en texto**
  (`data/world/zones/<zona>.txt` + `<zona>.deco.txt`). Hipótesis prudente
  confirmada: la zona enseña la causa antes del combate. Contrato en el anexo
  de la parte 3.
- **Movimiento y zonas: «Umbral»** (2026-09-30): caja de colisión de 12×8 px en
  los pies, deslizamiento en esquina de 4 px, salidas solo donde el camino
  cruza el borde (máximo 2 por pantalla), con la tecla pulsada se sigue
  andando tras el fundido.
- **Colisión del terreno = tile entero** (2026-09-30, parte 2, paso 2): no
  sigue la silueta en sierra; entre la caja y el borde dibujado quedan 1–3 px.
- **Rótulo de lugar con movimiento reducido** (2026-09-30): mantiene la espera
  de 2 s; solo desaparece el fundido.
- **Módulo de IA ampliado** (2026-09-30), guía §3.3: IA-1 monstruos que
  patrullan y persiguen; IA-2 fauna en bandada; IA-3 pistas adaptativas de
  Yara; IA-4 bot de equilibrado; **IA-5 sintonía del grupo**: el jugador solo
  maneja a Ilan y los compañeros aprenden de él con una red neuronal (enmienda
  pendiente del contrato de batalla); **IA-6 memoria de Rasgo**, con la
  historia ampliada y tres desenlaces. Sin librerías ni servicios externos;
  un modelo de lenguaje en directo se descartó.

---

## Decisiones abiertas

| Qué | Dónde se resuelve |
|---|---|
| Si dE 9,2 entre materiales basta en pantalla, o hace falta la **enmienda 11** (la 5 se usó para la cámara; la 6 a la 8, para Valdehoja; la 9, para la arena; la 10, para la piedra) | Paso 2b, sobre la captura del tileset |
| Si la Cripta lleva una salida a la superficie detrás de la Sombra (hoy no tiene paso cerrado ni salida de ida, por ser el final) | Diego, al dar el visto bueno a la Cripta |
| IA-5: enmienda del contrato de batalla (solo el turno de Ilan) y orden de líder | Diego, en el anexo de la parte 4 |
| IA-6: umbrales de los tres desenlaces de Rasgo | Anexo de la parte 5 |
| Prueba con personas de «¿Por qué pierdo?» y de materiales | **Aplazadas por Diego el 2026-10-01.** Deuda; hoja lista en `docs/ux/pruebas/2026-10-01-hoja-de-pruebas.md` |
| Mobbin y Pinterest, no consultadas | Primera sesión con navegador |

## Hallazgos medidos — 2026-09-23

- **El verde y la brasa se separan casi solo por matiz** (`VITAL_500` /
  `EMBER_300`: 1,08:1 de contraste; con deuteranopía `VITAL_500` / `EMBER_400`
  baja a 1,22:1). Purificado frente a causa activa nunca depende solo del
  color. Detalle en la guía §2.3.
- **Deriva de paleta cerrada:** `EMBER_700` y `VITAL_900` se usaban en los
  sprites sin estar declarados. Ya están en `design_tokens.gd`; no son colores
  nuevos. Los 17 sprites pasan `verify_palette.py image`.

---

## Dónde está cada cosa

```
docs/plan-de-trabajo.md      Este archivo. Punto de retome de cada sesión.
docs/guia-de-continuacion.md Protocolo, repertorio e instrucciones por parte.
AGENTS.md                    Reglas para quien abra el proyecto.
tools/verify_palette.py      Paleta, saturación y visión del color, medidas.
docs/ux/anexos/              Un anexo por pantalla. Contratos de diseño.
src/README.md                Arquitectura del código.
README.md                    Cómo abrir y ejecutar el proyecto.
```
