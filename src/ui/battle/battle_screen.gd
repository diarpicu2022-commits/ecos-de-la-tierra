class_name BattleScreen
extends Control

## Pantalla de batalla completa.
##
## **Composición diagonal**, al estilo de los RPG de GBA. El grupo se escalona
## abajo a la izquierda y los enemigos arriba a la derecha, de modo que los dos
## bandos se miran y el hueco entre ellos es el campo. La versión anterior
## ponía al enemigo centrado arriba y al grupo en fila recta abajo: todo
## paralelo al borde, sin diagonal, sin solapamiento y sin sombras, y se leía
## como un diagrama en vez de como una escena.
##
## La profundidad sale de tres cosas, ninguna de ellas escalar el sprite (una
## fuente de píxeles solo admite escalas enteras):
##
##   1. La altura en pantalla. Más arriba es más lejos.
##   2. El solapamiento. Quien está más cerca se dibuja encima.
##   3. La sombra. Más grande y más marcada cuanto más cerca.
##
## Las fichas van en la esquina **contraria** a sus sprites, como en los RPG de
## consola portátil: la del enemigo arriba a la izquierda, la del grupo abajo a
## la derecha. Así ningún panel tapa a quien describe.
##
## Reparto vertical de los 270 px:
##
##   cola de turnos     y   0..13    franja horizontal
##   campo              y  13..180   los dos bandos y sus fichas
##   banda inferior     y 180..270   menú · mensaje · ventana del grupo
##
## **Ritmo.** `BattleManager` resuelve toda la ronda de forma síncrona: cuando
## devuelve el control, el turno de los enemigos ya ocurrió entero. La pantalla
## encola los eventos y los reproduce uno a uno, volcando en cada paso las
## barras que estaban en pausa, y `confirm` adelanta el paso.

signal battle_finished(result: Enums.BattleResult)

## A 640 × 360, el viewport del juego (contrato «Piel nueva»). Hasta el
## 2026-11-02 seguía a 480 × 270 y en el juego ocupaba solo una esquina.
const SCREEN := Vector2(640, 360)

# --- Bandas ------------------------------------------------------------------
const TURNS_HEIGHT := 13.0
const FIELD_TOP := 13.0
const FIELD_HEIGHT := 167.0
const BAND_TOP := 270.0

## Línea del horizonte dentro del campo. Los enemigos se apoyan cerca de ella
## (lejos) y el grupo muy por debajo (cerca).
const HORIZON := 104.0

# --- Colocación de los dos bandos (sistema de diseño, combate_enfermo.png) ----
## Sprite de espaldas del grupo: la rotación norte-este de PixelLab al doble
## (`battle-back: 96px`). Es la caja de referencia para las cifras.
const CHARACTER_SPRITE := Vector2(54, 90)
const PARTY_SLOTS := 5
## Pies del grupo, sobre su plataforma (centro 160, 268): el primero delante a
## la izquierda y los demás un paso a la derecha y 8 px más atrás.
const PARTY_FEET := Vector2(150, 276)
const PARTY_STEP := 70.0
const PARTY_BACK := 8.0
## Distancia máxima entre el primero y el último.
const PARTY_SPAN := 228.0

## Pies del monstruo, sobre su plataforma (centro 470, 176).
const ENEMY_SOLO := Vector2(470, 184)
## Con más de uno, los siguientes se escalonan hacia atrás a la izquierda.
const ENEMY_STEP := Vector2(-96, -14)

# --- Interfaz (paso 2 del rediseño del combate: sus marcos) --------------------
const MENU_RECT := Rect2(Vector2(432, 284), Vector2(204, 66))
const MESSAGE_RECT := Rect2(Vector2(6, 282), Vector2(420, 72))
## Filas del grupo (`PartyRow`): desde (456, 196), una cada 27 px. Se ven tres
## como en el sistema; con más miembros, las tres que rodean a quien tiene el
## turno.
const PARTY_WINDOW := Rect2(Vector2(456, 196), Vector2(176, 78))
const PARTY_ROW_STEP := 27.0
const PARTY_ROWS_SHOWN := 3

## Ficha del enemigo enfocado, arriba a la izquierda (`EnemyPlate`, 10, 10).
const ENEMY_PANEL := Vector2(10, 10)

## Sprites del sistema de diseño (`tools/gen_tierra_viva_cast.py`) y fondos
## (`tools/gen_tierra_viva_battle.py`).
const PARTY_BACK_DIR := "res://assets/sprites/party/tierra_viva/"
const BACKGROUND_DIR := "res://assets/sprites/battle/tierra_viva/"

## Cuánto se queda en pantalla cada línea del registro antes de pasar sola a
## la siguiente: depende de lo que hay que leer. Con 0,75 s fijos no se
## entendía (Juan José Rueda, 2026-11-03). `confirm` la adelanta.
const LOG_READ_BASE := 1.2
const LOG_READ_PER_CHAR := 0.045
const LOG_READ_MIN := 1.8
## Tiempo de más en los momentos que cambian la estrategia.
const LOG_BEAT_EXTRA := 0.8
## El aviso de ronda es corto y no explica nada.
const LOG_ROUND_SECONDS := 1.2
## Durante este tiempo `confirm` no adelanta: una pulsación de más no se come
## una línea sin que llegue a verse.
const LOG_MIN_SHOW := 0.25

