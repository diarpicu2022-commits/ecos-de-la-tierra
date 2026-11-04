extends Node

## Cuando cae Ilan contra la Llama y Bruma sigue sola:
##
##   godot --path . res://tools/verify_cae_ilan.tscn
##
## Mide que «FUERA» sigue a lo que se ve y no al motor, que se avisa de que Bruma
## sigue por su cuenta y que el combate termina sin pulsar nada. Con ventana,
## escribe docs/ux/capturas/<fecha>-cae-ilan.png. Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-cae-ilan.png"

var _pass := 0
var _fail := 0


func _ready() -> void:
	get_node("/root/GameState").flags.clear()
	var layer := CanvasLayer.new()
	add_child(layer)
	var screen := BattleScreen.new()
	screen.region = "ashen_forest"
	screen.companions_auto = true
	layer.add_child(screen)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(0):
		add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(0)
	add_child(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(0), Enums.Team.PLAYER)
	var ilan := players[0]
	var bruma := players[1]
	var manager: BattleManager = screen._manager
	var messages := []
	while screen._phase != BattleScreen.Phase.CHOOSING:
		await get_tree().process_frame
	ilan.hp = 1
	screen._huds[0]._shown_hp = 1.0
	bruma.hp = 40
	screen._huds[1]._shown_hp = 40.0
	Engine.time_scale = 12.0
	screen._actor = ilan
	screen._submit(BattleAction.attack(ilan, monster))

	var bruma_hud: PartyMemberHud = screen._huds[1]
	var early := 0
	var ahead := false
	var said_burn := false
	var burn_early := 0
	var ahead_seen := false
	var shown_at_resolve := true
	var captured := false
	var t0 := Time.get_ticks_msec()
	while screen._phase != BattleScreen.Phase.FINISHED and Time.get_ticks_msec() - t0 < 60000:
		await get_tree().process_frame
		# El monstruo puede fallar: Ilan ataca hasta que caiga.
		if screen._phase == BattleScreen.Phase.CHOOSING:
			screen._submit(BattleAction.attack(ilan, monster))
			continue
		ahead = ahead or not bruma.is_alive()
		# La chapa llega con la primera línea de la acción que quema, como los PV.
		said_burn = said_burn or screen._message.contains("Onda de Calor")
		if bruma_hud._shown_flag == "QUEM." and not said_burn:
			burn_early += 1
		if not ahead_seen and ahead:
			ahead_seen = true
			shown_at_resolve = bruma_hud.is_shown_down()
		if bruma_hud.is_shown_down() and (screen._message.begins_with("Bruma usa")
				or screen._message.begins_with("Bruma duda")):
			early += 1
		if messages.is_empty() or messages[-1] != screen._message:
			messages.append(screen._message)
			print("  ", screen._message)
		if not captured and screen._message.contains("por su cuenta"):
			captured = true
			if DisplayServer.get_name() != "headless":
				await RenderingServer.frame_post_draw
				var date := Time.get_date_string_from_system()
				get_viewport().get_texture().get_image().save_png(OUT % date)
	Engine.time_scale = 1.0

	_check("la chapa de quemadura no se adelanta a su línea (%d cuadros)" % burn_early, burn_early == 0)
	_check("si Bruma cae, el motor lo resuelve antes de enseñarlo", ahead or bruma.is_alive())
	_check("en ese momento Bruma aún no sale «FUERA»", not shown_at_resolve or bruma.is_alive())
	_check("nunca sale «FUERA» mientras se la ve actuar (%d cuadros)" % early, early == 0)
	_check("avisa de que Bruma sigue por su cuenta",
		messages.has("Ilan queda fuera de combate. Bruma sigue por su cuenta."))
	_check("el combate termina sin pulsar nada", screen._phase == BattleScreen.Phase.FINISHED)
	_check("al final, Bruma sale «FUERA» si cayó",
		bruma.is_alive() or bruma_hud.is_shown_down())
	print("%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail > 0 else 0)


func _check(what: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", what])
