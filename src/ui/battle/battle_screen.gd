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

const SCREEN := Vector2(480, 270)

# --- Bandas ------------------------------------------------------------------
const TURNS_HEIGHT := 13.0
const FIELD_TOP := 13.0
const FIELD_HEIGHT := 167.0
const BAND_TOP := 180.0

## Línea del horizonte dentro del campo. Los enemigos se apoyan cerca de ella
## (lejos) y el grupo muy por debajo (cerca).
const HORIZON := 104.0

# --- Colocación de los dos bandos --------------------------------------------
const CHARACTER_SPRITE := Vector2(32, 48)
const PARTY_SLOTS := 5
## Punto de apoyo del miembro más cercano, abajo a la izquierda.
const PARTY_BASE := Vector2(14, 132)
## Cada miembro se aparta este paso hacia arriba y hacia la derecha.
const PARTY_STEP := Vector2(24, 12)

## Punto de apoyo del enemigo más cercano, a media altura por la derecha.
const ENEMY_BASE := Vector2(286, 104)
const ENEMY_STEP := Vector2(44, 24)
## Con un solo enemigo no hay diagonal que formar: se planta en el centro de su
## mitad, que es donde la mirada va sola.
const ENEMY_SOLO := Vector2(322, 74)

# --- Piezas de la banda inferior ---------------------------------------------
const MENU_RECT := Rect2(Vector2(8, 190), Vector2(108, 48))
const MESSAGE_RECT := Rect2(Vector2(124, 186), Vector2(156, 78))
const PARTY_WINDOW := Rect2(Vector2(288, 184), Vector2(184, 84))
const PARTY_ROW_INSET := Vector2(8, 2)

## Ficha del enemigo enfocado, arriba a la izquierda.
const ENEMY_PANEL := Vector2(8, 18)

const PARTY_SPRITE_DIR := "res://assets/sprites/party/"

## Cuánto se queda en pantalla cada línea del registro antes de pasar a la
## siguiente. Corto a propósito: el jugador verá miles de estas líneas.
const LOG_STEP_SECONDS := 0.75
## Pausa más larga en los momentos que cambian la estrategia.
const LOG_BEAT_SECONDS := 1.15

enum Phase { IDLE, PLAYING, CHOOSING, FINISHED }

var _font: Font = null
var _manager: BattleManager = null
var _phase: int = Phase.IDLE

var _monster_views: Array[MonsterView] = []
var _huds: Array[PartyMemberHud] = []
var _party_art: Array[Texture2D] = []
var _menu: ActionMenu = null
var _overlay: ResultOverlay = null
var _turns: TurnOrderStrip = null
var _numbers: DamageNumbers = null
## Cifras que ya ocurrieron en las reglas pero todavía no se han enseñado. Se
## sueltan al ritmo del registro, igual que las barras.
var _pending_numbers: Array[Dictionary] = []

var _queue: Array[Dictionary] = []
var _message: String = ""
var _message_tone: Color = DesignTokens.TEXT_PRIMARY
var _round: int = 0
var _step_timer: Timer = null

# Estado de la elección en curso.
## Cuántas veces se rehízo un monstruo. No es estadística: es la prueba que se
## le enseña al jugador cuando pierde, en lugar de darle un consejo.
var _regenerations: int = 0
var _result: int = Enums.BattleResult.ONGOING

var _actor: Character = null
var _pending_skill: Skill = null
var _pending_item: Item = null
var _focused_enemy: int = 0


func _ready() -> void:
	DesignTokens.load_settings()
	_font = load(DesignTokens.FONT_PATH)
	custom_minimum_size = SCREEN
	size = SCREEN

	for key in ["ilan", "bruma", "coral", "nix", "suri"]:
		var path: String = PARTY_SPRITE_DIR + key + ".png"
		_party_art.append(load(path) if ResourceLoader.exists(path) else null)

	_menu = ActionMenu.new()
	_menu.position = options_rect().position
	_menu.size = options_rect().size
	add_child(_menu)
	_menu.option_focused.connect(_on_option_focused)
	_menu.option_chosen.connect(_on_option_chosen)
	_menu.cancelled.connect(_on_menu_cancelled)
	_menu.close()

	_turns = TurnOrderStrip.new()
	_turns.position = Vector2(DesignTokens.SPACE_4, DesignTokens.SPACE_4)
	add_child(_turns)

	_numbers = DamageNumbers.new()
	_numbers.size = SCREEN

	_overlay = ResultOverlay.new()

	_step_timer = Timer.new()
	_step_timer.one_shot = true
	_step_timer.timeout.connect(_advance_queue)
	add_child(_step_timer)


