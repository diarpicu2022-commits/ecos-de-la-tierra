extends Node2D

## Capturas de Valdehoja en el motor (contrato «Rastro», Valdehoja, paso 3), a
## 480x270, el medio real del juego. Cada estado se fuerza con las banderas de
## GameState; no se espera a que salga jugando (guía §1.5).
##
##   casa       la aparición, al empezar la partida.
##   jardin     delante del jardín de Yara, el primer verde.
##   era        la era con la Costa purificada.
##   todo       la era con las cinco regiones purificadas.
##
## Necesita ventana: en un servidor sin pantalla,
##   xvfb-run -a godot --path . res://tools/valdehoja_capture.tscn
## Después: python tools/verify_palette.py image <captura> --world

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"
const REGIONS := ["ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak"]

var _world := WorldRoot.new()
var _state: Node = null


func _ready() -> void:
	_state = get_node("/root/GameState")
	_state.flags.clear()
	_world.start_zone = "valdehoja"
	_world.start_cell = Vector2i(9, 25)
	add_child(_world)
	await get_tree().physics_frame
	DesignTokens.reduced_motion = true
	_world.body.input_enabled = false
	await _capture("casa", Vector2i(9, 25))
	await _capture("jardin", Vector2i(29, 12))
	_state.set_zone_purified("broken_coast")
	await _capture("era", Vector2i(30, 21))
	for region in REGIONS:
		_state.set_zone_purified(region)
	await _capture("todo", Vector2i(30, 21))
	_state.flags.clear()
	get_tree().quit()


func _capture(tag: String, cell: Vector2i) -> void:
	_world.enter_zone("valdehoja", cell)
	_world.label.visible = false
	for _i in 4:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-valdehoja-motor-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s" % path.get_file())