enum Phase { IDLE, PLAYING, CHOOSING, FINISHED }

## Región del combate, por id de zona (contrato «Persiana» §4). Vacía: el
## fondo genérico de ceniza de la parte de batalla.
var region := ""
## IA-5 (contrato «Orden de líder»): con true, el menú solo se abre para el
## líder, Tab cambia la orden y los compañeros deciden solos. Las mentes y la
## sintonía llegan de GameState y vuelven allí al terminar.
var companions_auto := false
var minds: Dictionary = {}
var sync: float = DesignTokens.SYNC_START

## Las tres órdenes de grupo, con la etiqueta corta del aviso y su explicación.
const ORDERS := [
	{"label": "SEGUIDME", "description": "Orden: hacen lo que te ven hacer a ti."},
	{"label": "ATAJAD", "description": "Orden: atajad la causa. Usan su contramedida si pueden."},
	{"label": "CUBRÍOS", "description": "Orden: cubríos. Curan y usan la bolsa con quien esté tocado."},
]

const ORDER_KEY_HINT := "Tab para cambiarla."

var _font: Font = null
## Parallax de entrada: cuadros desde que empezó el combate. Cada capa del
## fondo entra desplazada BATTLE_PARALLAX px por su profundidad y llega a su
## sitio en DUR_BATTLE_BLINDS, mientras se abre la persiana.
var _entry_frame := 0
var _manager: BattleManager = null
var _phase: int = Phase.IDLE

var _monster_views: Array[MonsterView] = []
var _huds: Array[PartyMemberHud] = []
var _party_art: Array[Texture2D] = []
## Fondo de la región en sus dos estados: enfermo mientras la causa sigue
## activa y sano cuando todos los monstruos están purificados.
var _backgrounds := {}
var _drawn_pure := false
var _menu: ActionMenu = null
var _overlay: ResultOverlay = null
## Por encima de cualquier sprite del campo, que llevan como mucho su total.
const NUMBERS_Z := 16

var _numbers: DamageNumbers = null
## Cifras que ya ocurrieron en las reglas pero todavía no se han enseñado. Se
## sueltan al ritmo del registro, igual que las barras.
var _pending_numbers: Array[Dictionary] = []

var _queue: Array[Dictionary] = []
var _message: String = ""
var _message_tone: Color = DesignTokens.TEXT_PRIMARY
var _round: int = 0
var _step_timer: Timer = null
var _shown_at_msec := 0
## Indicación del desenlace si no es la de la demo: en el mundo, seguir jugando.
var continue_hint := ""

# Estado de la elección en curso.
## Cuántas veces se rehízo un monstruo. No es estadística: es la prueba que se
## le enseña al jugador cuando pierde, en lugar de darle un consejo.
var _regenerations: int = 0
var _result: int = Enums.BattleResult.ONGOING

var _actor: Character = null
var _pending_skill: Skill = null
var _pending_item: Item = null
var _focused_enemy: int = 0
## Mando de la raíz por el que se entró al submenú: al cancelar se vuelve a él.
var _root_focus: int = 0


func _ready() -> void:
	DesignTokens.load_settings()
	_font = load(DesignTokens.FONT_PATH)
	custom_minimum_size = SCREEN
	size = SCREEN

	for key in ["ilan", "bruma", "coral", "nix", "suri"]:
		_party_art.append(load(PARTY_BACK_DIR + key + "_back.png"))
	var zone := region if region != "" else "ashen_forest"
	for state in ["enfermo", "sano"]:
		_backgrounds[state] = load("%s%s_%s.png" % [BACKGROUND_DIR, zone, state])

	_menu = ActionMenu.new()
	_menu.position = options_rect().position
	_menu.size = options_rect().size
	_menu.plate = true
	add_child(_menu)
	_menu.option_focused.connect(_on_option_focused)
	_menu.option_chosen.connect(_on_option_chosen)
	_menu.cancelled.connect(_on_menu_cancelled)
	_menu.close()

	_numbers = DamageNumbers.new()
	_numbers.size = SCREEN
	# Los sprites llevan z_index positivo por orden de fila: la cifra va encima.
	_numbers.z_index = NUMBERS_Z

	_overlay = ResultOverlay.new()

	_step_timer = Timer.new()
	_step_timer.one_shot = true
	_step_timer.timeout.connect(_advance_queue)
	add_child(_step_timer)


# --- Anclajes del layout -----------------------------------------------------

## Esquina superior izquierda del sprite de espaldas del miembro `index` de
## `total`. El 0 va delante a la izquierda; el resto, a su derecha y un poco
## más atrás, como en la referencia del sistema.
static func character_anchor(index: int, total: int = PARTY_SLOTS) -> Vector2:
	var feet := character_feet(index, total)
	return Vector2(roundf(feet.x - CHARACTER_SPRITE.x * 0.5), roundf(feet.y - CHARACTER_SPRITE.y))