# --- Anclajes del layout -----------------------------------------------------

## Dónde se apoya el miembro `index` de un grupo de `total`.
##
## El índice 0 es el **más lejano** (arriba a la derecha del grupo) y el último
## el más cercano (abajo a la izquierda). La ventana del grupo lista las filas
## en ese mismo orden, así que la primera fila corresponde al que está más
## arriba en el campo: la lista y el campo se leen igual.
static func character_anchor(index: int, total: int = PARTY_SLOTS) -> Vector2:
	var from_front: int = maxi(0, total - 1 - index)
	return Vector2(
		roundf(PARTY_BASE.x + from_front * PARTY_STEP.x),
		roundf(PARTY_BASE.y - from_front * PARTY_STEP.y)
	)


## Dónde se planta el enemigo `index` de `total`. El 0 es el más cercano.
static func enemy_anchor(index: int, total: int) -> Vector2:
	if total <= 1:
		return ENEMY_SOLO
	return Vector2(
		roundf(ENEMY_BASE.x + index * ENEMY_STEP.x),
		roundf(ENEMY_BASE.y - index * ENEMY_STEP.y)
	)


## Fila `index` dentro de la ventana del grupo.
static func hud_row_position(index: int) -> Vector2:
	return PARTY_WINDOW.position + PARTY_ROW_INSET 			+ Vector2(0, index * PartyMemberHud.ROW.y)


static func message_rect() -> Rect2:
	return MESSAGE_RECT


static func options_rect() -> Rect2:
	return MENU_RECT


# --- Arranque del combate ----------------------------------------------------

func start_battle(players: Array[Combatant], enemies: Array[Combatant],
		inventory: Inventory) -> void:
	_manager = BattleManager.new()
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


## Suelta las cifras acumuladas sobre el sprite de cada objetivo.
func _release_numbers() -> void:
	for pending in _pending_numbers:
		var target: Combatant = pending["target"] as Combatant
		var anchor: Vector2 = _anchor_for(target)
		if bool(pending["healing"]):
			# La curación no puede ir en verde: el verde solo significa
			# «la causa se atajó». El hueso es el tono de lo que está sano.
			_numbers.spawn(anchor, "+%d" % int(pending["amount"]),
					DesignTokens.ASH_050)
		elif bool(pending["resisted"]):
			# Golpe que el monstruo se quita de encima: apagado y con `~`.
			# Es la regla del juego, dicha con una cifra.
			_numbers.spawn(anchor, "~%d" % int(pending["amount"]),
					DesignTokens.ASH_400)
		else:
			var tone: Color = DesignTokens.EMBER_400 					if target.team == Enums.Team.PLAYER 					else DesignTokens.EMBER_300
			_numbers.spawn(anchor, str(int(pending["amount"])), tone)
	_pending_numbers.clear()


## Punto sobre el que se escribe la cifra: el borde superior de su sprite.
func _anchor_for(combatant: Combatant) -> Vector2:
	for view in _monster_views:
		if view.monster == combatant:
			return view.position + Vector2(MonsterView.SPRITE_SIZE * 0.5, 10.0)
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
func _on_action_resolved(log_lines: Array) -> void:
	for line in log_lines:
		_queue.append({"type": "log", "text": str(line), "order": _snapshot()})


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
	if event.has("order"):
		_turns.set_pending(event["order"])

	match event["type"]:
		"turn":
			# El cambio de turno no consume tiempo propio: se enciende la ficha
			# y se pasa de inmediato a lo que ese turno produjo.
			_turns.set_current(event["combatant"] as Combatant)
			_advance_queue()
			return
		"round":
			_round = int(event["round"])
			_set_message("-- Ronda %d --" % _round, DesignTokens.TEXT_SECONDARY)
			_schedule(LOG_STEP_SECONDS * 0.6)
		"log":
			_flush_views()
			_set_message(str(event["text"]), _tone_for(str(event["text"])))
			_schedule(LOG_BEAT_SECONDS if event.get("beat", false)
					else LOG_STEP_SECONDS)
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
			_schedule(LOG_BEAT_SECONDS)
		"input":
			_flush_views()
			_begin_choice(event["character"] as Character)
		"end":
			_flush_views()
			_turns.clear()
			_finish(int(event["result"]))
	queue_redraw()


