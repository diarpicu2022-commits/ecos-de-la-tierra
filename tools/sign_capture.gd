extends Node

## Captura del cartel de lugar (`LocationSign`) en el motor, a 640 × 360 y con
## ventana:
##
##   godot --path . res://tools/sign_capture.tscn -- <zona> [purificada]
##
## Entra en la zona por su casilla de llegada, espera a que el cartel esté
## entero y guarda `docs/ux/capturas/<fecha>-cartel-<zona>[-purificada].png`.

const OUT := "res://docs/ux/capturas/%s-cartel-%s%s.png"


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0] if args.size() > 0 else "ashen_forest"
	var pure := args.size() > 1 and args[1] == "purificada"
	var state := get_node("/root/GameState")
	state.flags.clear()
	state.set_zone_purified(zone, pure)
	DesignTokens.reduced_motion = false
	var cell := Vector2i(1, 1)
	for e in ZoneRules.load_exits():
		if e["to"] == zone:
			cell = ZoneRules.cell_of(e, "to_cell")
			break
	var world := WorldRoot.new()
	world.start_zone = zone
	world.start_cell = cell
	add_child(world)
	if world.monster != null:
		world.monster.active = false
	while world.label.phase != PlaceLabel.Phase.HOLD:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	var path := OUT % [Time.get_date_string_from_system(), zone, "-purificada" if pure else ""]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
	print("captura: %s («%s» / «%s»)" % [path, world.label.text, world.label.subtitle])
	get_tree().quit()
