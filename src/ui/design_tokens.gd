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


# --- Enmienda 6 (2026-10-28): lo construido y el color que vuelve -----------
## Autorizada por Diego al revisar Valdehoja: «Rica + color al purificar».
## Madera y tejado: cinco tonos, bajo WORLD_SATURATION_CEILING. La piedra usa
## la rampa ASH. Agua viva (AQUA), flores (BLOOM) y VITAL_300 superan el techo
## a propósito y solo existen en celdas purificadas: el color de GBA vuelve con
## la purificación, igual que el verde.
const WOOD_900 := Color("#2b2622")  ## Madera en sombra.
const WOOD_700 := Color("#453d36")  ## Madera, sombra media.
const WOOD_500 := Color("#61564d")  ## Madera, tono base.
const WOOD_300 := Color("#827367")  ## Madera iluminada.
const WOOD_100 := Color("#a69383")  ## Veta clara y canto.
const ROOF_900 := Color("#332a28")  ## Tejado en sombra.
const ROOF_700 := Color("#4c403c")  ## Tejado, sombra media.
const ROOF_500 := Color("#6b5955")  ## Tejado, tono base.
const ROOF_300 := Color("#8c756f")  ## Teja iluminada.
const ROOF_100 := Color("#ad9089")  ## Brillo del tejado.
const AQUA_900 := Color("#12485c")  ## Agua viva profunda.
const AQUA_700 := Color("#2b748f")  ## Agua viva, sombra.
const AQUA_500 := Color("#51a8c2")  ## Agua viva, tono base.
const AQUA_300 := Color("#85d5e6")  ## Agua viva, reflejo.
const AQUA_100 := Color("#d2f7fa")  ## Destello del agua.
const BLOOM_900 := Color("#7a315c")  ## Flor, sombra.
const BLOOM_700 := Color("#bd5b88")  ## Flor, pétalo oscuro.
const BLOOM_500 := Color("#f285a6")  ## Flor rosa.
const BLOOM_300 := Color("#c68ee6")  ## Flor lila.
const BLOOM_100 := Color("#aacffa")  ## Flor celeste.
const VITAL_300 := Color("#91f2b2")  ## Hoja al sol. Solo purificado.
## Hierba del prado purificado, más amarilla que el acento: un prado entero de
## VITAL_500 se leía como neón. Solo purificado.
const VITAL_600 := Color("#54b250")  ## Prado, tono base.
const VITAL_400 := Color("#86d66b")  ## Prado, brizna al sol.


