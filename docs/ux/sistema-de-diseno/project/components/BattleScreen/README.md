# BattleScreen

Combate de acción en el mismo mapa, a la manera de Minish Cap y Link's Awakening. No hay pantalla aparte ni turnos.

## Cómo se juega
- Te mueves y atacas en tiempo real con un héroe. **Q / E** cambian de héroe al instante; cada uno sabe atajar una causa (Bruma: FUEGO, Coral: PETRÓLEO, Nix: PLÁSTICO, Suri: MONOCULTIVO, Ilan: DESHIELO).
- Golpear a un monstruo con la causa activa lo deja en SE REHACE: la cifra sale con `~` y el aviso dice el hecho y la salida.
- La habilidad eco (**C**) del héroe adecuado lo purifica: cambia de forma, su placa pasa a PURIFICADO y el color sano vuelve al mapa en una ola circular tramada.
- La bolsa está siempre a la vista (**1–4**, **V** usa el elegido): no hay menú que pare la acción.

## Composición (640×360)
- `ActionHUD` en las cuatro esquinas: héroe y relevo arriba a la izquierda, cartel de lugar arriba a la derecha, bolsa abajo a la izquierda, mandos abajo a la derecha.
- Aviso de papel abajo en el centro; placa flotante sobre el monstruo.
- El centro queda libre para el campo de juego.
