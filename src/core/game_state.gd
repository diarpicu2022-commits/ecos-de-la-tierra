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

## IA-5: la mente de cada compañero (`PartyMind`, por nombre) y la sintonía
## del grupo. Viven aquí entre combates; el guardado (parte 9) las persiste.
var party_minds: Dictionary = {}
var party_sync: float = DesignTokens.SYNC_START


## Bandera de zona purificada: `purified_<id de zona>`. La escribe la ola de
## purificación (parte 4); el mundo la lee al pintar la zona.
const PURIFIED_PREFIX := "purified_"


func is_zone_purified(id: String) -> bool:
	return bool(flag(PURIFIED_PREFIX + id))


func set_zone_purified(id: String, value := true) -> void:
	set_flag(PURIFIED_PREFIX + id, value)


## Pone el grupo como llega al combate `encounter_index` (`Encounters`). Los
## que ya viajaban conservan sus PV, su energía y sus estados: el combate
## continúa el viaje (contrato «Persiana» §5). La bolsa se llena la primera
## vez. Los personajes cuelgan de este nodo para vivir entre combates. La
## progresión de verdad (quién se une dónde) es de la parte 6.
func ensure_party(encounter_index: int) -> void:
	var wanted: Array[Character] = Encounters.build_party(encounter_index)
	if party.size() == wanted.size():
		for c in wanted:
			c.free()
		return
	var old := {}
	for c in party:
		old[c.display_name] = c
	party.clear()
	for c in wanted:
		add_child(c)
		if old.has(c.display_name):
			c.free()
			party.append(old[c.display_name])
			old.erase(party[-1].display_name)
		else:
			party.append(c)
	for c in old.values():
		c.queue_free()
	if bag.get_all().is_empty():
		bag = Encounters.build_inventory(encounter_index)


func set_zone(id: String) -> void:
	zone_id = id
	zone_changed.emit(id)


func set_flag(key: String, value: Variant = true) -> void:
	flags[key] = value


func flag(key: String, default: Variant = false) -> Variant:
	return flags.get(key, default)
