class_name TvFrame
extends RefCounted

## Marcos, texto, chapas y barras del sistema de diseño «Tierra Viva»
## (`docs/ux/sistema-de-diseno/project/components/bundle.css`).
##
## Los marcos son las mismas imágenes que usa el sistema, de nueve partes con
## bordes de 8 px (`border-image: ... 8 fill / 8px stretch`). Salen de
## `tools/tierra_viva/ui.py` y están en `assets/ui/marcos/`; todo su píxel es
## token (`verify_palette.py image`).

const DIR := "res://assets/ui/marcos/"
const SLICE := 8

## Placa de pizarra, la activa con borde de oro, fila del grupo, papel, chapa
## del nombre, retrato y los cuatro mandos.
const PLATE := "plate"
const PLATE_ACTIVE := "plate-active"
const ROW := "row"
const TEXTBOX := "textbox"
const TAG := "tag"
const SIGN := "sign"
const CMD_FIGHT := "cmd-luchar"
const CMD_ECO := "cmd-eco"
const CMD_BAG := "cmd-bolsa"
const CMD_RUN := "cmd-huir"
const CMD_SELECTED := "cmd-selected"

## `CommandMenu` (bundle.css, `.cmds`, `.cmd`, `.cmd-sel`): mandos de 100 × 30, con
## 4 px entre columnas y 6 entre filas. El marco del elegido sobresale 2 px por
## cada lado. La línea base sale de medir `combate_enfermo.png`.
const CMD_SIZE := Vector2(100, 30)
const CMD_GAP := Vector2(4, 6)
const CMD_RING := 2.0
const CMD_BASELINE := 17.0

## Lo que ocupa el canto de `PLATE`, medido sobre el PNG: 3 px arriba, 2 abajo y
## 2 a cada lado. Lo de dentro es el alto útil de una lista.
const PLATE_EDGE_TOP := 3.0
const PLATE_EDGE_BOTTOM := 2.0
const PLATE_EDGE_SIDE := 2.0

static var _boxes := {}


static func box(name: String) -> StyleBoxTexture:
	if not _boxes.has(name):
		var sb := StyleBoxTexture.new()
		sb.texture = load(DIR + name + ".png")
		sb.texture_margin_left = SLICE
		sb.texture_margin_top = SLICE
		sb.texture_margin_right = SLICE
		sb.texture_margin_bottom = SLICE
		sb.draw_center = true
		_boxes[name] = sb
	return _boxes[name]


static func draw(ci: CanvasItem, name: String, rect: Rect2) -> void:
	ci.draw_style_box(box(name), rect)


## Texto con sombra de 1 px abajo a la derecha (README §Tipografía): sobre
## pizarra, `text-on-slate` con sombra `ui-1`; sobre papel, `text-on-paper` con
## sombra `text-shadow-paper`.
static func text(ci: CanvasItem, font: Font, at: Vector2, value: String, color: Color,
		shadow: Color, size: int = DesignTokens.FONT_SIZE_BODY) -> void:
	ci.draw_string(font, at + Vector2(1, 1), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, shadow)
	ci.draw_string(font, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


static func slate_text(ci: CanvasItem, font: Font, at: Vector2, value: String,
		color: Color = DesignTokens.TV_TEXT_ON_SLATE) -> void:
	text(ci, font, at, value, color, DesignTokens.TV_UI_0)


static func paper_text(ci: CanvasItem, font: Font, at: Vector2, value: String) -> void:
	text(ci, font, at, value, DesignTokens.TV_TEXT_ON_PAPER, DesignTokens.TV_TEXT_SHADOW_PAPER)


## Un mando del `CommandMenu`: su marco fijo, el anillo si es el elegido y la
## etiqueta blanca centrada con sombra `ink-1` (`TV_INK_0`: las rampas del CSS
## cuentan desde 1).
static func command(ci: CanvasItem, font: Font, frame: String, rect: Rect2, value: String,
		selected: bool) -> void:
	if selected:
		draw(ci, CMD_SELECTED, rect.grow(CMD_RING))
	draw(ci, frame, rect)
	var x := rect.position.x + roundf((rect.size.x - width(font, value)) * 0.5)
	text(ci, font, Vector2(x, rect.position.y + CMD_BASELINE), value,
			DesignTokens.TV_TEXT_ON_SLATE, DesignTokens.TV_INK_0)


static func width(font: Font, value: String, size: int = DesignTokens.FONT_SIZE_BODY) -> float:
	return font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


## Chapa de 11 px (`TypeBadge`): relleno de 3 px a cada lado, esquina de 1 px
## y contorno `ink-1`. Devuelve su ancho.
static func badge(ci: CanvasItem, font: Font, at: Vector2, value: String, fill: Color,
		ink: Color = DesignTokens.TV_UI_6) -> float:
	var w := width(font, value) + 8.0
	var r := Rect2(at, Vector2(w, 11))
	ci.draw_rect(Rect2(r.position + Vector2(1, 0), Vector2(w - 2, 11)), DesignTokens.TV_INK_0)
	ci.draw_rect(Rect2(r.position + Vector2(0, 1), Vector2(w, 9)), DesignTokens.TV_INK_0)
	ci.draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(w - 2, 9)), fill)
	ci.draw_string(font, at + Vector2(4, 9), value, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, ink)
	return w


## Color de la chapa de cada tipo de daño (`.b-fuego`, `.b-petroleo`…).
static func type_fill(eco: int) -> Color:
	match eco:
		Enums.EcoType.FIRE:
			return DesignTokens.TV_FIRE_2
		Enums.EcoType.OIL:
			return DesignTokens.TV_SHEEN_0
		Enums.EcoType.PLASTIC:
			return DesignTokens.TV_PLASTIC_0
		Enums.EcoType.MONOCULTURE:
			return DesignTokens.TV_DRY_GRASS_3
		Enums.EcoType.THAW:
			return DesignTokens.TV_ICE_1
	return DesignTokens.TV_GOLD_1   ## avaricia: el jefe de la Cripta


## Barra con su carril oscuro. Al menos 1 px mientras quede algo.
static func bar(ci: CanvasItem, origin: Vector2, w: float, h: float, ratio: float, fill: Color) -> void:
	ci.draw_rect(Rect2(origin, Vector2(w, h)), DesignTokens.TV_INK_0)
	if ratio > 0.0:
		ci.draw_rect(Rect2(origin + Vector2(1, 1), Vector2(maxf(1.0, roundf((w - 2) * ratio)), h - 2)), fill)


## `hp-high` hasta la mitad, `hp-mid` hasta el 20 % y `hp-low` por debajo.
static func hp_fill(ratio: float) -> Color:
	if ratio <= 0.2:
		return DesignTokens.TV_HP_LOW
	if ratio <= 0.5:
		return DesignTokens.TV_HP_MID
	return DesignTokens.TV_HP_HIGH
