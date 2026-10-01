extends Node

## Estado global de la partida. Autoload `GameState` (contrato «Umbral»,
## cláusula «Estado global»): una sola fuente de verdad que leen el mundo, el
## combate (parte 4), el menú (parte 8), el guardado (parte 9) y el título
## (parte 10).
##
## En la parte 2 solo el mundo escribe aquí: la zona en la que se está y
## hacia dónde se mira. El grupo, la bolsa y las banderas existen ya para que
## las partes siguientes no tengan que inventar dónde guardarlos.

signal zone_changed(zone_id: String)

## Zona actual, por id de `data/world/zones/`.
var zone_id := ""

## Hacia dónde mira el personaje: se conserva al cruzar una salida.
var facing := Vector2i.DOWN

## Miembros del grupo (`Character`). Los llena la parte 4.
var party: Array = []

## Bolsa compartida del grupo.
var bag := Inventory.new()

## Banderas de la partida: región purificada, compañero unido, puzzle resuelto…
## Clave en inglés y `snake_case`, valor libre.
var flags: Dictionary = {}


## Bandera de zona purificada: `purified_<id de zona>`. La escribe la ola de
## purificación (parte 4); el mundo la lee al pintar la zona.
const PURIFIED_PREFIX := "purified_"


func is_zone_purified(id: String) -> bool:
	return bool(flag(PURIFIED_PREFIX + id))


func set_zone_purified(id: String, value := true) -> void:
	set_flag(PURIFIED_PREFIX + id, value)


func set_zone(id: String) -> void:
	zone_id = id
	zone_changed.emit(id)


func set_flag(key: String, value: Variant = true) -> void:
	flags[key] = value


func flag(key: String, default: Variant = false) -> Variant:
	return flags.get(key, default)