func _schedule(seconds: float) -> void:
	_step_timer.start(seconds)


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
	_open_root_menu()


func _open_root_menu() -> void:
	var skills: Array[Skill] = _actor.get_known_skills()
	var items: Array[Item] = _manager.inventory.get_battle_items()
	_menu.set_entries([
		{"label": "ATACAR", "cost": -1, "enabled": true, "kind": "attack",
			"description": "Golpe directo. No ataja la causa: el monstruo se rehará."},
		{
			"label": "HABILIDADES", "cost": -1, "kind": "skills",
			"enabled": not skills.is_empty(),
			# Una opcion apagada sin explicacion solo frustra. Si el personaje
			# no tiene ninguna habilidad aqui, se dice, y ademas se dice que
			# eso es cosa suya y no del juego: otro del grupo si la tendra.
			"description": "Habilidades Ecológicas. Solo la correcta purifica."
					if not skills.is_empty()
					else "%s aún no conoce ninguna Habilidad Ecológica. Otro del grupo sí." % _actor.display_name,
		},
		{
			"label": "BOLSA", "cost": -1, "kind": "items",
			"enabled": not items.is_empty(),
			"description": "Objetos de curación del grupo." if not items.is_empty()
					else "La bolsa está vacía.",
		},
		{"label": "HUIR", "cost": -1, "enabled": true, "kind": "flee",
			"description": "Retirarse. Depende de la velocidad del grupo."},
	])
	_menu.open()


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
			_pending_skill = null
			_pending_item = null
			_open_target_menu(false)
		"skills":
			_open_skill_menu()
		"items":
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
	if _phase != Phase.CHOOSING:
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
	_overlay.show_result(result, _regenerations, FIELD_HEIGHT)
	queue_redraw()
	battle_finished.emit(result)


# --- Teclado -----------------------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	# Adelantar el registro. Solo mientras se reproduce: durante la elección el
	# teclado es del menú.
	if _phase == Phase.PLAYING and event.is_action_pressed("confirm"):
		_step_timer.stop()
		_advance_queue()
		get_viewport().set_input_as_handled()


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	_draw_background()
	_draw_enemy_ground()
	_draw_party()
	_draw_bands()
	_draw_message()


## Fondo del campo, en escalones de token. Nada de degradados interpolados: un
## lerp genera tonos que no son tokens y la auditoría de paleta los detecta.
func _draw_background() -> void:
	draw_rect(Rect2(Vector2(0, 0), Vector2(SCREEN.x, FIELD_TOP + 34.0)),
			DesignTokens.ASH_900)
	draw_rect(Rect2(Vector2(0, FIELD_TOP + 34.0),
			Vector2(SCREEN.x, HORIZON - FIELD_TOP - 34.0)),
			DesignTokens.ASH_800)

	# Silueta de cordillera recortada contra el cielo, en dientes de sierra.
	var peaks := [4, 18, 8, 26, 14, 32, 10, 22, 6, 28, 12, 20]
	var step: float = SCREEN.x / float(peaks.size())
	for i in range(peaks.size()):
		var height: float = float(peaks[i]) + 6.0
		draw_rect(Rect2(Vector2(step * i, HORIZON - height),
				Vector2(step + 1.0, height)), DesignTokens.ASH_700)

	# Suelo: una franja clara justo bajo el horizonte da la sensación de
	# distancia, y el resto baja de tono según se acerca al jugador.
	draw_rect(Rect2(Vector2(0, HORIZON), Vector2(SCREEN.x, 1)),
			DesignTokens.ASH_600)
	draw_rect(Rect2(Vector2(0, HORIZON + 1.0), Vector2(SCREEN.x, 22.0)),
			DesignTokens.ASH_800)
	draw_rect(Rect2(Vector2(0, HORIZON + 23.0),
			Vector2(SCREEN.x, BAND_TOP - HORIZON - 23.0)),
			DesignTokens.ASH_900)

	# El grupo va apretado, así que le basta una plataforma ancha de primer
	# plano. Los enemigos se escalonan en diagonal y cada uno necesita la suya:
	# sobre una sola elipse plana, los de atrás quedaban flotando.
	_platform(Vector2(78, 176), 94.0, 15.0)


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
		var tone: Color = DesignTokens.ASH_700 if row < -half_height * 0.45 				else DesignTokens.ASH_800
		draw_rect(Rect2(Vector2(roundf(center.x - span), y),
				Vector2(roundf(span * 2.0), 1.0)), tone)


