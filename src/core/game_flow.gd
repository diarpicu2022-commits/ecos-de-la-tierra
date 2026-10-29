class_name GameFlow
extends Node

## El paso mundo ↔ combate (contrato «Persiana», docs/ux/anexos/
## 2026-10-28-encuentros.md, §3 a §5).
##
## Al tocar al monstruo: la persiana se cierra desde su fila y desde el lado
## de quien empieza, el mundo se para y se oculta, entra «Ceniza y Brasa» con
## el grupo de `GameState` y el monstruo de la región, y la persiana se abre.
## Al terminar y confirmar: la persiana se cierra, vuelve el mundo y se abre.
##
## - Victoria: el monstruo ya no está, la persiana se abre sobre la zona aún
##   enferma y la ola de purificación sale de la casilla del combate.
## - Huida: el monstruo sigue ahí, se rinde, e Ilan tiene DUR_FLEE_GRACE sin
##   contacto posible.
## - Derrota: vuelta a la casilla de llegada a la zona con el grupo a 1 PV,
##   hasta que exista el guardado (parte 9).

signal battle_over(result: Enums.BattleResult)

## Combate de `Encounters` por zona.
const ZONE_ENCOUNTER := {"ashen_forest": 0, "tar_basin": 1, "broken_coast": 2,
	"withered_plain": 3, "waning_peak": 4, "greed_crypt": 5}

@export var start_zone := "valdehoja"
@export var start_cell := Vector2i(9, 25)

var world := WorldRoot.new()
var blinds := BattleBlinds.new()
var screen: BattleScreen = null
var result: int = -1
## Ventaja del último contacto y lado del que se cerró la persiana.
var advantage := MapMonster.Advantage.NONE
var awaiting_confirm := false
## Casilla del monstruo al tocarlo: de ahí sale la ola si se gana.
var battle_cell := Vector2i.ZERO

var _battle_layer := CanvasLayer.new()
var _enemy: Monster = null


func _ready() -> void:
	world.start_zone = start_zone
	world.start_cell = start_cell
	add_child(world)
	_battle_layer.layer = 15
	add_child(_battle_layer)
	var blinds_layer := CanvasLayer.new()
	blinds_layer.layer = 20
	blinds_layer.add_child(blinds)
	add_child(blinds_layer)
	world.encounter.connect(_on_encounter)


func _on_encounter(adv: MapMonster.Advantage) -> void:
	advantage = adv
	battle_cell = world.monster.cell
	var xf := world.get_viewport().get_canvas_transform()
	var mon_at := xf * world.monster.position
	var ilan_x := (xf * world.body.global_position).x
	var ilan_side: int = BattleBlinds.Side.LEFT if ilan_x < mon_at.x else BattleBlinds.Side.RIGHT
	var mon_side: int = BattleBlinds.Side.RIGHT if ilan_side == BattleBlinds.Side.LEFT else BattleBlinds.Side.LEFT
	var from: int = BattleBlinds.Side.BOTH
	if adv == MapMonster.Advantage.PLAYER:
		from = ilan_side
	elif adv == MapMonster.Advantage.MONSTER:
		from = mon_side
	blinds.close(int(mon_at.y) - DesignTokens.TILE_SIZE / 2, from)
	await blinds.finished
	world.visible = false
	world.process_mode = Node.PROCESS_MODE_DISABLED
	_start_battle()
	blinds.open()
	await blinds.finished


func _start_battle() -> void:
	var index: int = ZONE_ENCOUNTER[world.zone_id]
	var state := get_node("/root/GameState")
	state.ensure_party(index)
	result = -1
	screen = BattleScreen.new()
	screen.region = world.zone_id
	screen.companions_auto = true
	screen.minds = state.party_minds
	screen.sync = state.party_sync
	_battle_layer.add_child(screen)
	screen.battle_finished.connect(_on_finished)
	_enemy = Encounters.build_monster(index)
	add_child(_enemy)
	var players: Array[Combatant] = []
	for c in state.party:
		players.append(c)
	var enemies: Array[Combatant] = [_enemy]
	var opening := -1
	if advantage == MapMonster.Advantage.PLAYER:
		opening = Enums.Team.PLAYER
	elif advantage == MapMonster.Advantage.MONSTER:
		opening = Enums.Team.ENEMY
	screen.start_battle(players, enemies, state.bag, opening)


func _on_finished(r: Enums.BattleResult) -> void:
	result = r
	awaiting_confirm = true


func _unhandled_input(event: InputEvent) -> void:
	if awaiting_confirm and event.is_action_pressed("confirm"):
		get_viewport().set_input_as_handled()
		leave_battle()


## Vuelve al mundo con el desenlace. Lo llama `confirm`; la prueba, a mano.
func leave_battle() -> void:
	awaiting_confirm = false
	if screen != null and screen._manager != null:
		get_node("/root/GameState").party_sync = screen._manager.sync
	blinds.close(int(blinds.size.y / 2), blinds.side)
	await blinds.finished
	if screen != null:
		screen.queue_free()
		screen = null
	if _enemy != null:
		_enemy.queue_free()
		_enemy = null
	world.visible = true
	world.process_mode = Node.PROCESS_MODE_INHERIT
	var state := get_node("/root/GameState")
	var zone := world.zone_id
	match result:
		Enums.BattleResult.VICTORY:
			# El monstruo se va con el combate; la zona sigue enferma hasta la ola.
			if world.monster != null:
				var body_node := world.solids.get_node_or_null("solid_" + world.monster.name)
				if body_node != null:
					body_node.queue_free()
				world.monster.queue_free()
				world.monster = null
		Enums.BattleResult.FLED:
			if world.monster != null:
				world.monster.force(MapMonster.State.GIVE_UP)
		Enums.BattleResult.DEFEAT:
			for c in state.party:
				c.hp = 1
			world.enter_zone(zone, world.arrival_cell)
	blinds.open()
	await blinds.finished
	if result == Enums.BattleResult.VICTORY:
		await world.purify_wave(battle_cell)
	# Solo con el mundo entero a la vista: la gracia no se gasta tras la persiana.
	world.body.input_enabled = true
	if result == Enums.BattleResult.FLED and world.monster != null:
		world.monster.grace_frames = roundi(DesignTokens.DUR_FLEE_GRACE
			* Engine.physics_ticks_per_second)
		world.monster.active = true
	battle_over.emit(result)
