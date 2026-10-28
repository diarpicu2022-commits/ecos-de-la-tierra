# Continuar *Ecos de la Tierra* en la nube

Escrito el 2026-10-28 revisando GitHub (`diarpicu2022-commits/ecos-de-la-tierra`).
La última actividad en el repositorio es del **2026-10-01**: lleva casi cuatro
semanas parado, y parado en una pregunta, no en código.

Este archivo es el punto de entrada para una sesión en la nube. **No sustituye a
`docs/plan-de-trabajo.md`**, que sigue siendo la fuente de verdad; resume dónde
quedó todo, qué bloquea y qué falta, para no tener que explorar el repo.

---

## 1. Lo primero: el contrato «Rastro» espera visto bueno

**Desbloqueado el 2026-10-28.** El PR #11 se fusionó sin comentario, y en la
sesión 7 Diego respondió las tres preguntas:

1. Dirección **A · «Rastro»**.
2. Mapas en **texto** (`data/world/zones/<zona>.txt` + `<zona>.deco.txt`).
3. **Confirma la hipótesis prudente:** cada zona enseña la causa antes del
   combate.

Con eso se escribió el **contrato «Rastro»** en
`docs/ux/anexos/2026-10-01-las-siete-zonas.md`. **Lo siguiente es el visto
bueno de Diego a sus valores** (3 viñetas junto al camino, una por pantalla;
hito de 2×3 a 4×4 tiles; paso cerrado detrás de la fuente). Después empieza
**Valdehoja**, con sus dos preguntas propias.

> Regla del proyecto: la sesión en la nube **no elige por Diego**. Si falta
> una respuesta suya, se le pregunta y se espera.

---

## 2. Estado por partes

