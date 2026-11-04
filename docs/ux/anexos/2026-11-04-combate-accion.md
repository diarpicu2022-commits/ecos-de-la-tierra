# Anexo: combate de acción en el mapa (R2)

Abierto el 2026-11-04 en la rama `noche/demo-accion`, con el plan de `CONTINUAR.md` §3, bloque C.

La dirección no se discute aquí. Diego eligió el combate de acción en el mismo mapa el 2026-10-30 (anexo de Tierra Viva, «combate de acción sustituye a Persiana») y lo repitió el 2026-11-04: «las peleas iban a hacer en mundo abierto, que yo controlaba al jugador, no por turno». Este anexo deja escritos sus usuarios, su comunicación, sus fuentes y el contrato que se cumple al programarlo.

## Fase 1. Usuarios

- **Quién juega la demo:** compañeros de curso y la profesora, de 18 a 30 años, la mayoría con experiencia en juegos de acción. Juegan con teclado, una sola vez y sin tutorial.
- **Qué necesitan:** entender en el primer golpe que pegar más fuerte no sirve y que la causa del daño se ataja con la habilidad correcta. Es la idea del juego entero.
- **Riesgo:** quien no juega mucho se pierde si hay muchas teclas. Por eso cada tecla se ve al lado de lo que hace, como pide `ActionHUD`.

## Fase 2. Comunicación

| Qué tiene que entender | Cómo se dice en pantalla | Con qué más se dice, para no depender del color |
|---|---|---|
| Golpe común, que no ataja la causa | Cifra con `~` y el aviso «La llama se rehace. Su causa es FUEGO» | El monstruo vuelve a llenar su vida |
| Quién ataja la causa | El aviso nombra a Bruma y su tecla | La chapa de tipo de la tarjeta del héroe coincide con la del monstruo |
| El monstruo va a atacar | Zona marcada en el suelo antes del golpe | Postura de alerta del monstruo y tiempo de aviso fijo |
| La ventana de aturdimiento | Chapa ATURDIDO en la placa y el monstruo quieto | Cuenta atrás en la barra de la placa |
| Purificado | Chapa PURIFICADO, cambio de forma y ola | El mundo vuelve a tener color |

## Fase 3. Investigación

Las fuentes 4 a 7 del anexo de Tierra Viva (`2026-10-30-tierra-viva.md`, fase 3) ya argumentan este combate. Se resumen aquí con lo que decide cada una.

1. **CrossCode (Wikipedia)**, https://en.wikipedia.org/wiki/CrossCode. Se pelea en el mismo mundo, sin pantalla aparte, con cambio instantáneo de elemento. Decide que Q y E cambian de héroe sin pausa ni menú.
2. **GamingBolt sobre CrossCode**, https://gamingbolt.com/crosscode-deciphering-the-pillars-of-an-action-rpg-classic/amp. Los enemigos tienen fases de aturdimiento y los compañeros adoptan posturas. Decide que la contramedida de dos rondas pasa a ser una ventana de aturdimiento, y que la orden de líder pasa a ser postura del grupo.
3. **Game-Wisdom sobre Moonlighter**, https://game-wisdom.com/analysis/moonlighter. Critica que un arma con un solo ataque especial vuelve repetitivo el combate. Decide que cada héroe se distingue por lo que hace.
4. **Zelda Wiki, «Items Screen»**, https://zelda.fandom.com/wiki/Items_Screen. Link lleva pocos objetos equipados y el resto va en una subpantalla. Decide que la bolsa del HUD tiene cuatro casillas fijas.
5. **Las maquetas del sistema**, `docs/ux/tierra-viva/referencias/combate_accion.png` y `combate_purifica.png`. Fijan la disposición del HUD, la placa flotante, el aviso de papel y el tajo.
6. **`components/ActionHUD/README.md`**. Fija medidas, teclas y colores de cada pieza.

No se repitió la búsqueda en la lista de fuentes de pantalla de Diego, porque los anexos anteriores ya registraron que no aplican a un mapa de juego en pixel art.

## Fase 4. Dirección

Una sola, la que eligió Diego: combate de acción en el mapa, como en las maquetas. No se proponen otras.

## Contrato «Tajo» (bloqueado el 2026-11-04 por la elección de Diego)

**Teclas.** Z ataca, X esquiva, C usa la habilidad eco del héroe activo, V usa el objeto elegido, Q y E cambian de héroe y 1 a 4 eligen en la bolsa. Las flechas mueven, como hoy.

**Reglas del juego.**