static func character_feet(index: int, total: int = PARTY_SLOTS) -> Vector2:
	# Con más de tres, el paso se encoge para que nadie se salga por la izquierda
	# (con cinco, a 70 px Ilan quedaba cortado).
	var step: float = minf(PARTY_STEP, PARTY_SPAN / maxf(1.0, total - 1.0))
	var x: float = PARTY_FEET.x + (index - (total - 1) * 0.5) * step
	var y: float = PARTY_FEET.y - (0.0 if index == 0 else PARTY_BACK)
	return Vector2(roundf(x), y)


## Dónde pisa el enemigo `index` de `total`. El 0 es el más cercano.
static func enemy_anchor(index: int, total: int) -> Vector2:
	if total <= 1:
		return ENEMY_SOLO
	return ENEMY_SOLO + ENEMY_STEP * index


## Fila `index` dentro de la ventana del grupo.
static func hud_row_position(index: int) -> Vector2:
	return PARTY_WINDOW.position + Vector2(0, index * PARTY_ROW_STEP)


## Enseña las filas que caben, alrededor de quien tiene el turno.
func _layout_huds(active: int = 0) -> void:
	var n := _huds.size()
	var start := clampi(active - 1, 0, maxi(0, n - PARTY_ROWS_SHOWN))
	for i in n:
		_huds[i].visible = i >= start and i < start + PARTY_ROWS_SHOWN
		_huds[i].position = hud_row_position(i - start)


static func message_rect() -> Rect2:
	return MESSAGE_RECT


static func options_rect() -> Rect2:
	return MENU_RECT


# --- Arranque del combate ----------------------------------------------------

func start_battle(players: Array[Combatant], enemies: Array[Combatant],
		inventory: Inventory, opening_team: int = -1) -> void:
	_manager = BattleManager.new()
	_manager.opening_team = opening_team
	_manager.companions_auto = companions_auto
	_manager.minds = minds
	_manager.sync = sync
	add_child(_manager)

	_build_party_huds(players)
	_build_monster_views(enemies)

	_manager.round_started.connect(_on_round_started)
	_manager.turn_started.connect(_on_turn_started)
	_manager.action_resolved.connect(_on_action_resolved)
	_manager.combatant_defeated.connect(_on_combatant_defeated)
	_manager.enemy_joined.connect(_on_enemy_joined)
	_manager.player_input_required.connect(_on_player_input_required)
	_manager.battle_ended.connect(_on_battle_ended)

	# Las vistas quedan en pausa el resto del combate: solo avanzan cuando la
	# reproducción del registro las vuelca.
	# La capa del desenlace se añade la última: en Godot los hijos se pintan en
	# orden, así que ser el último es lo que garantiza que quede arriba.
	# Las cifras van por encima de los sprites y por debajo del desenlace.
	for layer in [_numbers, _overlay]:
		if layer.get_parent() != null:
			remove_child(layer)
		add_child(layer)
	_numbers.clear()
	_overlay.hide_result()

	_set_views_paused(true)
	_entry_frame = 0
	_manager.start_battle(players, enemies, inventory)
	_start_playback()


func _build_party_huds(players: Array) -> void:
	for hud in _huds:
		hud.queue_free()
	_huds.clear()
	for i in range(mini(players.size(), PARTY_SLOTS)):
		var hud := PartyMemberHud.new()
		hud.position = hud_row_position(i)
		add_child(hud)
		hud.bind(players[i] as Character)
		hud.set_paused(true)
		_huds.append(hud)
		_watch_numbers(players[i] as Combatant)
	_layout_huds()


func _build_monster_views(enemies: Array) -> void:
	for view in _monster_views:
		view.queue_free()
	_monster_views.clear()
	for i in range(enemies.size()):
		var view := MonsterView.new()
		add_child(view)
		view.bind(enemies[i] as Monster)
		view.set_paused(true)
		_monster_views.append(view)
		(enemies[i] as Monster).regenerated.connect(_on_regenerated)
		_watch_numbers(enemies[i] as Combatant)
	_focused_enemy = 0
	_layout_monsters()


## Coloca a los enemigos por el campo. La ficha completa la enseña solo el que
## está en el punto de mira; los demás se quedan en el sprite, porque tres
## fichas de 176 px no caben en 480 y competirían entre ellas.
func _layout_monsters() -> void:
	var total: int = _monster_views.size()
	for i in range(total):
		var view: MonsterView = _monster_views[i]
		var anchor := enemy_anchor(i, total)
		view.position = anchor
		view.sprite_offset = Vector2.ZERO
		view.show_panel = i == _focused_enemy
		# La ficha va siempre arriba a la izquierda, la esquina contraria a los
		# sprites enemigos: así ningún panel tapa a quien describe.
		view.panel_offset = ENEMY_PANEL - anchor
		# De lejos a cerca: el enemigo más cercano (índice 0) se dibuja encima.
		# El valor tiene que ser **positivo**: con z_index negativo el hijo se
		# va por detrás del fondo que pinta esta misma pantalla y desaparece.
		view.z_index = total - i
		view.queue_redraw()


