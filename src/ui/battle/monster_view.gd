class_name MonsterView
extends Control

## El monstruo y su estado de purificación.
##
## Es el componente que carga la **decisión dominante** de la pantalla de
## batalla (fase 2 del anexo): «qué hago este turno, sabiendo si el monstruo ya
## está purificado o no». Por eso es lo más grande de la pantalla y por eso el
## estado de purificación no es un icono pequeño en una esquina, sino una franja
## que ocupa media ficha y que cambia de color, de texto y de sprite a la vez.
##
## No conoce el BattleManager. Se le entrega un Monster con `bind()` y se limita
## a escuchar sus señales, igual que el resto de la interfaz.
##
## **Pausa y volcado.** `BattleManager` resuelve la ronda entera de forma
## síncrona: cuando la interfaz recupera el control, los PV ya son los finales.
## Si la vista siguiera las señales al vuelo, las barras se vaciarían de golpe
## mientras el registro todavía narra el primer golpe. Por eso la pantalla la
## pone en pausa durante la resolución y llama a `flush()` al ritmo del
## registro: lo que se ve y lo que se lee van juntos.

## Medidas del componente, todas en la escala de espaciado del contrato.
const SPRITE_SIZE := 48
const PANEL_WIDTH := 176
const PANEL_HEIGHT := 52
const GAP := DesignTokens.SPACE_4
const TOTAL_SIZE := Vector2(PANEL_WIDTH, SPRITE_SIZE + GAP + PANEL_HEIGHT)

const SPRITE_DIR := "res://assets/sprites/monsters/"

## Umbrales de la barra de PV. La vida se drena hacia la brasa, nunca al verde:
## el verde es el acento reservado a la purificación.
const HP_WOUNDED := 0.55
const HP_CRITICAL := 0.25

## Con varios enemigos en el campo, solo el que está en el punto de mira enseña
## su ficha; los demás se quedan en el sprite.
var show_panel: bool = true
## Desplazamiento de la ficha respecto al origen de la vista. Permite que el
## sprite viva en su sitio del campo y la ficha siempre en el mismo lugar.
var panel_offset: Vector2 = Vector2(0, SPRITE_SIZE + GAP)
## Dónde se dibuja el sprite dentro de la vista.
var sprite_offset: Vector2 = Vector2((PANEL_WIDTH - SPRITE_SIZE) * 0.5, 0.0)

var monster: Monster = null

var _font: Font = null
var _art_active: Texture2D = null      ## La causa sigue activa.
var _art_purified: Texture2D = null    ## La causa se atajó.

# Estado dibujado, que va por detrás del estado real para poder animarlo.
var _shown_hp: float = 0.0
var _purify_progress: float = 0.0
var _shake: float = 0.0
var _flash: float = 0.0

# Pausa: lo que ya ocurrió en las reglas pero todavía no se ha mostrado.
var _paused: bool = false
var _pending_hp: float = -1.0
var _pending_purified: bool = false
var _pending_regenerated: bool = false

var _hp_tween: Tween = null
var _purify_tween: Tween = null
var _shake_tween: Tween = null
var _flash_tween: Tween = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	custom_minimum_size = TOTAL_SIZE
	size = TOTAL_SIZE


## Conecta la vista a un monstruo concreto. Se puede llamar más de una vez: los
## clones del Espectro del Monocultivo reutilizan vistas.
func bind(target: Monster) -> void:
	_disconnect_current()
	monster = target
	if monster == null:
		queue_redraw()
		return

	_art_active = _load_art("")
	_art_purified = _load_art("_purified")

	_shown_hp = float(monster.hp)
	_purify_progress = 1.0 if monster.is_purified else 0.0
	_pending_hp = -1.0
	_pending_purified = false
	_pending_regenerated = false

	monster.hp_changed.connect(_on_hp_changed)
	monster.purified.connect(_on_purified)
	monster.regenerated.connect(_on_regenerated)
	monster.defeated.connect(_on_defeated)
	queue_redraw()


## El sprite se deduce del nombre del script del monstruo: `deforestation_flame.gd`
## busca `deforestation_flame.png`. Así añadir un monstruo no obliga a tocar
## ningún registro de la interfaz.
func _load_art(suffix: String) -> Texture2D:
	var script: Script = monster.get_script()
	if script == null:
		return null
	var key: String = script.resource_path.get_file().get_basename()
	var path: String = SPRITE_DIR + key + suffix + ".png"
	return load(path) if ResourceLoader.exists(path) else null


func _disconnect_current() -> void:
	if monster == null:
		return
	for signal_name in ["hp_changed", "purified", "regenerated", "defeated"]:
		for connection in monster.get_signal_connection_list(signal_name):
			if connection["callable"].get_object() == self:
				monster.disconnect(signal_name, connection["callable"])


# --- Pausa durante la resolución --------------------------------------------

func set_paused(value: bool) -> void:
	_paused = value


