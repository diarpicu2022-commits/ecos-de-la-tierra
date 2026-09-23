class_name DesignTokens
extends RefCounted

## Tokens de la interfaz. Única fuente de verdad del contrato de diseño
## «Ceniza y Brasa», bloqueado el 2026-09-13 en
## docs/ux/anexos/2026-09-13-pantalla-de-batalla.md
##
## Ningún color, espaciado o duración se escribe suelto en una escena o en un
## script de interfaz: todo sale de aquí. Si un valor hace falta y no está en
## este archivo, es que el contrato no lo contempla, y eso se discute antes de
## añadirlo.


# --- Ceniza: estructura, fondos y texto -------------------------------------

const ASH_950 := Color("#17141c")  ## Fondo más profundo y bandas del viewport.
const ASH_900 := Color("#221d2a")  ## Fondo de panel.
const ASH_800 := Color("#2e2836")  ## Relleno de panel de interfaz.
const ASH_700 := Color("#3a3540")  ## Cielo ceniza y canal de las barras.
const ASH_600 := Color("#4d4657")  ## Borde inactivo. Solo forma, nunca texto.
## Texto secundario y opción sin foco. Enmienda del 2026-09-13: el valor
## original #7a7189 medía 3,1:1 sobre ASH_800 y no llegaba al piso AA exigido
## por el contrato. Se aclaró conservando matiz y saturación.
const ASH_400 := Color("#9c95a7")
const ASH_200 := Color("#b8b0c4")  ## Barra de energía y texto de apoyo.
const ASH_050 := Color("#e8e4ee")  ## Texto primario y cifras.


# --- Brasa: el daño y la causa todavía activa -------------------------------

## Solo para rellenos de barra y formas. Nunca para texto: sobre ASH_800 da
## 3,9:1 y no llega al mínimo AA de 4,5:1.
const EMBER_500 := Color("#e8562e")
const EMBER_400 := Color("#f08a3c")  ## Texto de aviso (5,7:1 sobre ASH_800).
const EMBER_300 := Color("#ffc14d")  ## Cursor, foco y cifras críticas (8,8:1).
## Borde apagado de la llama. Solo sprites: en uso en tools/pixel.py desde el
## 2026-09-13 sin estar declarado aquí. Se declara el 2026-09-23 para cerrar la
## deriva que detectó tools/verify_palette.py; no es un color nuevo.
const EMBER_700 := Color("#7a2518")


# --- Acento único: la purificación ------------------------------------------

## Reservado a la purificación y a nada más. El verde tiene un solo significado
## en todo el juego: «la causa se atajó». Las barras de vida NO son verdes.
const VITAL_500 := Color("#4ade80")  ## 8,2:1 sobre ASH_800.
const VITAL_700 := Color("#2b9d5a")  ## Sombra del verde, 1 px.
## Fondo de las variantes purificadas. Solo sprites; misma historia que
## EMBER_700: ya estaba en tools/pixel.py y se declara para cerrar la deriva.
const VITAL_900 := Color("#1a5e38")


# --- Papeles semánticos ------------------------------------------------------
# La interfaz referencia estos nombres, no los tokens crudos, para que un
# cambio de paleta no obligue a repasar cada escena.

const TEXT_PRIMARY := ASH_050
const TEXT_SECONDARY := ASH_400
const TEXT_WARNING := EMBER_400
const TEXT_CRITICAL := EMBER_300
const TEXT_PURIFIED := VITAL_500

const PANEL_FILL := ASH_800
const PANEL_FILL_DEEP := ASH_900
const BAR_TRACK := ASH_700

const BORDER_IDLE := ASH_600
const BORDER_FOCUS := EMBER_300
const BORDER_PURIFIED := VITAL_500

const ENERGY_FILL := ASH_200


# --- Escala de espaciado -----------------------------------------------------
# Múltiplos de 4 sobre un lienzo de 480x270. Ningún valor fuera de esta escala
# sin justificarlo por escrito en el anexo.

const SPACE_2 := 2
const SPACE_4 := 4
const SPACE_8 := 8
const SPACE_12 := 12
const SPACE_16 := 16
const SPACE_24 := 24
const SPACE_32 := 32


# --- Forma -------------------------------------------------------------------

## Bloqueo de forma: todo agudo. A 480x270 una curva de 2 px se lee como un
## error de dibujo, no como un estilo.
const CORNER_RADIUS := 0
const BORDER_WIDTH := 1


# --- Tipografía --------------------------------------------------------------