## Conecta a un combatiente para escribir sus cifras. Se guarda a quién
## pertenece cada una: la señal por sí sola no dice sobre qué sprite va.
func _watch_numbers(combatant: Combatant) -> void:
	combatant.damage_taken.connect(
		func(amount: int, _eco: Enums.EcoType, resisted: bool) -> void:
			_pending_numbers.append({
				"target": combatant, "amount": amount, "resisted": resisted,
				"healing": false,
			})
	)
	combatant.healing_received.connect(
		func(amount: int) -> void:
			_pending_numbers.append({
				"target": combatant, "amount": amount, "resisted": false,
				"healing": true,
			})
	)


func _on_regenerated(_current_hp: int) -> void:
	_regenerations += 1


func _set_views_paused(value: bool) -> void:
	for view in _monster_views:
		view.set_paused(value)
	for hud in _huds:
		hud.set_paused(value)


func _flush_views() -> void:
	for view in _monster_views:
		view.flush()
	for hud in _huds:
		hud.flush()
	_release_numbers()


## Las dos líneas que enseñan la regla del juego llevan su sonido, a la vez que
## su color.
func _play_line_sound(tone: Color) -> void:
	if tone == DesignTokens.TEXT_PURIFIED:
		GameAudio.play("purify")
	elif tone == DesignTokens.TEXT_WARNING:
		GameAudio.play("regen")


## Suelta las cifras acumuladas sobre el sprite de cada objetivo, con su sonido.
func _release_numbers() -> void:
	for pending in _pending_numbers:
		if bool(pending["healing"]):
			GameAudio.play("heal")
		else:
			GameAudio.play("hit_resisted" if bool(pending["resisted"]) else "hit")
		var target: Combatant = pending["target"] as Combatant
		var anchor: Vector2 = _anchor_for(target)
		if bool(pending["healing"]):
			# La curación no puede ir en verde: el verde solo significa
			# «la causa se atajó». Va en el blanco de la rampa de interfaz.
			_numbers.spawn(anchor, "+%d" % int(pending["amount"]),
					DesignTokens.TV_UI_6)
		elif bool(pending["resisted"]):
			# Golpe que el monstruo se quita de encima: apagado y con `~`, en el
			# `ui-4` de `combat_mock.py`. Es la regla del juego, dicha con una cifra.
			_numbers.spawn(anchor, "~%d" % int(pending["amount"]),
					DesignTokens.TV_UI_4)
		else:
			_numbers.spawn(anchor, str(int(pending["amount"])), DesignTokens.TV_GOLD_4)
	_pending_numbers.clear()


## Punto sobre el que se escribe la cifra: el borde superior de su sprite.
func _anchor_for(combatant: Combatant) -> Vector2:
	for view in _monster_views:
		if view.monster == combatant:
			return view.position + view.top_center() + Vector2(0, 10.0)
	for i in range(_huds.size()):
		if _huds[i].character == combatant:
			return character_anchor(i, _huds.size()) + Vector2(
					CHARACTER_SPRITE.x * 0.5, 6.0)
	return Vector2(SCREEN.x * 0.5, 60.0)


# --- Cola de eventos ---------------------------------------------------------

## Cada evento viaja con la cola de turnos del momento en que ocurrió. Como la
## reproducción va por detrás de las reglas, sin esto la cola mostraría el
## estado final mientras el registro narra todavía el principio de la ronda.
func _snapshot() -> Array[Combatant]:
	return _manager.get_pending_turns()


func _on_round_started(round_number: int) -> void:
	_queue.append({"type": "round", "round": round_number, "order": _snapshot()})


func _on_turn_started(combatant: Combatant) -> void:
	_queue.append({"type": "turn", "combatant": combatant, "order": _snapshot()})


## Cada línea del registro es un paso propio: si se volcaran juntas, el jugador
## vería cinco cosas a la vez y no relacionaría ninguna con su efecto.
##
## El motor resuelve la ronda entera antes de que se enseñe nada. Por eso cada
## acción se lleva aquí lo que acaba de pasar (PV, cifras, purificación) y lo
## suelta con su primera línea: primero baja la vida del monstruo y, cuando le
## toca actuar a él, la tuya (Juan José Rueda, 2026-11-03).
func _on_action_resolved(log_lines: Array) -> void:
	var effects := _take_effects()
	for line in log_lines:
		_queue.append({"type": "log", "text": str(line), "order": _snapshot(),
			"effects": effects})
		effects = {}


## Lo que ha pasado desde la última acción y aún no se ha enseñado.
func _take_effects() -> Dictionary:
	var monsters := []
	for view in _monster_views:
		monsters.append([view, view.take_pending()])
	var party := []
	for hud in _huds:
		party.append([hud, hud.take_pending()])
	var numbers := _pending_numbers.duplicate()
	_pending_numbers.clear()
	return {"monsters": monsters, "party": party, "numbers": numbers}


