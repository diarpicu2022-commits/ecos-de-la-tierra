extends Node2D

## Capturas de una zona regional en el motor, a 480x270 (contrato «Rastro»,
## pasos 3 y 4). Cada toma fuerza su estado con GameState; no se espera a que
## salga jugando (guía §1.5). Valdehoja tiene la suya, `valdehoja_capture`.
##
##   xvfb-run -a godot --path . res://tools/zone_capture.tscn -- <zona>
##
## Además, 60 cuadros del movimiento de la zona purificada (enmienda 8), uno
## cada 3 cuadros de física, en `user://ambiente_<zona>/`, para
## `python tools/frames_to_gif.py`.

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"

## Tomas por zona: [etiqueta, casilla, purificada].
const SHOTS := {
	"ashen_forest": [
		["entrada", Vector2i(1, 12), false],
		["tala", Vector2i(10, 12), false],
		["asomo", Vector2i(46, 11), false],
		["troncos", Vector2i(84, 6), false],
		["quemado", Vector2i(73, 28), false],
		["fuente", Vector2i(60, 23), false],
		["fuente-purificada", Vector2i(60, 23), true],
		["paso-abierto", Vector2i(56, 29), true],
	],
}
const MOTION := {"ashen_forest": Vector2i(52, 11)}
const SLUG := {"ashen_forest": "bosque"}

var _world := WorldRoot.new()
var _state: Node = null


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0] if not args.is_empty() else "ashen_forest"
	_state = get_node("/root/GameState")
	_state.flags.clear()
	_world.start_zone = zone
	_world.start_cell = SHOTS[zone][0][1]
	add_child(_world)
	await get_tree().physics_frame
	DesignTokens.reduced_motion = true
	_world.body.input_enabled = false
	for shot in SHOTS[zone]:
		_state.flags.clear()
		if shot[2]:
			_state.set_zone_purified(zone)
		await _capture(zone, shot[0], shot[1])
	_state.flags.clear()
	_state.set_zone_purified(zone)
	await _record_motion(zone, MOTION[zone])
	_state.flags.clear()
	get_tree().quit()


func _capture(zone: String, tag: String, cell: Vector2i) -> void:
	_world.enter_zone(zone, cell)
	_world.label.visible = false
	for _i in 4:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-%s-motor-%s.png" % [DATE, SLUG[zone], tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s" % path.get_file())


func _record_motion(zone: String, cell: Vector2i) -> void:
	DesignTokens.reduced_motion = false
	_world.enter_zone(zone, cell)
	_world.label.visible = false
	_world.ambient.set_physics_process(false)
	for _i in 4:
		await get_tree().physics_frame
	var dir := ProjectSettings.globalize_path("user://ambiente_%s/" % zone)
	DirAccess.make_dir_recursive_absolute(dir)
	for i in 60:
		for _t in 3:
			_world.ambient.advance()
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(dir + "%03d.png" % i)
	print("  movimiento: 60 cuadros en %s" % dir)
	DesignTokens.reduced_motion = true