const FONT_PATH := "res://assets/fonts/ceniza.fnt"

## La fuente es de mapa de bits: solo escala por múltiplos enteros. Un valor
## intermedio la rompe, así que no hay tamaños entre estos dos.
const FONT_SIZE_BODY := 11   ## Altura de celda nativa, 1x.
const FONT_SIZE_TITLE := 22  ## 2x: nombre del monstruo y cifras de daño.
const LINE_HEIGHT := 12


# --- Movimiento --------------------------------------------------------------
# Techo de 300 ms: el jugador verá esta pantalla cientos de veces. Solo se
# animan position, scale y modulate.

const DUR_CURSOR := 0.09         ## Salto del cursor entre opciones.
const DUR_MENU_IN := 0.16        ## Entrada del menú de acción.
const DUR_BAR := 0.22            ## Barra de PV hacia su nuevo valor.
const DUR_SHAKE := 0.12          ## Sacudida al recibir daño.
const DUR_DAMAGE_NUMBER := 0.26  ## La cifra sube y se desvanece.
const DUR_PURIFY := 0.30         ## El momento que carga el mensaje del juego.

## El menú entra desde 0.94, no desde cero: arrancar en scale(0) se lee como un
## fallo de dibujo, no como una entrada.
const MENU_IN_SCALE := 0.94

const EASE_OUT_TRANS := Tween.TRANS_CUBIC
const EASE_OUT_EASE := Tween.EASE_OUT


## Ajuste de movimiento reducido. Godot no recibe `prefers-reduced-motion` del
## sistema operativo, así que se expone como ajuste del proyecto y la interfaz
## lo consulta antes de animar.
static var reduced_motion: bool = false

## Ruta del ajuste en `project.godot`. Se puede cambiar desde el editor, desde
## la línea de órdenes o desde una futura pantalla de opciones, sin tocar código.
const REDUCED_MOTION_SETTING := "game/accessibility/reduced_motion"


## Lee los ajustes de accesibilidad. La llama la pantalla al arrancar.
static func load_settings() -> void:
	if ProjectSettings.has_setting(REDUCED_MOTION_SETTING):
		reduced_motion = bool(ProjectSettings.get_setting(REDUCED_MOTION_SETTING))


## Duración efectiva de una transición. Con movimiento reducido, todo salta al
## estado final en lugar de recorrerlo.
static func duration(seconds: float) -> float:
	return 0.0 if reduced_motion else seconds


# ---------------------------------------------------------------------------
# Mundo — contrato «Vereda», bloqueado el 2026-09-14 en
# docs/ux/anexos/2026-09-14-exploracion-top-down.md
#
# Enmienda 1 de aquel contrato, autorizada por el usuario: la paleta de
# «Ceniza y Brasa» tiene ocho grises de un mismo violeta apagado, y en vista
# cenital suelo, agua y follaje colapsan en una sola masa. Se añaden tres
# rampas de material con techo de saturación 0,22 en HSV, muy por debajo de
# brasa (0,80) y de vital (0,70): el mundo sigue apagado y la regla del acento
# único no se toca.
#
# Los nueve valores no se eligieron a ojo. Salen de una búsqueda que exige, a
# la vez: saturación <= 0,22; el verde de purificación y la brasa legibles
# sobre cualquier terreno (3:1, mínimo gráfico de WCAG 1.4.11); separación
# perceptual dentro de una misma rampa >= 7 de dE, que es sombreado del mismo
# material; y separación contra los grises que tocan el terreno.
#
# Lo que NO se consiguió, y se dice: la separación entre materiales distintos
# queda en dE 9,2, no en los 12 que me había fijado como margen. Nueve tonos no
# caben con esa holgura en un rango de valor tan estrecho, y al forzar que el
# verde se lea sobre el follaje hubo que oscurecerlo, lo que apretó todavía
# más. dE 9,2 sigue siendo unas cuatro veces el mínimo perceptible y basta para
# áreas planas contiguas, pero el color no puede cargar solo con distinguir
# materiales: el contorno y la silueta del contrato tienen que acompañar.
# ---------------------------------------------------------------------------

## Suelo. Matiz 24°, el extremo cálido de la tierra removida.
const SOIL_700 := Color("#403732")  ## Tierra en sombra.
const SOIL_500 := Color("#594d46")  ## Tierra, tono base.
const SOIL_300 := Color("#73645a")  ## Camino pisado y borde iluminado.

