class_name Combatant
extends Node

## Clase base de todo lo que participa en un combate: el protagonista, los
## compañeros y los monstruos. Concentra estadísticas, puntos de vida, energía
## y estados alterados, de modo que Character y Monster solo añadan lo suyo.

signal hp_changed(current: int, maximum: int)
signal energy_changed(current: int, maximum: int)
## Daño realmente aplicado, ya pasado por defensa y por resistencias. La
## interfaz lo usa para escribir la cifra sobre el objetivo; hasta ahora el
## único aviso era la frase del registro, de la que habría que extraer el
## número con análisis de texto, que es frágil.
signal damage_taken(amount: int, eco_type: Enums.EcoType, resisted: bool)
## Vida realmente recuperada, que puede ser menor que la curación pedida.
signal healing_received(amount: int)
signal status_applied(effect: StatusEffect)
signal status_removed(effect: StatusEffect)
signal defeated()

@export var display_name: String = "Sin nombre"
@export var max_hp: int = 100
@export var max_energy: int = 30
@export var base_attack: int = 12
@export var base_defense: int = 8
@export var base_speed: int = 10
@export var base_accuracy: float = 0.95

var hp: int = 0
var energy: int = 0
var team: Enums.Team = Enums.Team.PLAYER

var _status_effects: Array[StatusEffect] = []


func _ready() -> void:
	if hp <= 0:
		restore_all()


## Deja al combatiente a pleno rendimiento y sin estados alterados.
func restore_all() -> void:
	hp = max_hp
	energy = max_energy
	clear_statuses()
	hp_changed.emit(hp, max_hp)
	energy_changed.emit(energy, max_energy)


func is_alive() -> bool:
	return hp > 0


# --- Estadísticas efectivas -------------------------------------------------
# Las estadísticas base pasan por todos los estados alterados activos, así que
# la interfaz y el cálculo de daño siempre leen el valor real del turno.

func get_attack() -> int:
	var value: int = base_attack
	for effect in _status_effects:
		value = effect.modify_attack(value)
	return value


func get_defense() -> int:
	var value: int = base_defense
	for effect in _status_effects:
		value = effect.modify_defense(value)
	return value


func get_speed() -> int:
	var value: int = base_speed
	for effect in _status_effects:
		value = effect.modify_speed(value)
	return value


func get_accuracy() -> float:
	var value: float = base_accuracy
	for effect in _status_effects:
		value = effect.modify_accuracy(value)
	return clampf(value, 0.05, 1.0)


func get_hp_ratio() -> float:
	return float(hp) / float(max_hp) if max_hp > 0 else 0.0


# --- Vida y energía ---------------------------------------------------------

## Aplica daño. `eco_type` sirve para que las subclases reaccionen al tipo
## (resistencias del monstruo); `ignore_defense` lo usan los estados alterados,
## cuyo daño no se reduce por defensa.
func take_damage(amount: int, eco_type: Enums.EcoType = Enums.EcoType.NONE, ignore_defense: bool = false) -> int:
	# La defensa resta la mitad de su valor: a plena potencia dejaría a los
	# monstruos más blindados recibiendo siempre el mínimo de 1 punto.
	var final_damage: int = amount if ignore_defense else maxi(1, amount - int(float(get_defense()) * 0.5))
	final_damage = mini(final_damage, hp)
	hp -= final_damage
	hp_changed.emit(hp, max_hp)
	# Se avisa antes de comprobar si cayó: la cifra pertenece al golpe, y el
	# monstruo puede regenerarse justo después.
	damage_taken.emit(final_damage, eco_type, get_resistance_for(eco_type) > 0.0)
	if hp <= 0:
		_on_hp_depleted()
	return final_damage


## Gancho para las subclases: el monstruo lo usa para regenerarse si aún no ha
## sido purificado. Por defecto, quedarse sin PV significa caer.
func _on_hp_depleted() -> void:
	defeated.emit()


func heal(amount: int) -> int:
	var healed: int = mini(amount, max_hp - hp)
	hp += healed
	hp_changed.emit(hp, max_hp)
	if healed > 0:
		healing_received.emit(healed)
	return healed


## Fracción del daño de un tipo que este combatiente resiste, de 0 a 1.
##
## La base no resiste nada. `Monster` lo sobrescribe con el sistema de debilidad
## ambiental, y es lo que permite a la interfaz distinguir un golpe que hizo
## mella de uno que el monstruo se quitó de encima.
func get_resistance_for(_eco_type: Enums.EcoType) -> float:
	return 0.0


func has_energy(cost: int) -> bool:
	return energy >= cost


func spend_energy(cost: int) -> bool:
	if not has_energy(cost):
		return false
	energy -= cost
	energy_changed.emit(energy, max_energy)
	return true


func restore_energy(amount: int) -> void:
	energy = mini(max_energy, energy + amount)
	energy_changed.emit(energy, max_energy)


# --- Estados alterados ------------------------------------------------------

func apply_status(effect: StatusEffect) -> String:
	# Reaplicar un estado que ya está activo refresca su duración en lugar de
	# acumular dos copias del mismo modificador.
	var existing: StatusEffect = get_status(effect.status_type)
	if existing != null:
		existing.duration = maxi(existing.duration, effect.duration)
		return "%s sigue sufriendo %s." % [display_name, existing.display_name]
	_status_effects.append(effect)
	var message: String = effect.on_applied(self)
	status_applied.emit(effect)
	return message


func get_status(status_type: Enums.StatusType) -> StatusEffect:
	for effect in _status_effects:
		if effect.status_type == status_type:
			return effect
	return null


func has_status(status_type: Enums.StatusType) -> bool:
	return get_status(status_type) != null


func get_statuses() -> Array[StatusEffect]:
	return _status_effects.duplicate()


func remove_status(status_type: Enums.StatusType) -> String:
	var effect: StatusEffect = get_status(status_type)
	if effect == null:
		return ""
	_status_effects.erase(effect)
	var message: String = effect.on_removed()
	status_removed.emit(effect)
	return message


func clear_statuses() -> void:
	for effect in _status_effects.duplicate():
		remove_status(effect.status_type)


## ¿Puede actuar este turno? Falso si algún estado se lo impide (aturdimiento).
func can_act() -> bool:
	if not is_alive():
		return false
	for effect in _status_effects:
		if effect.blocks_action():
			return false
	return true


## Procesa los estados al inicio del turno. Devuelve las líneas para el registro.
func tick_statuses_on_turn_start() -> Array[String]:
	var messages: Array[String] = []
	for effect in _status_effects.duplicate():
		var message: String = effect.on_turn_start()
		if message != "":
			messages.append(message)
	return messages


## Procesa los estados al final del turno y retira los que ya expiraron.
func tick_statuses_on_turn_end() -> Array[String]:
	var messages: Array[String] = []
	for effect in _status_effects.duplicate():
		effect.on_turn_end()
		if effect.is_expired():
			var message: String = remove_status(effect.status_type)
			if message != "":
				messages.append(message)
	return messages