# --- TIERRA VIVA: BEGIN (enmienda 13, contrato «Piel nueva», 2026-10-30) ---
## Generado por tools/gen_tierra_viva_tokens.py: no se edita a mano.
## Rampas del mundo de Tierra Viva, de la sombra (0) a la luz. El techo
## de saturación no se aplica a estas rampas: su significado lo fijan
## TV_PURIFIED_ONLY y TV_SICK_ONLY, medidos con verify_palette.py tv-state.
## Tinta: contorno del decorado más oscuro.
const TV_INK_0 := Color("#14101c")
const TV_INK_1 := Color("#231c2e")
const TV_INK_2 := Color("#372b42")
## Piedra: cotas, muros, rocas.
const TV_STONE_0 := Color("#2a2434")
const TV_STONE_1 := Color("#40384d")
const TV_STONE_2 := Color("#5c5268")
const TV_STONE_3 := Color("#7d7387")
const TV_STONE_4 := Color("#a198a8")
const TV_STONE_5 := Color("#c9c1cc")
const TV_STONE_6 := Color("#ece6ec")
## Hierba viva.
const TV_GRASS_0 := Color("#123a2e")
const TV_GRASS_1 := Color("#1a5234")
const TV_GRASS_2 := Color("#256e3a")
const TV_GRASS_3 := Color("#358c3e")
const TV_GRASS_4 := Color("#4fa645")
const TV_GRASS_5 := Color("#7cc456")
const TV_GRASS_6 := Color("#b5e073")
## Copa y arbusto vivos.
const TV_LEAF_0 := Color("#0f2b26")
const TV_LEAF_1 := Color("#174232")
const TV_LEAF_2 := Color("#215c38")
const TV_LEAF_3 := Color("#2f7a3c")
const TV_LEAF_4 := Color("#48983f")
const TV_LEAF_5 := Color("#74b84a")
const TV_LEAF_6 := Color("#aad65e")
## Tierra y camino.
const TV_DIRT_0 := Color("#3b2226")
const TV_DIRT_1 := Color("#5a332c")
const TV_DIRT_2 := Color("#7d4b35")
const TV_DIRT_3 := Color("#a06741")
const TV_DIRT_4 := Color("#c48a52")
const TV_DIRT_5 := Color("#e0b070")
const TV_DIRT_6 := Color("#f4d699")
## Arena limpia.
const TV_SAND_0 := Color("#8a6a4a")
const TV_SAND_1 := Color("#b08d5e")
const TV_SAND_2 := Color("#d1b077")
const TV_SAND_3 := Color("#e8cf98")
const TV_SAND_4 := Color("#f7ebc4")
## Agua viva.
const TV_WATER_0 := Color("#16244f")
const TV_WATER_1 := Color("#1b3c7a")
const TV_WATER_2 := Color("#2360a8")
const TV_WATER_3 := Color("#3489cc")
const TV_WATER_4 := Color("#56b3e6")
const TV_WATER_5 := Color("#92d9f4")
const TV_WATER_6 := Color("#dff7ff")
## Madera.
const TV_WOOD_0 := Color("#2e1a1e")
const TV_WOOD_1 := Color("#4a2a26")
const TV_WOOD_2 := Color("#6b3f2e")
const TV_WOOD_3 := Color("#8f5a3a")
const TV_WOOD_4 := Color("#b27a4c")
const TV_WOOD_5 := Color("#d1a068")
## Teja roja.
const TV_ROOF_RED_0 := Color("#3a1426")
const TV_ROOF_RED_1 := Color("#5e1f30")
const TV_ROOF_RED_2 := Color("#8c2c3a")
const TV_ROOF_RED_3 := Color("#b8443f")
const TV_ROOF_RED_4 := Color("#dc6a4c")
const TV_ROOF_RED_5 := Color("#f29c6e")
## Teja azul.
const TV_ROOF_BLUE_0 := Color("#1a1d40")
const TV_ROOF_BLUE_1 := Color("#253366")
const TV_ROOF_BLUE_2 := Color("#2f4f94")
const TV_ROOF_BLUE_3 := Color("#3f75be")
const TV_ROOF_BLUE_4 := Color("#62a2dc")
const TV_ROOF_BLUE_5 := Color("#9ccdf0")
## Muro encalado.
const TV_WALL_0 := Color("#6b5a66")
const TV_WALL_1 := Color("#8f7d82")
const TV_WALL_2 := Color("#b5a598")
const TV_WALL_3 := Color("#d8cbb4")
const TV_WALL_4 := Color("#f2e8d2")
## Flores (tonos sueltos, no rampa).
const TV_FLOWER_0 := Color("#b0304f")
const TV_FLOWER_1 := Color("#e8566b")
const TV_FLOWER_2 := Color("#ff8fa3")
const TV_FLOWER_3 := Color("#ffd34e")
const TV_FLOWER_4 := Color("#fff3b0")
const TV_FLOWER_5 := Color("#8a6bd9")
const TV_FLOWER_6 := Color("#c3a8ff")
const TV_FLOWER_7 := Color("#ffffff")
## Hierba seca.
const TV_DRY_GRASS_0 := Color("#2a1f2a")
const TV_DRY_GRASS_1 := Color("#3d2e2e")
const TV_DRY_GRASS_2 := Color("#56432f")
const TV_DRY_GRASS_3 := Color("#735c37")
const TV_DRY_GRASS_4 := Color("#94783f")
const TV_DRY_GRASS_5 := Color("#b39a52")
const TV_DRY_GRASS_6 := Color("#cfbd70")
## Hoja muerta.
const TV_DEAD_LEAF_0 := Color("#1e1622")
const TV_DEAD_LEAF_1 := Color("#2f2229")
const TV_DEAD_LEAF_2 := Color("#46332e")
const TV_DEAD_LEAF_3 := Color("#61483a")
const TV_DEAD_LEAF_4 := Color("#7f6146")
const TV_DEAD_LEAF_5 := Color("#9c7d55")
## Ceniza del mundo y arena enferma.
const TV_ASH_0 := Color("#221d29")
const TV_ASH_1 := Color("#342d3b")
const TV_ASH_2 := Color("#4a4252")
const TV_ASH_3 := Color("#645c6b")
const TV_ASH_4 := Color("#827a88")
const TV_ASH_5 := Color("#a39ca6")
const TV_ASH_6 := Color("#c7c1c6")
## Crudo.
const TV_OIL_0 := Color("#0b0812")
const TV_OIL_1 := Color("#15111f")
const TV_OIL_2 := Color("#221b30")
const TV_OIL_3 := Color("#302744")
const TV_OIL_4 := Color("#433757")
## Irisado del crudo.
const TV_SHEEN_0 := Color("#5a3f8c")
const TV_SHEEN_1 := Color("#3f7f86")
const TV_SHEEN_2 := Color("#a3963f")
const TV_SHEEN_3 := Color("#c0577a")
## Lodo tóxico.
const TV_SLUDGE_0 := Color("#2f3a12")
const TV_SLUDGE_1 := Color("#4f6418")
const TV_SLUDGE_2 := Color("#77921f")
const TV_SLUDGE_3 := Color("#a4c42c")
const TV_SLUDGE_4 := Color("#d2ef5a")
## Humo y neblina.
const TV_SMOG_0 := Color("#4b3f4a")
const TV_SMOG_1 := Color("#6e5d62")
const TV_SMOG_2 := Color("#93807a")
const TV_SMOG_3 := Color("#b8a594")
## Óxido y metal.
const TV_RUST_0 := Color("#3a1a16")
const TV_RUST_1 := Color("#5e2a1e")
const TV_RUST_2 := Color("#8a4126")
const TV_RUST_3 := Color("#b5602f")
const TV_RUST_4 := Color("#d68a45")
## Plástico (tonos sueltos).
const TV_PLASTIC_0 := Color("#2a4f6e")
const TV_PLASTIC_1 := Color("#3f7fa8")
const TV_PLASTIC_2 := Color("#7cc0e0")
const TV_PLASTIC_3 := Color("#c9ecf7")
const TV_PLASTIC_4 := Color("#e25a6a")
const TV_PLASTIC_5 := Color("#f2c94c")
const TV_PLASTIC_6 := Color("#ffffff")
## Fuego de antorcha.
const TV_FIRE_0 := Color("#3d0f14")
const TV_FIRE_1 := Color("#7a1a16")
const TV_FIRE_2 := Color("#c13a1c")
const TV_FIRE_3 := Color("#ec6a24")
const TV_FIRE_4 := Color("#ffa83a")
const TV_FIRE_5 := Color("#ffe07a")
const TV_FIRE_6 := Color("#fffbe0")
## Hielo.
const TV_ICE_0 := Color("#1d2c52")
const TV_ICE_1 := Color("#2c4c80")
const TV_ICE_2 := Color("#4a7fb4")
const TV_ICE_3 := Color("#7ab6df")
const TV_ICE_4 := Color("#b0e0f4")
const TV_ICE_5 := Color("#e4f8ff")
## Oro y paja.
const TV_GOLD_0 := Color("#3a2412")
const TV_GOLD_1 := Color("#6b4316")
const TV_GOLD_2 := Color("#a6701c")
const TV_GOLD_3 := Color("#d9a52a")
const TV_GOLD_4 := Color("#f5d24a")
const TV_GOLD_5 := Color("#fff1a0")
## Turquesa de detalle.
const TV_ECO_0 := Color("#0f3b3f")
const TV_ECO_1 := Color("#14706a")
const TV_ECO_2 := Color("#20a88f")
const TV_ECO_3 := Color("#4fd8b0")
const TV_ECO_4 := Color("#9cf5d4")
const TV_ECO_5 := Color("#e2fff3")
## Agua turbia.
const TV_TURBID_0 := Color("#1f2a2c")
const TV_TURBID_1 := Color("#2c3a3a")
const TV_TURBID_2 := Color("#3b4a48")
const TV_TURBID_3 := Color("#4b5a55")
const TV_TURBID_4 := Color("#5f6d66")
const TV_TURBID_5 := Color("#7d877c")
const TV_TURBID_6 := Color("#a3a898")
## Ciénaga de crudo.
const TV_OIL_WATER_0 := Color("#07050c")
const TV_OIL_WATER_1 := Color("#110c1a")
const TV_OIL_WATER_2 := Color("#1b1428")
const TV_OIL_WATER_3 := Color("#261d36")
const TV_OIL_WATER_4 := Color("#3a2c4c")
const TV_OIL_WATER_5 := Color("#5a3f8c")
const TV_OIL_WATER_6 := Color("#3f7f86")
## Mar con plástico.
const TV_PLASTIC_WATER_0 := Color("#1d2a33")
const TV_PLASTIC_WATER_1 := Color("#2a3b45")
const TV_PLASTIC_WATER_2 := Color("#3a4d57")
const TV_PLASTIC_WATER_3 := Color("#4b5f68")
const TV_PLASTIC_WATER_4 := Color("#61757b")
const TV_PLASTIC_WATER_5 := Color("#839393")
const TV_PLASTIC_WATER_6 := Color("#b5bfbb")
## Pasto manchado de crudo.
const TV_SLUDGE_GRASS_0 := Color("#1f1d14")
const TV_SLUDGE_GRASS_1 := Color("#2b2a19")
const TV_SLUDGE_GRASS_2 := Color("#3a3820")
const TV_SLUDGE_GRASS_3 := Color("#4b4826")
const TV_SLUDGE_GRASS_4 := Color("#5d592d")
const TV_SLUDGE_GRASS_5 := Color("#77713a")
const TV_SLUDGE_GRASS_6 := Color("#938b4c")
## Arena gris de la costa enferma.
const TV_GREY_SAND_0 := Color("#7d7466")
const TV_GREY_SAND_1 := Color("#988e7d")
const TV_GREY_SAND_2 := Color("#b0a690")
const TV_GREY_SAND_3 := Color("#c4baa2")
const TV_GREY_SAND_4 := Color("#d6cdb6")
## Pajonal de páramo vivo.
const TV_PARAMO_0 := Color("#1c2f2a")
const TV_PARAMO_1 := Color("#2a4434")
const TV_PARAMO_2 := Color("#3d5c3a")
const TV_PARAMO_3 := Color("#587a42")
const TV_PARAMO_4 := Color("#7a954c")
const TV_PARAMO_5 := Color("#a3b45e")
const TV_PARAMO_6 := Color("#cdd17c")
## Nieve del glaciar.
const TV_SNOW_0 := Color("#7d8fb8")
const TV_SNOW_1 := Color("#a9bbd9")
const TV_SNOW_2 := Color("#cfdcef")
const TV_SNOW_3 := Color("#e9f1fa")
const TV_SNOW_4 := Color("#ffffff")
## Páramo seco.
const TV_PARAMO_DRY_0 := Color("#2a2226")
const TV_PARAMO_DRY_1 := Color("#3d302c")
const TV_PARAMO_DRY_2 := Color("#56432f")
const TV_PARAMO_DRY_3 := Color("#6e5838")
const TV_PARAMO_DRY_4 := Color("#8a7044")
const TV_PARAMO_DRY_5 := Color("#a58a55")
const TV_PARAMO_DRY_6 := Color("#bea56a")
## Pedregal del glaciar derretido.
const TV_SCREE_0 := Color("#3e3943")
const TV_SCREE_1 := Color("#57505a")
const TV_SCREE_2 := Color("#726a72")
const TV_SCREE_3 := Color("#8f878c")
const TV_SCREE_4 := Color("#aca4a6")
## Tierra enferma.
const TV_SICK_SOIL_0 := Color("#2a2226")
const TV_SICK_SOIL_1 := Color("#3d322f")
const TV_SICK_SOIL_2 := Color("#54463d")
const TV_SICK_SOIL_3 := Color("#6f5f50")
const TV_SICK_SOIL_4 := Color("#8c7a64")
const TV_SICK_SOIL_5 := Color("#a8957a")
const TV_SICK_SOIL_6 := Color("#c2b092")
## Roseta del frailejón.
const TV_FRAILEJON_0 := Color("#4d6a4a")
const TV_FRAILEJON_1 := Color("#7b9670")
const TV_FRAILEJON_2 := Color("#a7bc9a")
const TV_FRAILEJON_3 := Color("#cfdcc4")
const TV_FRAILEJON_4 := Color("#eef4e6")
## Puya.
const TV_PUYA_0 := Color("#2d4a3c")
const TV_PUYA_1 := Color("#466b4c")
const TV_PUYA_2 := Color("#6a8f62")
const TV_PUYA_3 := Color("#94b183")
const TV_PUYA_4 := Color("#c3d6ae")
## Paja de páramo.
const TV_STRAW_0 := Color("#56502e")
const TV_STRAW_1 := Color("#7d7238")
const TV_STRAW_2 := Color("#a6984a")
const TV_STRAW_3 := Color("#cdbd66")
const TV_STRAW_4 := Color("#e6d98a")
## Fuego maldito de la Cripta.
const TV_CURSE_FIRE_0 := Color("#2a1d3a")
const TV_CURSE_FIRE_1 := Color("#5a2d6b")
const TV_CURSE_FIRE_2 := Color("#8f4fb0")
const TV_CURSE_FIRE_3 := Color("#c98ae0")
const TV_CURSE_FIRE_4 := Color("#f2d1ff")
const TV_PURIFIED_ONLY := ["grass", "leaf", "flower", "water", "eco", "paramo", "snow", "frailejon", "puya"]
const TV_SICK_ONLY := ["dry_grass", "dead_leaf", "oil", "sheen", "sludge", "smog", "plastic", "turbid", "oil_water", "plastic_water", "sludge_grass", "grey_sand", "paramo_dry", "scree", "sick_soil", "curse_fire"]
# --- TIERRA VIVA: END ---


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