| # | Parte | Estado en GitHub |
|---|---|---|
| — | Motor de combate, IA por pesos, tabla Q del jefe | Hecho |
| — | Pantalla de batalla «Ceniza y Brasa» | Hecho, `verify_usability` 16/16 |
| 1 | Tokens de mundo, tileset y cámara | Todo aprobado; **abierta solo por la prueba con personas** de los materiales (aplazada) |
| 2 | Movimiento, colisiones y transición entre zonas | **Cerrada** 2026-10-01 (PR #4–#9), `verify_movement` 99/99 |
| 3 | Las siete zonas | **En curso**: contrato «Rastro» escrito el 2026-10-28; espera visto bueno |
| 4 | Encuentros y paso mundo ↔ combate | Sin empezar |
| 5 | Diálogos y retratos (Yara, compañeros, Rasgo) | Sin empezar |
| 6 | Progresión | Sin empezar |
| 7 | Puzzles ambientales, uno por región | Sin empezar |
| 8 | Menú fuera de combate | Sin empezar |
| 9 | Guardado de partida | Sin empezar |
| 10 | Título y opciones | Sin empezar |
| 11 | Audio | Sin empezar |
| 12 | Final y créditos | Sin empezar |

Alcance cerrado el 2026-09-14: **el juego completo, cinco regiones**, sin
versión de muestra. Faltan nueve partes y media; las caras por contenido son la
3, la 5 y la 7.

---

## 3. Lo que falta, en orden

### Parte 3 — una zona por sesión (tras el visto bueno al contrato)

Valdehoja → Bosque de las Cenizas → Cuenca de Alquitrán → Costa Quebrada →
Llanura Marchita → Cumbre Menguante → Cripta de la Avaricia.

Cada zona lleva: fuente del daño, gradiente que se aclara al alejarse, **un paso
cerrado que la purificación abre**, un único hito visual, al menos una pista
por franja de 480 px, y la fauna en bandada al purificar (IA-2). Valdehoja
empieza gris salvo el jardín de Yara y hace de marcador de progreso.

Verificación por zona, todavía **por escribir**: `tools/verify_zone.gd <zona>`
(BFS: salida inalcanzable enferma y alcanzable purificada; pista por franja;
decorado fuera del catálogo; `verify_palette.py image --world` sobre la captura).
Detalle en `docs/guia-de-continuacion.md` §5, parte 3.

### Partes 4 a 12

Instrucciones de cada una en la guía §5. Decisiones que quedan pendientes
dentro de ellas:

| Qué | Dónde se decide |
|---|---|
| IA-5 (sintonía del grupo): enmienda del contrato de batalla, solo maneja a Ilan; orden de líder | Diego, anexo de la parte 4 |
| IA-6: umbrales de los tres desenlaces de Rasgo | Anexo de la parte 5 |
| IA-1 patrulla/persecución, IA-3 pistas de Yara, IA-4 bot de equilibrado | Cada una en su parte (guía §3.3) |

### Deudas sueltas (guía §4)

- **Pruebas con personas** «¿Por qué pierdo?» y materiales (dE 9,2): aplazadas
  por Diego el 2026-10-01. Hoja lista en
  `docs/ux/pruebas/2026-10-01-hoja-de-pruebas.md`. Cierran la parte 1. **No se
  pueden hacer en la nube**: necesitan tres personas reales.
- **Enmienda 6** si dE 9,2 entre materiales no basta (se decide con esa prueba).
- **Fondo de batalla por región + parallax de 3 capas**, con las rampas del
  tileset de la región. Parte 4.
- **Mobbin y Pinterest** sin consultar en el anexo de exploración: abrir con
  navegador o registrarlas como «no aplicable» con motivo.
- **GIF del follaje purificado en movimiento**: Diego tiene que juzgarlo (anexo
  de la parte 2, paso 6).
- **F5 abre el selector de región de pruebas**: dejar `region_select.gd` como
  herramienta de depuración. Parte 10.
- **Legal** (norma global de Diego desde 2026-09-28): el juego no tiene cuentas
  ni red, pero el guardado (parte 9) y una posible exportación a Android
  obligan a dejar escrito en el anexo qué datos guarda (o que ninguno
  personal), una política breve en `docs/legal/` y, si va a Google Play, el
  formulario de Seguridad de los datos. Hoy **no está anotado en ningún sitio**
  del repo.

---

## 4. Preparar el entorno en la nube

El proyecto es Godot 4 + GDScript, sin dependencias externas.

```bash
# Godot 4.7.2 estándar (NO .NET), Linux
wget https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
unzip Godot_v4.7.2-stable_linux.x86_64.zip && chmod +x Godot_v4.7.2-stable_linux.x86_64
export GODOT=$PWD/Godot_v4.7.2-stable_linux.x86_64

# Python para las herramientas de paleta y tileset
pip install pillow

# Importar el proyecto una vez (crea .godot/)
$GODOT --headless --path . --import
```

Comprobar que todo sigue en verde antes de tocar nada:

```bash
python tools/verify_palette.py tokens
python tools/verify_tileset.py
$GODOT --headless --path . res://tools/verify_usability.tscn   # 16/16
$GODOT --headless --path . res://tools/verify_movement.tscn    # 99/99
$GODOT --headless --path . res://tools/verify_camera.tscn      # 37/37
```

Las capturas (`tools/*_capture.tscn`, `tools/*_sheet.tscn`) necesitan ventana.
En un servidor sin pantalla: `xvfb-run -a $GODOT --path . res://tools/<x>.tscn`
(instalar `xvfb` si falta). Salen a 480×270, que es el medio real del juego.

---

## 5. Reglas que no se saltan

Resumen; el texto completo está en `CLAUDE.md` y en la guía §1.

- **Abrir leyendo** `docs/plan-de-trabajo.md` y la guía; no explorar el repo.
- **Una parte por sesión** (en la parte 3, una zona por sesión). No se abre la
  siguiente sin cerrar la actual.
- **Diseño antes que código**: anexo con usuarios, comunicación, investigación
  (≥ 6 fuentes reales con URL) y 2–3 direcciones; **Diego elige y se espera**.
- **Contratos bloqueados se cumplen.** Todo valor visual sale de
  `src/ui/design_tokens.gd`; assets por `tools/gen_*.py` con la paleta de
  `tools/pixel.py`.
- **El verde `VITAL_*` solo significa «purificado»**, y nunca lo carga solo
  (va con valor, silueta o fauna).
- **Paso a paso** (tokens → componente clave → esqueleto → resto → pantalla →
  estados), con captura, cláusula del contrato y parada para visto bueno en
  cada paso.
- **Verificar midiendo**, e informar también de lo que falla.
- Código en inglés; textos de jugador y comentarios en español.
- Git: rama `parte-N/<tema>` desde `master`, PR hacia `master` con la plantilla
  de la guía §1.6 (Dev: Diego Armando Pinta Cuasquen) y capturas reales. Nunca
  commits directos a `master`. **Sin firma de herramientas** en nada.
- **Al cerrar la sesión**: actualizar `docs/plan-de-trabajo.md` (y este
  archivo si cambia el bloqueo) y hacer commit.

---

## 6. Nota sobre la copia local del PC

La copia en el PC de Diego está en `master` **atrasada** (llega solo al PR #3)
y tiene `project.godot` modificado sin commit: es el editor de Godot que
reordenó secciones y borró los comentarios, y además le falta
`2d/snap/snap_2d_vertices_to_pixel=true`. No hay que subir ese cambio. Para
ponerla al día: `git checkout -- project.godot && git pull`.
