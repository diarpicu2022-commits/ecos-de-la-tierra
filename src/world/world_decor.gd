class_name WorldDecor
extends RefCounted

## Monta la capa de decorado de una zona (`<zona>.deco.txt`) en el motor.
## Contrato «Rastro», fase 5, Valdehoja, paso 3; enmiendas 6 y 7.
##
## Cada pieza es un `Sprite2D` en la capa de entidades, que se ordena por
## altura: su posición es el pie de la pieza (centro del borde inferior), así
## que Ilan pasa por delante de lo que está al norte y por detrás de lo que
## está al sur. Lo sólido lleva además un `StaticBody2D` del tamaño entero de
## la pieza, en tiles enteros como el terreno («Umbral»: la colisión es el tile
## entero, no la silueta). Es la misma regla que usa `verify_zone.gd` para el
## recorrido.
##
## El estado de cada pieza (enfermo o purificado) lo da la casilla central de
## su fila de abajo. La fauna silvestre solo se monta donde está purificado
## (enmienda 7). La aparición no se dibuja: solo dice dónde empieza Ilan.
##
## Los sprites salen de `tools/gen_world_decor.py`.

const DECOR_DIR := "res://assets/sprites/world/decor/"

## Sprite de cada id de la leyenda cuando no se llama igual.
const SPRITE := {"person": "yara", "chicken": "chicken_0", "bird": "bird_0",
	"butterfly": "butterfly_0"}


## Lo que se mece al purificar (enmienda 8): tiene un segundo cuadro
## `<id>_pure_1.png`.
const SWAYS := ["grass", "flower", "weed", "crop_row"]

## Árboles: se dibujan desplazados hasta JITTER_PX px por pieza para que un
## bosque no se lea como plantación (Bosque, 2026-10-28).
const JITTER := ["tree", "tree_b", "burnt_tree"]
const JITTER_PX := 3

## Lo que desaparece con la ola de purificación (catálogo 2a).
const VANISH_WHEN_PURE := ["blocker", "monster"]


## Monta las piezas de `zone_id`: los sprites van a `entities` y los cuerpos
## sólidos a `solids`; las casillas que ocupa lo sólido se anotan en
## `blocked`. Devuelve la casilla de aparición, o (-1, -1) si la capa no la
## tiene. Lo que se mueve (enmienda 8) lleva sus cuadros en la meta `frames`,
## para `WorldAmbient`.
static func build(zone_id: String, purified_at: Callable, entities: Node, solids: Node,
		blocked: Dictionary = {}) -> Vector2i:
	var deco := ZoneRules.load_deco(zone_id)
	if deco.is_empty():
		return Vector2i(-1, -1)
	var legend: Dictionary = deco["legend"]
	var rows: PackedStringArray = deco["rows"]
	var t := DesignTokens.TILE_SIZE
	var spawn := Vector2i(-1, -1)
	for piece in pieces(rows, legend):
		var entry: Dictionary = legend[piece["ch"]]
		var at: Vector2i = piece["at"]
		var size: Vector2i = entry["size"]
		if entry["kind"] == "spawn":
			spawn = at
			continue
		var pure: bool = purified_at.call(at + Vector2i(size.x / 2, size.y - 1))
		if entry["kind"] == "fauna" and not pure:
			continue
		# El paso cerrado y el monstruo desaparecen con la ola (catálogo 2a):
		# purificado, ni sprite ni cuerpo.
		if pure and entry["id"] in VANISH_WHEN_PURE:
			continue
		var texture := _texture(entry["id"], pure, zone_id)
		if texture == null:
			push_error("%s: no hay sprite para «%s»" % [zone_id, entry["id"]])
			continue
		var sprite := Sprite2D.new()
		sprite.texture = texture
		sprite.centered = false
		sprite.name = "%s_%d_%d" % [entry["id"], at.x, at.y]
		var feet := Vector2((at.x * t) + size.x * t / 2.0, (at.y + size.y) * t)
		var lift := 0
		if texture.get_width() < t:
			# Lo pequeño (animales, fauna) se apoya en el centro de su tile.
			lift = (t - texture.get_height()) / 2
		if entry["id"] in JITTER:
			# Rompe la cuadrícula: unos píxeles por árbol, fijos por posición.
			# Solo el dibujo; la colisión sigue en tiles enteros.
			var h := absi(hash(at))
			feet += Vector2((h % (2 * JITTER_PX + 1)) - JITTER_PX, ((h / 7) % 3) - 1)
		sprite.position = feet
		sprite.offset = Vector2(-texture.get_width() / 2, -texture.get_height() - lift)
		entities.add_child(sprite)
		_mark_motion(sprite, entry, at, pure)
		if entry["solid"]:
			for j in size.y:
				for i in size.x:
					blocked[at + Vector2i(i, j)] = true
			var body := StaticBody2D.new()
			body.name = "solid_" + sprite.name
			var shape := RectangleShape2D.new()
			shape.size = Vector2(size * t)
			var collider := CollisionShape2D.new()
			collider.shape = shape
			body.position = Vector2(at * t) + shape.size / 2.0
			body.add_child(collider)
			solids.add_child(body)
	return spawn


