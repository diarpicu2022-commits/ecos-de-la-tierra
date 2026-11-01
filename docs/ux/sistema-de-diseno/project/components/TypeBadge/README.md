# TypeBadge

Chapa de 11 px de alto con el tipo de daño o el estado del monstruo.

## Qué aporta quien la usa
- El texto en MAYÚSCULAS y su clase: `b-fuego`, `b-petroleo`, `b-plastico`, `b-monocultivo`, `b-deshielo`, `b-avaricia`, `b-eco`, `b-corrupto`, `b-purificado`.

## Reglas
- Esquina `corner-1` y contorno `ink-1`. Relleno de 3 px a cada lado.
- Texto blanco sobre el color del tipo (todos ≥ 5,4:1). CORRUPTO: `paper-5` sobre `status-corrupt`; PURIFICADO: `eco-5` sobre `status-purified`.
- Va en la placa del enemigo y en los menús de habilidades; nunca sola en el mapa.
