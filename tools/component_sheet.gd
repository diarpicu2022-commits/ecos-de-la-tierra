extends Node2D

## Banco de pruebas del paso 2: MonsterView en sus estados.
## No forma parte del juego.
##   godot --path . res://tools/component_sheet.tscn

const SHOT_PATH := "user://component_sheet.png"

## (titulo, PV restantes, purificado)
const CASES := [
	["Intacto, causa activa", 180, false],
	["Purificado", 180, true],
	["Herido", 78, false],
	["Critico", 21, false],
]

var _font: Font = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	var column := 0
	for case in CASES:
		var monster := DeforestationFlame.new()
		add_child(monster)
		monster.hp = case[1]
		monster.is_purified = case[2]

		var view := MonsterView.new()
		view.position = Vector2(
			8 + (column % 2) * 184,
			14 + int(column / 2) * 120
		)
		add_child(view)
		view.bind(monster)
		column += 1

	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(SHOT_PATH)
	print("Captura: ", ProjectSettings.globalize_path(SHOT_PATH))
	get_tree().quit()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(480, 270)), DesignTokens.ASH_950)
	var column := 0
	for case in CASES:
		var origin := Vector2(8 + (column % 2) * 184, 14 + int(column / 2) * 120)
		draw_string(_font, origin + Vector2(0, -3), case[0],
				HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
				DesignTokens.TEXT_SECONDARY)
		column += 1
