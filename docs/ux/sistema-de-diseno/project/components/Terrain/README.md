# Terrain

Cómo se construye el terreno. Todo en código con la paleta del sistema.

## Método
- Casillas de 16 px → máscara de píxeles por material → esquinas redondeadas por morfología (apertura y cierre con disco) y alisado (desenfoque + umbral). Bordes limpios, curvas amplias, sin escalones.
- **Hierba**: textura de 32×32 con matas en V; luego matas sueltas en rejilla con desfase.
- **Camino**: `dirt-5` con guijarros, borde `dirt-3`, sombra en el borde norte y briznas encima.
- **Agua**: profundidad por distancia a la orilla (`water-5` bajío, `water-4` medio, `water-3` fondo), borde `water-2`, talud de tierra en la orilla norte, destellos `water-6`.
- **Acantilado**: bloques de roca de Voronoi en `stone`, luz arriba a la izquierda, sombra bajo el labio, flecos de hierba, pie `stone-1`, sombra proyectada; escalera de piedra.
- **Empedrado**: losas de Voronoi en `wall` con junta oscura.
- Enfermo: `drygrass` apagada, camino de polvo, agua turbia, empedrado y madera ceniza.
