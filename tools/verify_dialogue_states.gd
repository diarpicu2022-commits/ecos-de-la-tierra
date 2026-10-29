extends Node

## Los estados del diálogo (contrato «Columna», paso 5), en el motor:
##
##   godot --path . res://tools/verify_dialogue_states.tscn
##
## - **Rasgo, brasa y ceniza:** sin la bandera `rasgo_left_company` su nombre
##   sale en EMBER_400; con ella, en TEXT_SECONDARY. Se mide el color del
##   nombre sobre el render y su contraste con el panel (≥ 4,5:1).
## - **Yara a distancia:** al cruzar de Valdehoja al Bosque, tras el fundido,
##   se abre sola «yara_ave_bosque» con el retrato del ave, a la izquierda;
##   Ilan y el monstruo se paran; al terminar vuelven, y no se repite.
## - **Sin máquina de escribir:** con movimiento reducido o la máquina
##   apagada, la línea está completa en el primer cuadro; encendida, no.
## Capturas: docs/ux/capturas/2026-10-29-dialogo-*.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/2026-10-29-dialogo-%s.png"

var _pass := 0
var _fail := 0
var _state: Node = null


func _ready() -> void:
	_state = get_node("/root/GameState")
	_state.flags.clear()
	DesignTokens.reduced_motion = false
	var world := WorldRoot.new()
	world.start_zone = "valdehoja"
	world.start_cell = Vector2i(58, 17)
	add_child(world)
	await get_tree().physics_frame
	await _rasgo(world)
	await _distance(world)
	await _no_typewriter(world)
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


func _rasgo(world: WorldRoot) -> void:
	print("Rasgo: brasa y ceniza")
	world.label.visible = false
	DialogueBox.typewriter_enabled = false
	for left in [false, true]:
		_state.set_flag("rasgo_left_company", left)
		world.dialogue.start("rasgo_bosque")
		var box := world.dialogue.box
		var img := await _shot()
		img.save_png(ProjectSettings.globalize_path(OUT % ("rasgo-ceniza" if left else "rasgo-brasa")))
		var want := DesignTokens.TEXT_SECONDARY if left else DesignTokens.EMBER_400
		var name_rect := Rect2(box.position + box.text_rect().position, Vector2(30, 12))
		var got := _brightest(img, name_rect)
		var ratio := _ratio(_lum(got), _lum(DesignTokens.PANEL_FILL))
		_check("%s: el nombre sale en %s (medido %s) y contrasta %.1f:1 (≥ 4,5)" % [
			"dejó la Compañía" if left else "sirve a la Compañía",
			"TEXT_SECONDARY" if left else "EMBER_400", got.to_html(false), ratio],
			got.is_equal_approx(want) and ratio >= 4.5 and box.side == DialogueBox.Side.RIGHT)
		while world.dialogue.is_running():
			box.confirm()
			await get_tree().process_frame
	_state.flags.clear()
	DialogueBox.typewriter_enabled = true


func _distance(world: WorldRoot) -> void:
	print("\nYara a distancia, por el ave")
	world.body.facing = Vector2i.RIGHT
	world.body.global_position = Vector2(WorldRoot.feet_of(Vector2i(60, 17)))
	for i in 240:
		await get_tree().physics_frame
		if world.zone_id == "ashen_forest" and world.fade == WorldRoot.Fade.NONE:
			break
	await get_tree().physics_frame
	_check("tras el fundido al Bosque se abre sola «%s»" % world.dialogue.conversation,
		world.zone_id == "ashen_forest" and world.dialogue.is_running()
		and world.dialogue.conversation == "yara_ave_bosque")
	var box := world.dialogue.box
	_check("habla «%s» con el retrato del ave, a la izquierda" % box.speaker,
		box.speaker == "Yara" and box.side == DialogueBox.Side.LEFT
		and box.portrait != null and box.portrait.resource_path.ends_with("yara_ave_neutral.png"))
	_check("Ilan y el monstruo se paran mientras habla",
		not world.body.input_enabled and world.monster != null and not world.monster.active)
	box.confirm()
	world.label.visible = false
	var img := await _shot()
	img.save_png(ProjectSettings.globalize_path(OUT % "ave-bosque"))
	while world.dialogue.is_running():
		box.confirm()
		await get_tree().process_frame
	_check("al terminar, Ilan y el monstruo vuelven a moverse",
		world.body.input_enabled and world.monster.active and not box.visible)
	_check("no se repite: está marcada como oída",
		world.try_arrival_talk() == "" and _state.flag("heard_yara_ave_bosque"))


func _no_typewriter(world: WorldRoot) -> void:
	print("\nSin máquina de escribir")
	var box := world.dialogue.box
	for mode in ["encendida", "movimiento reducido", "máquina apagada"]:
		DesignTokens.reduced_motion = mode == "movimiento reducido"
		DialogueBox.typewriter_enabled = mode != "máquina apagada"
		world.dialogue.start("yara_ave_bosque")
		await get_tree().physics_frame
		var complete := box.is_complete()
		_check("%s: %s en el primer cuadro (%d de %d caracteres)" % [mode,
			"incompleta" if mode == "encendida" else "completa", box.visible_chars, box.total_chars],
			complete == (mode != "encendida"))
		if mode == "movimiento reducido":
			var img := await _shot()
			img.save_png(ProjectSettings.globalize_path(OUT % "movimiento-reducido"))
		while world.dialogue.is_running():
			box.confirm()
			await get_tree().process_frame
	DesignTokens.reduced_motion = false
	DialogueBox.typewriter_enabled = true


func _shot() -> Image:
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


func _brightest(img: Image, r: Rect2) -> Color:
	var best := Color.BLACK
	for y in range(int(r.position.y), int(r.end.y)):
		for x in range(int(r.position.x), int(r.end.x)):
			var c := img.get_pixel(x, y)
			if _lum(c) > _lum(best):
				best = c
	return best


func _ratio(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


func _lum(c: Color) -> float:
	var ch := func(v: float) -> float:
		return v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4)
	return 0.2126 * ch.call(c.r) + 0.7152 * ch.call(c.g) + 0.0722 * ch.call(c.b)
