// Suelo purificado por partes (contrato «Piel nueva», paso 5): en Valdehoja
// cada parte del pueblo sigue a su región, así que la capa del suelo sano no
// se enseña entera. La máscara tiene un píxel por casilla (blanco, purificada)
// y la capa solo se ve donde la casilla lo está. Cada píxel es enfermo o
// purificado, nunca una mezcla: no se interpola nada.
shader_type canvas_item;

uniform sampler2D cell_mask : filter_nearest;

void fragment() {
	if (texture(cell_mask, UV).r < 0.5) {
		discard;
	}
}
