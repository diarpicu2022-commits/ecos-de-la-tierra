extends Node2D

## Banco de pruebas del paso 4: sprites del grupo, HUD por columna y el menú
## genérico en sus dos usos (raíz y submenú de habilidades).
##   godot --path . res://tools/components4_sheet.tscn

const SHOT_PATH := "user://components4.png"
const SPRITE_DIR := "res://assets/sprites/party/"

var _font: Font = null
var _party: Array[Character] = []
var _huds: Array[PartyMemberHud] = []
var _portraits: Array[Texture2D] = []


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	# Las texturas se cargan aquí, no dentro de _draw(): en el primer cuadro
	# todavía no están listas y Godot dibuja un rectángulo blanco en su lugar.
	for key in ["ilan", "bruma", "coral", "nix", "suri"]:
		_portraits.append(load(SPRITE_DIR + key + ".png"))
	_party = PartyLibrary.full_party()
	for character in _party:
		add_child(character)

	# Estados variados, para ver el HUD en algo más que el caso feliz.
	_party[1].take_damage(46)                    # Bruma herida
	_party[2].take_damage(84)                    # Coral crítica
	_party[2].apply_status(BurnEffect.new())
	_party[3].apply_status(StunEffect.new())
	_party[3].apply_status(PoisonEffect.new())
	_party[4].take_damage(400)                   # Suri fuera de combate
	_party[0].spend_energy(12)

	for i in range(_party.size()):
		var hud := PartyMemberHud.new()
		hud.position = Vector2(BattleScreen.party_column(i, 5), 92)
		add_child(hud)
		hud.bind(_party[i])
		hud.set_active_turn(i == 0)
		_huds.append(hud)

	# Menú raíz.
	var root_menu := ActionMenu.new()
	root_menu.position = Vector2(16, 158)
	root_menu.size = Vector2(120, 48)
	add_child(root_menu)
	root_menu.set_entries([
		{"label": "ATACAR", "enabled": true, "cost": -1},
		{"label": "HABILIDADES", "enabled": true, "cost": -1},
		{"label": "BOLSA", "enabled": true, "cost": -1},
		{"label": "HUIR", "enabled": true, "cost": -1},
	])
	root_menu.open()

	# Submenú de habilidades: el mismo componente, con costes y una opción que
	# el personaje no puede pagar.
	var skills_menu := ActionMenu.new()
	skills_menu.position = Vector2(184, 158)
	skills_menu.size = Vector2(168, 48)
	add_child(skills_menu)
	skills_menu.set_entries([
		{"label": "Linea Cortafuegos", "enabled": true, "cost": 8},
		{"label": "Reforestacion", "enabled": true, "cost": 12},
		{"label": "Filtro Biologico", "enabled": false, "cost": 18},
		{"label": "Escudo de Albedo", "enabled": false, "cost": 22},
	])
	skills_menu.open()
	skills_menu.focused = 2
	skills_menu._cursor_y = skills_menu._row_top(2)
	skills_menu.queue_redraw()

	await get_tree().create_timer(0.35).timeout
	queue_redraw()
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(SHOT_PATH)
	print("Captura: ", ProjectSettings.globalize_path(SHOT_PATH))
	get_tree().quit()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(480, 270)), DesignTokens.ASH_900)

	_label("SPRITES DEL GRUPO", Vector2(4, 12))
	for i in range(_portraits.size()):
		draw_texture(_portraits[i],
				Vector2(BattleScreen.party_column(i, 5) + 32, 20))

	_label("HUD \u00b7 UNA COLUMNA BAJO CADA PERSONAJE", Vector2(4, 88))
	_label("MEN\u00da RA\u00cdZ", Vector2(16, 152))
	_label("MISMO COMPONENTE COMO SUBMEN\u00da (con coste)", Vector2(184, 152))
	_label("Filtro Biologico y Escudo de Albedo: coste en rojo, no en gris mudo",
			Vector2(16, 224))


func _label(text: String, position: Vector2) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, DesignTokens.TEXT_SECONDARY)
