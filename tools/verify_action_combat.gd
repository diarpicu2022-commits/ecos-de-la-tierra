extends Node

## Combate de acción en el mapa, contrato «Tajo»
## (docs/ux/anexos/2026-11-04-combate-accion.md):
##   godot --path . res://tools/verify_action_combat.tscn
##
## Con ventana escribe las capturas en docs/ux/capturas/2026-11-04-accion-*.png.

const OUT := "res://docs/ux/capturas/2026-11-04-accion-%s.png"
const ZONE := "ashen_forest"

var _pass := 0
var _fail := 0
var flow: GameFlow = null


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
		print("  OK    " + label)
	else:
		_fail += 1
		printerr("  FALLA " + label)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _shot(tag: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(OUT % tag))


## Ilan pegado al monstruo, mirándolo.
func _close_in() -> void:
	var m := flow.world.monster
	flow.world.body.global_position = m.position + Vector2(-56, 0)
	flow.world.body.facing = Vector2i.RIGHT


func _fight() -> ActionCombat:
	_close_in()
	flow._on_encounter(MapMonster.Advantage.PLAYER)
	await _frames(2)
	return flow.action


func _ready() -> void:
	var state := get_node("/root/GameState")
	state.flags.clear()
	DesignTokens.reduced_motion = false
	flow = GameFlow.new()
	flow.start_zone = ZONE
	flow.start_cell = Vector2i(1, 16)
	flow.action_combat = true
	add_child(flow)
	await _frames(3)
	flow.world.label.visible = false

	print("La pelea empieza en el mapa")
	var a := await _fight()
	_check("hay combate de acción y no pantalla aparte", a != null and a.running and flow.screen == null)
	_check("el mundo sigue a la vista y el monstruo deja de patrullar",
		flow.world.visible and not flow.world.monster.active)
	_check("el HUD está a la vista", flow.action_hud.visible)
	_check("empieza Ilan, con su habilidad de DESHIELO",
		a.hero().display_name == "Ilan" and a.eco_skill().weakness_type == Enums.EcoType.THAW)

	print("\nSe pelea moviéndose, por el camino real del contacto")
	a.running = false
	flow._on_action_finished(Enums.BattleResult.FLED)
	for i in 180:
		if flow.action == null:
			break
		await get_tree().physics_frame
	flow.world.monster.grace_frames = 0
	_close_in()
	flow.world._on_contact(MapMonster.Advantage.PLAYER)
	await _frames(2)
	a = flow.action
	_check("tras el contacto, Ilan sigue aceptando el teclado", a != null and flow.world.body.input_enabled)
	var from := flow.world.body.global_position
	Input.action_press("move_left")
	await _frames(20)
	Input.action_release("move_left")
	var moved := from.x - flow.world.body.global_position.x
	_check("con la flecha se mueve en plena pelea (%.0f px)" % moved, moved >= 10.0)
	_close_in()
	a._attack_cooldown = 0
	var cooldown_before := a._attack_cooldown
	var press := InputEventAction.new()
	press.action = "attack"
	press.pressed = true
	Input.parse_input_event(press)
	await _frames(2)
	var release := InputEventAction.new()
	release.action = "attack"
	Input.parse_input_event(release)
	_check("la tecla de ataque responde en plena pelea", a._attack_cooldown > cooldown_before)

	print("\nLa fuerza bruta no gana")
	var regen := [0]
	a.monster.regenerated.connect(func(_hp): regen[0] += 1)
	for i in 300:
		_close_in()
		a._attack_cooldown = 0
		a.attack()
		a.hero().hp = a.hero().max_hp
	_check("300 tajos y el monstruo sigue en pie y sin purificar (se rehízo %d veces)" % regen[0],
		a.running and not a.monster.is_purified and a.monster.is_alive() and regen[0] > 0)
	var told := " ".join(a.hud.toast_lines())
	_check("el aviso dice la causa y a quién cambiar («%s»)" % told,
		told.contains("Su causa es FUEGO") and told.contains("Bruma"))
	await _frames(2)
	await _shot("rehace")

	print("\nLa habilidad equivocada no aturde")
	_close_in()
	a.use_eco()
	_check("el Escudo de Albedo de Ilan no aturde a la Llama", a.foe != ActionCombat.Foe.STUNNED)
	_check("y el aviso lo explica", " ".join(a.hud.toast_lines()).contains("resiste"))
	var widest := 0.0
	for row in a.hud.wrapped_toast():
		widest = maxf(widest, TvFrame.width(load(DesignTokens.FONT_PATH), row))
	_check("el aviso largo cabe en el papel (%.0f de %.0f px)" % [widest, ActionHud.TOAST.size.x - 24.0],
		widest <= ActionHud.TOAST.size.x - 24.0)

	print("\nEl compañero en el mapa")
	_check("Bruma aparece en el mapa como compañera", a.follower.visible and a.follower.is_inside_tree()
		and a.companion().display_name == "Bruma")
	var start_pos := flow.world.body.global_position
	for i in 40:
		flow.world.body.step(Vector2i.LEFT, false)
		await get_tree().physics_frame
	var gap := a.follower.position.distance_to(flow.world.body.global_position)
	_check("sigue a Ilan a unos pasos (a %.0f px)" % gap, gap >= a.FOLLOW_GAP - 1.0 and gap <= 40.0)
	await _shot("companera")
	flow.world.body.global_position = start_pos

	print("\nCambio de héroe")
	var frame := Engine.get_physics_frames()
	a.swap(1)
	_check("E cambia a Bruma en el mismo cuadro", a.hero().display_name == "Bruma"
		and Engine.get_physics_frames() == frame)
	a.swap(-1)
	_check("Q vuelve a Ilan", a.hero().display_name == "Ilan")
	a.swap(1)
	_check("al cambiar, el compañero pasa a ser Ilan", a.companion().display_name == "Ilan")
	a.swap(-1)
	a.swap(1)

	print("\nLa ventana de aturdimiento")
	_close_in()
	a.use_eco()
	_check("la Línea Cortafuegos aturde", a.foe == ActionCombat.Foe.STUNNED and a.counters == 1)
	await _frames(10)
	await _shot("aturdido")
	await _frames(roundi(DesignTokens.DUR_STUN_WINDOW * Engine.physics_ticks_per_second))
	_check("si la ventana se acaba, se rehace y la cuenta vuelve a cero",
		a.foe != ActionCombat.Foe.STUNNED and a.counters == 0)

	print("\nAtacar la causa purifica")
	a.hero().energy = a.hero().max_energy
	_close_in()
	a.use_eco()
	await _frames(20)
	_close_in()
	a.use_eco()
	_check("dos contramedidas dentro de la ventana purifican",
		a.monster.is_purified and a.foe == ActionCombat.Foe.PURIFIED and a.result == Enums.BattleResult.VICTORY)
	await _frames(2)
	await _shot("purifica")
	var ended := [false]
	flow.battle_over.connect(func(_r): ended[0] = true)
	for i in 600:
		if ended[0]:
			break
		await get_tree().physics_frame
	_check("sale la ola y la zona queda purificada", ended[0] and state.is_zone_purified(ZONE))
	var runner := flow.world.dialogue
	_check("después hablan Bruma y Yara por el ave", runner.is_running()
		and runner.conversation == "bosque_purificado")
	await _shot("bruma-habla")
	var voices := PackedStringArray()
	while runner.is_running():
		if not voices.has(runner.box.speaker):
			voices.append(runner.box.speaker)
		runner.box.confirm()
		await get_tree().process_frame
	_check("hablan Bruma, Ilan y Yara (%s)" % ", ".join(voices),
		voices.has("Bruma") and voices.has("Ilan") and voices.has("Yara"))
	_check("el monstruo deja el mapa y el HUD se va",
		flow.world.monster == null and not flow.action_hud.visible and flow.action == null)
	var left := 0
	for n in flow.world.entities.get_children():
		if n is Sprite2D and n.region_enabled and n.texture != null \
				and n.texture.resource_path.contains("/cast/bruma"):
			left += 1
	_check("y el compañero también", left == 0)
	_check("fuera de la pelea se vuelve a andar con Ilan",
		flow.world.body._sprite.texture.resource_path == PlayerBody.SPRITE_PATH)

	print("\nAviso y esquiva")
	state.flags.clear()
	flow.world.enter_zone(ZONE, Vector2i(1, 16))
	await _frames(3)
	flow.world.label.visible = false
	a = await _fight()
	var h := a.hero()
	h.hp = h.max_hp
	a._begin_telegraph()
	await _frames(2)
	await _shot("aviso")
	await _frames(roundi(DesignTokens.DUR_TELEGRAPH * Engine.physics_ticks_per_second))
	_check("quieto en la zona de aviso, recibe el golpe (%d/%d)" % [h.hp, h.max_hp], h.hp < h.max_hp)
	h.hp = h.max_hp
	a._begin_telegraph()
	a._dodge_cooldown = 0
	flow.world.body.facing = Vector2i.LEFT
	a.dodge()
	await _frames(roundi(DesignTokens.DUR_TELEGRAPH * Engine.physics_ticks_per_second) + 2)
	_check("esquivando a tiempo, no recibe nada", h.hp == h.max_hp)
	_check("la esquiva acaba y devuelve el control", not a.dodging and flow.world.body.input_enabled)

	print("\nSin energía y sin objetos")
	a.swap(1)
	a.hero().energy = 0
	_close_in()
	_check("sin energía la habilidad eco no sale y se dice por qué",
		not a.use_eco() and " ".join(a.hud.toast_lines()).contains("no tiene energía"))
	var saved := a.bag
	a.bag = Inventory.new()
	_check("con la bolsa vacía no se usa nada y se dice", not a.use_item()
		and " ".join(a.hud.toast_lines()).contains("vacía"))
	a.bag = saved
	var before := a.bag.get_amount(a.items()[0])
	a.hero().hp = 10
	a.slot = 0
	_check("con objetos, V cura al héroe activo y gasta uno",
		a.use_item() and a.hero().hp > 10 and a.bag.get_amount(a.items()[0]) == before - 1)
	a.swap(-1)

	print("\nPerder")
	for c in a.party:
		c.hp = 1
	var arrival := flow.world.arrival_cell
	ended[0] = false
	for k in a.party.size() + 1:
		if not a.running:
			break
		_close_in()
		a._begin_telegraph()
		await _frames(roundi(DesignTokens.DUR_TELEGRAPH * Engine.physics_ticks_per_second) + 1)
	_check("si caen todos, se pierde", a.result == Enums.BattleResult.DEFEAT)
	for i in 300:
		if ended[0]:
			break
		await get_tree().physics_frame
	_check("y se vuelve a la entrada con 1 PV",
		MapMonster.cell_of(Vector2i(flow.world.body.global_position)) == arrival
		and flow.world.monster != null and state.party.all(func(c): return c.hp == 1))

	print("\nApagado, se pelea por turnos")
	flow.action_combat = false
	_close_in()
	flow.world.monster.active = false
	flow._on_encounter(MapMonster.Advantage.NONE)
	for i in 120:
		if flow.screen != null:
			break
		await get_tree().physics_frame
	_check("sin el interruptor abre la pantalla de combate por turnos", flow.screen != null and flow.action == null)

	state.flags.clear()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)