func _show_effects(effects: Dictionary) -> void:
	if effects.is_empty():
		return
	for entry in effects["monsters"]:
		if is_instance_valid(entry[0]):
			entry[0].show_pending(entry[1])
	for entry in effects["party"]:
		if is_instance_valid(entry[0]):
			entry[0].show_pending(entry[1])
	_pending_numbers.assign(effects["numbers"])
	_release_numbers()


func _on_combatant_defeated(combatant: Combatant) -> void:
	_queue.append({
		"type": "log", "beat": true, "order": _snapshot(),
		"text": "%s queda fuera de combate." % combatant.display_name,
	})


func _on_enemy_joined(enemy: Combatant) -> void:
	_queue.append({"type": "spawn", "enemy": enemy, "order": _snapshot()})


func _on_player_input_required(character: Character) -> void:
	_queue.append({"type": "input", "character": character, "order": _snapshot()})


func _on_battle_ended(result: Enums.BattleResult) -> void:
	_queue.append({"type": "end", "result": result})


func _start_playback() -> void:
	_phase = Phase.PLAYING
	_advance_queue()


func _advance_queue() -> void:
	if _queue.is_empty():
		if _phase == Phase.PLAYING:
			_phase = Phase.IDLE
		return

	var event: Dictionary = _queue.pop_front()

	match event["type"]:
		"turn":
			# El cambio de turno no consume tiempo propio: se enciende la ficha
			# y se pasa de inmediato a lo que ese turno produjo.
			_advance_queue()
			return
		"round":
			_round = int(event["round"])
			_set_message("-- Ronda %d --" % _round, DesignTokens.TEXT_SECONDARY)
			_schedule(LOG_ROUND_SECONDS)
		"log":
			_show_effects(event.get("effects", {}))
			_set_message(str(event["text"]), _tone_for(str(event["text"])))
			_play_line_sound(_message_tone)
			_schedule(_read_seconds(str(event["text"]), event.get("beat", false)))
		"spawn":
			var view := MonsterView.new()
			add_child(view)
			view.bind(event["enemy"] as Monster)
			view.set_paused(true)
			_monster_views.append(view)
			(event["enemy"] as Monster).regenerated.connect(_on_regenerated)
			_watch_numbers(event["enemy"] as Combatant)
			_layout_monsters()
			_set_message("Se suma al combate: %s"
					% (event["enemy"] as Combatant).display_name,
					DesignTokens.TEXT_WARNING)
			_schedule(_read_seconds(_message, true))
		"input":
			_flush_views()
			_begin_choice(event["character"] as Character)
		"end":
			_flush_views()
			_finish(int(event["result"]))
	queue_redraw()


func _schedule(seconds: float) -> void:
	_step_timer.start(seconds)
	_shown_at_msec = Time.get_ticks_msec()


## Tiempo de lectura de una línea del registro.
func _read_seconds(text: String, beat: bool) -> float:
	var seconds := maxf(LOG_READ_MIN, LOG_READ_BASE + text.length() * LOG_READ_PER_CHAR)
	return seconds + LOG_BEAT_EXTRA if beat else seconds


## Las líneas que anuncian regeneración o purificación se tiñen, porque son las
## dos que enseñan la regla central del juego.
func _tone_for(text: String) -> Color:
	if text.contains("deja de regenerarse"):
		return DesignTokens.TEXT_PURIFIED
	if text.contains("rehace") or text.contains("regenera"):
		return DesignTokens.TEXT_WARNING
	return DesignTokens.TEXT_PRIMARY


func _set_message(text: String, tone: Color) -> void:
	_message = text
	_message_tone = tone
	queue_redraw()


# --- Elección del jugador ----------------------------------------------------

func _begin_choice(character: Character) -> void:
	_phase = Phase.CHOOSING
	_actor = character
	_pending_skill = null
	_pending_item = null
	for i in range(_huds.size()):
		_huds[i].set_active_turn(_huds[i].character == character)
		if _huds[i].character == character:
			_layout_huds(i)
	_root_focus = 0
	_open_root_menu()


func _open_root_menu() -> void:
	_menu.set_entries(_root_entries(), true, _root_focus)
	_menu.open()


