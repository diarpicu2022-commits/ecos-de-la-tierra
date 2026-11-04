extends Node

## La primera escena de historia, en el juego de verdad:
##
##   godot --path . res://tools/verify_opening.tscn
##
## Arranca `GameFlow` como `scenes/game.tscn`: al empezar, Yara llama por el ave; Ilan
## no se mueve hasta terminar; la escena no se repite; en el jardín, mirando a Yara,
## ella cuenta lo que pasa; y al entrar en el Bosque, Yara habla por el ave. Con
## ventana, escribe docs/ux/capturas/<fecha>-historia-*.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-historia-%s.png"

var _pass := 0
var _fail := 0


func _ready() -> void:
	var state := get_node("/root/GameState")
	state.flags.clear()
	DesignTokens.reduced_motion = true
	var flow := GameFlow.new()
	flow.play_opening = true
	add_child(flow)
	await get_tree().process_frame
	await get_tree().process_frame
	var world := flow.world
	var runner := world.dialogue

	print("La llamada")
	_check("al empezar se abre la llamada de Yara",
		runner.is_running() and runner.conversation == "yara_llamada")
	_check("Ilan no se mueve mientras escucha", not world.body.input_enabled)
	await _shot("llamada")
	_check("no avanza sola", await _stays(runner, 0))
	await _finish(runner)
	_check("al terminar, Ilan vuelve a moverse", world.body.input_enabled and not runner.box.visible)
	_check("no se repite", world.try_opening_talk() == "")

	print("\nEn el jardín")
	var below := Vector2i(86, 22)
	world.enter_zone("valdehoja", below)
	world.body.facing = Vector2i.UP
	await get_tree().process_frame
	_check("mirando a Yara, cuenta lo que pasa", world.try_talk() == "yara_inicio")
	await _shot("jardin")
	var seen := PackedStringArray()
	while runner.is_running():
		seen.append(runner.box.speaker)
		if runner.index == 1:
			await _shot("jardin-ilan")
		runner.box.confirm()
		await get_tree().process_frame
	_check("hablan los dos (%d líneas)" % seen.size(), seen.has("Yara") and seen.has("Ilan"))
	_check("al terminar, Ilan vuelve a moverse", world.body.input_enabled)

	print("\nEn el Bosque")
	world.enter_zone("ashen_forest", Vector2i(1, 16))
	await get_tree().process_frame
	_check("al llegar, Yara habla por el ave", world.try_arrival_talk() == "yara_ave_bosque")
	if world.monster != null:
		_check("el monstruo espera mientras se habla", not world.monster.active)
	await _shot("bosque")
	await _finish(runner)
	_check("solo la primera vez", world.try_arrival_talk() == "")

	state.flags.clear()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _stays(runner: DialogueRunner, line: int) -> bool:
	for i in 180:
		await get_tree().physics_frame
	return runner.is_running() and runner.index == line


func _finish(runner: DialogueRunner) -> void:
	while runner.is_running():
		runner.box.confirm()
		await get_tree().process_frame


func _shot(tag: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	var path := OUT % [Time.get_date_string_from_system(), tag]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