# --- Cuerpo y salidas ------------------------------------------------------
# Contrato «Umbral», bloqueado el 2026-09-30
# (docs/ux/anexos/2026-09-30-movimiento-y-zonas.md).

## Caja de colisión del personaje: 12 x 8 px, centrada en la base de su tile,
## en los pies. Un paso de un tile (16 px) siempre cabe con 2 px de margen a
## cada lado, y uno de cero tiles nunca: no hay huecos que caben a medias
## (la «zona muerta métrica» de Nic Phan).
const PLAYER_HITBOX := Vector2i(12, 8)

## Deslizamiento en esquina: si al chocar sobran 4 px o menos para librar la
## esquina, el personaje avanza 1 px lateral por cuadro hasta librarla y sigue
## recto. A 5 px o más, se para.
const CORNER_SLIP := 4

## Salidas: solo donde el camino pisado cruza el borde del mapa, y como mucho
## dos en cualquier pantalla de 640 px (contrato «Piel nueva», 2026-10-30).
const MAX_EXITS_PER_SCREEN := 2


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

## Ritmo de la anticipación. Enmienda 5, autorizada el 2026-09-30: se abre a
## 1 px por cuadro mientras se avanza por un eje y, al soltarlo, vuelve a neutro
## a 30 px/s, 1 px cada dos cuadros, la cifra del mismo devlog. Los dos ritmos
## se cuentan en píxeles enteros: la cámara nunca queda en subpíxel. Con
## movimiento reducido no hay anticipación, y la cámara es solo zona muerta.
const CAMERA_LOOKAHEAD_OPEN_SPEED := 60.0
const CAMERA_LOOKAHEAD_RETURN_SPEED := 30.0


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
## Tiempo que el rótulo del lugar se queda en pantalla antes de irse solo.
## Contrato «Umbral».
const PLACE_LABEL_HOLD := 2.0

