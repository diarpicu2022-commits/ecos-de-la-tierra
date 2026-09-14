extends Node2D

## Muestrario de los tokens del contrato «Ceniza y Brasa», dibujado dentro de
## Godot para comprobar la cadena completa: fuente de mapa de bits, paleta y
## escalado entero. No forma parte del juego; es la prueba del paso 1.
##
##   godot --path . res://tools/token_sheet.tscn

const SHOT_PATH := "user://token_sheet.png"

var _font: Font = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var image: Image = get_viewport().get_texture().get_image()
	image.save_png(SHOT_PATH)
	print("Captura: ", ProjectSettings.globalize_path(SHOT_PATH))
	get_tree().quit()


func _draw() -> void:
	var size := Vector2(480, 270)
	draw_rect(Rect2(Vector2.ZERO, size), DesignTokens.ASH_950)
	draw_rect(Rect2(Vector2(8, 8), size - Vector2(16, 16)), DesignTokens.ASH_800)

	_text("CENIZA Y BRASA", Vector2(16, 24), DesignTokens.TEXT_PRIMARY,
			DesignTokens.FONT_SIZE_TITLE)
	_text("Tokens del contrato bloqueado el 2026-09-13", Vector2(16, 38),
			DesignTokens.TEXT_SECONDARY)

	# Rampa de ceniza: la estructura del mundo apagado.
	_text("CENIZA", Vector2(16, 60), DesignTokens.TEXT_SECONDARY)
	var ash: Array[Color] = [
		DesignTokens.ASH_950, DesignTokens.ASH_900, DesignTokens.ASH_800,
		DesignTokens.ASH_700, DesignTokens.ASH_600, DesignTokens.ASH_400,
		DesignTokens.ASH_200, DesignTokens.ASH_050,
	]
	_swatches(ash, Vector2(16, 66))

	# Rampa de brasa: el dano y la causa activa.
	_text("BRASA", Vector2(16, 96), DesignTokens.TEXT_SECONDARY)
	_swatches([DesignTokens.EMBER_500, DesignTokens.EMBER_400,
			DesignTokens.EMBER_300], Vector2(16, 102))

	# Acento unico.
	_text("ACENTO: PURIFICACION", Vector2(140, 96), DesignTokens.TEXT_SECONDARY)
	_swatches([DesignTokens.VITAL_500, DesignTokens.VITAL_700], Vector2(140, 102))

	# Papeles de texto, cada uno con su contraste medido.
	_text("TEXTO Y CONTRASTE MEDIDO SOBRE ASH_800", Vector2(16, 136),
			DesignTokens.TEXT_SECONDARY)
	_text("Texto primario y cifras           11,4:1  AAA", Vector2(16, 150),
			DesignTokens.TEXT_PRIMARY)
	_text("Texto secundario                   4,9:1  AA", Vector2(16, 162),
			DesignTokens.TEXT_SECONDARY)
	_text("✖ Aviso: sin purificar              5,7:1  AA", Vector2(16, 174),
			DesignTokens.TEXT_WARNING)
	_text("Cifra critica y foco               8,8:1  AAA", Vector2(16, 186),
			DesignTokens.TEXT_CRITICAL)
	_text("✓ Purificado: la causa se atajo     8,2:1  AAA", Vector2(16, 198),
			DesignTokens.TEXT_PURIFIED)

	# La vida se drena hacia la brasa, nunca hacia el verde.
	_text("LA VIDA SE DRENA HACIA LA BRASA, NO AL VERDE", Vector2(16, 220),
			DesignTokens.TEXT_SECONDARY)
	_bar(Vector2(16, 232), 1.00, DesignTokens.ASH_050, "110/110")
	_bar(Vector2(16, 244), 0.48, DesignTokens.EMBER_400, "53/110")
	_bar(Vector2(16, 256), 0.14, DesignTokens.EMBER_500, "15/110")

	# Escala de espaciado, en multiplos de 4.
	_text("ESPACIADO", Vector2(288, 220), DesignTokens.TEXT_SECONDARY)
	var x: float = 288.0
	for step in [2, 4, 8, 12, 16, 24, 32]:
		draw_rect(Rect2(Vector2(x, 232), Vector2(step, 8)),
				DesignTokens.EMBER_300)
		x += step + 4


## Una fila de muestras de color con borde de 1 px y radio 0.
func _swatches(colors: Array, origin: Vector2) -> void:
	var x: float = origin.x
	for color in colors:
		draw_rect(Rect2(Vector2(x, origin.y), Vector2(24, 20)), color)
		draw_rect(Rect2(Vector2(x, origin.y), Vector2(24, 20)),
				DesignTokens.BORDER_IDLE, false, DesignTokens.BORDER_WIDTH)
		x += 26


## Barra de PV: canal en ASH_700, relleno segun lo herido que esté el personaje.
func _bar(origin: Vector2, ratio: float, fill: Color, label: String) -> void:
	var track := Vector2(120, 8)
	draw_rect(Rect2(origin, track), DesignTokens.BAR_TRACK)
	draw_rect(Rect2(origin, Vector2(track.x * ratio, track.y)), fill)
	draw_rect(Rect2(origin, track), DesignTokens.BORDER_IDLE, false,
			DesignTokens.BORDER_WIDTH)
	_text(label, origin + Vector2(128, 8), DesignTokens.TEXT_PRIMARY)


func _text(text: String, position: Vector2, color: Color,
		size: int = DesignTokens.FONT_SIZE_BODY) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
