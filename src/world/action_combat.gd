class_name ActionCombat
extends Node

## Combate de acción en el mapa, contrato «Tajo»
## (docs/ux/anexos/2026-11-04-combate-accion.md).
##
## Se pelea en el mismo mundo: Ilan sigue moviéndose con su cuerpo y el
## monstruo de la región deja de patrullar y pelea donde está.
##
## - Z: tajo. Hace daño con resistencia; sin la causa, el monstruo se rehace.
## - C: habilidad eco del héroe activo. La del tipo correcto aturde durante
##   DUR_STUN_WINDOW, y una segunda dentro de la ventana lo purifica. Es la
##   traducción de COUNTER_SUSTAIN_ROUNDS = 2 a tiempo real.
## - X: esquiva de DODGE_DISTANCE en DUR_DODGE, sin recibir daño.
## - V: objeto elegido con 1 a 4, sobre el héroe activo.
## - Q y E: cambio de héroe al instante.
##
## El monstruo descansa, se acerca, avisa con una zona en el suelo durante
## DUR_TELEGRAPH y golpea esa zona. Todo se cuenta en cuadros de física para
## que la prueba lo mida.

signal finished(result: Enums.BattleResult)
signal toast(lines: PackedStringArray)

enum Foe { REST, APPROACH, TELEGRAPH, STUNNED, PURIFIED }

var world: WorldRoot = null
var hud: ActionHud = null
var monster: Monster = null
var map: MapMonster = null
var party: Array = []
var bag: Inventory = null
var active := 0
var slot := 0
var foe := Foe.REST
## Centro de la zona de aviso, en coordenadas del mundo.
var strike_at := Vector2.ZERO
var dodging := false
var running := false
## Contramedidas correctas dentro de la ventana de aturdimiento.
var counters := 0
var result: int = -1

var _timer := 0
var _dodge_frames := 0
var _dodge_cooldown := 0
var _attack_cooldown := 0
var _dodge_dir := Vector2i.ZERO
var _sheets := {}
var _ground := ActionGround.new()
var _warned_cause := false


## Empieza la pelea. `party` son los `Character` de `GameState`.
func start(p_world: WorldRoot, p_hud: ActionHud, p_monster: Monster, p_party: Array,
		p_bag: Inventory, adv: MapMonster.Advantage) -> void:
	world = p_world
	hud = p_hud
	monster = p_monster
	map = world.monster
	party = p_party
	bag = p_bag
	map.active = false
	running = true
	result = -1
	counters = 0
	active = _first_alive(0)
	_ground.combat = self
	world.add_child(_ground)
	world.move_child(_ground, world.entities.get_index())
	for c in party:
		var key: String = str(c.display_name).to_lower()
		var path := "res://assets/sprites/world/cast/%s.png" % key
		if ResourceLoader.exists(path):
			_sheets[key] = load(path)
	_apply_sheet()
	monster.regenerated.connect(_on_regenerated)
	hud.bind(self)
	# Quien tomó la ventaja golpea primero.
	if adv == MapMonster.Advantage.MONSTER:
		_begin_telegraph()
	else:
		_enter(Foe.REST)
		if adv == MapMonster.Advantage.PLAYER:
			_timer = -_frames(DesignTokens.DUR_MONSTER_REST)


func hero() -> Character:
	return party[active] if active >= 0 and active < party.size() else null


func hero_feet() -> Vector2:
	return world.body.global_position


func monster_feet() -> Vector2:
	return map.position


## La habilidad eco del héroe activo, o null.
func eco_skill() -> EcoSkill:
	var h := hero()
	if h == null:
		return null
	for s in h.get_eco_skills():
		if s is EcoSkill and (s as EcoSkill).ally_healing == 0:
			return s
	return null


func items() -> Array[Item]:
	return bag.get_battle_items() if bag != null else []


func _frames(seconds: float) -> int:
	return maxi(1, roundi(seconds * Engine.physics_ticks_per_second))


# --- Teclado -----------------------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if not running or not world.body.input_enabled or not event.is_pressed() or event.is_echo():
		return
	var handled := true
	if event.is_action("attack"):
		attack()
	elif event.is_action("eco"):
		use_eco()
	elif event.is_action("dodge"):
		dodge()
	elif event.is_action("use_item"):
		use_item()
	elif event.is_action("hero_prev"):
		swap(-1)
	elif event.is_action("hero_next"):
		swap(1)
	else:
		handled = false
		for i in 4:
			if event.is_action("slot_%d" % (i + 1)):
				select_slot(i)
				handled = true
	if handled:
		get_viewport().set_input_as_handled()


# --- Acciones del héroe --------------------------------------------------------

## Distancia de pie a pie y si el héroe mira hacia el monstruo.
func _in_reach(reach: float) -> bool:
	var d := monster_feet() - hero_feet()
	if d.length() > reach:
		return false
	var f := Vector2(world.body.facing)
	return d.length() < DesignTokens.MONSTER_BODY_RADIUS or f.dot(d.normalized()) > 0.3


