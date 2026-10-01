extends Node2D

## Captura del paso 4 del contrato «Umbral»: límites de la cámara, fundido y
## rótulo de lugar, a 480x270.
##
## Cuatro momentos:
##   antes     a 4 tiles de la salida este de `prueba_a`: la cámara topa con el
##             borde de la zona y ya no enseña el vacío.
##   fundido   el cuarto de los siete cuadros del fundido de salida (4/7). Es
##             la única captura con colores fuera de la paleta: la cortina
##             `ASH_950` mezcla con opacidad, y eso es lo que es un fundido.
##   llegada   diez cuadros después del cambio: la cortina ya se fue (7) y el
##             rótulo acaba de entrar entero (10), con la tecla aún pulsada.
##   esquina   la esquina inferior izquierda de `prueba_a`: el cuerpo fuera de
##             la zona muerta y la pantalla encerrada en la zona.
##   godot --path . res://tools/umbral_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-01"

var _world := WorldRoot.new()


func _ready() -> void:
	_world.start_zone = "prueba_a"
	_world.start_cell = Vector2i(32, 9)
	add_child(_world)
	DesignTokens.reduced_motion = false
	await get_tree().physics_frame
	Input.action_press("move_right")
	var before_done := false
	var fade_done := false
	while _world.zone_id == "prueba_a":
		await get_tree().physics_frame
		if not before_done and int(_world.body.global_position.x) >= 36 * DesignTokens.TILE_SIZE:
			before_done = true
			await _capture("antes")
		if not fade_done and _world.fade == WorldRoot.Fade.OUT and _world.curtain.modulate.a >= 4.0 / 7.0 - 0.001:
			fade_done = true
			await _capture("fundido")
	for _i in 10:
		await get_tree().physics_frame
	await _capture("llegada")
	Input.action_release("move_right")

	_world.enter_zone("prueba_a", Vector2i(3, 13))
	await get_tree().physics_frame
	Input.action_press("move_left")
	Input.action_press("move_down")
	for _i in 120:
		await get_tree().physics_frame
	Input.action_release("move_left")
	Input.action_release("move_down")
	await get_tree().physics_frame
	await _capture("esquina")
	get_tree().quit()


## Congela el mundo mientras se espera al render, para que la captura enseñe
## exactamente el cuadro medido.
func _capture(tag: String) -> void:
	_freeze(true)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-umbral-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s  zona %s  pies %s  cortina %.2f  rotulo %s" % [path.get_file(),
		_world.zone_id, Vector2i(_world.body.global_position), _world.curtain.modulate.a,
		PlaceLabel.Phase.keys()[_world.label.phase]])
	_freeze(false)


func _freeze(on: bool) -> void:
	for node in [_world, _world.body, _world.camera, _world.label]:
		node.set_physics_process(not on)