## Los cuatro mandos del `CommandMenu`, en el orden de la rejilla. Sus marcos son
## fijos por contrato: lo deshabilitado no se apaga, dice el porqué en el aviso.
func _root_entries() -> Array:
	var skills: Array[Skill] = _actor.get_known_skills()
	var items: Array[Item] = _manager.inventory.get_battle_items()
	var hint := _order_hint()
	return [
		{"label": "LUCHAR", "frame": TvFrame.CMD_FIGHT, "cost": -1, "enabled": true, "kind": "attack",
			"description": "Golpe directo. No ataja la causa: el monstruo se rehará." + hint},
		{
			"label": "ECO", "frame": TvFrame.CMD_ECO, "cost": -1, "kind": "skills",
			"enabled": not skills.is_empty(),
			# Una opcion apagada sin explicacion solo frustra. Si el personaje
			# no tiene ninguna habilidad aqui, se dice, y ademas se dice que
			# eso es cosa suya y no del juego: otro del grupo si la tendra.
			"description": ("Habilidades Ecológicas. Solo la correcta purifica."
					if not skills.is_empty()
					else "%s aún no conoce ninguna Habilidad Ecológica. Otro del grupo sí." % _actor.display_name) + hint,
		},
		{
			"label": "BOLSA", "frame": TvFrame.CMD_BAG, "cost": -1, "kind": "items",
			"enabled": not items.is_empty(),
			"description": ("Objetos de curación del grupo." if not items.is_empty()
					else "La bolsa está vacía.") + hint,
		},
		{"label": "HUIR", "frame": TvFrame.CMD_RUN, "cost": -1, "enabled": true, "kind": "flee",
			"description": "Retirarse. Depende de la velocidad del grupo." + hint},
	]


## La orden es del líder con los compañeros en automático.
func _order_applies() -> bool:
	return companions_auto and _manager != null and _actor == _manager.leader


## Segunda línea del aviso en la raíz: que la orden no quede escondida en Tab.
func _order_hint() -> String:
	if not _order_applies():
		return ""
	return "\nOrden: %s. %s" % [ORDERS[_manager.order]["label"], ORDER_KEY_HINT]


## Tab: pasa a la orden siguiente sin gastar el turno y sin mover el foco.
func _cycle_order() -> void:
	_manager.order = (_manager.order + 1) % ORDERS.size()
	_menu.replace_entries(_root_entries())
	GameAudio.play("ui_confirm")
	_set_message("%s %s" % [ORDERS[_manager.order]["description"], ORDER_KEY_HINT],
			DesignTokens.TEXT_SECONDARY)


func _open_skill_menu() -> void:
	var entries: Array[Dictionary] = []
	# Se listan las que el personaje sabe, no solo las que puede pagar: el
	# coste en rojo enseña cuánta energía falta, y una opción escondida no
	# enseña nada.
	for skill in _actor.get_known_skills():
		entries.append({
			"label": skill.display_name,
			"cost": skill.energy_cost,
			"enabled": _actor.has_energy(skill.energy_cost),
			"kind": "skill", "skill": skill,
			"description": skill.description,
		})
	_menu.set_entries(entries)
	_menu.open()


func _open_item_menu() -> void:
	var entries: Array[Dictionary] = []
	for item in _manager.inventory.get_battle_items():
		entries.append({
			"label": "%s x%d" % [item.display_name,
					_manager.inventory.get_amount(item)],
			"cost": -1, "enabled": true, "kind": "item", "item": item,
			"description": item.description,
		})
	_menu.set_entries(entries)
	_menu.open()


## Menú de objetivos. Se usa el mismo componente que todo lo demás, así que el
## jugador no tiene que aprender otra forma de elegir.
func _open_target_menu(allies: bool) -> void:
	var entries: Array[Dictionary] = []
	var pool: Array[Combatant] = _manager.player_party if allies \
			else _manager.enemy_party
	for combatant in pool:
		if not combatant.is_alive():
			continue
		entries.append({
			"label": combatant.display_name,
			"cost": -1, "enabled": true, "kind": "target", "target": combatant,
			"description": "%d/%d PV" % [combatant.hp, combatant.max_hp],
		})
	if entries.size() == 1:
		_commit(entries[0]["target"] as Combatant)
		return
	_menu.set_entries(entries)
	_menu.open()


func _on_option_focused(entry: Dictionary) -> void:
	_set_message(str(entry.get("description", "")), DesignTokens.TEXT_SECONDARY)
	# Al recorrer objetivos enemigos, la ficha sigue al cursor: el jugador ve
	# de quién está hablando antes de confirmar.
	if entry.get("kind", "") == "target":
		var target: Variant = entry.get("target")
		for i in range(_monster_views.size()):
			if _monster_views[i].monster == target:
				_focused_enemy = i
				_layout_monsters()
				break


func _on_option_chosen(entry: Dictionary) -> void:
	match str(entry.get("kind", "")):
		"attack":
			_root_focus = _menu.focused
			_pending_skill = null
			_pending_item = null
			_open_target_menu(false)
		"skills":
			_root_focus = _menu.focused
			_open_skill_menu()
		"items":
			_root_focus = _menu.focused
			_open_item_menu()
		"flee":
			_submit(BattleAction.flee(_actor))
		"skill":
			_pending_skill = entry["skill"] as Skill
			if _pending_skill.targets_all:
				_commit(null)
			else:
				_open_target_menu(_is_support(_pending_skill))
		"item":
			_pending_item = entry["item"] as Item
			_open_target_menu(true)
		"target":
			_commit(entry["target"] as Combatant)


func _is_support(skill: Skill) -> bool:
	return skill is EcoSkill and (skill as EcoSkill).ally_healing > 0