func attack() -> bool:
	if _attack_cooldown > 0 or dodging or foe == Foe.PURIFIED:
		return false
	_attack_cooldown = _frames(DesignTokens.DUR_HERO_ATTACK)
	GameAudio.play("ui_confirm")
	_ground.slash()
	if not _in_reach(DesignTokens.MONSTER_BODY_RADIUS + DesignTokens.HERO_REACH):
		return false
	var dmg := SkillLibrary.basic_attack().calculate_damage(hero())
	_hit_monster(dmg, Enums.EcoType.NONE)
	if not _warned_cause:
		_warned_cause = true
		_say_cause()
	return true


func use_eco() -> bool:
	var skill := eco_skill()
	var h := hero()
	if skill == null or h == null or foe == Foe.PURIFIED:
		return false
	if not h.has_energy(skill.energy_cost):
		GameAudio.play("ui_denied")
		toast.emit(PackedStringArray(["%s no tiene energía para %s." % [h.display_name, skill.display_name]]))
		return false
	if not _in_reach(DesignTokens.MONSTER_BODY_RADIUS + DesignTokens.ECO_REACH):
		GameAudio.play("ui_denied")
		toast.emit(PackedStringArray(["%s está demasiado lejos para %s." % [monster.display_name, skill.display_name]]))
		return false
	h.spend_energy(skill.energy_cost)
	if skill.weakness_type != monster.required_counter_type:
		_hit_monster(skill.calculate_damage(h), skill.weakness_type)
		toast.emit(PackedStringArray([
			"%s resiste: %s no corrige el daño que lo origina." % [monster.display_name, skill.display_name],
			_cause_hint()]))
		return false
	counters += 1
	if counters >= DesignTokens.COUNTER_SUSTAIN_ROUNDS:
		_purify(skill)
	else:
		# Primero el aturdimiento: si este golpe lo deja sin vida, se rehace
		# pero sigue aturdido y la cuenta no se pierde.
		_enter(Foe.STUNNED)
		var dealt := monster.take_damage(skill.calculate_damage(h), skill.weakness_type)
		hud.number(monster_feet(), str(dealt), DesignTokens.TV_GOLD_4)
		GameAudio.play("hit")
		toast.emit(PackedStringArray([
			"%s frena a %s. ¡Está aturdido!" % [skill.display_name, monster.display_name],
			"Úsala otra vez antes de que se rehaga."]))
	return true


func dodge() -> bool:
	if dodging or _dodge_cooldown > 0:
		return false
	dodging = true
	_dodge_dir = world.body.facing
	_dodge_frames = _frames(DesignTokens.DUR_DODGE)
	_dodge_cooldown = _frames(DesignTokens.DUR_DODGE_COOLDOWN)
	world.body.input_enabled = false
	GameAudio.play("ui_move")
	return true


func use_item() -> bool:
	var list := items()
	var h := hero()
	if list.is_empty() or h == null:
		GameAudio.play("ui_denied")
		toast.emit(PackedStringArray(["La bolsa está vacía."]))
		return false
	var item: Item = list[clampi(slot, 0, list.size() - 1)]
	var before := h.hp
	bag.use(item, h, h)
	GameAudio.play("heal")
	hud.number(hero_feet(), "+%d" % (h.hp - before), DesignTokens.TV_UI_6)
	return true


func select_slot(i: int) -> void:
	slot = i
	GameAudio.play("ui_move")


func swap(direction: int) -> bool:
	var next := _first_alive(wrapi(active + direction, 0, party.size()), direction)
	if next < 0 or next == active:
		return false
	active = next
	_apply_sheet()
	GameAudio.play("ui_confirm")
	return true


func _first_alive(from: int, direction := 1) -> int:
	for k in party.size():
		var i := wrapi(from + k * direction, 0, party.size())
		if party[i].is_alive():
			return i
	return -1


func _apply_sheet() -> void:
	var h := hero()
	if h == null:
		return
	var key := str(h.display_name).to_lower()
	if _sheets.has(key):
		world.body.set_sheet(_sheets[key])


# --- Daño y reglas ---------------------------------------------------------------

func _hit_monster(amount: int, eco: Enums.EcoType) -> void:
	var dealt := monster.take_damage(amount, eco)
	var resisted := monster.get_resistance_for(eco) > 0.0
	GameAudio.play("hit_resisted" if resisted else "hit")
	hud.number(monster_feet(), ("~%d" if resisted else "%d") % dealt,
		DesignTokens.TV_UI_4 if resisted else DesignTokens.TV_GOLD_4)


func _on_regenerated(_hp: int) -> void:
	GameAudio.play("regen")
	if foe == Foe.STUNNED:
		return
	counters = 0
	_say_cause("se rehace")


