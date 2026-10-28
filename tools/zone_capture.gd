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
	"tar_basin": [
		["entrada", Vector2i(56, 1), false],
		["barriles", Vector2i(49, 9), false],
		["tuberia", Vector2i(14, 26), false],
		["asomo", Vector2i(30, 28), false],
		["barcas", Vector2i(62, 46), false],
		["fuente", Vector2i(39, 35), false],
		["fuente-purificada", Vector2i(39, 35), true],
		["paso-abierto", Vector2i(20, 34), true],
	],
	"broken_coast": [
		["entrada", Vector2i(94, 12), false],
		["viento", Vector2i(86, 12), false],
		["asomo", Vector2i(42, 11), false],
		["red", Vector2i(10, 24), false],
		["reguero", Vector2i(44, 26), false],
		["fuente", Vector2i(42, 23), false],
		["fuente-purificada", Vector2i(42, 23), true],
		["playa-purificada", Vector2i(28, 29), true],
		["paso-abierto", Vector2i(62, 21), true],
	],
	"withered_plain": [
		["entrada", Vector2i(1, 11), false],
		["setos", Vector2i(13, 11), false],
		["asomo", Vector2i(40, 11), false],
		["sacos", Vector2i(83, 5), false],
		["pulverizadora", Vector2i(71, 32), false],
		["fuente", Vector2i(57, 24), false],
		["fuente-purificada", Vector2i(57, 24), true],
		["campo-purificado", Vector2i(30, 8), true],
		["paso-abierto", Vector2i(52, 30), true],
	],
	"waning_peak": [
		["entrada", Vector2i(52, 1), false],
		["roca", Vector2i(48, 9), false],
		["estaca", Vector2i(12, 25), false],
		["asomo", Vector2i(34, 28), false],
		["hielo", Vector2i(57, 46), false],
		["fuente", Vector2i(40, 37), false],
		["fuente-purificada", Vector2i(40, 37), true],
		["ladera-purificada", Vector2i(13, 14), true],
		["paso-abierto", Vector2i(20, 36), true],
	],
	"greed_crypt": [
		["entrada", Vector2i(58, 36), false],
		["boveda-1", Vector2i(52, 29), false],
		["boveda-2", Vector2i(23, 7), false],
		["boveda-3", Vector2i(8, 32), false],
		["asomo", Vector2i(8, 38), false],
		["boveda-4", Vector2i(8, 54), false],
		["boveda-5", Vector2i(46, 55), false],
		["fuente", Vector2i(30, 46), false],
		["fuente-purificada", Vector2i(30, 46), true],
		["galeria-purificada", Vector2i(23, 7), true],
		# Enmienda 12: el túnel detrás de la Sombra y el pozo a Valdehoja.
		["tunel", Vector2i(33, 30), false],
		["reja-pozo", Vector2i(33, 5), false],
		["tunel-abierto", Vector2i(33, 12), true],
		["pozo-abierto", Vector2i(33, 3), true],
	],
}
const MOTION := {"ashen_forest": Vector2i(52, 11), "tar_basin": Vector2i(40, 38),
	"broken_coast": Vector2i(28, 29), "withered_plain": Vector2i(30, 8),
	"waning_peak": Vector2i(44, 41)}
## En la Cripta purificada no hay nada que se mueva (ni agua ni plantas que se
## mezan): no se graba movimiento.
const SLUG := {"ashen_forest": "bosque", "tar_basin": "cuenca", "broken_coast": "costa",
	"withered_plain": "llanura", "waning_peak": "cumbre", "greed_crypt": "cripta"}

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
	if MOTION.has(zone):
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