## La ola de purificación de zona. Enmienda 3, autorizada el 2026-09-23: pasa
## de 300 a 900 ms porque ocurre siete veces en toda la partida, no cientos.
## El verde avanza desde el lugar del combate en un tramado ordenado de 4x4, y
## cada píxel es enfermo o purificado, nunca una mezcla: no hay tokens nuevos.
## El tramado es exclusivo de este momento; no se usa en ninguna otra parte.
const DUR_ZONE_PURIFY := 0.90
const PURIFY_DITHER_STEPS := 8

## Movimiento ambiental. Enmienda 8, autorizada el 2026-10-28: solo se mueve
## lo purificado (agua, plantas, fauna y animales), porque en este mundo estar
## vivo se lee como moverse. Lo enfermo queda quieto. Son ciclos lentos de dos
## cuadros, nunca tweens: el pixel art cambia de dibujo, no se interpola. Cada
## pieza arranca con una fase propia, para que un prado no se mezca a la vez
## (Kowalski: lo que se repite en todas partes pierde su efecto). Con
## movimiento reducido, todo queda en su primer cuadro y los animales quietos.
const DUR_AMBIENT_WATER := 0.50  ## Cada cuadro del brillo del agua viva.
const DUR_AMBIENT_SWAY := 0.70   ## Cada cuadro del vaivén de hierba y flores.
const DUR_FAUNA_FLAP := 0.15     ## Aleteo de pájaros y mariposas.
## Los animales andan a WALK_SPEED (1 px por cuadro, la regla de velocidades) a
## saltos cortos dentro de un radio de su sitio, con pausas largas entre uno y
## otro: picotean y miran más de lo que andan.
const ANIMAL_HOP_MAX := 12       ## Píxeles de un salto, como mucho.
const ANIMAL_RANGE := 24         ## Distancia máxima a su sitio, en píxeles.
const ANIMAL_PAUSE_MIN := 1.2
const ANIMAL_PAUSE_MAX := 3.0
## La fauna silvestre se mece en el sitio: sube y baja 1 px con el aleteo.
const FAUNA_BOB := 1

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