## «La llama se rehace. Su causa es FUEGO» y a quién cambiar.
func _say_cause(verb := "no cede") -> void:
	var cause := Enums.eco_type_name(monster.required_counter_type).to_upper()
	toast.emit(PackedStringArray(["%s %s. Su causa es %s." % [monster.display_name, verb, cause],
		_cause_hint()]))


func _cause_hint() -> String:
	for i in party.size():
		var c: Character = party[i]
		for s in c.get_eco_skills():
			if s is EcoSkill and (s as EcoSkill).weakness_type == monster.required_counter_type:
				if i == active:
					return "Usa %s [C]." % s.display_name
				var key := "Q" if wrapi(i - active, 0, party.size()) > party.size() / 2 else "E"
				return "Cambia a %s [%s] y usa %s." % [c.display_name, key, s.display_name]
	return "Nadie del grupo conoce todavía su contramedida."


func _purify(skill: EcoSkill) -> void:
	_enter(Foe.PURIFIED)
	monster.is_purified = true
	monster.purified.emit()
	map.show_pure()
	GameAudio.play("purify")
	toast.emit(PackedStringArray(["¡Purificado! %s ataja la causa del daño." % skill.display_name,
		"El bosque recupera el color a su alrededor."]))
	_end(Enums.BattleResult.VICTORY)


func _end(r: Enums.BattleResult) -> void:
	if not running:
		return
	running = false
	result = r
	world.body.input_enabled = true
	finished.emit(r)


## Se sale de la zona en plena pelea: el monstruo se rinde.
func abort() -> void:
	_end(Enums.BattleResult.FLED)


func cleanup() -> void:
	if is_instance_valid(_ground):
		_ground.queue_free()
	if monster != null and monster.regenerated.is_connected(_on_regenerated):
		monster.regenerated.disconnect(_on_regenerated)


# --- Cada cuadro -------------------------------------------------------------------

func _physics_process(_delta: float) -> void:
	if not running:
		return
	tick()


## Un cuadro de la pelea. Lo llama `_physics_process`; la prueba, a mano.
func tick() -> void:
	if _attack_cooldown > 0:
		_attack_cooldown -= 1
	if _dodge_cooldown > 0:
		_dodge_cooldown -= 1
	if dodging:
		# Paso a paso de 1 px para que choque como al andar.
		var per_frame := ceili(float(DesignTokens.DODGE_DISTANCE) / _frames(DesignTokens.DUR_DODGE))
		for _i in per_frame:
			world.body.step(_dodge_dir, false)
		_dodge_frames -= 1
		if _dodge_frames <= 0:
			dodging = false
			world.body.input_enabled = true
	_timer += 1
	match foe:
		Foe.REST:
			map.fight_face(Vector2i(hero_feet()))
			if _timer >= _frames(DesignTokens.DUR_MONSTER_REST):
				_enter(Foe.APPROACH)
		Foe.APPROACH:
			var far := (hero_feet() - monster_feet()).length() > DesignTokens.MONSTER_KEEP_DISTANCE
			if not far or map.fight_step(Vector2i(hero_feet())) or _timer > _frames(2.0):
				map.fight_face(Vector2i(hero_feet()))
				_begin_telegraph()
		Foe.TELEGRAPH:
			if _timer >= _frames(DesignTokens.DUR_TELEGRAPH):
				_strike()
				_enter(Foe.REST)
		Foe.STUNNED:
			if _timer >= _frames(DesignTokens.DUR_STUN_WINDOW):
				counters = 0
				_say_cause("se rehace")
				_enter(Foe.REST)
	hud.queue_redraw()
	_ground.queue_redraw()


func _enter(f: Foe) -> void:
	foe = f
	_timer = 0


func _begin_telegraph() -> void:
	strike_at = hero_feet()
	_enter(Foe.TELEGRAPH)


func _strike() -> void:
	var h := hero()
	if h == null:
		return
	if dodging or hero_feet().distance_to(strike_at) > DesignTokens.MONSTER_ATTACK_RADIUS:
		return
	var skill: Skill = monster.skills.pick_random() if not monster.skills.is_empty() \
		else SkillLibrary.basic_attack()
	var dealt := h.take_damage(skill.calculate_damage(monster))
	GameAudio.play("hit")
	hud.number(hero_feet(), str(dealt), DesignTokens.TV_RUST_4)
	if h.is_alive():
		return
	var next := _first_alive(active)
	if next < 0:
		toast.emit(PackedStringArray(["El grupo cae. Vuelve a la entrada del bosque."]))
		_end(Enums.BattleResult.DEFEAT)
		return
	var fallen := h.display_name
	active = next
	_apply_sheet()
	toast.emit(PackedStringArray(["%s queda fuera de combate. Sigue %s." % [fallen, hero().display_name]]))
