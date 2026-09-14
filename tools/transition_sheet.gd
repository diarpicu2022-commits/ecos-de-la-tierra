extends Node2D

## Prueba de movimiento del paso 2: captura la transición de purificación
## cuadro a cuadro para comprobar que dura lo que dice el contrato (300 ms) y
## que el fundido entre los dos sprites ocurre de verdad.
##   godot --path . res://tools/transition_sheet.tscn

const FRAMES := 6
const STEP_SECONDS := 0.06

var _font: Font = null
var _view: MonsterView = null
var _monster: Monster = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	_monster = DeforestationFlame.new()
	add_child(_monster)
	_monster.hp = 96

	_view = MonsterView.new()
	_view.position = Vector2(152, 40)
	add_child(_view)
	_view.bind(_monster)

	await RenderingServer.frame_post_draw
	_shoot(0, 0.0)

	# La Línea Cortafuegos ataja la causa: misma llamada que hace el combate.
	_monster.receive_eco_skill(SkillLibrary.firebreak_line())

	var elapsed := 0.0
	for i in range(1, FRAMES):
		await get_tree().create_timer(STEP_SECONDS).timeout
		await RenderingServer.frame_post_draw
		elapsed += STEP_SECONDS
		_shoot(i, elapsed)

	print("Transicion capturada en %d cuadros." % FRAMES)
	get_tree().quit()


func _shoot(index: int, elapsed: float) -> void:
	var image := get_viewport().get_texture().get_image()
	image.save_png("user://transition_%d.png" % index)
	print("  cuadro %d  t=%3d ms" % [index, int(elapsed * 1000.0)])


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(480, 270)), DesignTokens.ASH_950)
