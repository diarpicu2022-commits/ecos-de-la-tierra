class_name ActionHud
extends Control

## HUD del combate de acción, componente `ActionHUD` del sistema de diseño y
## maquetas `combate_accion.png` y `combate_purifica.png`. Contrato «Tajo».
##
## Nunca tapa el centro de la pantalla: ocupa las esquinas y una franja baja.
## - Arriba a la izquierda, la tarjeta del héroe (168 × 40) y el relevo.
## - Abajo a la izquierda, la bolsa con sus teclas 1 a 4.
## - Abajo a la derecha, los mandos en rombo: Z, X, C y V.
## - Sobre el monstruo, su placa con tipo, estado y vida.
## - Abajo al centro, el aviso de papel.
## Las teclas siempre se ven al lado de lo que hacen.

const CARD := Rect2(8, 8, 168, 40)
const RELAY_Y := 52.0
const RELAY_FACE := 22.0
const BAG_ORIGIN := Vector2(8, 312)
const SLOT := 26.0
const PAD_CENTER := Vector2(580, 300)
const PAD_STEP := 26.0
const BUTTON_R := 13.0
const PLATE_SIZE := Vector2(184, 44)
const TOAST := Rect2(150, 292, 340, 60)
const PORTRAITS := "res://assets/sprites/portraits/tierra_viva/"
## Iconos del prototipo (`tools/gen_tierra_viva_icons.py`).
const ICONS := "res://assets/ui/iconos/"
## Icono de cada objeto por el comienzo de su nombre.
const ITEM_ICON := {"Hierba": "hierba", "Agua": "agua", "Antídoto": "antidoto", "Ración": "racion"}

var combat: ActionCombat = null
var _font: Font = null
var _numbers := DamageNumbers.new()
var _toast := PackedStringArray()
var _toast_frames := 0
var _faces := {}
var _icons := {}


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(640, 360)
	_numbers.size = size
	add_child(_numbers)
	for n in ["espada", "bota", "hoja", "hierba", "agua", "antidoto", "racion"]:
		_icons[n] = load(ICONS + n + ".png")


func _item_icon(item: Item) -> Texture2D:
	for prefix in ITEM_ICON:
		if item.display_name.begins_with(prefix):
			return _icons.get(ITEM_ICON[prefix])
	return null


func bind(c: ActionCombat) -> void:
	combat = c
	# Cada pelea empieza sin el aviso de la anterior.
	_toast = PackedStringArray()
	_toast_frames = 0
	combat.toast.connect(show_toast)
	for p in combat.party:
		var key := str(p.display_name).to_lower()
		var path := PORTRAITS + key + ".png"
		if ResourceLoader.exists(path):
			_faces[key] = load(path)
	visible = true
	queue_redraw()


func show_toast(lines: PackedStringArray) -> void:
	_toast = lines
	_toast_frames = roundi(DesignTokens.DUR_TOAST * Engine.physics_ticks_per_second)
	queue_redraw()


func toast_lines() -> PackedStringArray:
	return _toast if _toast_frames > 0 else PackedStringArray()


## Una cifra sobre un punto del mundo.
func number(world_at: Vector2, text: String, color: Color) -> void:
	var xf := get_viewport().get_canvas_transform() if combat == null \
		else combat.world.get_viewport().get_canvas_transform()
	_numbers.spawn((xf * world_at - Vector2(0, 40)).round(), text, color)


func _physics_process(_delta: float) -> void:
	if _toast_frames > 0:
		_toast_frames -= 1
		if _toast_frames == 0:
			queue_redraw()


func _draw() -> void:
	if combat == null:
		return
	_draw_card()
	_draw_relay()
	_draw_bag()
	_draw_pad()
	_draw_plate()
	_draw_toast()


# --- Héroe y relevo ------------------------------------------------------------

func _draw_card() -> void:
	var h := combat.hero()
	if h == null:
		return
	TvFrame.draw(self, TvFrame.PLATE, CARD)
	_face(str(h.display_name).to_lower(), Rect2(CARD.position + Vector2(4, 4), Vector2(32, 32)))
	var x := CARD.position.x + 40.0
	TvFrame.slate_text(self, _font, Vector2(x, CARD.position.y + 12), h.display_name, DesignTokens.TV_GOLD_5)
	var eco := combat.eco_skill()
	if eco != null:
		var label := Enums.eco_type_name(eco.weakness_type).to_upper()
		var w := TvFrame.width(_font, label) + 8.0
		TvFrame.badge(self, _font, Vector2(CARD.end.x - w - 4.0, CARD.position.y + 4), label,
			TvFrame.type_fill(eco.weakness_type))
	_meter(Vector2(x, CARD.position.y + 24), "PV", h.get_hp_ratio(), TvFrame.hp_fill(h.get_hp_ratio()),
		"%d/%d" % [h.hp, h.max_hp])
	var en := float(h.energy) / maxf(1.0, float(h.max_energy))
	_meter(Vector2(x, CARD.position.y + 34), "EN", en, DesignTokens.TV_ECO_2, "")


