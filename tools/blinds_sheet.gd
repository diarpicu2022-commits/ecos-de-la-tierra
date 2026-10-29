extends Node

## Capturas de la persiana (contrato «Persiana», paso 4), a 480x270:
##
##   godot --path . res://tools/blinds_sheet.tscn
##
## En el Bosque, con Ilan junto a la Llama: la persiana a mitad de cierre
## (cuadro 9 de 18) con cada ventaja, y «Ceniza y Brasa» ya abierta con el
## grupo de GameState, y una línea del registro en que un compañero dice por
## qué actúa (IA-5).

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"
const SHOTS := [
	[MapMonster.Advantage.PLAYER, "ventaja-ilan"],
	[MapMonster.Advantage.MONSTER, "ventaja-monstruo"],
	[MapMonster.Advantage.NONE, "sin-ventaja"],
]


func _ready() -> void:
	var state := get_node("/root/GameState")
	state.flags.clear()
	var flow := GameFlow.new()
	flow.start_zone = "ashen_forest"
	flow.start_cell = Vector2i(51, 22)
	add_child(flow)
	await get_tree().physics_frame
	flow.world.body.input_enabled = false
	flow.world.label.visible = false
	DesignTokens.reduced_motion = false
	for shot in SHOTS:
		flow.world.monster.active = false
		flow.world.monster.contact.emit(shot[0])
		for _i in 9:
			await get_tree().physics_frame
		await _save("persiana-" + shot[1])
		while flow.screen == null or flow.blinds.running:
			await get_tree().physics_frame
		if shot[0] == MapMonster.Advantage.PLAYER:
			for _i in 30:
				await get_tree().physics_frame
			await _save("combate-desde-el-mapa")
			# IA-5: Ilan manda «Atajad» y ataca; se avanza el registro hasta la
			# línea en que un compañero dice por qué actúa.
			var screen: BattleScreen = flow.screen
			screen._manager.order = PartyMind.Order.CAUSE
			screen._submit(BattleAction.attack(screen._actor, screen._manager._monster()))
			for _i in 40:
				if " sigue " in screen._message or " duda:" in screen._message:
					break
				screen._advance_queue()
				await get_tree().process_frame
			await _save("combate-orden-registro")
		flow.result = Enums.BattleResult.FLED
		flow.leave_battle()
		while flow.screen != null or flow.blinds.running:
			await get_tree().physics_frame
		flow.world.label.visible = false
	get_tree().quit()


func _save(tag: String) -> void:
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path(OUT_DIR + "%s-%s.png" % [DATE, tag])
	get_viewport().get_texture().get_image().save_png(path)
	print("  capturado: %s" % path.get_file())
