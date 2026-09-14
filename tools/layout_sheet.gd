extends Node2D

## Prueba del paso 3: el esqueleto de la pantalla de batalla, con y sin guías.
##   godot --path . res://tools/layout_sheet.tscn

var _screen: BattleScreen = null
var _monster: Monster = null


func _ready() -> void:
	_monster = DeforestationFlame.new()
	add_child(_monster)
	_monster.hp = 128

	_screen = BattleScreen.new()
	add_child(_screen)
	_screen.show_monster(_monster)

	for with_guides in [true, false]:
		_screen.show_skeleton = with_guides
		_screen.queue_redraw()
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var tag := "guias" if with_guides else "limpio"
		get_viewport().get_texture().get_image().save_png("user://layout_%s.png" % tag)
		print("  capturado: layout_%s.png" % tag)

	get_tree().quit()
