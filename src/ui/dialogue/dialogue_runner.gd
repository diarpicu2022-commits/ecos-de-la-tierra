class_name DialogueRunner
extends CanvasLayer

## Lleva una conversación de `data/dialogue/<id>.json` línea a línea sobre una
## `DialogueBox` (contrato «Columna»). Cada línea dice quién habla y con qué
## expresión; el lado, el nombre y su color salen de `voices.json`. Avanza solo
## con `confirm`, y al terminar cierra la caja y emite `finished`.

signal finished(conversation_id: String)

const DATA := "res://data/dialogue/"
const PORTRAITS := "res://assets/sprites/portraits/"

var box := DialogueBox.new()
var conversation := ""
var index := -1
var _lines: Array = []
var _voices := {}


func _init() -> void:
	layer = 8
	add_child(box)


func _ready() -> void:
	var data = JSON.parse_string(FileAccess.get_file_as_string(DATA + "voices.json"))
	_voices = data["voices"] if data is Dictionary else {}
	box.advanced.connect(_next)


func is_running() -> bool:
	return index >= 0


func start(conversation_id: String) -> void:
	var data = JSON.parse_string(FileAccess.get_file_as_string(DATA + conversation_id + ".json"))
	if not (data is Dictionary):
		push_error("No hay conversación «%s»" % conversation_id)
		return
	conversation = conversation_id
	_lines = data["lines"]
	index = -1
	_next()


func _next() -> void:
	index += 1
	if index >= _lines.size():
		index = -1
		box.close()
		finished.emit(conversation)
		return
	var line: Dictionary = _lines[index]
	var voice: Dictionary = _voices.get(line["who"], {})
	var side: int = DialogueBox.Side.RIGHT if voice.get("side", "left") == "right" else DialogueBox.Side.LEFT
	var tint: Color = DesignTokens.EMBER_400 if voice.get("name_color", "") == "ember" \
		else DesignTokens.TEXT_SECONDARY
	var face: Texture2D = load(PORTRAITS + "%s_%s.png" % [line["who"], line["mood"]])
	box.show_line(voice.get("name", line["who"]), line["text"], side, face, tint)
