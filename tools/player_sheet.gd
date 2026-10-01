extends Node2D

## Captura del paso 5 del contrato «Umbral»: el sprite de Ilan en el mundo, a
## 480x270.
##
##   muestrario  las 8 poses (2 por orientación) sobre suelo, camino y follaje,
##               en las dos versiones del terreno: se lee en todos.
##   andando     en `prueba_a`, por el camino hacia el este, a mitad de paso.
##   pared       apoyado contra el follaje del norte de `prueba_a`: el hueco
##               entre los pies y el borde dibujado, con el sprite de verdad.
##   godot --path . res://tools/player_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-01"
const T := DesignTokens.TILE_SIZE

## Seis franjas de 2 tiles: suelo, camino y follaje, enfermos y purificados.
const STRIPES := ["..", "==", "##", "..", "==", "##"]


func _ready() -> void:
	await _sampler()
	await _in_world()
	get_tree().quit()


func _sampler() -> void:
	var layer := TileMapLayer.new()
	layer.tile_set = WorldTiles.build_tileset()
	add_child(layer)
	var lines := PackedStringArray()
	for y in 17:
		var stripe: String = STRIPES[mini(y / 3, STRIPES.size() - 1)]
		lines.append(stripe[0].repeat(30))
	WorldTiles.paint(layer, WorldTiles.parse(lines), func(c: Vector2i) -> bool: return c.y >= 9)
	var tex: Texture2D = load(PlayerBody.SPRITE_PATH)
	for band in 6:
		for i in 8:
			var s := Sprite2D.new()
			s.texture = tex
			s.centered = false
			s.region_enabled = true
			s.region_rect = Rect2(Vector2((i % 2) * 16, (i / 2) * 24), Vector2(16, 24))
			# La última franja solo tiene 2 tiles visibles: 270 px no son 6 x 48.
			s.position = Vector2(24 + i * 56, mini(band * 3 * T + 12, 270 - 26))
			add_child(s)
	await _capture("muestrario")
	for child in get_children():
		child.queue_free()
	await get_tree().process_frame


func _in_world() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	world.body.input_enabled = false
	world.label.visible = false
	# Andando: 12 px por el camino hacia el este, a mitad de la segunda pose.
	world.enter_zone("prueba_a", Vector2i(16, 9))
	world.label.visible = false
	for _i in 12:
		world.body.step(Vector2i.RIGHT, false)
	world.camera.snap_to_target()
	await _capture("andando")
	# Contra el follaje del norte: sube hasta tocarlo.
	world.enter_zone("prueba_a", Vector2i(12, 4))
	world.label.visible = false
	for _i in 40:
		world.body.step(Vector2i.UP, false)
	world.camera.snap_to_target()
	await _capture("pared")


func _capture(tag: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-ilan-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s" % path.get_file())