## Las piezas por su esquina superior izquierda: `[{ch, at}]`. Una pieza de
## varios tiles ocupa su tamaño entero; `verify_zone.gd` comprueba que está
## completa.
static func pieces(rows: PackedStringArray, legend: Dictionary) -> Array:
	var claimed := {}
	var out := []
	for y in rows.size():
		for x in rows[y].length():
			var ch := rows[y][x]
			if ch == " " or claimed.has(Vector2i(x, y)) or not legend.has(ch):
				continue
			var size: Vector2i = legend[ch]["size"]
			for j in size.y:
				for i in size.x:
					claimed[Vector2i(x + i, y + j)] = true
			out.append({"ch": ch, "at": Vector2i(x, y)})
	return out


## Estado de cada casilla de una zona, como lo pinta el mundo. En una zona sin
## partes, toda la zona sigue la bandera `purified_<zona>`. En Valdehoja, cada
## parte sigue la bandera de su región, el jardín de Yara está purificado desde
## el principio y lo que no es de ninguna parte sigue la de Valdehoja (el
## final del juego).
static func purified_lookup(zone_id: String, state: Node) -> Callable:
	var zone_pure: bool = state != null and state.is_zone_purified(zone_id)
	var parts := ZoneRules.load_parts(zone_id)
	if parts.is_empty():
		return func(_c: Vector2i) -> bool: return zone_pure
	var pure_cells := {}
	for id in parts:
		var on: bool = id == "yara_garden" or (state != null and state.is_zone_purified(id))
		if on:
			for c: Vector2i in parts[id]:
				pure_cells[c] = true
	return func(c: Vector2i) -> bool: return zone_pure or pure_cells.has(c)


## Cuadros y fase de lo que se mueve. Lo enfermo no lleva cuadros: no se
## mueve. Los animales sí los llevan siempre; `WorldAmbient` solo los deja
## andar por lo purificado.
static func _mark_motion(sprite: Sprite2D, entry: Dictionary, at: Vector2i, pure: bool) -> void:
	var id: String = entry["id"]
	var kind: String = entry["kind"]
	var frames: Array[Texture2D] = []
	if kind == "decor" and pure and id in SWAYS:
		var alt := "%s%s_pure_1.png" % [DECOR_DIR, id]
		if ResourceLoader.exists(alt):
			frames = [sprite.texture, load(alt)]
	elif kind == "fauna" or kind == "animal":
		var base: String = SPRITE.get(id, id)
		frames = [sprite.texture]
		if base.ends_with("_0"):
			var alt := "%s%s_1_%s.png" % [DECOR_DIR, base.trim_suffix("_0"), "pure" if pure else "sick"]
			if ResourceLoader.exists(alt):
				frames.append(load(alt))
	if frames.is_empty():
		return
	sprite.set_meta("frames", frames)
	sprite.set_meta("kind", kind)
	sprite.set_meta("phase", absi(hash(at)) % 97)
	sprite.set_meta("base_y", sprite.position.y)


## El sprite de una pieza: primero el propio de la región
## (`monster_ashen_forest_sick.png`), después el común. Las viñetas se dibujan
## con el sprite de su elemento: `v1_stump` usa `stump`.
static func _texture(id: String, pure: bool, zone_id: String) -> Texture2D:
	var name: String = SPRITE.get(id, id)
	if name.length() > 3 and name[0] == "v" and name[1].is_valid_int() and name[2] == "_":
		name = name.substr(3)
	for state in (["pure", "sick"] if pure else ["sick", "pure"]):
		for base in ["%s_%s" % [name, zone_id], name]:
			var path := "%s%s_%s.png" % [DECOR_DIR, base, state]
			if ResourceLoader.exists(path):
				return load(path)
	return null
