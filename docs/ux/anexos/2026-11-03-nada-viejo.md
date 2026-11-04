# Anexo UX, nada viejo a la vista · 2026-11-03

Diego pidió que al jugar no quede nada con el diseño viejo. El sistema de `docs/ux/sistema-de-diseno/` ya está elegido, así que aquí no hay ronda de investigación ni direcciones. Este anexo guarda la auditoría contra las referencias y lo que falta.

## Estado al cerrar esta sesión

La pasada final de regeneración y capturas la detuvo el sistema por falta de memoria (1,7 GB libres de 12 GB) y no se relanzó. Por eso hay dos estados distintos.

- **El commit `8931c6f` de la rama está probado.** Trae Valdehoja nueva. Las regiones y el combate siguen como antes en ese commit.
- **La copia de trabajo sin commit no está probada y no se debe jugar todavía.** Tiene las regiones, el combate y el retiro de los respaldos. Hay sprites nuevos sin importar, así que faltarían piezas al montar las zonas.

Para terminar hay que correr, cuando haya memoria, estos pasos:

1. `python tools/gen_tierra_viva_terrain.py waning_peak`, porque el sano de la Cumbre quedó con la masa anterior y el enfermo con la nueva.
2. `"$G" --headless --path . --import` y descartar `docs/balance/*.import`.
3. Las pruebas y capturas de la lista «Sin verificar».

## Qué referencia manda en Valdehoja

`assets/img/valdehoja-inicio.png` no es del sistema nuevo. Su MD5 (`e362b32f…`) es igual al de `docs/ux/capturas/2026-10-28-valdehoja-inicio.png`, la captura del contrato «Rastro» anterior a Tierra Viva. De ahí salen las copas oliváceas y las casitas pequeñas. Igualarla habría sido volver a lo viejo.

La referencia que se usó es la que enseña `components/Overworld`, o sea `valdehoja_enfermo.png`, `valdehoja_sano.png` y `v_*.png`. La matriz de 60 × 34 no podía llegar a esa imagen, porque el pueblo mide 90 × 64 y sus edificios de PixelLab no caben en huellas de 3 × 3. Por eso se cambió la matriz, como permite la guía en §4.3.

## Auditoría

Las rutas de captura son relativas a `docs/ux/capturas/nada-viejo/`. Cada imagen `cmp-*` lleva el juego a la izquierda y la referencia a la derecha. Todas se miraron, salvo donde la tabla dice otra cosa.

| Pieza | Comparación | Antes | Ahora | Archivo y qué falta |
|---|---|---|---|---|
| Valdehoja enferma | `cmp-despues-valdehoja-enfermo.png` | Viejo | **Igual**, 4,2 % de píxeles distintos | `tools/gen_tierra_viva_valdehoja.py`. La diferencia es lo añadido a propósito |
| Valdehoja sana | `despues-valdehoja-sano-mapa.png` frente a `valdehoja_sano.png` | Viejo | **Igual**, 5,3 % de píxeles distintos | Mismo generador |
| Jardín de Yara | `despues-valdehoja-enfermo-mapa.png` | Viejo | Con piezas del sistema, sin referencia propia | La referencia no lo trae. Yara es una variante de Toña |
| Bosque enfermo y sano | `cmp-t1.png`, `cmp-antes-ashen_forest-enfermo.png` | Viejo | **Distinto en la composición**, árboles y arbustos ya del sistema | Sin commit. La referencia es una viñeta y el mapa del juego es otro |
| Cuenca | `cmp-t2-tar_basin-*.png` | Viejo | **Distinta**, árboles del sistema, sin la ciénaga en la llegada | Sin commit. Balancines y petrolero añadidos, sin ver |
| Costa | `cmp-t2-broken_coast-*.png` | Viejo | **Distinta**, palmas del sistema, mucha más arena y sin mar a la vista | Sin commit. Manglares y vecinos añadidos, sin ver |
| Llanura | `cmp-t2-withered_plain-*.png` | Viejo | **Distinta**, sin surcos ni molino ni granero | Sin commit. Grietas y espantapájaros añadidos, sin ver |
| Cumbre | `cmp-t2-waning_peak-*.png` | Viejo | **Distinta**, frailejones del sistema demasiado densos | Sin commit. Masa aclarada y pedregal, sin ver |
| Cripta | `cmp-t2-greed_crypt-*.png` | Viejo | **Distinta**, pasillos con piedra gris frente a una sala morada | Sin commit. Antorchas, tinte y ajuar, sin ver |
| Masa sana de Cuenca, Llanura y Cumbre | `cmp-t2-*-sano.png` | Viejo | **Distinta**, muy cerrada donde la referencia deja claros | `MASS` en `gen_tierra_viva_terrain.py` |
| Ilan en el mapa | Capturas de pantalla de cada zona | Igual | Igual | Sin cambios |
| Monstruos en el mapa | Solo el de la Cripta en la captura | Sin juzgar | Sin juzgar | Faltan capturas de los otros cinco. Banda de alerta nueva, sin importar |
| Cartel de lugar | Capturas de cada zona | Igual | Igual | Sigue abierto el contraste de 3,22:1 |
| Persiana de entrada | Sin captura | Sin juzgar | Sin ver | `battle_blinds.gd` pasa a `TV_INK_0`, sin commit |
| Fondo, monstruo, grupo, placa, filas, menú y aviso de combate | `combate_enfermo.png`, sin captura nueva | Sin juzgar | Sin ver | Filas de §3.1 marcadas como hechas. Quitados los respaldos, sin commit |
| Cola de turnos | Sin captura | Viejo, no está en el sistema | Retirada, sin ver | `turn_order_strip.gd` borrado, sin commit |
| Cifras de daño | Por lectura de código | Viejo, tokens `EMBER_*` y `ASH_*` | Sin cambios | `damage_numbers.gd`, de Juan José |
| Pantalla de resultado | Por lectura de código | Viejo, tokens `TEXT_*` y `PANEL_FILL` | Sin cambios | `result_overlay.gd`, de Juan José |
| Selector de región | Sin captura | Viejo | Sin ver | `region_select.gd` con `TvFrame`, sin commit. Solo se llega desde `main.tscn`, no desde el juego |