func _meter(at: Vector2, label: String, ratio: float, fill: Color, value: String) -> void:
	TvFrame.slate_text(self, _font, at, label, DesignTokens.TV_TEXT_HIGHLIGHT)
	var bar_x := at.x + 14.0
	var right := CARD.end.x - 6.0 - (TvFrame.width(_font, value) + 4.0 if value != "" else 0.0)
	TvFrame.bar(self, Vector2(bar_x, at.y - 5.0), right - bar_x, 4, ratio, fill)
	if value != "":
		TvFrame.slate_text(self, _font, Vector2(right + 4.0, at.y), value, DesignTokens.TV_TEXT_MUTED_SLATE)


func _draw_relay() -> void:
	var x := CARD.position.x + 14.0
	_key_chip(Vector2(CARD.position.x, RELAY_Y + 6), "Q")
	for i in combat.party.size():
		if i == combat.active:
			continue
		var c: Character = combat.party[i]
		var r := Rect2(Vector2(x, RELAY_Y), Vector2(RELAY_FACE, RELAY_FACE))
		TvFrame.draw(self, TvFrame.PLATE, r.grow(2))
		_face(str(c.display_name).to_lower(), r)
		TvFrame.bar(self, Vector2(x, RELAY_Y + RELAY_FACE + 3), RELAY_FACE, 4, c.get_hp_ratio(),
			TvFrame.hp_fill(c.get_hp_ratio()))
		x += RELAY_FACE + 6.0
	_key_chip(Vector2(x, RELAY_Y + 6), "E")


func _face(key: String, r: Rect2) -> void:
	if not _faces.has(key):
		return
	var tex: Texture2D = _faces[key]
	var region := Rect2(Vector2(roundf((tex.get_width() - r.size.x) * 0.5), 2.0), r.size)
	draw_texture_rect_region(tex, r, region)


func _key_chip(at: Vector2, key: String) -> void:
	TvFrame.badge(self, _font, at, key, DesignTokens.TV_PAPER_4, DesignTokens.TV_INK_1)


# --- Bolsa y mandos ---------------------------------------------------------------

func _draw_bag() -> void:
	TvFrame.slate_text(self, _font, BAG_ORIGIN + Vector2(0, -4), "BOLSA", DesignTokens.TV_GOLD_5)
	var list := combat.items()
	for i in 4:
		var r := Rect2(BAG_ORIGIN + Vector2(i * (SLOT + 6.0), 0), Vector2(SLOT, SLOT))
		TvFrame.draw(self, TvFrame.PLATE_ACTIVE if i == combat.slot else TvFrame.PLATE, r)
		if i < list.size():
			var item: Item = list[i]
			var n := str(combat.bag.get_amount(item))
			var ic := _item_icon(item)
			if ic != null:
				draw_texture(ic, (r.get_center() - Vector2(6, 7)).round())
			TvFrame.slate_text(self, _font, r.end - Vector2(TvFrame.width(_font, n) + 3, 4), n,
				DesignTokens.TV_TEXT_MUTED_SLATE)
		_key_chip(r.position + Vector2(-2, SLOT - 4), str(i + 1))


func _draw_pad() -> void:
	var eco := combat.eco_skill()
	var h := combat.hero()
	var eco_ready := eco != null and h != null and h.has_energy(eco.energy_cost)
	# Rombo: V arriba, C a la izquierda, Z a la derecha y X abajo (maqueta).
	var list := combat.items()
	var item_icon: Texture2D = _item_icon(list[clampi(combat.slot, 0, list.size() - 1)]) 		if not list.is_empty() else null
	_button(PAD_CENTER + Vector2(0, -PAD_STEP), DesignTokens.TV_CMD_BAG, "V", item_icon)
	var eco_at := PAD_CENTER + Vector2(-PAD_STEP, 0)
	_button(eco_at, DesignTokens.TV_CMD_ECO if eco_ready else DesignTokens.TV_UI_2, "C", _icons["hoja"])
	# Sin energía el botón se apaga, pero sigue diciendo cuánto cuesta (ActionHUD).
	if eco != null:
		_key_chip((eco_at + Vector2(-BUTTON_R - 2, BUTTON_R - 8)).round(), str(eco.energy_cost))
	_button(PAD_CENTER + Vector2(PAD_STEP, 0), DesignTokens.TV_CMD_FIGHT, "Z", _icons["espada"])
	_button(PAD_CENTER + Vector2(0, PAD_STEP), DesignTokens.TV_CMD_RUN, "X", _icons["bota"])