## Sombra bajo un combatiente. Es lo que lo pega al suelo: sin ella los sprites
## flotan, que era buena parte de lo que hacía plana la pantalla anterior.
func _shadow(center: Vector2, half_width: float) -> void:
	for row in range(3):
		var shrink: float = half_width * (1.0 - row * 0.3)
		draw_rect(Rect2(Vector2(roundf(center.x - shrink), center.y + row),
				Vector2(roundf(shrink * 2.0), 1.0)), DesignTokens.ASH_950)


## Plataforma y sombra de cada enemigo. Se dibujan aquí, en la pantalla, y no
## en `MonsterView`, porque los hijos se pintan **después** del padre: si cada
## vista dibujara su propio suelo, se lo pondría encima al enemigo de delante.
func _draw_enemy_ground() -> void:
	var total: int = _monster_views.size()
	for i in range(total):
		var anchor := enemy_anchor(i, total)
		var feet := Vector2(anchor.x + MonsterView.SPRITE_SIZE * 0.5,
				anchor.y + MonsterView.SPRITE_SIZE - 2.0)
		# Cuanto más lejos, más pequeña la plataforma y más tenue la sombra.
		var depth: float = 1.0 - 0.16 * float(i)
		_platform(feet + Vector2(0, 4), 34.0 * depth, 7.0 * depth)
		_shadow(feet, 13.0 * depth)


func _draw_party() -> void:
	var total: int = _huds.size()
	# De lejos a cerca: quien está delante se dibuja encima y tapa al de atrás.
	# El solapamiento es el segundo indicio de profundidad.
	for i in range(total):
		var character: Character = _huds[i].character
		if character == null or i >= _party_art.size():
			continue
		var art: Texture2D = _party_art[i]
		if art == null:
			continue
		var anchor := character_anchor(i, total)
		var alpha: float = 1.0 if character.is_alive() else 0.3
		# La sombra crece con la cercanía, igual que en el mundo real.
		var nearness: float = float(i + 1) / float(maxi(1, total))
		_shadow(Vector2(anchor.x + CHARACTER_SPRITE.x * 0.5,
				anchor.y + CHARACTER_SPRITE.y - 2.0), 8.0 + 4.0 * nearness)
		draw_texture(art, anchor, Color(1, 1, 1, alpha))


func _draw_bands() -> void:
	draw_rect(Rect2(Vector2(0, BAND_TOP), Vector2(SCREEN.x, SCREEN.y - BAND_TOP)),
			DesignTokens.PANEL_FILL)
	draw_rect(Rect2(Vector2(0, BAND_TOP), Vector2(SCREEN.x, 1)),
			DesignTokens.BORDER_IDLE)

	# Ventana del grupo, abajo a la derecha: la esquina contraria a sus sprites.
	draw_rect(PARTY_WINDOW, DesignTokens.PANEL_FILL_DEEP)
	draw_rect(PARTY_WINDOW, DesignTokens.BORDER_IDLE, false,
			DesignTokens.BORDER_WIDTH)


## Mitad central de la banda: descripción de la opción enfocada mientras el
## jugador elige, y última línea del registro mientras se resuelve el turno.
func _draw_message() -> void:
	var rect := MESSAGE_RECT
	draw_rect(rect, DesignTokens.PANEL_FILL_DEEP)
	draw_rect(Rect2(rect.position, Vector2(2, rect.size.y)),
			DesignTokens.BORDER_IDLE)

	var pad: float = DesignTokens.SPACE_8
	var y: float = rect.position.y + 12.0
	for line in _wrap(_message, rect.size.x - pad * 2.0):
		if y > rect.end.y - 2.0:
			break
		draw_string(_font, Vector2(rect.position.x + pad, y), line,
				HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
				_message_tone)
		y += DesignTokens.LINE_HEIGHT

	# Indicador de «hay más»: sin él, el jugador no sabe si la pantalla espera
	# una tecla o se quedó colgada.
	if _phase == Phase.PLAYING and not _queue.is_empty():
		draw_string(_font, Vector2(rect.end.x - 12.0, rect.end.y - 4.0),
				"▼", HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY, DesignTokens.TEXT_CRITICAL)


## Reparte el texto en líneas que quepan, cortando por palabras.
func _wrap(text: String, available: float) -> PackedStringArray:
	var lines := PackedStringArray()
	var current := ""
	for word in text.split(" ", false):
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
