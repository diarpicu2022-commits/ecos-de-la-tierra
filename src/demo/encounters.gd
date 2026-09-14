class_name Encounters
extends RefCounted

## Catálogo de los seis combates de *Ecos de la Tierra*.
##
## Sale de la tabla de monstruos de la propuesta: una región, un daño ambiental,
## un monstruo y la contramedida que lo ataja. El grupo crece región a región
## según se van uniendo los compañeros, y cada uno trae la Habilidad Ecológica
## de su tierra: Bruma el fuego, Coral el petróleo, Nix el plástico, Suri el
## monocultivo e Ilan el deshielo.
##
## Por eso el jefe final exige exactamente a los cinco: cada contramedida vive
## en una persona distinta, y esa es la idea del juego traducida a reparto.

## Clave del monstruo -> constructor. La clave coincide con el nombre del script
## y con el del sprite, así que añadir un monstruo no obliga a tocar nada más.
const MONSTERS := {
	"deforestation_flame": "res://src/actors/monsters/deforestation_flame.gd",
	"oil_devourer": "res://src/actors/monsters/oil_devourer.gd",
	"plastic_golem": "res://src/actors/monsters/plastic_golem.gd",
	"monoculture_specter": "res://src/actors/monsters/monoculture_specter.gd",
	"thaw_colossus": "res://src/actors/monsters/thaw_colossus.gd",
	"adaptive_boss": "res://src/actors/monsters/adaptive_boss.gd",
}


## Los seis, en el orden de la historia.
static func all() -> Array[Dictionary]:
	return [
		{
			"region": "Bosque de las Cenizas",
			"place": "Robledal Quemado",
			"monster": "deforestation_flame",
			"eco": Enums.EcoType.FIRE,
			"party": ["ilan", "bruma"],
			"hint": "Bruma conoce la Linea Cortafuegos.",
		},
		{
			"region": "Cuenca de Alquitran",
			"place": "Puerto Brea",
			"monster": "oil_devourer",
			"eco": Enums.EcoType.OIL,
			"party": ["ilan", "bruma", "coral"],
			"hint": "Coral trae la Barrera Absorbente.",
		},
		{
			"region": "Costa Quebrada",
			"place": "Bahia Clara",
			"monster": "plastic_golem",
			"eco": Enums.EcoType.PLASTIC,
			"party": ["ilan", "bruma", "coral", "nix"],
			"hint": "Nix aporta la Separacion en la Fuente.",
		},
		{
			"region": "Llanura Marchita",
			"place": "Aldea Grano de Sal",
			"monster": "monoculture_specter",
			"eco": Enums.EcoType.MONOCULTURE,
			"party": ["ilan", "bruma", "coral", "nix", "suri"],
			"hint": "Se multiplica: hay que purificar cada clon.",
		},
		{
			"region": "Cumbre Menguante",
			"place": "Refugio de Altahielo",
			"monster": "thaw_colossus",
			"eco": Enums.EcoType.THAW,
			"party": ["ilan", "bruma", "coral", "nix", "suri"],
			"hint": "Ilan lleva el Escudo de Albedo desde el principio.",
		},
		{
			"region": "Cripta de la Avaricia",
			"place": "Ciudad Dorada",
			"monster": "adaptive_boss",
			"eco": Enums.EcoType.NONE,
			"party": ["ilan", "bruma", "coral", "nix", "suri"],
			"hint": "Aprende de lo que repites. Hay que combinar las cinco.",
		},
	]


static func count() -> int:
	return all().size()


static func get_encounter(index: int) -> Dictionary:
	var list: Array[Dictionary] = all()
	return list[clampi(index, 0, list.size() - 1)]


## Construye el monstruo de un combate.
static func build_monster(index: int) -> Monster:
	var key: String = str(get_encounter(index)["monster"])
	var script: GDScript = load(MONSTERS[key])
	return script.new() as Monster


## Construye el grupo tal y como llega a esa región.
##
## El Conocimiento Ambiental se concede **acumulado hasta la región actual**:
## es lo que el grupo ha aprendido por el camino. Sin esto, las Habilidades
## Ecológicas no aparecerían en el menú, porque `Character` las condiciona al
## conocimiento, no solo a tenerlas escritas en la ficha.
static func build_party(index: int) -> Array[Character]:
	var encounter: Dictionary = get_encounter(index)
	var learned: Array[int] = []
	for i in range(index + 1):
		var eco: int = int(get_encounter(i)["eco"])
		if eco != Enums.EcoType.NONE and not learned.has(eco):
			learned.append(eco)
	# En la Cripta ya se domina todo: es el requisito del jefe final.
	if str(encounter["monster"]) == "adaptive_boss":
		learned = [Enums.EcoType.FIRE, Enums.EcoType.OIL, Enums.EcoType.PLASTIC,
				Enums.EcoType.MONOCULTURE, Enums.EcoType.THAW]

	var party: Array[Character] = []
	for key in encounter["party"]:
		var character: Character = _build_character(str(key))
		for eco in learned:
			character.gain_knowledge(eco)
		party.append(character)
	return party


## Bolsa del grupo. Crece con el viaje, como el propio grupo.
static func build_inventory(index: int) -> Inventory:
	var inventory := Inventory.new()
	inventory.add(ItemLibrary.healing_herb(), 3 + index)
	inventory.add(ItemLibrary.purified_water(), 2 + int(index / 2))
	return inventory


static func _build_character(key: String) -> Character:
	match key:
		"ilan": return PartyLibrary.ilan()
		"bruma": return PartyLibrary.bruma()
		"coral": return PartyLibrary.coral()
		"nix": return PartyLibrary.nix()
		"suri": return PartyLibrary.suri()
		_: return PartyLibrary.ilan()
