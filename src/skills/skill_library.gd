class_name SkillLibrary
extends RefCounted

## Catálogo central de habilidades. Cada función devuelve una instancia nueva y
## ya configurada, de modo que monstruos y personajes no repitan la
## configuración y el balanceo se toque en un único archivo.
##
## Más adelante estas habilidades pueden guardarse como archivos .tres desde el
## editor de Godot; este catálogo sirve mientras el contenido se define en código.


# --- Habilidades de los monstruos -------------------------------------------

## Llama de la Deforestación: daño progresivo por quemadura.
static func heat_wave() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Onda de Calor"
	skill.description = "El aire arde y la quemadura sigue consumiendo turno a turno."
	skill.power = 14
	skill.eco_type = Enums.EcoType.FIRE
	skill.inflicted_statuses = [BurnEffect.new(3, 7.0)]
	skill.status_chance = 0.7
	return skill


## Llama de la Deforestación: reduce precisión y puede aturdir.
static func smoke_suffocation() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Sofocación por Humo"
	skill.description = "Una humareda densa que ciega y deja sin aire."
	skill.power = 8
	skill.eco_type = Enums.EcoType.FIRE
	skill.inflicted_statuses = [BlindEffect.new(3, 0.35), StunEffect.new(1)]
	skill.status_chance = 0.5
	return skill


## Devorador de Petróleo: envenena.
static func black_tide() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Marea Negra"
	skill.description = "El crudo cubre todo lo que toca y envenena lentamente."
	skill.power = 12
	skill.eco_type = Enums.EcoType.OIL
	skill.inflicted_statuses = [PoisonEffect.new(4, 6.0)]
	skill.status_chance = 0.75
	return skill


## Devorador de Petróleo: reduce la velocidad.
static func viscous_trap() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Trampa Viscosa"
	skill.description = "Una capa pegajosa que impide moverse con soltura."
	skill.power = 7
	skill.eco_type = Enums.EcoType.OIL
	skill.inflicted_statuses = [SlowEffect.new(3, 0.35)]
	skill.status_chance = 0.8
	return skill


## Gólem de Plástico: ciega con microplásticos.
static func microparticles() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Micropartículas"
	skill.description = "Una nube de microplásticos que se mete en los ojos."
	skill.power = 10
	skill.eco_type = Enums.EcoType.PLASTIC
	skill.inflicted_statuses = [BlindEffect.new(4, 0.4)]
	skill.status_chance = 0.85
	return skill


## Gólem de Plástico: golpe pesado sin estado alterado.
static func debris_slam() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Golpe de Chatarra"
	skill.description = "Descarga toda su masa de residuos compactados."
	skill.power = 20
	skill.eco_type = Enums.EcoType.PLASTIC
	return skill


## Espectro del Monocultivo: genera un clon de sí mismo.
static func multiplication() -> SummonSkill:
	var skill := SummonSkill.new()
	skill.display_name = "Multiplicación"
	skill.description = "Repite el mismo cultivo una y otra vez hasta agotar la tierra."
	skill.power = 0
	return skill


## Espectro del Monocultivo: reduce la defensa de todo el grupo.
static func withering() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Marchitez"
	skill.description = "La tierra se agota y las defensas del grupo se resienten."
	skill.power = 9
	skill.eco_type = Enums.EcoType.MONOCULTURE
	skill.targets_all = true
	skill.inflicted_statuses = [WitherEffect.new(3, 0.4)]
	skill.status_chance = 0.9
	return skill


## Coloso del Deshielo: daño en área.
static func avalanche() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Avalancha"
	skill.description = "Toneladas de hielo desprendido caen sobre el grupo."
	skill.power = 16
	skill.eco_type = Enums.EcoType.THAW
	skill.targets_all = true
	return skill