## Muestra todo lo que quedó pendiente mientras la vista estaba en pausa.
func flush() -> void:
	if _pending_hp >= 0.0:
		var target: float = _pending_hp
		_pending_hp = -1.0
		if target < _shown_hp:
			_play_shake()
		_tween_hp(target)
	if _pending_regenerated:
		_pending_regenerated = false
		_play_flash()
	if _pending_purified:
		_pending_purified = false
		_play_purify()


# --- Reacciones a las señales del combate -----------------------------------

func _on_hp_changed(current: int, _maximum: int) -> void:
	if _paused:
		_pending_hp = float(current)
		return
	if float(current) < _shown_hp:
		_play_shake()
	_tween_hp(float(current))


## La regeneración es el momento en que el jugador debe entender que la fuerza
## bruta no basta. Se subraya con un destello, además del texto del registro.
func _on_regenerated(_current_hp: int) -> void:
	if _paused:
		_pending_regenerated = true
		return
	_play_flash()


func _on_purified() -> void:
	if _paused:
		_pending_purified = true
		return
	_play_purify()


func _on_defeated() -> void:
	queue_redraw()


## La transición más larga de la pantalla (300 ms), y la única que llega al
## tope: es el evento que carga el mensaje del juego.
func _play_purify() -> void:
	if _purify_tween != null and _purify_tween.is_valid():
		_purify_tween.kill()
	if DesignTokens.reduced_motion:
		_purify_progress = 1.0
		queue_redraw()
		return
	_purify_tween = create_tween()
	_purify_tween.set_trans(DesignTokens.EASE_OUT_TRANS)
	_purify_tween.set_ease(DesignTokens.EASE_OUT_EASE)
	_purify_tween.tween_method(_set_purify, _purify_progress, 1.0,
			DesignTokens.DUR_PURIFY)


func _set_purify(value: float) -> void:
	_purify_progress = value
	queue_redraw()


func _play_flash() -> void:
	if _flash_tween != null and _flash_tween.is_valid():
		_flash_tween.kill()
	if DesignTokens.reduced_motion:
		return
	_flash_tween = create_tween()
	_flash_tween.tween_method(_set_flash, 1.0, 0.0, DesignTokens.DUR_PURIFY)


func _set_flash(value: float) -> void:
	_flash = value
	queue_redraw()


func _tween_hp(target: float) -> void:
	if _hp_tween != null and _hp_tween.is_valid():
		_hp_tween.kill()
	if DesignTokens.reduced_motion:
		_shown_hp = target
		queue_redraw()
		return
	_hp_tween = create_tween()
	_hp_tween.set_trans(DesignTokens.EASE_OUT_TRANS)
	_hp_tween.set_ease(DesignTokens.EASE_OUT_EASE)
	_hp_tween.tween_method(_set_shown_hp, _shown_hp, target, DesignTokens.DUR_BAR)


func _set_shown_hp(value: float) -> void:
	_shown_hp = value
	queue_redraw()


## Sacudida al recibir daño. Solo se mueve el sprite, no la ficha: si saltara
## el texto, el jugador perdería la cifra justo cuando quiere leerla.
func _play_shake() -> void:
	if DesignTokens.reduced_motion:
		return
	if _shake_tween != null and _shake_tween.is_valid():
		_shake_tween.kill()
	_shake = 1.0
	_shake_tween = create_tween()
	_shake_tween.tween_method(_set_shake, 1.0, 0.0, DesignTokens.DUR_SHAKE)


func _set_shake(value: float) -> void:
	_shake = value
	queue_redraw()


# --- Dibujo ------------------------------------------------------------------

func _ratio() -> float:
	if monster == null or monster.max_hp <= 0:
		return 0.0
	return clampf(_shown_hp / float(monster.max_hp), 0.0, 1.0)


func _draw() -> void:
	if monster == null:
		return
	_draw_sprite()
	if show_panel:
		_draw_panel()


func _draw_sprite() -> void:
	var origin := sprite_offset
	# El temblor se redondea a píxel entero: un desplazamiento fraccionario
	# rompería la rejilla de la que vive el pixel art.
	if _shake > 0.001:
		origin.x += roundf(sin(_shake * TAU * 3.0) * _shake * 3.0)

	if _art_active == null:
		# Sin sprite todavía: se marca el hueco en vez de no dibujar nada, que
		# es como se pierde una hora buscando un fallo que no existe.
		draw_rect(Rect2(origin, Vector2(SPRITE_SIZE, SPRITE_SIZE)),
				DesignTokens.ASH_700)
		return

	# Quien ya cayó se queda tenue, no desaparece: el jugador tiene que poder
	# ver qué había ahí.
	var alpha: float = 1.0 if monster.is_alive() else 0.35
	var rect := Rect2(origin, Vector2(SPRITE_SIZE, SPRITE_SIZE))
	# Fundido entre los dos estados: la purificación se ve en el propio
	# monstruo, no solo en una etiqueta.
	draw_texture_rect(_art_active, rect, false,
			Color(1, 1, 1, (1.0 - _purify_progress) * alpha))
	if _art_purified != null and _purify_progress > 0.0:
		draw_texture_rect(_art_purified, rect, false,
				Color(1, 1, 1, _purify_progress * alpha))
	if _flash > 0.01:
		draw_texture_rect(_art_active, rect, false, Color(1, 1, 1, _flash * 0.7))


