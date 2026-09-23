# Plan de trabajo — *Ecos de la Tierra*

Última actualización: 2026-09-23 (sesión 3)

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

> **Parte 1 — Tokens de mundo, tileset y cámara.** En curso.
>
> Hecho: fases 1 a 4 del anexo de exploración (contrato «Vereda» bloqueado) y
> el **paso 1 de la fase 5, los tokens, aprobados por Diego el 2026-09-23**.
> En la sesión 3 también se cerró la deriva de paleta entre `pixel.py` y
> `design_tokens.gd` y se añadió `tools/verify_palette.py`.
>
> **Paso 2a — catálogo de lo que responde: hecho** (anexo de exploración, fase
> 5, y `data/world/interactables.json`). **Esperando visto bueno de Diego.**
>
> **Siguiente: paso 2b — tileset** de terreno enfermo y purificado (guía §5,
> parte 1). P1 y P2 aprobados el 2026-09-23: son las enmiendas 3 y 4.

---

## Las doce partes

Van en este orden porque cada una se apoya en la anterior: no hay diálogo sin
zonas, ni progresión sin encuentros.

| # | Parte | Estado |
|---|---|---|
| — | Motor de combate por turnos, IA por pesos, tabla Q del jefe | **Hecho**, verificado por consola |
| — | Pantalla de batalla «Ceniza y Brasa» | **Hecho**, 16/16 en usabilidad |
| 1 | Tokens de mundo, tileset y cámara | **En curso** — tokens aprobados 2026-09-23 |
| 2 | Movimiento, colisiones y transición entre zonas | |
| 3 | Las siete zonas: Valdehoja + cinco regiones + Cripta de la Avaricia | |
| 4 | Encuentros y paso mundo ↔ combate conservando el estado del grupo | |
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

---

## Decisiones abiertas

| Qué | Dónde se resuelve |
|---|---|
| Si dE 9,2 entre materiales basta en pantalla, o hace falta la **enmienda 5** | Paso 2b, sobre la captura del tileset |
| Visto bueno del catálogo de lo que responde | Diego, antes del paso 2b |
| Mapas como texto ASCII o pintados en el editor | Diego, en la primera zona (parte 3) |
| Prueba con personas de «¿Por qué pierdo?» | Antes de la parte 3. Guía §4 |
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
CLAUDE.md                    Lo que cualquier Claude lee al abrir el proyecto.
tools/verify_palette.py      Paleta, saturación y visión del color, medidas.
docs/ux/anexos/              Un anexo por pantalla. Contratos de diseño.
src/README.md                Arquitectura del código.
README.md                    Cómo abrir y ejecutar el proyecto.
```