1. El golpe común hace daño con resistencia. Si deja al monstruo sin vida, este se rehace con su `regeneration_ratio`, igual que en el combate por turnos.
2. La habilidad eco del tipo correcto **aturde** al monstruo durante `DUR_STUN_WINDOW`. Una segunda habilidad eco correcta dentro de esa ventana lo **purifica**. Si la ventana se acaba sin la segunda, se rehace y la cuenta vuelve a cero. Así se traduce `COUNTER_SUSTAIN_ROUNDS` = 2.
3. La habilidad eco del tipo equivocado hace daño con resistencia y se avisa igual que el golpe común.
4. El monstruo avisa cada ataque con una zona en el suelo durante `DUR_TELEGRAPH`, y después golpea. Quien está fuera de la zona o esquivando no recibe daño.
5. La esquiva dura `DUR_DODGE`, mueve `DODGE_DISTANCE` y no se puede repetir antes de `DUR_DODGE_COOLDOWN`.
6. El héroe que no manejas sigue al activo y no recibe golpes mientras no esté en la zona. Su postura es la del grupo (IA-5), y en esta versión solo sigue.
7. Si el héroe activo cae, se cambia solo al siguiente que siga en pie. Si caen todos, se pierde y se vuelve a la entrada de la zona con 1 PV, como hoy.
8. Al purificar sale la ola de `purify_wave` desde el monstruo y la zona queda purificada, como hoy.

**Lo visual.** Todo color sale de `design_tokens.gd`. El tajo es una media luna de oro a blanco, `TV_GOLD_4` a `TV_UI_6`. La zona de aviso usa `TV_FIRE_2` con borde `TV_INK_0`, tramada en Bayer 4×4 como la ola, porque así nunca hay un color mezclado. Las cifras son las de `DamageNumbers`. El aviso va en el papel de `TvFrame.TEXTBOX`. Solo se animan posición, escala y opacidad. Con `DesignTokens.reduced_motion` todo salta al estado final.

**Medidas nuevas en `design_tokens.gd`.**

| Token | Valor | Por qué |
|---|---|---|
| `DUR_STUN_WINDOW` | 4,0 s | Da tiempo a cambiar a Bruma con Q y usar C, unas 2 s, con margen para quien no juega mucho |
| `DUR_TELEGRAPH` | 0,8 s | El aviso tiene que verse antes de poder esquivar |
| `DUR_DODGE` | 0,25 s | Una esquiva corta y clara |
| `DUR_DODGE_COOLDOWN` | 0,6 s | Evita esquivar sin parar |
| `DODGE_DISTANCE` | 48 px | Tres casillas. Con 32 px, quien esquivaba desde el centro de la zona seguía dentro, porque la zona mide 40 de radio (medido con `verify_action_combat`, 2026-11-04) |
| `HERO_REACH` | 28 px | El tajo alcanza un poco más que una casilla y media |
| `MONSTER_ATTACK_RADIUS` | 40 px | La zona de aviso, más grande que el alcance del héroe para obligar a moverse |
| `DUR_MONSTER_REST` | 1,4 s | Pausa del monstruo entre ataques |

**Conexión.** Un interruptor `action_combat` en `GameFlow`. Apagado, todo sigue como hoy y las pruebas del combate por turnos no cambian. El combate por turnos no se borra.

## Registro de pasos

### Fases 1, 2 y 4: el bucle, la regla de la causa y el HUD (2026-11-04)

- **Código:** `src/world/action_combat.gd` (reglas y monstruo), `src/world/action_ground.gd` (zona de aviso y tajo), `src/ui/action_hud.gd` (HUD) y el interruptor `action_combat` en `GameFlow`. Iconos del prototipo con `tools/gen_tierra_viva_icons.py`, todo píxel es token.
- **Medido con `tools/verify_action_combat.tscn`, 21 de 21:** 300 tajos no purifican y el monstruo se rehace 15 veces. El aviso nombra la causa y a Bruma. La habilidad equivocada no aturde. Q y E cambian en el mismo cuadro. La ventana de aturdimiento caduca. Dos contramedidas purifican, sale la ola y la zona queda purificada. Quieto en el aviso se recibe el golpe y esquivando no. Si caen todos, se vuelve a la entrada con 1 PV. Con el interruptor apagado se pelea por turnos.
- **Sin cambios en lo demás:** `verify_flow` 34/34, `verify_encounters` 82/82, `verify_usability` 28/28, `verify_party_ai` 34/34, `verify_movement` 100/100 y `verify_demo` 15/15.
- **Corregido al mirar las capturas:** el alcance se medía de pie a pie y Ilan quedaba detrás del sprite de 110 px. Ahora cuenta desde `MONSTER_BODY_RADIUS`. La trama de la zona bajó de 8 a 5 de cada 16 píxeles porque se veía sólida. La bolsa y los mandos llevan los iconos del prototipo en vez de abreviaturas.
- **Capturas:** `docs/ux/capturas/2026-11-04-accion-rehace.png`, `-aviso.png`, `-aturdido.png` y `-purifica.png`.
- **Pendiente:** la fase 3 (el compañero en el mapa con su postura), el ataque de la Llama con estados (hoy solo hace daño, sin quemadura ni humo), sonidos propios del combate de acción y que alguien lo juegue.
