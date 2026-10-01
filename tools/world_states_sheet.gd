extends Node2D

## Hoja de estados del mundo (contrato «Umbral», fase 5, paso 6), a 480x270.
## Cada estado se fuerza; no se espera a que salga jugando (guía §1.5).
##
##   reposo      recién llegado a la zona: de pie y con el rótulo entero.
##   andando     a mitad de paso por el camino.
##   pared       empujando el follaje: de pie, sin pasos.
##   borde       en la esquina de la zona: la pantalla encerrada.
##   fundido     el cuadro 4 de 7 del fundido de salida.
##   llegada     10 cuadros después del cambio, con el rótulo entrando.
##   reducido    movimiento reducido: el cuadro mismo del cruce, sin fundido y
##               con el rótulo ya entero.
##   pequena     una zona menor que la pantalla: centrada, bandas ASH_950.
##   purificada  la bandera purified_<zona> pinta la zona purificada.
##
## Además, 40 cuadros seguidos corriendo hacia el este sobre `prueba_a`
## purificada, para juzgar en movimiento la nota de Diego sobre el follaje (la
## diagonal de las dos copas). Se guardan en `user://recorrido/`, fuera del
## repositorio, y `python tools/frames_to_gif.py` monta con ellos el GIF que sí
## se guarda en `docs/ux/capturas/`.
##   godot --path . res://tools/world_states_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-01"

var _world := WorldRoot.new()
var _state: Node = null


func _ready() -> void:
	add_child(_world)
	_state = get_node("/root/GameState")
	await get_tree().physics_frame
	DesignTokens.reduced_motion = false
	_world.body.input_enabled = false
	_world.label.visible = true

	_world.enter_zone("prueba_a", Vector2i(16, 9))
	await _frames(14)
	await _capture("reposo")

	for _i in 12:
		_world.body.step(Vector2i.RIGHT, false)
	_world.camera.snap_to_target()
	await _capture("andando")

	_world.enter_zone("prueba_a", Vector2i(12, 4))
	for _i in 40:
		_world.body.step(Vector2i.UP, false)
	_world.camera.snap_to_target()
	await _capture("pared")

	_world.enter_zone("prueba_a", Vector2i(3, 13))
	for _i in 120:
		_world.body.step(Vector2i(-1, 1), false)
		_world.camera.advance()
	await _capture("borde")

	# Fundido y llegada, con el teclado de verdad.
	_world.body.input_enabled = true
	_world.enter_zone("prueba_a", Vector2i(37, 9))
	Input.action_press("move_right")
	while _world.fade != WorldRoot.Fade.OUT or _world.curtain.modulate.a < 4.0 / 7.0 - 0.001:
		await get_tree().physics_frame
	await _capture("fundido")
	while _world.zone_id == "prueba_a":
		await get_tree().physics_frame
	await _frames(10)
	await _capture("llegada")
	Input.action_release("move_right")

	# Movimiento reducido: el cuadro del cruce.
	DesignTokens.reduced_motion = true
	_world.enter_zone("prueba_a", Vector2i(37, 9))
	Input.action_press("move_right")
	while _world.zone_id == "prueba_a":
		await get_tree().physics_frame
	await _capture("reducido")
	Input.action_release("move_right")
	DesignTokens.reduced_motion = false
	_world.body.input_enabled = false

	_world.enter_zone("prueba_c", Vector2i(10, 6))
	await _frames(14)
	await _capture("pequena")

	_state.set_zone_purified("prueba_b")
	_world.enter_zone("prueba_b", Vector2i(10, 9))
	await _frames(14)
	await _capture("purificada")
	_state.set_zone_purified("prueba_b", false)

	# Recorrido sobre zona purificada, cuadro a cuadro.
	_state.set_zone_purified("prueba_a")
	_world.enter_zone("prueba_a", Vector2i(3, 9))
	_world.label.visible = false
	for i in 40:
		_world.body.step(Vector2i.RIGHT, true)
		_world.camera.advance()
		await _capture("user://recorrido/%02d.png" % i, false)
	_state.set_zone_purified("prueba_a", false)
	get_tree().quit()


func _frames(n: int) -> void:
	for _i in n:
		await get_tree().physics_frame


## Congela el mundo mientras se espera al render, para que la captura enseñe
## exactamente el cuadro medido.
func _capture(tag: String, verbose := true) -> void:
	for node in [_world, _world.body, _world.camera, _world.label]:
		node.set_physics_process(false)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var target := tag if tag.begins_with("user://") else OUT_DIR + "%s-estados-%s.png" % [DATE, tag]
	var path := ProjectSettings.globalize_path(target)
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	get_viewport().get_texture().get_image().save_png(path)
	if verbose:
		print("  capturado: %s  zona %s  cortina %.2f  rotulo %s" % [path.get_file(), _world.zone_id,
			_world.curtain.modulate.a, PlaceLabel.Phase.keys()[_world.label.phase]])
	for node in [_world, _world.body, _world.camera, _world.label]:
		node.set_physics_process(true)
