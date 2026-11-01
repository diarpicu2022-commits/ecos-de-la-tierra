# DialogBox

Caja de diálogo y de mensajes, abajo en pantalla (12, 276), 616×76.

## Qué aporta quien la usa
- Las líneas de texto (dos por caja, 15 px de interlínea), quién habla y, si lo hay, su retrato de 40×44.

## Anatomía
- Marco `f-textbox`: papel `paper`, marco de madera de 2 px `paper-edge`, esquina `corner-3`, hojita `eco` en la esquina.
- Chapa con el nombre (`f-tag`, verde `eco`) asomando sobre el borde superior.
- Retrato en su propio marco `f-portrait`.
- Texto `text-on-paper` con sombra `text-shadow-paper`. `▼` en `rust-3` cuando hay más.

## Comportamiento
- El texto se escribe letra a letra (`dur-text-char`); Enter lo completa y, con la línea entera, avanza.
