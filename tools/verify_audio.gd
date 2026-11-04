extends Node

## El sonido provisional (`src/core/game_audio.gd`, guía del equipo §4.13):
##
##   godot --headless --path . res://tools/verify_audio.tscn
##
## Mide lo que se puede medir sin oírlo: los cuatro buses, que cargan todos los
## audios, que los bucles se repiten y los efectos no, que el filtro del ambiente
## sigue a lo sano y lo enfermo, y que el mundo y el combate cambian la música.
## Si suena bien hay que juzgarlo de oído.
## Sale con código 1 si algo falla.

## Por debajo de esto, el bus está en silencio.
const SILENT_DB := -70.0

var _pass := 0
var _fail := 0


func _ready() -> void:
	var audio := get_node("/root/GameAudio")
	DesignTokens.reduced_motion = true

	print("Buses")
	for bus in ["Música", "Ambiente", "Efectos", "Interfaz"]:
		_check("existe el bus %s" % bus, AudioServer.get_bus_index(bus) >= 0)
	var ambient := AudioServer.get_bus_index("Ambiente")
	_check("el ambiente lleva el filtro de paso bajo",
		AudioServer.get_bus_effect(ambient, 0) is AudioEffectLowPassFilter)

	print("\nAudios")
	for sound in audio.UI_SOUNDS + audio.EFFECT_SOUNDS:
		var stream: AudioStreamWAV = audio._streams.get(sound)
		_check("%s carga, dura menos de 3 s y no se repite" % sound, stream != null
			and stream.get_length() > 0.0 and stream.get_length() < 3.0
			and stream.loop_mode == AudioStreamWAV.LOOP_DISABLED)
	for sound in audio.LOOPS:
		var stream: AudioStreamWAV = audio._streams.get(sound)
		_check("%s se repite entero (%.1f s)" % [sound, stream.get_length()],
			stream.loop_mode == AudioStreamWAV.LOOP_FORWARD and stream.loop_end > 0)

	print("\nReparto")
	audio.play("ui_move")
	_check("la interfaz va a su bus", _last_voice(audio).bus == "Interfaz")
	audio.play("hit")
	_check("los efectos van al suyo", _last_voice(audio).bus == "Efectos")

	print("\nAmbiente")
	audio.start_ambient(false)
	_check("enfermo: suena el viento, apagado", audio._filter.cutoff_hz == audio.CUTOFF_SICK
		and audio._wind.volume_db == 0.0 and audio._life.volume_db == audio.SILENCE)
	audio.set_alive(true)
	_check("sano: suena la vida, con el filtro abierto", audio._filter.cutoff_hz == audio.CUTOFF_ALIVE
		and audio._life.volume_db == 0.0 and audio._wind.volume_db == audio.SILENCE)
	audio.set_in_battle(true)
	_check("en combate, el ambiente se retira", true if await _settled(audio) else false)
	audio.set_in_battle(false)

	print("\nMúsica y juego")
	var flow := GameFlow.new()
	add_child(flow)
	await get_tree().physics_frame
	_check("al empezar, la del mundo", audio.current_music == "music_world")
	_check("Valdehoja empieza fuera del jardín: ambiente enfermo", not audio.alive)
	flow.world.enter_zone("ashen_forest", Vector2i(44, 15))
	await get_tree().physics_frame
	flow.world.monster.contact.emit(MapMonster.Advantage.NONE)
	_check("al tocar al monstruo, la del combate", audio.current_music == "music_battle" and audio.in_battle)
	for i in 120:
		await get_tree().physics_frame
		if flow.screen != null and not flow.blinds.running:
			break
	flow.result = Enums.BattleResult.FLED
	flow.leave_battle()
	_check("al salir, vuelve la del mundo", audio.current_music == "music_world" and not audio.in_battle)
	for i in 120:
		await get_tree().physics_frame
		if flow.screen == null and not flow.blinds.running:
			break
	if DisplayServer.get_name() != "headless":
		print("
Señal (con ventana y el driver de audio real)")
		var music := AudioServer.get_bus_index("Música")
		var peak := SILENT_DB
		for i in 120:
			await get_tree().physics_frame
			peak = maxf(peak, AudioServer.get_bus_peak_volume_left_db(music, 0))
		_check("por el bus Música pasa señal (pico %.1f dB)" % peak, peak > SILENT_DB)
		audio.play("hit")
		var effects := AudioServer.get_bus_index("Efectos")
		peak = SILENT_DB
		for i in 12:
			await get_tree().physics_frame
			peak = maxf(peak, AudioServer.get_bus_peak_volume_left_db(effects, 0))
		_check("por el bus Efectos pasa señal (pico %.1f dB)" % peak, peak > SILENT_DB)
	get_node("/root/GameState").flags.clear()
	flow.queue_free()

	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _settled(audio: Node) -> bool:
	for i in roundi((audio.FADE_SECONDS + 0.2) * Engine.physics_ticks_per_second):
		await get_tree().physics_frame
	return audio._life.volume_db <= audio.SILENCE + 0.5 and audio._wind.volume_db <= audio.SILENCE + 0.5


func _last_voice(audio: Node) -> AudioStreamPlayer:
	return audio._voices[(audio._next_voice - 1 + audio.VOICES) % audio.VOICES]


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
