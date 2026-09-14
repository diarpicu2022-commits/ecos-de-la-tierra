class_name ResultOverlay
extends Control

## Vista de cierre del combate: victoria, derrota o retirada.
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
## Alturas de la ficha, medidas desde su borde superior.
const HEADLINE_BASELINE := 26.0   ## Titular a doble tamaño.
const DETAIL_TOP := 46.0          ## Primera línea de la explicación.
const HINT_GAP := 14.0            ## Separación entre explicación e indicación.
const BOTTOM_PAD := 7.0

var _font: Font = null
var _result: int = Enums.BattleResult.ONGOING
var _regenerations: int = 0


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false


## Muestra el desenlace. `regenerations` es el número de veces que un monstruo
## se rehizo durante el combate.
func show_result(result: int, regenerations: int, field_height: float) -> void:
	_result = result
	_regenerations = regenerations
	size = Vector2(BattleScreen.SCREEN.x, field_height)
	visible = true
	queue_redraw()


func hide_result() -> void:
	visible = false


func _draw() -> void:
	# Velo sobre el campo: el desenlace pasa a primer plano sin borrar lo que
	# había detrás, que sigue siendo información.
	draw_rect(Rect2(Vector2.ZERO, size), Color(DesignTokens.ASH_950, 0.78))

	var tone: Color = DesignTokens.TEXT_PRIMARY
	var headline := ""
	var detail := ""
	var hint := "Enter para volver a intentarlo"

	match _result:
		Enums.BattleResult.VICTORY:
			tone = DesignTokens.TEXT_PURIFIED
			headline = "✓ VICTORIA"
			detail = "La causa del daño quedó atajada."
			hint = "Enter para jugar otra vez"
		Enums.BattleResult.DEFEAT:
			tone = DesignTokens.TEXT_WARNING
			headline = "✖ EL GRUPO CAE"
			detail = _evidence("El monstruo sigue en pie.")
		Enums.BattleResult.FLED:
			tone = DesignTokens.TEXT_SECONDARY
			headline = "EL GRUPO SE RETIRA"
			detail = _evidence("El bosque sigue ardiendo.")

	var pad: float = DesignTokens.SPACE_16
	var detail_lines := _wrap(detail, PANEL_WIDTH - pad * 2.0)
	# La ficha crece con el texto. Con altura fija, una explicación de dos
	# líneas pisaba la indicación de Enter.
	var panel_height: float = (DETAIL_TOP
			+ detail_lines.size() * DesignTokens.LINE_HEIGHT
			+ HINT_GAP + BOTTOM_PAD)
	var origin := Vector2(
		roundf((size.x - PANEL_WIDTH) * 0.5),
		roundf((size.y - panel_height) * 0.5)
	)
	var panel := Rect2(origin, Vector2(PANEL_WIDTH, panel_height))

	draw_rect(panel, DesignTokens.PANEL_FILL)
	draw_rect(panel, tone, false, DesignTokens.BORDER_WIDTH)

	# El titular va al doble de tamaño, que es el único salto de escala que
	# permite una fuente de mapa de bits.
	draw_string(_font, origin + Vector2(pad, HEADLINE_BASELINE), headline,
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_TITLE, tone)

	var y: float = origin.y + DETAIL_TOP
	for line in detail_lines:
		draw_string(_font, Vector2(origin.x + pad, y), line,
				HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
				DesignTokens.TEXT_PRIMARY)
		y += DesignTokens.LINE_HEIGHT

	draw_string(_font, Vector2(origin.x + pad, panel.end.y - BOTTOM_PAD), hint,
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
			DesignTokens.TEXT_CRITICAL)


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
