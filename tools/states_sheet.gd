extends Node2D

## Paso 6: cada desenlace tiene su vista. Fuerza los tres finales del combate y
## los captura, en lugar de confiar en que salgan jugando.
##   godot --path . res://tools/states_sheet.tscn

const CASES := [
	[Enums.BattleResult.VICTORY, 0, "victoria"],
	[Enums.BattleResult.DEFEAT, 4, "derrota"],
	[Enums.BattleResult.FLED, 2, "retirada"],
]

var _index: int = 0


func _ready() -> void:
	for case in CASES:
		var screen := BattleScreen.new()
		add_child(screen)

		var bruma: Character = PartyLibrary.bruma()
		var coral: Character = PartyLibrary.coral()
		var players: Array[Combatant] = []
		for character in [bruma, coral]:
			character.gain_knowledge(Enums.EcoType.FIRE)
			add_child(character)
			players.append(character)

		var monster := DeforestationFlame.new()
		add_child(monster)
		var enemies: Array[Combatant] = [monster]
		screen.start_battle(players, enemies, Inventory.new())

		# Se fuerza el desenlace sin jugar la partida entera.
		screen.set("_regenerations", case[1])
		screen.call("_finish", case[0])
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(
				"user://state_%s.png" % case[2])
		print("  capturado: %s" % case[2])

		screen.queue_free()
		for node in players:
			node.queue_free()
		monster.queue_free()
		await get_tree().process_frame

	get_tree().quit()
