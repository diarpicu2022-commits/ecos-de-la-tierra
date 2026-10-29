// La ola de purificación (enmienda 3 del contrato de exploración; contrato
// «Persiana» §5). Va en la capa del suelo purificado, encima del enfermo, y
// decide por píxel si se ve: cuando el frente (radius) toca un píxel, este
// pasa a purificado en el paso floor(umbral de Bayer / 2) de los ocho que
// dura la banda. Cada píxel es enfermo o purificado, nunca una mezcla: no se
// interpola color y no aparece ningún tono fuera de la paleta.
//
// Todos los valores llegan como uniformes desde DesignTokens.
shader_type canvas_item;

uniform vec2 origin;          // Punto del combate, en píxeles del mundo.
uniform float radius;         // Frente de la ola, en píxeles.
uniform float band;           // Ancho de la banda del tramado, en píxeles.
uniform float steps = 8.0;    // PURIFY_DITHER_STEPS.
uniform int bayer[16];        // BAYER_4X4, por filas.

varying vec2 world_px;

void vertex() {
	world_px = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	ivec2 p = ivec2(floor(world_px));
	int threshold = bayer[(p.y & 3) * 4 + (p.x & 3)];
	float step_index = floor(float(threshold) / 2.0);
	float behind = radius - distance(floor(world_px), origin);
	if (behind < step_index * band / steps) {
		discard;
	}
}
