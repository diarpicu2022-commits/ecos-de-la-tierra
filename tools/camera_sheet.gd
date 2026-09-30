extends Node2D

## Captura del paso 3 del contrato «Vereda»: la cámara en el medio de salida,
## 480x270, sobre el mapa de prueba del tileset repetido dos por dos.
##
## Tres momentos del mismo recorrido hacia el este: en reposo, andando con la
## anticipación abierta y un segundo después de parar. La zona muerta y el
## punto que sigue la cámara se dibujan encima en `EMBER_300`: es una marca de
## herramienta para leer la captura, no forma parte del juego.
##   godot --path . res://tools/camera_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-09-30"

var _camera: WorldCamera = null
var _walker: Node2D = null
var _overlay: Overlay = null


class Overlay extends Node2D:
	var camera: WorldCamera = null
	var walker: Node2D = null

	func _draw() -> void:
		var zone := camera.deadzone()
		var color := DesignTokens.EMBER_300
		var w := zone.size.x + 1
		var h := zone.size.y + 1
		draw_rect(Rect2(zone.position, Vector2(w, 1)), color)
		draw_rect(Rect2(zone.position + Vector2i(0, h - 1), Vector2(w, 1)), color)
		draw_rect(Rect2(zone.position, Vector2(1, h)), color)
		draw_rect(Rect2(zone.position + Vector2i(w - 1, 0), Vector2(1, h)), color)
		var p := Vector2i(walker.position)
		draw_rect(Rect2(p - Vector2i(2, 0), Vector2(5, 1)), color)
		draw_rect(Rect2(p - Vector2i(0, 2), Vector2(1, 5)), color)


func _ready() -> void:
	var sheet: GDScript = load("res://tools/tileset_sheet.gd")
	var lines := PackedStringArray()
	for _repeat in 2:
		for row: String in sheet.MAP:
			lines.append(row + row)
	var layer := TileMapLayer.new()
	layer.tile_set = WorldTiles.build_tileset()
	add_child(layer)
	WorldTiles.paint(layer, WorldTiles.parse(lines), func(_c: Vector2i) -> bool: return false)

	_walker = Node2D.new()
	_walker.position = Vector2(20 * DesignTokens.TILE_SIZE, 17 * DesignTokens.TILE_SIZE)
	add_child(_walker)
	_camera = WorldCamera.new()
	_camera.target = _walker
	add_child(_camera)
	_camera.set_physics_process(false)
	_camera.make_current()
	_overlay = Overlay.new()
	_overlay.camera = _camera
	_overlay.walker = _walker
	add_child(_overlay)

	await _capture("reposo")
	for _i in 45:
		_walker.position += Vector2(1, 0)
		_camera.advance()
	await _capture("andando")
	for _i in 60:
		_camera.advance()
	await _capture("parado")
	get_tree().quit()


func _capture(tag: String) -> void:
	_overlay.queue_redraw()
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-camara-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s  centro %s  anticipación %s" % [path.get_file(), _camera.center, _camera.lookahead])
