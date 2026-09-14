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


# --- Acento único: la purificación ------------------------------------------

## Reservado a la purificación y a nada más. El verde tiene un solo significado
## en todo el juego: «la causa se atajó». Las barras de vida NO son verdes.
const VITAL_500 := Color("#4ade80")  ## 8,2:1 sobre ASH_800.
const VITAL_700 := Color("#2b9d5a")  ## Sombra del verde, 1 px.


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