## Coloso del Deshielo: ralentiza a todo el grupo.
static func searing_cold() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Frío Calcinante"
	skill.description = "Un frío que quema y entumece los movimientos."
	skill.power = 8
	skill.eco_type = Enums.EcoType.THAW
	skill.targets_all = true
	skill.inflicted_statuses = [SlowEffect.new(3, 0.4)]
	skill.status_chance = 0.85
	return skill


## Sombra de la Avaricia: golpe genérico del jefe final.
static func greed_grasp() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Zarpa de la Avaricia"
	skill.description = "Arrebata sin medida lo que encuentra a su paso."
	skill.power = 18
	skill.eco_type = Enums.EcoType.NONE
	skill.inflicted_statuses = [WitherEffect.new(2, 0.3)]
	skill.status_chance = 0.4
	return skill


# --- Habilidades Ecológicas del grupo ---------------------------------------
# Una por tipo de daño ambiental: son las únicas que purifican a un monstruo.

## Bruma — contramedida de los incendios forestales.
static func firebreak_line() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Línea Cortafuegos"
	skill.description = "Abre una franja sin combustible y aísla el oxígeno del incendio."
	skill.energy_cost = 6
	skill.power = 18
	skill.weakness_type = Enums.EcoType.FIRE
	return skill


## Coral — contramedida de los derrames de crudo.
static func absorbent_barrier() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Barrera Absorbente"
	skill.description = "Contiene el vertido y lo filtra con material biológico."
	skill.energy_cost = 6
	skill.power = 18
	skill.weakness_type = Enums.EcoType.OIL
	return skill


## Nix — contramedida de los residuos sólidos.
static func source_separation() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Separación en la Fuente"
	skill.description = "Clasifica el residuo antes de que se mezcle y se vuelva irrecuperable."
	skill.energy_cost = 6
	skill.power = 18
	skill.weakness_type = Enums.EcoType.PLASTIC
	return skill


## Suri — contramedida del monocultivo intensivo.
static func crop_rotation() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Rotación de Cultivos"
	skill.description = "Alterna las especies y devuelve nutrientes al suelo con compostaje vivo."
	skill.energy_cost = 6
	skill.power = 18
	skill.weakness_type = Enums.EcoType.MONOCULTURE
	return skill


## Ilan — contramedida del deshielo glaciar.
static func albedo_shield() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Escudo de Albedo"
	skill.description = "Devuelve la radiación al cielo y frena el deshielo con reforestación de altura."
	skill.energy_cost = 7
	skill.power = 18
	skill.weakness_type = Enums.EcoType.THAW
	return skill


# --- Habilidades Ecológicas de apoyo ----------------------------------------

## Coral — purifica el agua, cura y corta el veneno.
static func biological_filter() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Filtro Biológico"
	skill.description = "Agua limpia para el grupo; también corta el veneno."
	skill.energy_cost = 5
	skill.power = 6
	skill.weakness_type = Enums.EcoType.OIL
	skill.ally_healing = 35
	skill.cures_status = true
	skill.cured_status_type = Enums.StatusType.POISON
	return skill


## Bruma — reforesta y recupera al grupo.
static func reforestation() -> EcoSkill:
	var skill := EcoSkill.new()
	skill.display_name = "Reforestación"
	skill.description = "Planta especies nativas: sombra, raíces y aire limpio."
	skill.energy_cost = 5
	skill.power = 6
	skill.weakness_type = Enums.EcoType.FIRE
	skill.ally_healing = 30
	return skill


# --- Acción básica ----------------------------------------------------------

## Ataque estándar del menú de batalla. Su potencia sale del ataque de quien lo
## usa; existe como habilidad para que todas las acciones se resuelvan por la
## misma vía dentro del BattleManager.
static func basic_attack() -> AttackSkill:
	var skill := AttackSkill.new()
	skill.display_name = "Atacar"
	skill.description = "Golpe directo. Nunca purifica a un monstruo."
	skill.power = 4
	skill.eco_type = Enums.EcoType.NONE
	return skill
