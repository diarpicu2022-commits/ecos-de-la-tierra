extends Node

## Sonido del juego (autoload `GameAudio`). Provisional: los audios salen de
## `tools/gen_audio.py` y la parte 11 (guía del equipo §4.13) aún no tiene anexo.
##
## Cuatro buses, los que pide la guía: Música, Ambiente, Efectos e Interfaz. El
## ambiente lleva un filtro de paso bajo: lo enfermo suena apagado y se abre al
## ritmo de la ola (`DUR_ZONE_PURIFY`). Ningún sonido dice nada que no diga ya la
## pantalla.

const DIR := "res://assets/audio/"
const BUS_MUSIC := "Música"
const BUS_AMBIENT := "Ambiente"
const BUS_EFFECTS := "Efectos"
const BUS_UI := "Interfaz"

## Niveles de mezcla, en dB.
const VOLUME_MUSIC := -15.0
const VOLUME_AMBIENT := -14.0
const VOLUME_EFFECTS := -7.0
const VOLUME_UI := -13.0
const SILENCE := -60.0

## Corte del filtro del ambiente, en Hz: apagado en lo enfermo, abierto en lo sano.
const CUTOFF_SICK := 500.0
const CUTOFF_ALIVE := 16000.0

const FADE_SECONDS := 0.8
const VOICES := 8

const UI_SOUNDS := ["ui_move", "ui_confirm", "ui_cancel", "ui_denied"]
const EFFECT_SOUNDS := ["hit", "hit_resisted", "heal", "regen", "purify", "wave", "blinds",
	"victory", "defeat"]
const LOOPS := ["amb_wind", "amb_life", "music_world", "music_battle"]

var alive := false
var in_battle := false
var current_music := ""

var _streams := {}
var _voices: Array[AudioStreamPlayer] = []
var _next_voice := 0
var _music: AudioStreamPlayer = null
var _wind: AudioStreamPlayer = null
var _life: AudioStreamPlayer = null
var _filter: AudioEffectLowPassFilter = null
var _music_tween: Tween = null
var _ambient_tween: Tween = null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_make_buses()
	for sound in UI_SOUNDS + EFFECT_SOUNDS + LOOPS:
		var stream: AudioStreamWAV = load(DIR + sound + ".wav")
		if sound in LOOPS:
			stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
			stream.loop_begin = 0
			stream.loop_end = roundi(stream.get_length() * stream.mix_rate)
		_streams[sound] = stream
	for i in VOICES:
		_voices.append(_player(BUS_EFFECTS))
	_music = _player(BUS_MUSIC)
	_wind = _player(BUS_AMBIENT)
	_life = _player(BUS_AMBIENT)


func _make_buses() -> void:
	var levels := {BUS_MUSIC: VOLUME_MUSIC, BUS_AMBIENT: VOLUME_AMBIENT,
		BUS_EFFECTS: VOLUME_EFFECTS, BUS_UI: VOLUME_UI}
	for bus_name: String in levels:
		var index := AudioServer.bus_count
		AudioServer.add_bus(index)
		AudioServer.set_bus_name(index, bus_name)
		AudioServer.set_bus_volume_db(index, levels[bus_name])
	_filter = AudioEffectLowPassFilter.new()
	_filter.cutoff_hz = CUTOFF_SICK
	AudioServer.add_bus_effect(AudioServer.get_bus_index(BUS_AMBIENT), _filter)


func _player(bus: String) -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.bus = bus
	add_child(player)
	return player


## Suena un efecto. Los de interfaz van a su bus, para que luego se regulen aparte.
func play(sound: String) -> void:
	if not _streams.has(sound):
		push_error("GameAudio: no existe el sonido «%s»" % sound)
		return
	var voice := _voices[_next_voice]
	_next_voice = (_next_voice + 1) % VOICES
	voice.bus = BUS_UI if sound in UI_SOUNDS else BUS_EFFECTS
	voice.stream = _streams[sound]
	voice.play()


## Cambia de música con un fundido. Vacío, la apaga.
func play_music(track: String) -> void:
	if track == current_music:
		return
	current_music = track
	if _music_tween != null and _music_tween.is_valid():
		_music_tween.kill()
	_music_tween = create_tween()
	if _music.playing:
		_music_tween.tween_property(_music, "volume_db", SILENCE, FADE_SECONDS / 2.0)
	_music_tween.tween_callback(_start_music.bind(track))


func _start_music(track: String) -> void:
	_music.stop()
	if track.is_empty():
		return
	_music.stream = _streams[track]
	_music.volume_db = SILENCE
	_music.play()
	_music_tween = create_tween()
	_music_tween.tween_property(_music, "volume_db", 0.0, FADE_SECONDS / 2.0)


## Arranca el ambiente de la exploración.
func start_ambient(is_alive: bool) -> void:
	if not _wind.playing:
		_wind.stream = _streams["amb_wind"]
		_life.stream = _streams["amb_life"]
		_wind.play()
		_life.play()
	alive = not is_alive
	set_alive(is_alive)


## Lo que rodea al jugador está sano o enfermo: se abre o se cierra el filtro y
## pasa del viento a la vida. Tarda lo que la ola; con movimiento reducido, de golpe.
func set_alive(is_alive: bool) -> void:
	if is_alive == alive:
		return
	alive = is_alive
	_mix_ambient(DesignTokens.duration(DesignTokens.DUR_ZONE_PURIFY))


## En combate, el ambiente se retira y manda la música.
func set_in_battle(value: bool) -> void:
	in_battle = value
	_mix_ambient(FADE_SECONDS)


func _mix_ambient(seconds: float) -> void:
	var life_db := SILENCE if in_battle or not alive else 0.0
	var wind_db := SILENCE if in_battle or alive else 0.0
	var cutoff := CUTOFF_ALIVE if alive else CUTOFF_SICK
	if _ambient_tween != null and _ambient_tween.is_valid():
		_ambient_tween.kill()
	if seconds <= 0.0:
		_life.volume_db = life_db
		_wind.volume_db = wind_db
		_filter.cutoff_hz = cutoff
		return
	_ambient_tween = create_tween().set_parallel()
	_ambient_tween.tween_property(_life, "volume_db", life_db, seconds)
	_ambient_tween.tween_property(_wind, "volume_db", wind_db, seconds)
	_ambient_tween.tween_property(_filter, "cutoff_hz", cutoff, seconds)
