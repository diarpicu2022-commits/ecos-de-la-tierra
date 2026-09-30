extends Node2D

## Captura del paso 3 del contrato «Umbral»: el esqueleto jugable, a 480x270.
##
## El cuerpo anda hacia el este por el camino de `prueba_a` con la tecla
## pulsada, cruza la salida y sigue andando en `prueba_b`. Tres momentos:
##   antes    a 4 tiles de la salida: el camino sale del mapa, y es la única
##            pista de que por ahí se sale.
##   llegada  el cuadro del cambio: aparece un tile dentro de `prueba_b`.
##   despues  20 cuadros más tarde, sin haber soltado la tecla.
## El cambio es un corte directo; el fundido, el rótulo y los límites de la
## cámara son del paso 4.
##   godot --path . res://tools/zone_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-09-30"

var _world := WorldRoot.new()


func _ready() -> void:
	_world.start_zone = "prueba_a"
	_world.start_cell = Vector2i(32, 9)
	add_child(_world)
	await get_tree().physics_frame
	Input.action_press("move_right")
	var before_done := false
	while _world.zone_id == "prueba_a":
		if not before_done and int(_world.body.global_position.x) >= 36 * DesignTokens.TILE_SIZE:
			before_done = true
			await _capture("antes")
		await get_tree().physics_frame
	await _capture("llegada")
	for _i in 20:
		await get_tree().physics_frame
	await _capture("despues")
	Input.action_release("move_right")
	get_tree().quit()


## Congela el cuerpo, la cámara y el mundo mientras se espera al render, para
## que la captura enseñe exactamente el cuadro medido.
func _capture(tag: String) -> void:
	_freeze(true)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-esqueleto-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s  zona %s  pies %s" % [path.get_file(), _world.zone_id,
		Vector2i(_world.body.global_position)])
	_freeze(false)


func _freeze(on: bool) -> void:
	for node in [_world, _world.body, _world.camera]:
		node.set_physics_process(not on)
