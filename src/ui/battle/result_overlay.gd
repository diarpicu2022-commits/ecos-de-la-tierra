class_name ResultOverlay
extends Control

## Vista de cierre del combate: victoria, derrota o retirada, con la pizarra del
## sistema de diseño (`TvFrame.PLATE`) y el titular de 22 px (guía del equipo
## §3.1, filas 6 y 14).
##
## Es una capa propia y no un dibujo más de `BattleScreen` porque en Godot los
## hijos se pintan **después** del padre: si el desenlace se dibujara en la
## pantalla, la ficha del monstruo le pasaría por encima y le cortaría el
## titular. Como capa añadida al final, queda garantizado que va arriba.
##
## En la derrota y en la retirada **no se da un consejo**, se enseña el hecho:
## cuántas veces se rehízo el monstruo. La fase 2 del anexo pide que el jugador
## cambie de estrategia «sin que se lo digan», así que la pantalla aporta la
## prueba y le deja la conclusión.

const PANEL_WIDTH := 304.0
## Medidas de la placa, desde su borde superior. El marco ocupa `TvFrame.SLICE`.
const HEADLINE_BASELINE := 28.0   ## Titular de 22 px.
const DETAIL_TOP := 46.0          ## Primera línea de la explicación.
const HINT_GAP := 16.0            ## Separación entre explicación e indicación.
const BOTTOM_PAD := 11.0
const TEXT_PAD := 16.0
## El velo baja el campo sin esconderlo, que sigue siendo información.
const VEIL_ALPHA := 0.6
## Por encima del `z_index` de las vistas de monstruo (`BattleScreen._layout_monsters`).
const FRONT_Z := 100

var _font: Font = null
var _result: int = Enums.BattleResult.ONGOING
var _regenerations: int = 0
## Sustituye a la indicación de la demo («jugar otra vez»).
var continue_hint := ""


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false


## Muestra el desenlace. `regenerations` es el número de veces que un monstruo
## se rehizo durante el combate. Cubre la pantalla entera y se pone delante de
## todo: los monstruos se añaden después que esta capa, con `z_index` propio, y
## le pasaban por encima.
func show_result(result: int, regenerations: int, _field_height: float) -> void:
	_result = result
	_regenerations = regenerations
	size = BattleScreen.SCREEN
	move_to_front()
	z_index = FRONT_Z
	visible = true
	queue_redraw()


func hide_result() -> void:
	visible = false


## Lo que dice el desenlace: {headline, tone, detail, hint}. El titular de la
## victoria va en `eco`, el color de lo purificado, y nunca solo: lleva el ✓ y
## la frase.
func outcome() -> Dictionary:
	var said := {"headline": "", "tone": DesignTokens.TV_TEXT_ON_SLATE, "detail": "",
		"hint": "Enter para volver a intentarlo"}
	match _result:
		Enums.BattleResult.VICTORY:
			said["tone"] = DesignTokens.TV_ECO_3
			said["headline"] = "✓ VICTORIA"
			said["detail"] = "La causa del daño quedó atajada."
			said["hint"] = "Enter para jugar otra vez"
		Enums.BattleResult.DEFEAT:
			said["tone"] = DesignTokens.TV_FIRE_4
			said["headline"] = "✖ EL GRUPO CAE"
			said["detail"] = _evidence("El monstruo sigue en pie.")
		Enums.BattleResult.FLED:
			said["tone"] = DesignTokens.TV_TEXT_HIGHLIGHT
			said["headline"] = "EL GRUPO SE RETIRA"
			said["detail"] = _evidence("El monstruo sigue en pie.")
	if not continue_hint.is_empty():
		said["hint"] = continue_hint
	return said


## Las líneas de la explicación, tal como se dibujan.
func detail_lines() -> PackedStringArray:
	return _wrap(outcome()["detail"], PANEL_WIDTH - TEXT_PAD * 2.0)


## La placa. Crece con el texto: con altura fija, una explicación de dos líneas
## pisaba la indicación de Enter.
func panel_rect() -> Rect2:
	var height: float = DETAIL_TOP + detail_lines().size() * DesignTokens.LINE_HEIGHT \
			+ HINT_GAP + BOTTOM_PAD
	return Rect2(Vector2(roundf((size.x - PANEL_WIDTH) * 0.5), roundf((size.y - height) * 0.5)),
			Vector2(PANEL_WIDTH, height))


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(DesignTokens.TV_INK_0, VEIL_ALPHA))
	var said := outcome()
	var panel := panel_rect()
	TvFrame.draw(self, TvFrame.PLATE, panel)

	var headline: String = said["headline"]
	var title_w := TvFrame.width(_font, headline, DesignTokens.FONT_SIZE_TITLE)
	TvFrame.text(self, _font, Vector2(panel.position.x + roundf((PANEL_WIDTH - title_w) * 0.5),
			panel.position.y + HEADLINE_BASELINE), headline, said["tone"],
			DesignTokens.TV_UI_0, DesignTokens.FONT_SIZE_TITLE)

	var y: float = panel.position.y + DETAIL_TOP
	for line in detail_lines():
		TvFrame.slate_text(self, _font, Vector2(_centered(panel, line), y), line)
		y += DesignTokens.LINE_HEIGHT

	var hint: String = said["hint"]
	TvFrame.slate_text(self, _font, Vector2(_centered(panel, hint), panel.end.y - BOTTOM_PAD), hint,
			DesignTokens.TV_TEXT_HIGHLIGHT)


func _centered(panel: Rect2, line: String) -> float:
	return panel.position.x + roundf((PANEL_WIDTH - TvFrame.width(_font, line)) * 0.5)


## El dato que explica el desenlace, cuando lo hay.
func _evidence(fallback: String) -> String:
	if _regenerations <= 0:
		return fallback
	if _regenerations == 1:
		return "El monstruo se rehízo una vez: la causa seguía activa."
	return "El monstruo se rehízo %d veces: la causa seguía activa." % _regenerations


func _wrap(text: String, available: float) -> PackedStringArray:
	var lines := PackedStringArray()
	var current := ""
	for word in text.split(" ", false):
		var candidate: String = word if current.is_empty() else current + " " + word
		if _font.get_string_size(candidate, HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY).x <= available:
			current = candidate
		else:
			if not current.is_empty():
				lines.append(current)
			current = word
	if not current.is_empty():
		lines.append(current)
	return lines
