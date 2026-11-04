extends Node

## Hablar en el mundo (contrato «Columna», paso 4), en el motor:
##
##   godot --path . res://tools/verify_talk.tscn
##
## En Valdehoja, con Ilan bajo Yara:
## - de espaldas a ella no se abre nada;
## - mirándola, `confirm` abre «yara_inicio» y Ilan deja de moverse;
## - cada línea sale con su voz, su lado y su retrato (Yara e Ilan a la
##   izquierda); `confirm` completa y avanza, hasta cerrar;
## - al terminar, la caja se va e Ilan vuelve a moverse.
## Capturas: docs/ux/capturas/2026-10-28-dialogo-mundo-*.png.
## Sale con código 1 si algo falla.

var _pass := 0
var _fail := 0


func _ready() -> void:
	get_node("/root/GameState").flags.clear()
	var world := WorldRoot.new()
	world.start_zone = "valdehoja"
	world.start_cell = Vector2i(32, 8)
	add_child(world)
	await get_tree().physics_frame
	world.label.visible = false
	world.body.facing = Vector2i.DOWN
	_check("de espaldas a Yara no se abre nada", world.try_talk() == "")
	world.body.facing = Vector2i.UP
	var id := world.try_talk()
	_check("mirándola se abre «%s»" % id, id == "yara_inicio" and world.dialogue.is_running())
	_check("Ilan deja de moverse mientras se habla", not world.body.input_enabled)
	var seen := []
	var shots := 0
	for i in 20:
		var box := world.dialogue.box
		if not world.dialogue.is_running():
			break
		seen.append([box.speaker, box.side, box.portrait != null])
		box.confirm()          # completa
		await RenderingServer.frame_post_draw
		if shots < 2 and box.speaker in ["Yara", "Ilan"] and (shots == 0 or box.speaker == "Ilan"):
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(
				"res://docs/ux/capturas/2026-10-28-dialogo-mundo-%s.png" % box.speaker.to_lower()))
			shots += 1
		box.confirm()          # avanza
		await get_tree().process_frame
	_check("seis líneas, cada una con voz, lado izquierdo y retrato (%s)" % [seen.map(func(s): return s[0])],
		seen.size() == 6 and seen.all(func(s): return s[1] == DialogueBox.Side.LEFT and s[2]))
	_check("al terminar la caja se va e Ilan vuelve a moverse",
		not world.dialogue.box.visible and world.body.input_enabled and not world.dialogue.is_running())
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
