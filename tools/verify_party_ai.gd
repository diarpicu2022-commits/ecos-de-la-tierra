extends Node

## Prueba de IA-5, el componente clave (contrato «Orden de líder», paso 2).
## Sin ventana y con semilla fija:
##
##   godot --headless --path . res://tools/verify_party_ai.tscn
##
## - La red aprende un estilo sintético: > 80 % de acierto sobre situaciones
##   nuevas tras PARTY_LEARN_DECISIONS decisiones.
## - Cada orden sesga lo que debe.
## - Con un líder bueno la sintonía sube; con uno malo baja; desde 0,
##   SYNC_RECOVER decisiones buenas la devuelven al tramo medio.
## - Con la sintonía alta el compañero duda menos que con la baja.
## Sale con código 1 si algo falla.

const C := PartyMind.Choice

var _pass := 0
var _fail := 0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = 20261028
	_learning()
	_orders()
	_sync()
	_doubt()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


## Una situación al azar con las 12 entradas.
func _situation() -> PackedFloat32Array:
	var x := PackedFloat32Array()
	for i in DesignTokens.PARTY_INPUTS:
		x.append(_rng.randf())
	for i in [5, 6, 7, 8]:
		x[i] = float(_rng.randf() < 0.5)
	return x


## El estilo sintético de un líder: ataja la causa si puede; si no, cura a
## quien baja del 45 %; si no, ataca.
func _style(x: PackedFloat32Array) -> int:
	if x[5] > 0.5 and x[6] > 0.5:
		return C.COUNTER
	if x[3] < PartyMind.HURT and x[7] > 0.5:
		return C.HEAL
	return C.ATTACK


func _learning() -> void:
	print("La red aprende del líder")
	var mind := PartyMind.new(7)
	var before := _accuracy(mind)
	for n in DesignTokens.PARTY_LEARN_DECISIONS:
		var x := _situation()
		mind.train(x, _style(x))
	var after := _accuracy(mind)
	_check("acierto sobre 500 situaciones nuevas: %d %% antes, %d %% tras %d decisiones (> 80 %%)" % [
		roundi(before * 100), roundi(after * 100), DesignTokens.PARTY_LEARN_DECISIONS], after > 0.8)


func _accuracy(mind: PartyMind) -> float:
	var ok := 0
	var all := [true, true, true, true]
	for n in 500:
		var x := _situation()
		ok += int(mind.preferred(x, PartyMind.Order.FOLLOW, all) == _style(x))
	return ok / 500.0


func _orders() -> void:
	print("\nLa orden sesga")
	var mind := PartyMind.new(3)
	var all := [true, true, true, true]
	var cause := 0
	var cover := 0
	for n in 300:
		var x := _situation()
		cause += int(mind.preferred(x, PartyMind.Order.CAUSE, all) == C.COUNTER)
		var c := mind.preferred(x, PartyMind.Order.COVER, all)
		cover += int(c == C.HEAL or c == C.ITEM)
	_check("«Atajad la causa» lleva a la contramedida (%d de 300)" % cause, cause > 270)
	_check("«Cubríos» lleva a curar u objeto (%d de 300)" % cover, cover > 270)
	var no_counter := [true, false, true, true]
	var x := _situation()
	_check("nunca elige lo que no puede hacer",
		mind.preferred(x, PartyMind.Order.CAUSE, no_counter) != C.COUNTER)


func _sync() -> void:
	print("\nSintonía")
	var s := DesignTokens.SYNC_START
	for n in 6:
		s = PartyMind.update_sync(s, PartyMind.judge(C.COUNTER, true, true, 1.0, false))
	_check("un líder bueno la sube: %.2f → %.2f" % [DesignTokens.SYNC_START, s], s > DesignTokens.SYNC_START)
	s = DesignTokens.SYNC_START
	for n in 6:
		s = PartyMind.update_sync(s, PartyMind.judge(C.ATTACK, true, true, 1.0, false))
	_check("uno malo la baja: %.2f → %.2f" % [DesignTokens.SYNC_START, s], s < DesignTokens.SYNC_START)
	s = 0.0
	for n in DesignTokens.SYNC_RECOVER:
		s = PartyMind.update_sync(s, 1)
	_check("desde 0, %d decisiones buenas la devuelven al tramo medio (%.2f ≥ 0,5)" % [
		DesignTokens.SYNC_RECOVER, s], s >= 0.5)
	_check("repetir un tipo contra la Sombra es malo",
		PartyMind.judge(C.COUNTER, true, true, 1.0, true) == -1)
	_check("curar sin que haga falta es malo; curar a quien baja del 45 % es bueno",
		PartyMind.judge(C.HEAL, true, true, 0.9, false) == -1 and PartyMind.judge(C.HEAL, true, true, 0.3, false) == 1)


func _doubt() -> void:
	print("\nPrecisión según la sintonía")
	var mind := PartyMind.new(5)
	var all := [true, true, true, true]
	var doubts := {}
	for sync in [0.0, 1.0]:
		var d := 0
		for n in 1000:
			d += int(mind.choose(_situation(), PartyMind.Order.FOLLOW, sync, all, _rng)["doubted"])
		doubts[sync] = d
	_check("duda %d de 1000 con sintonía 0 y %d con sintonía 1" % [doubts[0.0], doubts[1.0]],
		doubts[0.0] > 400 and doubts[1.0] == 0)
