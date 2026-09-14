class_name RegionSelect
extends Control

## Pantalla de elección de región.
##
## No introduce ningún patrón visual nuevo: la lista es el mismo `ActionMenu`
## que usa el combate, con los mismos tokens, el mismo cursor y el mismo
## teclado. Quien ya sabe moverse por el menú de batalla sabe moverse por aquí
## sin aprender nada.
##
## A la derecha se enseña el monstruo de la región enfocada, con su tipo de daño
## y quién del grupo trae la contramedida. Es la misma información que la ficha
## del combate, adelantada: elegir región y elegir acción son la misma clase de
## decisión, y se presentan igual.

signal region_chosen(index: int)

const MENU_POSITION := Vector2(24, 78)
const MENU_SIZE := Vector2(184, 72)
const ART_CENTER := Vector2(352, 108)
const SPRITE_DIR := "res://assets/sprites/monsters/"

var _font: Font = null
var _menu: ActionMenu = null
var _focused: int = 0
var _art: Array[Texture2D] = []


func _ready() -> void:
	DesignTokens.load_settings()
	_font = load(DesignTokens.FONT_PATH)
	custom_minimum_size = BattleScreen.SCREEN
	size = BattleScreen.SCREEN

	# Las texturas se cargan aquí y no dentro de `_draw()`: en el primer cuadro
	# todavía no están listas y Godot dibuja un rectángulo blanco en su lugar.
	for encounter in Encounters.all():
		var path: String = SPRITE_DIR + str(encounter["monster"]) + ".png"
		_art.append(load(path) if ResourceLoader.exists(path) else null)

	_menu = ActionMenu.new()
	_menu.position = MENU_POSITION
	_menu.size = MENU_SIZE
	add_child(_menu)
	_menu.option_focused.connect(_on_focused)
	_menu.option_chosen.connect(_on_chosen)

	var entries: Array[Dictionary] = []
	for i in range(Encounters.count()):
		var encounter: Dictionary = Encounters.get_encounter(i)
		entries.append({
			"label": str(encounter["region"]),
			"cost": -1, "enabled": true, "index": i,
		})
	_menu.set_entries(entries)
	_menu.open()


func _on_focused(entry: Dictionary) -> void:
	_focused = int(entry.get("index", 0))
	queue_redraw()


func _on_chosen(entry: Dictionary) -> void:
	_menu.close()
	region_chosen.emit(int(entry.get("index", 0)))


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), DesignTokens.ASH_950)
	# Franja de cielo, la misma escalera de tokens que el campo de batalla.
	draw_rect(Rect2(Vector2.ZERO, Vector2(size.x, 60)), DesignTokens.ASH_900)
	draw_rect(Rect2(Vector2(0, 60), Vector2(size.x, 100)), DesignTokens.ASH_800)

	draw_string(_font, Vector2(24, 34), "ECOS DE LA TIERRA",
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_TITLE,
			DesignTokens.TEXT_PRIMARY)
	draw_string(_font, Vector2(24, 50), "Elige una region",
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
			DesignTokens.TEXT_SECONDARY)

	_draw_detail()

	draw_string(_font, Vector2(24, 260),
			"Flechas o WASD para moverte · Enter para entrar",
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
			DesignTokens.TEXT_SECONDARY)


## Ficha de la región enfocada: el monstruo, su daño y quién lo ataja.
func _draw_detail() -> void:
	var encounter: Dictionary = Encounters.get_encounter(_focused)

	if _focused < _art.size() and _art[_focused] != null:
		var art: Texture2D = _art[_focused]
		draw_texture(art, ART_CENTER - art.get_size() * 0.5)

	var panel := Rect2(Vector2(232, 152), Vector2(224, 84))
	draw_rect(panel, DesignTokens.PANEL_FILL)
	draw_rect(panel, DesignTokens.BORDER_IDLE, false, DesignTokens.BORDER_WIDTH)

	var pad: float = DesignTokens.SPACE_8
	var x: float = panel.position.x + pad
	_text(str(encounter["place"]), Vector2(x, panel.position.y + 14),
			DesignTokens.TEXT_SECONDARY)

	var monster_name: String = _monster_name(_focused)
	_text(monster_name, Vector2(x, panel.position.y + 28),
			DesignTokens.TEXT_PRIMARY)

	var eco: int = int(encounter["eco"])
	var eco_label: String = "Dano: %s" % Enums.eco_type_name(eco) \
			if eco != Enums.EcoType.NONE else "Dano: acumulado"
	_text(eco_label, Vector2(x, panel.position.y + 42),
			DesignTokens.TEXT_WARNING)

	var group: int = (encounter["party"] as Array).size()
	_text("Grupo de %d" % group, Vector2(x, panel.position.y + 56),
			DesignTokens.TEXT_SECONDARY)

	for line in _wrap(str(encounter["hint"]), panel.size.x - pad * 2.0):
		_text(line, Vector2(x, panel.position.y + 70), DesignTokens.TEXT_CRITICAL)
		break


## El nombre lo sabe el propio monstruo, así que se construye uno de usar y
## tirar en vez de repetir la cadena en el catálogo y arriesgarse a que se
## desincronicen.
func _monster_name(index: int) -> String:
	var monster: Monster = Encounters.build_monster(index)
	var display: String = monster.display_name
	monster.free()
	return display


func _text(text: String, position: Vector2, color: Color) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, color)


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