# --- Encuentros ------------------------------------------------------------
# Contrato «Persiana», bloqueado el 2026-10-28
# (docs/ux/anexos/2026-10-28-encuentros.md). Ningún color nuevo: la sombra de
# alerta y la persiana son ASH_950. El monstruo anda y persigue a WALK_SPEED,
# la regla de velocidades: quien corre (RUN_SPEED) siempre escapa.

## IA-1. A cuántos tiles ve el monstruo a Ilan, en el semiplano al que mira.
const MONSTER_SIGHT_TILES := 6
## Pausa en cada extremo de la ruta de patrulla.
const MONSTER_PATROL_PAUSE := 1.2
## La alerta: la sombra se estira hacia Ilan un tile por paso, hasta
## MONSTER_ALERT_STEPS. Cuando llega al último, empieza la persecución. Es la
## señal de que lo ha visto, y avanza en vez de aparecer (Shadow Tactics).
const DUR_MONSTER_ALERT_STEP := 0.12
const MONSTER_ALERT_STEPS := 4
## Sin ver a Ilan durante este tiempo, el monstruo se rinde y vuelve a su ruta.
const DUR_MONSTER_GIVE_UP := 2.0

## La persiana: franjas horizontales que cubren la pantalla al entrar en
## combate y la descubren al salir. Exclusiva de ese paso (repertorio §3.1).
## Usa el techo de 300 ms del contrato de batalla.
const DUR_BATTLE_BLINDS := 0.30
const BLIND_STRIP := 8           ## Alto de cada franja, en píxeles.
## Margen entre la primera franja (la de la fila del monstruo) y la más lejana.
## Se reparte por igual entre las franjas que haya, estén donde estén, y cada
## una se cierra en DUR_BATTLE_BLINDS - BLIND_SPREAD: la última termina justo a
## los 300 ms, con el monstruo en el centro o en el borde.
const BLIND_SPREAD := 0.10

