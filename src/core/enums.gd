class_name Enums
extends RefCounted

## Enumeraciones compartidas por todo el juego.
## Se registra como clase global (class_name), así que se accede como
## Enums.EcoType.FIRE desde cualquier script sin necesidad de autoload.


## Tipo de daño ambiental. Es la pieza central del sistema de debilidades:
## cada monstruo solo se purifica con la Habilidad Ecológica de su mismo tipo.
enum EcoType {
	NONE,          ## Ataques físicos y objetos: no purifican a nadie.
	FIRE,          ## Incendios y tala — Llama de la Deforestación.
	OIL,           ## Derrames de crudo — Devorador de Petróleo.
	PLASTIC,       ## Residuos sólidos y microplásticos — Gólem de Plástico.
	MONOCULTURE,   ## Agroquímicos y monocultivo — Espectro del Monocultivo.
	THAW,          ## Deshielo glaciar — Coloso del Deshielo.
}

## Opciones del menú de batalla.
enum ActionType {
	ATTACK,   ## Atacar
	SKILL,    ## Habilidades Ecológicas
	ITEM,     ## Bolsa
	FLEE,     ## Huir
}

## Estados alterados que pueden aplicarse a cualquier combatiente.
enum StatusType {
	POISON,   ## Veneno: daño por turno.
	BURN,     ## Quemadura: daño por turno de tipo fuego.
	STUN,     ## Aturdimiento: pierde el turno.
	BLIND,    ## Ceguera: reduce la precisión.
	WITHER,   ## Marchitez: reduce la defensa.
	SLOW,     ## Lentitud: reduce la velocidad y altera el orden de turnos.
}

## Bando al que pertenece un combatiente.
enum Team {
	PLAYER,
	ENEMY,
}

## Estado del combate consultado por el BattleManager.
enum BattleResult {
	ONGOING,
	VICTORY,
	DEFEAT,
	FLED,
}


## Nombre legible de un tipo ecológico, para la interfaz y el registro de batalla.
static func eco_type_name(eco_type: EcoType) -> String:
	match eco_type:
		EcoType.FIRE: return "Fuego"
		EcoType.OIL: return "Petróleo"
		EcoType.PLASTIC: return "Plástico"
		EcoType.MONOCULTURE: return "Monocultivo"
		EcoType.THAW: return "Deshielo"
		_: return "Neutro"


## Nombre legible de un estado alterado.
static func status_type_name(status_type: StatusType) -> String:
	match status_type:
		StatusType.POISON: return "Veneno"
		StatusType.BURN: return "Quemadura"
		StatusType.STUN: return "Aturdimiento"
		StatusType.BLIND: return "Ceguera"
		StatusType.WITHER: return "Marchitez"
		StatusType.SLOW: return "Lentitud"
		_: return "Desconocido"
