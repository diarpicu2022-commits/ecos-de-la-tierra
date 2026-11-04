class_name ActionGround
extends Node2D

## Lo que el combate de acción dibuja en el mundo (contrato «Tajo»):
##
## - La zona de aviso del monstruo, bajo los sprites. Va tramada en Bayer 4×4
##   con `TV_FIRE_2` y borde `TV_INK_0`, igual que la ola: nunca hay un color
##   mezclado, todo píxel es token.
## - El tajo del héroe, una media luna de `TV_GOLD_4` con filo `TV_UI_6`,
##   encima de los sprites durante DUR_SLASH.

const BAYER := [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
## Densidad de la trama: 5 de cada 16 píxeles, para que el suelo se siga leyendo
## (con la mitad, a 640 × 360 se veía como una mancha sólida).
const DENSITY := 5

var combat: ActionCombat = null

var _zone_tex: ImageTexture = null
var _slash_tex: ImageTexture = null
var _slash := Sprite2D.new()
var _slash_frames := 0


func _ready() -> void:
	_zone_tex = ImageTexture.create_from_image(_zone_image(DesignTokens.MONSTER_ATTACK_RADIUS))
	_slash_tex = ImageTexture.create_from_image(_slash_image())
	_slash.texture = _slash_tex
	_slash.visible = false
	_slash.z_index = 60
	add_child(_slash)


## El tajo delante del héroe, girado hacia donde mira (giros de 90°: solo
## transform, la imagen no se repinta).
func slash() -> void:
	var f := Vector2(combat.world.body.facing)
	if f == Vector2.ZERO:
		f = Vector2.DOWN
	f = f.normalized()
	_slash.position = combat.hero_feet() + f * 16.0 - Vector2(0, 10)
	_slash.rotation = f.angle()
	_slash.visible = true
	_slash_frames = maxi(1, roundi(DesignTokens.DUR_SLASH * Engine.physics_ticks_per_second))


func _physics_process(_delta: float) -> void:
	if _slash_frames > 0:
		_slash_frames -= 1
		if _slash_frames == 0:
			_slash.visible = false


func _draw() -> void:
	if combat == null or combat.foe != ActionCombat.Foe.TELEGRAPH:
		return
	var r := DesignTokens.MONSTER_ATTACK_RADIUS
	draw_texture(_zone_tex, (combat.strike_at - Vector2(r, r)).round())


static func _zone_image(r: int) -> Image:
	var size := r * 2 + 1
	var img := Image.create(size, size, false, Image.FORMAT_RGBA8)
	for y in size:
		for x in size:
			var d := Vector2(x - r, y - r).length()
			if d > r:
				continue
			# Un aro que se lee de lejos (tinta, brasa, tinta) y por dentro una
			# trama que se desvanece hacia el centro: el suelo se sigue viendo y
			# la zona no parece un disco pintado encima.
			if d > r - 1.0 or (d > r - 4.0 and d <= r - 3.0):
				img.set_pixel(x, y, DesignTokens.TV_INK_0)
			elif d > r - 3.0:
				img.set_pixel(x, y, DesignTokens.TV_FIRE_3)
			elif BAYER[y % 4][x % 4] < int(DENSITY * (d / r)):
				img.set_pixel(x, y, DesignTokens.TV_FIRE_2)
	return img


## Media luna que mira a la derecha (ángulo 0), de 14 px de radio y 4 de grosor.
static func _slash_image() -> Image:
	var r := 14
	var img := Image.create(r + 4, r * 2 + 1, false, Image.FORMAT_RGBA8)
	for y in img.get_height():
		for x in img.get_width():
			var d := Vector2(x, y - r).length()
			if d <= r and d > r - 4 and x >= 2:
				img.set_pixel(x, y, DesignTokens.TV_UI_6 if d > r - 1.5 else DesignTokens.TV_GOLD_4)
	return img