## Agua. Matiz 196°, frío. Es la rampa más oscura de las tres: el agua de
## Solmira está enferma y no refleja cielo.
const WATER_700 := Color("#1e2426")  ## Fondo y agua profunda.
const WATER_500 := Color("#364145")  ## Agua, tono base.
const WATER_300 := Color("#4e5e63")  ## Orilla y reflejo.

## Follaje sin purificar. Matiz 68°, oliva sucio. No es verde: el verde de este
## juego tiene un solo significado y no se gasta en decorado.
const FLORA_700 := Color("#434536")  ## Follaje en sombra.
const FLORA_500 := Color("#575946")  ## Follaje, tono base.
const FLORA_300 := Color("#6a6e56")  ## Hoja iluminada.

## Techo de saturación de todo token de mundo que se añada en el futuro.
## Superarlo rompe la regla del acento único, porque empieza a competir con la
## brasa y con el verde.
const WORLD_SATURATION_CEILING := 0.22


# --- Lenguaje del entorno --------------------------------------------------
# Se declara una vez y no se contradice. Lo que responde lleva contorno sólido
# y es más claro que su fondo; el decorado no lleva contorno y es más oscuro.

const WORLD_OUTLINE_INTERACTIVE := ASH_050  ## Contorno de lo que responde.
const WORLD_PURIFIED := VITAL_500           ## Follaje y agua ya purificados.
const WORLD_PURIFIED_SHADOW := VITAL_700    ## Su sombra de 1 px.


# --- Rejilla ---------------------------------------------------------------

const TILE_SIZE := 16

## El mapa es mayor que el viewport, así que los tiles cortados en el borde de
## la pantalla son el comportamiento normal del scroll, no un defecto.


# --- Cámara ----------------------------------------------------------------
# Zona muerta medida, no estimada: sale del devlog de *Odd Verdure*, que la
# amplió de 28 px a 48 px de alto entre la jam y la publicación.

const CAMERA_DEADZONE_WIDTH := 28
const CAMERA_DEADZONE_HEIGHT := 48

## El personaje va sesgado hacia el borde inferior de la zona muerta: en vista
## cenital importa más ver hacia dónde se va que de dónde se viene.
const CAMERA_BIAS_DOWN := 12

## Anticipación en la dirección del avance, tope del devlog citado.
const CAMERA_LOOKAHEAD := 30


# --- Velocidades -----------------------------------------------------------
# No son números de gusto: son la razón por la que la cámara puede redondearse
# a píxel entero sin tirones. A 60 Hz dan un número entero de píxeles por
# cuadro, así que no hay fracción que redondear. Cualquier velocidad nueva debe
# ser múltiplo de 60 px/s o rompe el trato.

const WALK_SPEED := 60.0   ## 1 píxel por cuadro.
const RUN_SPEED := 120.0   ## 2 píxeles por cuadro.

## Caminar NO se anima. Es la acción de teclado más repetida del juego, y
## amortiguarla la vuelve lenta. El techo de 300 ms del contrato de batalla es
## para eventos —purificar, entrar en combate, abrir un diálogo—, no un permiso
## para suavizar movimiento continuo.


# --- Duraciones del mundo --------------------------------------------------

const DUR_PLACE_LABEL := 0.16  ## Rótulo del lugar: entra y se va.
const DUR_ZONE_FADE := 0.12    ## Medio fundido. Cruzar una zona son dos.

## La ola de purificación de zona. Enmienda 3, autorizada el 2026-09-23: pasa
## de 300 a 900 ms porque ocurre siete veces en toda la partida, no cientos.
## El verde avanza desde el lugar del combate en un tramado ordenado de 4x4, y
## cada píxel es enfermo o purificado, nunca una mezcla: no hay tokens nuevos.
## El tramado es exclusivo de este momento; no se usa en ninguna otra parte.
const DUR_ZONE_PURIFY := 0.90
const PURIFY_DITHER_STEPS := 8

## Matriz de Bayer 4x4. Un píxel pasa a purificado en el paso
## floor(umbral / 2) de los ocho, contado desde que el frente de la ola lo toca.
const BAYER_4X4 := [
	[0, 8, 2, 10],
	[12, 4, 14, 6],
	[3, 11, 1, 9],
	[15, 7, 13, 5],
]

## Diagonal. Enmienda 4, autorizada el 2026-09-23: la velocidad se cumple POR
## EJE. En diagonal se avanzan WALK_SPEED en X y WALK_SPEED en Y, sin
## normalizar: normalizar daría 0,707 px por cuadro, fracciones de píxel que la
## cámara a entero convierte en tirones.
const DIAGONAL_NORMALIZED := false
