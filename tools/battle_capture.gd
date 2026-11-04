extends Node

## Captura el combate tal como lo monta `GameFlow`: en una capa del viewport de
## 640 × 360, con la región y el grupo de la partida.
##
##   godot --path . res://tools/battle_capture.tscn -- [zona] [etiqueta] [opciones]
##
## Escribe docs/ux/capturas/<fecha>-<etiqueta>-<zona>.png en la primera
## elección de Ilan. Sin argumentos, el Bosque y «combate». Las opciones, a
## cualquier orden:
##   purificado      con el monstruo ya purificado
##   foco=<0..3>     mando enfocado, con las teclas de verdad
##   entrar          confirma lo enfocado (abre su submenú); se puede repetir
##   bajar           baja una fila en un submenú
##   sin-energia     Ilan sin energía, para ver el coste que no alcanza
##   lleno           los cuatro objetos y una segunda habilidad para Ilan

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
	var flags := args.slice(2)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(index + 1):
		add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(index)
	add_child(monster)
	var enemies: Array[Combatant] = [monster]
	var inventory := Encounters.build_inventory(index + 1)
	if "lleno" in flags:
		inventory.add(ItemLibrary.suri_antidote(), 2)
		inventory.add(ItemLibrary.field_ration(), 2)
	screen.start_battle(players, enemies, inventory, Enums.Team.PLAYER)
	for i in 600:
		if screen._phase == BattleScreen.Phase.CHOOSING and screen._actor == screen._manager.leader:
			break
		screen._advance_queue()
		await get_tree().process_frame
	if "purificado" in flags:
		monster.is_purified = true
		monster.purified.emit()
		for v in screen._monster_views:
			v.flush()
	if "lleno" in flags:
		screen._actor.skills.append(SkillLibrary.firebreak_line())
	if "sin-energia" in flags:
		screen._actor.energy = 0
	await get_tree().create_timer(0.3).timeout
	for flag in flags:
		if flag.begins_with("foco="):
			var focus := int(flag.trim_prefix("foco="))
			if focus % 2 == 1:
				await _press("move_right")
			if focus >= 2:
				await _press("move_down")
		elif flag == "bajar":
			await _press("move_down")
		elif flag == "entrar":
			await _press("confirm")
	await get_tree().create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	var path := OUT % [Time.get_date_string_from_system(), tag, zone]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
	print("captura: ", path)
	get_tree().quit()


func _press(action: String) -> void:
	for pressed in [true, false]:
		var event := InputEventAction.new()
		event.action = action
		event.pressed = pressed
		Input.parse_input_event(event)
		await get_tree().process_frame
