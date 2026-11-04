extends Node

## La demo hasta el primer jefe (`docs/plan-para-terminar-la-historia.md`):
##   godot --headless --path . res://tools/verify_demo.tscn
##
## - la salida de Valdehoja a la Cripta no cambia de zona y lo explica;
## - al llegar al Bosque hablan Yara y después Rasgo, sin retrato viejo;
## - la salida del Bosque a la Cuenca cierra la demo y deja a Ilan en el mapa;
## - la escena de juego lleva la demo encendida, y sin ella las salidas funcionan.

var _pass := 0
var _fail := 0


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
		print("  OK    " + label)
	else:
		_fail += 1
		printerr("  FALLA " + label)


func _finish(runner: DialogueRunner) -> void:
	while runner.is_running():
		runner.box.confirm()
		await get_tree().process_frame


func _cross(world: WorldRoot, outside: Vector2i) -> void:
	world.body.global_position = Vector2(WorldRoot.feet_of(outside))
	await get_tree().physics_frame
	await get_tree().physics_frame


## Sin ventana no hay dibujo: la captura solo se hace con ventana.
func _shot(tag: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	# La línea completa, no el arranque de la máquina de escribir.
	(get_node("/root").find_child("VerifyDemo", true, false) as Node).get_child(0).world.dialogue.box.confirm()
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var path := "res://docs/ux/capturas/2026-11-03-demo-%s.png" % tag
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))


func _ready() -> void:
	var scene := FileAccess.get_file_as_string("res://scenes/game.tscn")
	_check("la escena de juego lleva la demo encendida", scene.contains("demo = true"))
	var state := get_node("/root/GameState")
	state.flags.clear()
	DesignTokens.reduced_motion = true
	var flow := GameFlow.new()
	flow.demo = true
	add_child(flow)
	await get_tree().process_frame
	var world := flow.world
	var runner := world.dialogue

	print("La Cripta, cerrada")
	await _cross(world, Vector2i(3, -1))
	_check("no cambia de zona", world.zone_id == "valdehoja")
	_check("Ilan explica por qué", runner.is_running() and runner.conversation == "demo_cripta")
	_check("Ilan sigue dentro del mapa", Rect2i(Vector2i.ZERO, world.zone_size).has_point(
		MapMonster.cell_of(Vector2i(world.body.global_position))))
	await _finish(runner)
	_check("al terminar, Ilan vuelve a moverse", world.body.input_enabled)

	print("El Bosque")
	world.enter_zone("ashen_forest", Vector2i(1, 16))
	await get_tree().process_frame
	_check("al llegar, Yara habla por el ave", world.try_arrival_talk() == "yara_ave_bosque")
	_check("Yara lleva retrato del sistema", runner.box.portrait != null
		and runner.box.portrait.resource_path.contains("/tierra_viva/"))
	await _shot("yara-ave")
	while runner.is_running() and runner.conversation == "yara_ave_bosque":
		runner.box.confirm()
		await get_tree().process_frame
	_check("después aparece Rasgo", runner.is_running() and runner.conversation == "rasgo_bosque")
	_check("Rasgo habla sin retrato viejo", runner.box.portrait == null)
	await _shot("rasgo")
	await _finish(runner)
	_check("al terminar, Ilan y el monstruo se mueven",
		world.body.input_enabled and world.monster != null and world.monster.active)

	print("El fin de la demo")
	var last := world.zone_size.y
	await _cross(world, Vector2i(75, last))
	_check("no pasa a la Cuenca", world.zone_id == "ashen_forest")
	_check("abre el mensaje final", runner.is_running() and runner.conversation == "demo_fin")
	_check("sin retrato, y lo dice la demo", runner.box.portrait == null and runner.box.speaker == "Demo")
	await _shot("fin")
	await _finish(runner)
	_check("Ilan puede seguir paseando por el Bosque", world.body.input_enabled)

	print("Sin demo")
	world.demo = false
	await _cross(world, Vector2i(75, last))
	for i in 10:
		await get_tree().physics_frame
	_check("sin demo, la salida lleva a la Cuenca", world.zone_id == "tar_basin")

	state.flags.clear()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)
