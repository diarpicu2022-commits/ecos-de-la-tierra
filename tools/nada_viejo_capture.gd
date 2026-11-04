extends Node

## Capturas del mundo real para la auditoría «nada viejo» (anexo 2026-11-03).
##   godot --path . res://tools/nada_viejo_capture.tscn -- <zona> <enfermo|sano> <etiqueta> [x y]
## Monta `WorldRoot` tal cual lo monta el juego y escribe en
## docs/ux/capturas/nada-viejo/:
##   <etiqueta>-<zona>-<estado>-mapa.png      la zona entera, a 1×
##   <etiqueta>-<zona>-<estado>-pantalla.png  640 × 360 con Ilan en la casilla
## Sin casilla, la de llegada a la zona.

const OUT := "res://docs/ux/capturas/nada-viejo/%s-%s-%s-%s.png"


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0]
	var healed: bool = args[1] == "sano"
	var tag: String = args[2]
	var state := get_node("/root/GameState")
	state.flags.clear()
	DesignTokens.reduced_motion = true
	if healed:
		for id in ["ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak",
				"greed_crypt", zone]:
			state.set_zone_purified(id)
	var cell := _arrival(zone)
	if args.size() > 4:
		cell = Vector2i(int(args[3]), int(args[4]))
	var lines := ZoneRules.load_zone(zone)
	var size := Vector2i(lines[0].length(), lines.size()) * DesignTokens.TILE_SIZE
	# La pantalla de juego.
	var world := WorldRoot.new()
	world.start_zone = zone
	world.start_cell = cell
	add_child(world)
	for i in 3:
		await get_tree().physics_frame
	if world.monster != null:
		world.monster.active = false
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(
		ProjectSettings.globalize_path(OUT % [tag, zone, args[1], "pantalla"]))
	world.queue_free()
	await get_tree().process_frame
	# La zona entera, en un viewport del tamaño del mapa.
	var view := SubViewport.new()
	view.size = size
	view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	view.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(view)
	var whole := WorldRoot.new()
	whole.start_zone = zone
	whole.start_cell = cell
	view.add_child(whole)
	for i in 3:
		await get_tree().physics_frame
	whole.label.visible = false
	if whole.monster != null:
		whole.monster.active = false
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	view.get_texture().get_image().save_png(
		ProjectSettings.globalize_path(OUT % [tag, zone, args[1], "mapa"]))
	state.flags.clear()
	get_tree().quit(0)


func _arrival(zone: String) -> Vector2i:
	var deco := ZoneRules.load_deco(zone)
	if not deco.is_empty():
		for piece in WorldDecor.pieces(deco["rows"], deco["legend"]):
			if deco["legend"][piece["ch"]]["kind"] == "spawn":
				return piece["at"]
	for e in ZoneRules.load_exits():
		if e["to"] == zone:
			return ZoneRules.cell_of(e, "to_cell")
	return Vector2i(1, 1)
