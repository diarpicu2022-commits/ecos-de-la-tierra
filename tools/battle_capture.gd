extends Node

## Captura el combate tal como lo monta `GameFlow`: en una capa del viewport de
## 640 × 360, con la región y el grupo de la partida.
##
##   godot --path . res://tools/battle_capture.tscn -- [zona] [etiqueta] [purificado]
##
## Escribe docs/ux/capturas/<fecha>-<etiqueta>-<zona>.png en la primera
## elección de Ilan. Sin argumentos, el Bosque y «combate».

const OUT := "res://docs/ux/capturas/%s-%s-%s.png"


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0] if args.size() > 0 else "ashen_forest"
	var tag: String = args[1] if args.size() > 1 else "combate"
	var index: int = GameFlow.ZONE_ENCOUNTER[zone]
	var layer := CanvasLayer.new()
	add_child(layer)
	var screen := BattleScreen.new()
	screen.region = zone
	screen.companions_auto = true
	layer.add_child(screen)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(index + 1):
		add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(index)
	add_child(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(index + 1), Enums.Team.PLAYER)
	for i in 600:
		if screen._phase == BattleScreen.Phase.CHOOSING and screen._actor == screen._manager.leader:
			break
		screen._advance_queue()
		await get_tree().process_frame
	if args.size() > 2 and args[2] == "purificado":
		monster.is_purified = true
		monster.purified.emit()
		for v in screen._monster_views:
			v.flush()
	await get_tree().create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	var path := OUT % [Time.get_date_string_from_system(), tag, zone]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
	print("captura: ", path)
	get_tree().quit()
