class_name SummonSkill
extends Skill

## Habilidad que invoca una copia del usuario en vez de hacer daño.
## La usa la Multiplicación del Espectro del Monocultivo: el monocultivo se
## extiende repitiendo siempre lo mismo, y en combate eso se traduce en clones.
##
## No conoce la clase Monster: pregunta por los métodos (duck typing) para no
## crear una dependencia cíclica entre habilidades y monstruos.

func can_use(user: Combatant) -> bool:
	if not super.can_use(user):
		return false
	var summoner = user   # sin tipo: la llamada se resuelve en ejecución
	return summoner.has_method("can_summon") and summoner.can_summon()


func execute(user: Combatant, target: Combatant) -> Array[String]:
	var summoner = user
	if not summoner.has_method("summon_clone"):
		return []
	return summoner.summon_clone()