func _commit(target: Combatant) -> void:
	if _pending_skill != null:
		_submit(BattleAction.use_skill(_actor, _pending_skill, target))
	elif _pending_item != null:
		_submit(BattleAction.use_item(_actor, _pending_item, target))
	else:
		_submit(BattleAction.attack(_actor, target))


func _submit(action: BattleAction) -> void:
	_menu.close()
	for hud in _huds:
		hud.set_active_turn(false)
	_phase = Phase.PLAYING
	# Todo lo que ocurra aquí dentro se encola; nada se dibuja todavía.
	_manager.submit_action(action)
	_advance_queue()


## Cancelar retrocede un paso en vez de cerrar el turno: perder la elección
## entera por pulsar Escape sería un castigo desproporcionado.
func _on_menu_cancelled() -> void:
	# En la raíz, Escape ya volvió al mando anterior dentro del menú.
	if _phase != Phase.CHOOSING or _menu.is_grid():
		return
	if _pending_skill != null or _pending_item != null:
		_pending_skill = null
		_pending_item = null
		_open_root_menu()
	else:
		_open_root_menu()


func _finish(result: int) -> void:
	_phase = Phase.FINISHED
	_result = result
	_menu.close()
	_set_message("", DesignTokens.TEXT_PRIMARY)
	if result == Enums.BattleResult.VICTORY:
		GameAudio.play_music("")
		GameAudio.play("victory")
	elif result == Enums.BattleResult.DEFEAT:
		GameAudio.play_music("")
		GameAudio.play("defeat")
	_overlay.continue_hint = continue_hint
	_overlay.show_result(result, _regenerations, FIELD_HEIGHT)
	queue_redraw()
	battle_finished.emit(result)


# --- Teclado -----------------------------------------------------------------

## En `_input` y no más abajo: Godot usa Tab para mover el foco de los controles
## y se lo quedaría antes de `_unhandled_input`. Solo en la raíz, como la fila que
## sustituye: en un submenú el aviso está explicando otra cosa.
func _input(event: InputEvent) -> void:
	if _phase == Phase.CHOOSING and event.is_action_pressed("order"):
		get_viewport().set_input_as_handled()
		if _order_applies() and _menu.is_active() and _menu.is_grid():
			_cycle_order()


func _unhandled_input(event: InputEvent) -> void:
	# Adelantar el registro. Solo mientras se reproduce: durante la elección el
	# teclado es del menú.
	if _phase == Phase.PLAYING and event.is_action_pressed("confirm"):
		get_viewport().set_input_as_handled()
		if Time.get_ticks_msec() - _shown_at_msec < LOG_MIN_SHOW * 1000.0:
			return
		_step_timer.stop()
		_advance_queue()


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	_draw_background()
	_draw_enemy_ground()
	_draw_party()
	_draw_bands()
	_draw_message()


func _physics_process(_delta: float) -> void:
	# El fondo pasa a sano en cuanto el último monstruo se purifica.
	if _all_purified() != _drawn_pure:
		_drawn_pure = not _drawn_pure
		queue_redraw()
	var frames := roundi(DesignTokens.DUR_BATTLE_BLINDS * Engine.physics_ticks_per_second)
	if region != "" and _entry_frame < frames:
		_entry_frame += 1
		queue_redraw()


## Desplazamiento de la capa `depth` (1 lejos, 3 cerca) en el parallax de
## entrada, en píxeles enteros. Con movimiento reducido, quieto.
func parallax_offset(depth: int) -> int:
	if DesignTokens.reduced_motion:
		return 0
	var frames := roundi(DesignTokens.DUR_BATTLE_BLINDS * Engine.physics_ticks_per_second)
	var t := clampf(float(_entry_frame) / frames, 0.0, 1.0)
	var eased := 1.0 - pow(1.0 - t, 3.0)
	return roundi((1.0 - eased) * depth * DesignTokens.BATTLE_PARALLAX)


## Fondo del campo: la imagen de la región del sistema de diseño, con las dos
## plataformas ya pintadas. Enfermo mientras quede un monstruo sin purificar;
## sano cuando todos lo están (`combate_purificado.png`).
func _draw_background() -> void:
	var state := "sano" if _all_purified() else "enfermo"
	draw_texture(_backgrounds[state], Vector2.ZERO)


func _all_purified() -> bool:
	if _monster_views.is_empty():
		return false
	for view in _monster_views:
		if view.monster == null or not view.monster.is_purified:
			return false
	return true


## Plataforma elíptica bajo un bando. Es lo que convierte el suelo en un
## escenario: sin ella los dos grupos aparecen sobre una franja de color y la
## escena se queda sin sitio donde ocurrir.
func _platform(center: Vector2, half_width: float, half_height: float) -> void:
	for row in range(int(-half_height), int(half_height) + 1):
		var t: float = float(row) / half_height
		var span: float = half_width * sqrt(maxf(0.0, 1.0 - t * t))
		if span < 1.0:
			continue
		var y: float = center.y + row
		# El borde superior va un tono más claro: es donde daría la luz.
		var tone: Color = DesignTokens.TV_UI_2 if row < -half_height * 0.45 				else DesignTokens.TV_UI_1
		draw_rect(Rect2(Vector2(roundf(center.x - span), y),
				Vector2(roundf(span * 2.0), 1.0)), tone)


