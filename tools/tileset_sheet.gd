extends Node2D

## Prueba del paso 2b del contrato «Vereda»: el tileset de terreno en el medio
## de salida, 480x270, con los tres materiales y el camino.
##
## Captura el mismo mapa tres veces: enfermo, purificado y partido por la mitad.
## La tercera es la comparación que importa: el mismo paisaje a los dos lados de
## la línea deja ver si el estado se lee por valor y silueta, no solo por color.
##   godot --path . res://tools/tileset_sheet.tscn

## Treinta por diecisiete tiles: una pantalla entera. Un río que baja en
## diagonal, dos masas de follaje, un camino que cruza y el suelo en medio.
const MAP := [
	"######......~~~~.......#######",
	"#######.....~~~~......########",
	"#####.......~~~~~.......######",
	"###..........~~~~~........####",
	"##....===========~~===========",
	"#.....=........~~~~~......=...",
	"......=........~~~~~......=...",
	"......=.........~~~~~.....=...",
	"...####.........~~~~~~....=...",
	"..######.........~~~~~~...=...",
	"..#######=========~~~~~~===...",
	"...######.........~~~~~~......",
	"....####...........~~~~~~.....",
	"....................~~~~~~~~~~",
	"......####.............####...",
	".....######...........######..",
	"....########.........########.",
]


func _ready() -> void:
	var layer := TileMapLayer.new()
	layer.tile_set = WorldTiles.build_tileset()
	add_child(layer)
	var grid := WorldTiles.parse(PackedStringArray(MAP))
	var half := int(MAP[0].length() / 2)

	var cases := {
		"enfermo": func(_c: Vector2i) -> bool: return false,
		"purificado": func(_c: Vector2i) -> bool: return true,
		"partido": func(c: Vector2i) -> bool: return c.x >= half,
	}
	for tag in cases:
		layer.clear()
		WorldTiles.paint(layer, grid, cases[tag])
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("user://tileset_%s.png" % tag)
		print("  capturado: tileset_%s.png" % tag)

	get_tree().quit()