func _button(center: Vector2, fill: Color, key: String, icon: Texture2D) -> void:
	draw_circle(center, BUTTON_R + 1.0, DesignTokens.TV_INK_0, true, -1.0, false)
	draw_circle(center, BUTTON_R, fill, true, -1.0, false)
	if icon != null:
		draw_texture(icon, (center - Vector2(6, 6)).round())
	_key_chip((center + Vector2(BUTTON_R - 6, BUTTON_R - 8)).round(), key)


# --- Monstruo y aviso ---------------------------------------------------------------

func _draw_plate() -> void:
	var m := combat.monster
	if m == null or combat.map == null:
		return
	var xf := combat.world.get_viewport().get_canvas_transform()
	var feet := xf * combat.monster_feet()
	var at := Vector2(feet.x - PLATE_SIZE.x * 0.5, feet.y - 150.0)
	at = at.clamp(Vector2(184, 4), Vector2(640 - PLATE_SIZE.x - 4, 360 - PLATE_SIZE.y - 70)).round()
	TvFrame.draw(self, TvFrame.PLATE, Rect2(at, PLATE_SIZE))
	TvFrame.slate_text(self, _font, at + Vector2(8, 13), m.display_name)
	var x := at.x + 8.0
	var cause := Enums.eco_type_name(m.required_counter_type).to_upper()
	x += TvFrame.badge(self, _font, Vector2(x, at.y + 17), cause, TvFrame.type_fill(m.required_counter_type)) + 3.0
	match combat.foe:
		ActionCombat.Foe.PURIFIED:
			TvFrame.badge(self, _font, Vector2(x, at.y + 17), "PURIFICADO",
				DesignTokens.TV_STATUS_PURIFIED, DesignTokens.TV_ECO_5)
		ActionCombat.Foe.STUNNED:
			TvFrame.badge(self, _font, Vector2(x, at.y + 17), "ATURDIDO", DesignTokens.TV_GOLD_1)
		_:
			TvFrame.badge(self, _font, Vector2(x, at.y + 17), "SE REHACE",
				DesignTokens.TV_STATUS_CORRUPT, DesignTokens.TV_PAPER_4)
	var ratio := m.get_hp_ratio()
	# Aturdido, la barra dice cuánto queda de la ventana: es la cuenta atrás.
	if combat.foe == ActionCombat.Foe.STUNNED:
		ratio = 1.0 - float(combat._timer) / maxf(1.0, DesignTokens.DUR_STUN_WINDOW * Engine.physics_ticks_per_second)
		TvFrame.bar(self, at + Vector2(8, 33), PLATE_SIZE.x - 16, 5, ratio, DesignTokens.TV_GOLD_3)
	else:
		TvFrame.bar(self, at + Vector2(8, 33), PLATE_SIZE.x - 16, 5, ratio, TvFrame.hp_fill(ratio))


func _draw_toast() -> void:
	var lines := toast_lines()
	if lines.is_empty():
		return
	var rows := wrapped_toast()
	# La caja crece hacia arriba si el aviso necesita más de dos líneas.
	var box := TOAST
	var extra := maxf(0.0, float(rows.size() - 2) * 15.0)
	box.position.y -= extra
	box.size.y += extra
	TvFrame.draw(self, TvFrame.TEXTBOX, box)
	for i in rows.size():
		TvFrame.paper_text(self, _font, box.position + Vector2(12, 22 + 15 * i), rows[i])


## Las líneas del aviso partidas por palabras para que quepan en el papel: un
## nombre largo como «Llama de la Deforestación» no puede salirse.
func wrapped_toast() -> PackedStringArray:
	var out := PackedStringArray()
	var room := TOAST.size.x - 24.0
	for line in toast_lines():
		var current := ""
		for word in line.split(" ", false):
			var candidate := word if current.is_empty() else current + " " + word
			if current != "" and TvFrame.width(_font, candidate) > room:
				out.append(current)
				current = word
			else:
				current = candidate
		if current != "":
			out.append(current)
	return out