## Sombra bajo un combatiente. Es lo que lo pega al suelo: sin ella los sprites
## flotan, que era buena parte de lo que hacía plana la pantalla anterior.
func _shadow(center: Vector2, half_width: float) -> void:
	for row in range(3):
		var shrink: float = half_width * (1.0 - row * 0.3)
		draw_rect(Rect2(Vector2(roundf(center.x - shrink), center.y + row),
				Vector2(roundf(shrink * 2.0), 1.0)), DesignTokens.TV_INK_0)


## Plataforma y sombra de cada enemigo. Se dibujan aquí, en la pantalla, y no
## en `MonsterView`, porque los hijos se pintan **después** del padre: si cada
## vista dibujara su propio suelo, se lo pondría encima al enemigo de delante.
func _draw_enemy_ground() -> void:
	var total: int = _monster_views.size()
	# El primero ya tiene su plataforma en el fondo; los que se suman, la suya.
	for i in range(1, total):
		var feet := enemy_anchor(i, total)
		var depth: float = 1.0 - 0.16 * float(i)
		_platform(feet + Vector2(0, -4), 60.0 * depth, 12.0 * depth)


func _draw_party() -> void:
	var total: int = _huds.size()
	# De lejos a cerca: quien está delante se dibuja encima y tapa al de atrás.
	# El solapamiento es el segundo indicio de profundidad.
	for i in range(total - 1, -1, -1):
		var character: Character = _huds[i].character
		if character == null or i >= _party_art.size():
			continue
		var art: Texture2D = _party_art[i]
		if art == null:
			continue
		var feet := character_feet(i, total)
		var alpha: float = 1.0 if character.is_alive() else 0.3
		var at := Vector2(roundf(feet.x - art.get_width() * 0.5), feet.y - art.get_height())
		draw_texture(art, at, Color(1, 1, 1, alpha))


func _draw_bands() -> void:
	# Sin banda ni ventana: el campo llega al borde y cada fila del grupo
	# lleva su propio marco (sistema de diseño).
	pass


## Interlínea del aviso de papel (`components/DialogBox`: 15 px).
const MESSAGE_LINE := 15.0


## El aviso de papel (`components/DialogBox`, guía §4.0): marco
## `TvFrame.TEXTBOX`, texto `text-on-paper` con su sombra y `▼` cuando hay
## más. Enseña la descripción de la opción enfocada mientras el jugador elige
## y la última línea del registro mientras se resuelve el turno.
func _draw_message() -> void:
	var rect := MESSAGE_RECT
	TvFrame.draw(self, TvFrame.TEXTBOX, rect)
	var pad: float = DesignTokens.SPACE_8 + 2.0
	var y: float = rect.position.y + 18.0
	var ink := _paper_tone(_message_tone)
	for line in _wrap(_message, rect.size.x - pad * 2.0):
		if y > rect.end.y - 6.0:
			break
		TvFrame.text(self, _font, Vector2(rect.position.x + pad, y), line, ink,
				DesignTokens.TV_TEXT_SHADOW_PAPER)
		y += MESSAGE_LINE

	# Indicador de «hay más»: sin él, el jugador no sabe si la pantalla espera
	# una tecla o se quedó colgada.
	if _phase == Phase.PLAYING and not _queue.is_empty():
		draw_string(_font, Vector2(rect.end.x - 14.0, rect.end.y - 7.0),
				"▼", HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY, DesignTokens.TV_RUST_2)


## El tono del registro, llevado al papel: los tonos de la pizarra vieja son
## claros y sobre papel no se leen. Lo normal en `text-on-paper`; lo
## secundario (rondas, descripciones) en `paper-0`; el aviso de que el
## monstruo se rehace en `rust-2`; y que deja de regenerarse en `eco-1`, que
## nunca va solo: la frase lo dice.
func _paper_tone(tone: Color) -> Color:
	if tone == DesignTokens.TEXT_SECONDARY:
		return DesignTokens.TV_PAPER_0
	if tone == DesignTokens.TEXT_WARNING:
		return DesignTokens.TV_RUST_2
	if tone == DesignTokens.TEXT_PURIFIED:
		return DesignTokens.TV_ECO_1
	return DesignTokens.TV_TEXT_ON_PAPER


## Reparte el texto en líneas que quepan, cortando por palabras y respetando los
## saltos de línea que traiga.
func _wrap(text: String, available: float) -> PackedStringArray:
	var lines := PackedStringArray()
	for paragraph in text.split("\n"):
		var current := ""
		for word in paragraph.split(" ", false):
			var candidate: String = word if current.is_empty() else current + " " + word
			if _width(candidate) <= available:
				current = candidate
			else:
				if not current.is_empty():
					lines.append(current)
				current = word
		if not current.is_empty():
			lines.append(current)
	return lines


func _width(text: String) -> float:
	return _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY).x
