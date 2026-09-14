extends Node2D

## Captura el selector de región y la apertura de los seis combates.
## Incluye el de la Llanura Marchita jugado hasta que el Espectro se multiplica,
## que es el único caso con varios enemigos en el campo.
##   godot --path . res://tools/regions_capture.tscn

const CHOOSING := 2


func _ready() -> void:
	await _capture_select()
	for i in range(Encounters.count()):
		await _capture_battle(i, 0)
	# El Espectro se multiplica a las pocas rondas: se juega hasta verlo.
	await _capture_battle(3, 26)
	print("Listo.")
	get_tree().quit()


func _capture_select() -> void:
	var select := RegionSelect.new()
	add_child(select)
	await get_tree().create_timer(0.35).timeout
	for i in range(Encounters.count()):
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("user://sel_%d.png" % i)
		await _press("move_down")
		await get_tree().create_timer(0.16).timeout
	print("  selector: %d regiones" % Encounters.count())
	select.queue_free()
	await get_tree().process_frame


## Abre el combate `index` y captura tras `turns` confirmaciones.
func _capture_battle(index: int, turns: int) -> void:
	var screen := BattleScreen.new()
	add_child(screen)

	var nodes: Array[Node] = []
	var players: Array[Combatant] = []
	for character in Encounters.build_party(index):
		add_child(character)
		nodes.append(character)
		players.append(character)

	var monster: Monster = Encounters.build_monster(index)
	add_child(monster)
	nodes.append(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(index))

	await _await_choice(screen)
	for _t in range(turns):
		if int(screen.get("_phase")) == CHOOSING:
			await _press("confirm")
		await get_tree().create_timer(0.12).timeout

	await get_tree().create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	var suffix := "_clones" if turns > 0 else ""
	get_viewport().get_texture().get_image().save_png(
			"user://reg_%d%s.png" % [index, suffix])
	print("  combate %d%s  grupo de %d" % [index, suffix, players.size()])

	screen.queue_free()
	for node in nodes:
		node.queue_free()
	await get_tree().process_frame


func _await_choice(screen: BattleScreen) -> void:
	for _i in range(900):
		if int(screen.get("_phase")) == CHOOSING:
			await get_tree().create_timer(0.3).timeout
			return
		await get_tree().process_frame


func _press(action: String) -> void:
	var down := InputEventAction.new()
	down.action = action
	down.pressed = true
	Input.parse_input_event(down)
	await get_tree().process_frame
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)
	await get_tree().process_frame
