# ActionHUD

Piezas del HUD del combate de acción. Todas en pizarra `slate` con contorno `ink-1` y esquina 2–3, menos el aviso, que va en papel.

## Piezas
- **Tarjeta del héroe** (168×40): retrato 32 px, nombre en `gold-5`, chapa de la causa que ataja, PV con cifra y energía `eco`.
- **Relevo**: retratos de 22 px de los otros cuatro, barra de PV debajo y un punto con el color de su causa. Teclas **Q** y **E** a los lados.
- **Bolsa** (quickbar): cuatro huecos de 26 px con icono de 12 px, cantidad y tecla **1–4**. El elegido lleva borde `gold-4`.
- **Mandos** en rombo, de color fijo: atacar `rust` (**Z**), esquivar `roofb` (**X**), eco `eco` con coste (**C**), objeto `gold` (**V**). Sin energía suficiente, el botón eco se apaga a `ui-2` pero sigue enseñando el coste.
- **Placa flotante** sobre el monstruo: nombre, chapa de tipo, SE REHACE (`rust`) o PURIFICADO (`eco`) y barra de PV.

## Reglas
- El HUD nunca tapa el centro de la pantalla: ocupa las esquinas y una franja baja.
- Las teclas siempre se ven al lado de lo que hacen.
