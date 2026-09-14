extends SceneTree

## Comprobación de que Godot carga la fuente de mapa de bits y mide bien el
## texto en español. Se ejecuta con:
##   godot --headless --path . --script res://tools/verify_font.gd

func _initialize() -> void:
	var font: Font = load(DesignTokens.FONT_PATH)
	if font == null:
		printerr("FALLO: no se pudo cargar ", DesignTokens.FONT_PATH)
		quit(1)
		return

	print("Fuente cargada: ", font.get_font_name())
	print("Altura de linea: ", font.get_height(DesignTokens.FONT_SIZE_BODY))

	var muestras := [
		"ATACAR",
		"Llama de la Deforestacion",
		"\u00bfQu\u00e9 Habilidad Ecol\u00f3gica uso? \u00a1L\u00ednea!",
		"PV 110/110",
	]
	for texto in muestras:
		var ancho: float = font.get_string_size(
			texto, HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY
		).x
		print("  %5.1f px  <- %s" % [ancho, texto])

	# Cada glifo del español debe existir en el atlas, no caer en el sustituto.
	var faltan: Array[String] = []
	for ch in "\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00bf\u00a1\u00ab\u00bb\u25b6\u2716\u2713":
		if font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY).x <= 0.0:
			faltan.append(ch)
	if faltan.is_empty():
		print("Cobertura de espanol y simbolos de interfaz: completa.")
	else:
		printerr("FALTAN glifos: ", faltan)
		quit(1)
		return
	quit(0)