Estas cosas no existen en el juego, así que no cuentan como viejas: diálogos, HUD del mapa, interiores, título, créditos y combate de acción.

Se quedan por razones no visuales `assets/tilesets/world.png`, que solo da la colisión en las zonas con suelo pintado, y los `TEXT_*` de `battle_screen.gd`, que funcionan como claves para escoger el tono del papel.

## Decisiones

- **Valdehoja sale del mismo código que su referencia.** `village5.py` corre con su semilla y el generador separa el suelo de las piezas, para que Ilan pase por delante o por detrás. El costo es un `.deco.txt` generado, con 138 entradas de leyenda, que no se edita a mano.
- **El decorado admite un desfase en píxeles** (`, +x-y` en la leyenda). Sin eso, cada sprite caía en la rejilla y la diferencia con la referencia era del 21 %. Con el desfase bajó a 4,2 %.
- **Se conservan las salidas, en otro sitio la del Bosque.** Pasa de (59, 17) a (89, 33), sobre la calle mayor. La bocamina sigue en (3, 0) y ahora está en una cara de roca.
- **La aparición pasa a (40, 31)**, al pie de la plaza, porque es el encuadre de `v_plaza.png`. Ilan ya no empieza junto a una casa suya.
- **El jardín de Yara queda en la orilla este**, donde la referencia pone su campo de flores. La referencia no tiene jardín y el juego lo necesita. Se quitaron dos árboles de la referencia para hacerle sitio.
- **El hito sigue siendo el roble del jardín**, porque `verify_zone` lo exige ahí. El Árbol del Vínculo de la plaza es decorado.
- **Los vecinos son decorado sólido** porque aún no hablan. Eso choca con `background_person` del catálogo viejo, y aquí manda el sistema.

## Pruebas adaptadas

Estos cambios bajan o mueven lo que se mide.

- `verify_zone`, puerta de cada casa. Ya no mira el centro de la huella, sino que haya camino en algún punto del frente, porque la puerta no va centrada en todos los edificios. La puerta exacta la comprueba el generador.
- `verify_zone`, vaivén de la hierba. Admite un cambio de diferencia, porque el número depende de la fase de cada mata.
- `verify_movement`, sin commit. Las bandas del viewport deben ser `TV_INK_0` y no `ASH_950`. No se ha corrido.

## Medidas

Corridas sobre el commit `8931c6f`:

- `verify_zone valdehoja` dio 75 de 75 OK, 0 pendientes.
- `verify_terrain valdehoja` dio 8 de 8 OK.
- `verify_palette image` dio «todo píxel es un token» en los dos suelos de Valdehoja.
- `verify_palette value` dio 2,05 en visión normal, 2,00 en deuteranopía, 2,12 en protanopía y 2,03 en tritanopía, con piso de 1,5.

## Sin verificar

Nada de esta lista se ha corrido sobre la copia de trabajo:

- `verify_zone` y `verify_terrain` de las seis regiones.
- `verify_flow`, `verify_usability`, `verify_encounters`, `verify_wave`, `verify_movement` y `verify_party_ai`.
- `verify_palette` de los sprites de Valdehoja, que traen tinta de PixelLab y colores de `ashen()` fuera de los tokens.
- La regla de que la copa no tape más del 8 % de camino, ahora con árboles de 102 × 95 en las regiones.
- Capturas de combate, persiana y selector, y `--write-movie` del recorrido real.
- Si queda algún id sin sprite ahora que no hay respaldo al decorado viejo.

## Preguntas para Diego

1. ¿Las regiones deben seguir el dibujo de las referencias `z_*`? Hoy se parecen en el arte y no en la composición, porque sus mapas son otros. Igualarlas exige matrices nuevas con su colisión y sus pruebas, como en Valdehoja.
2. Las calles del oeste y del sur llegan al borde sin salida y Ilan choca con una pared invisible. La guía habla de cinco salidas y `exits.json` tiene dos. ¿Se cierran con valla o se abren?
3. ¿El hito de Valdehoja es el roble de Yara o el Árbol del Vínculo? La guía y la prueba dicen cosas distintas.
4. ¿Yara se queda como variante de Toña hasta tener su original de PixelLab?
5. ¿Se quita `valdehoja-inicio.png` del sistema de diseño? Es una captura vieja y ya confundió a quien la usó como referencia.