func _draw_panel() -> void:
	var top: float = panel_offset.y
	var left: float = panel_offset.x
	var panel := Rect2(Vector2(left, top), Vector2(PANEL_WIDTH, PANEL_HEIGHT))
	var border: Color = DesignTokens.BORDER_IDLE.lerp(
			DesignTokens.BORDER_PURIFIED, _purify_progress)

	draw_rect(panel, DesignTokens.PANEL_FILL)
	draw_rect(panel, border, false, DesignTokens.BORDER_WIDTH)

	var pad: float = DesignTokens.SPACE_8
	_text(_fit(monster.display_name, PANEL_WIDTH - pad * 2.0),
			Vector2(left + pad, top + 13), DesignTokens.TEXT_PRIMARY)

	_draw_hp_bar(left, top)
	_draw_purification(left, top, border)


func _draw_hp_bar(left: float, top: float) -> void:
	var pad: float = DesignTokens.SPACE_8
	var track := Rect2(Vector2(left + pad, top + 19), Vector2(104, 6))
	draw_rect(track, DesignTokens.BAR_TRACK)

	var ratio: float = _ratio()
	var fill_color: Color = DesignTokens.ASH_050
	if ratio <= HP_CRITICAL:
		fill_color = DesignTokens.EMBER_500
	elif ratio <= HP_WOUNDED:
		fill_color = DesignTokens.EMBER_400

	if ratio > 0.0:
		# Al menos 1 px mientras siga vivo: una barra vacía diría que ya cayó.
		var width: float = maxf(1.0, roundf(track.size.x * ratio))
		draw_rect(Rect2(track.position, Vector2(width, track.size.y)), fill_color)
	draw_rect(track, DesignTokens.BORDER_IDLE, false, DesignTokens.BORDER_WIDTH)

	# La cifra exacta acompaña siempre a la barra. Una barra sola obliga a
	# estimar, y aquí el jugador decide con este número. Se lee del valor
	# animado, no del real, para que cifra y barra digan lo mismo.
	var label := "%d/%d" % [roundi(_shown_hp), monster.max_hp]
	var tone: Color = DesignTokens.TEXT_CRITICAL if ratio <= HP_CRITICAL \
			else DesignTokens.TEXT_PRIMARY
	_text(label, Vector2(left + PANEL_WIDTH - DesignTokens.SPACE_8 - _width(label),
			top + 25), tone)


## La franja que responde a «¿por qué el daño no sirvió?».
func _draw_purification(left: float, top: float, border: Color) -> void:
	var pad: float = DesignTokens.SPACE_8
	var band := Rect2(Vector2(left + 1, top + 30), Vector2(PANEL_WIDTH - 2, 21))
	draw_rect(band, DesignTokens.PANEL_FILL_DEEP)
	draw_rect(Rect2(band.position, Vector2(2, band.size.y)), border)

	var purified: bool = _purify_progress >= 0.5
	var headline: String = "✓ PURIFICADO" if purified else "✖ SIN PURIFICAR"
	var tone: Color = DesignTokens.TEXT_PURIFIED if purified 			else DesignTokens.TEXT_WARNING

	_text(headline, Vector2(left + pad, top + 40), tone)
	# El tipo de daño y lo que hace el monstruo van en una sola frase, no como
	# dos etiquetas flotando en extremos opuestos. Con nombres largos
	# («Monocultivo») las dos se tocaban, y además un tipo suelto a la derecha
	# no decía qué hacer con él.
	_text(_status_line(purified), Vector2(left + pad, top + 49),
			DesignTokens.TEXT_SECONDARY)


## Segunda línea de la franja: de qué daño se trata y qué implica ahora mismo.
func _status_line(purified: bool) -> String:
	var behaviour: String = "ya puede ser derrotado" if purified 			else "se regenera cada ronda"
	# El jefe final no tiene una sola contramedida: exige combinar las cinco,
	# y decir «Neutro» no le sirve de nada al jugador.
	if monster.required_counter_type == Enums.EcoType.NONE:
		return "aprende de lo que repites" if not purified else behaviour
	var eco: String = Enums.eco_type_name(monster.required_counter_type)
	var line: String = "%s · %s" % [eco, behaviour]
	if _width(line) <= PANEL_WIDTH - DesignTokens.SPACE_8 * 2.0:
		return line
	# Si la frase entera no cabe, manda el tipo: es la pista de qué usar.
	return "%s · %s" % [eco, "se regenera" if not purified else "puede caer"]


func _text(text: String, position: Vector2, color: Color) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, color)


func _width(text: String) -> float:
	return _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY).x


## Recorta un texto que no quepa y lo cierra con puntos suspensivos. Un nombre
## desbordado se solaparía con lo que tenga al lado, que es peor que perder
## tres letras.
func _fit(text: String, available: float) -> String:
	if _width(text) <= available:
		return text
	var trimmed: String = text
	while trimmed.length() > 1 and _width(trimmed + "...") > available:
		trimmed = trimmed.substr(0, trimmed.length() - 1)
	return trimmed.strip_edges() + "..."