## Fondo de batalla en tres capas: cuánto se desplaza cada capa, en píxeles,
## mientras se abre la persiana. Quieto con movimiento reducido.
const BATTLE_PARALLAX := 2

## Tras huir, tiempo sin contacto posible con el monstruo.
const DUR_FLEE_GRACE := 1.0


# --- Sintonía del grupo (IA-5) --------------------------------------------
# Contrato «Orden de líder», bloqueado el 2026-10-28. No son valores visuales,
# pero viven aquí por la misma regla: ningún número suelto en el código.

## Red de cada compañero: 12 entradas, 16 ocultas, 4 salidas.
const PARTY_INPUTS := 12
const PARTY_HIDDEN := 16
const PARTY_OUTPUTS := 4
## Paso de descenso por gradiente.
const PARTY_LEARNING_RATE := 0.15
## Pasos por cada decisión de Ilan. Enmienda 2 (2026-10-28): aprenden tres
## veces más rápido para que el líder pese en el mismo combate. Tres pasos de
## 0,15 y no uno de 0,45: con 0,45 el descenso se desestabiliza (el acierto del
## estilo sintético cayó del 88 % al 53 %).
const PARTY_STEPS_PER_DECISION := 3
## Decisiones con las que la red debe haber aprendido un estilo (> 80 %).
const PARTY_LEARN_DECISIONS := 200
## Cuánto empuja la orden de grupo la salida que favorece (en logits).
const ORDER_BIAS := 2.0
## Sintonía: empieza en el medio, sube más deprisa de lo que baja.
const SYNC_START := 0.5
const SYNC_UP := 0.25
const SYNC_DOWN := 0.15
## Decisiones buenas seguidas que bastan para salir del mínimo al tramo medio.
const SYNC_RECOVER := 3
## Rondas seguidas con la contramedida para atajar la causa de un monstruo
## regional (Diego, 2026-10-28: «sostener la contramedida»).
const COUNTER_SUSTAIN_ROUNDS := 2
