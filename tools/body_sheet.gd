extends Node2D

## Captura del paso 2 del contrato «Umbral»: el cuerpo contra el terreno, en el
## medio de salida, 480x270, sobre el tileset real.
##
## Tres casos en la misma pantalla, cada uno con su cuerpo:
##   A  sube hacia un paso de un tile entrando 5 px descentrado: se desliza en
##      la esquina 3 px, 1 por cuadro, y cruza.
##   B  sube contra el canto de un tile de follaje metido 5 px: se para, porque
##      librarlo pediría más de CORNER_SLIP.
##   C  sube en diagonal contra el agua: sigue por el eje libre.
## En la versión «guias», la caja de colisión (12x8) y el rastro de los pies se
## dibujan en EMBER_300: es una marca de herramienta para leer la captura, no
## forma parte del juego. El cuerpo es un marcador provisional con la firma de
## «persona» del catálogo (16x24, contorno ASH_050) hasta que exista su sprite.
##   godot --path . res://tools/body_sheet.tscn

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-09-30"
const T := DesignTokens.TILE_SIZE
const MARKER := Vector2i(16, 24)

const MAP := [
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	".#####.#####...................",
	"..............#......~~~~~~~~.",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
	"..............................",
]

## Por caso: pies de salida, dirección y cuadros.
const CASES := [
	[Vector2i(6 * T + T / 2 + 5, 11 * T), Vector2i.UP, 110],
	[Vector2i(14 * T + 5 - 6, 11 * T), Vector2i.UP, 110],
	[Vector2i(23 * T, 11 * T), Vector2i(1, -1), 90],
]

var _bodies: Array[PlayerBody] = []
var _trails: Array = []
var _show_guides := true
var _overlay := Node2D.new()


func _ready() -> void:
	var lines := PackedStringArray()
	for row: String in MAP:
		lines.append(row.substr(0, 30))
	var layer := TileMapLayer.new()
	layer.tile_set = WorldTiles.build_tileset()
	add_child(layer)
	WorldTiles.paint(layer, WorldTiles.parse(lines), func(_c: Vector2i) -> bool: return false)
	for c in CASES:
		var body := PlayerBody.new()
		body.input_enabled = false
		body.set_physics_process(false)
		body.global_position = Vector2(c[0])
		add_child(body)
		_bodies.append(body)
		_trails.append([c[0]])
	_overlay.z_index = 10
	_overlay.draw.connect(_draw_overlay)
	add_child(_overlay)
	# Los cuerpos de colisión del TileMapLayer se crean al final del cuadro.
	await get_tree().physics_frame
	await get_tree().physics_frame

	for i in CASES.size():
		for _f in CASES[i][2]:
			_bodies[i].step(CASES[i][1], false)
			_trails[i].append(Vector2i(_bodies[i].global_position))
		print("  caso %s: pies en %s" % ["ABC"[i], Vector2i(_bodies[i].global_position)])

	for guides in [true, false]:
		_show_guides = guides
		_overlay.queue_redraw()
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var tag := "guias" if guides else "limpio"
		var path := ProjectSettings.globalize_path(OUT_DIR + "%s-cuerpo-%s.png" % [DATE, tag])
		get_viewport().get_texture().get_image().save_png(path)
		print("  capturado: %s" % path.get_file())
	get_tree().quit()


func _draw_overlay() -> void:
	for i in _bodies.size():
		var feet := Vector2i(_bodies[i].global_position)
		# Marcador de persona: pies en el origen del cuerpo.
		var rect := Rect2i(feet - Vector2i(MARKER.x / 2, MARKER.y), MARKER)
		_overlay.draw_rect(rect, DesignTokens.ASH_400)
		_frame(Rect2i(rect), DesignTokens.ASH_050)
		if not _show_guides:
			continue
		for p: Vector2i in _trails[i]:
			_overlay.draw_rect(Rect2(p, Vector2.ONE), DesignTokens.EMBER_300)
		var box := DesignTokens.PLAYER_HITBOX
		_frame(Rect2i(feet - Vector2i(box.x / 2, box.y), box), DesignTokens.EMBER_300)


## Contorno de 1 px por dentro del rectángulo, en píxeles enteros.
func _frame(r: Rect2i, color: Color) -> void:
	_overlay.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), color)
	_overlay.draw_rect(Rect2(r.position + Vector2i(0, r.size.y - 1), Vector2(r.size.x, 1)), color)
	_overlay.draw_rect(Rect2(r.position, Vector2(1, r.size.y)), color)
	_overlay.draw_rect(Rect2(r.position + Vector2i(r.size.x - 1, 0), Vector2(1, r.size.y)), color)
