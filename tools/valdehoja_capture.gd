extends Node2D

## Capturas de Valdehoja en el motor (contrato «Rastro», Valdehoja, paso 3), a
## 480x270, el medio real del juego. Cada estado se fuerza con las banderas de
## GameState; no se espera a que salga jugando (guía §1.5).
##
##   casa       la aparición, al empezar la partida.
##   jardin     delante del jardín de Yara, el primer verde.
##   bosque, cuenca, costa, llanura, cumbre
##              cada región devuelve su parte del pueblo, sola: arboleda,
##              río, era, terrazas y acequia (paso 4, estados).
##   era        alias histórico de «costa» (paso 3).
##   todo       la era con las cinco regiones purificadas.
##
## Además, 60 cuadros del movimiento de la enmienda 8 sobre la era con todo
## purificado, uno cada 3 cuadros de física (50 ms), en `user://ambiente/`,
## fuera del repositorio. `python tools/frames_to_gif.py` monta con ellos el
## GIF, que sí se guarda en `docs/ux/capturas/`, a 50 ms: velocidad real.
##
## Necesita ventana: en un servidor sin pantalla,
##   xvfb-run -a godot --path . res://tools/valdehoja_capture.tscn
## Después: python tools/verify_palette.py image <captura> --world

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"
const REGIONS := ["ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak"]

var _world := WorldRoot.new()
var _state: Node = null


const PARTS := {
	"bosque": ["ashen_forest", Vector2i(39, 26)],
	"cuenca": ["tar_basin", Vector2i(44, 9)],
	"costa": ["broken_coast", Vector2i(30, 21)],
	"llanura": ["withered_plain", Vector2i(11, 8)],
	"cumbre": ["waning_peak", Vector2i(14, 14)],
}


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
	for tag in PARTS:
		_state.flags.clear()
		_state.set_zone_purified(PARTS[tag][0])
		await _capture(tag, PARTS[tag][1])
	_state.flags.clear()
	_state.set_zone_purified("broken_coast")
	await _capture("era", Vector2i(30, 21))
	for region in REGIONS:
		_state.set_zone_purified(region)
	await _capture("todo", Vector2i(30, 21))
	await _record_motion(Vector2i(30, 21))
	_state.flags.clear()
	get_tree().quit()


func _record_motion(cell: Vector2i) -> void:
	DesignTokens.reduced_motion = false
	_world.enter_zone("valdehoja", cell)
	_world.label.visible = false
	_world.ambient.set_physics_process(false)
	for _i in 4:
		await get_tree().physics_frame
	var dir := ProjectSettings.globalize_path("user://ambiente/")
	DirAccess.make_dir_recursive_absolute(dir)
	for i in 60:
		for _t in 3:
			_world.ambient.advance()
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(dir + "%03d.png" % i)
	print("  movimiento: 60 cuadros en %s" % dir)
	DesignTokens.reduced_motion = true


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
