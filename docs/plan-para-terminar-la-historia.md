# Plan para terminar Ecos de la Tierra

Escrito el 2026-11-03. Con Juan José vimos que por tiempo no alcanzamos a entregar el juego completo el 2026-11-04, así que presentamos una demo hasta el primer jefe y aquí queda planteado lo demás para acabar la historia.

Este plan cambia el alcance que cerramos el 2026-09-14, que era el juego completo sin versión de muestra. El detalle técnico de cada parte sigue en `docs/guia-del-equipo.md`.

## 1. La demo

**Estado:** confirmada por Diego el 2026-11-03, con las decisiones de la sección 4.

El recorrido es este:

1. Ilan empieza en Valdehoja y habla con Yara junto al semillero.
2. Sale por el este hacia el Bosque de las Cenizas. Yara le habla por el ave.
3. En el Bosque se encuentra con el Comandante Rasgo.
4. Pelea contra la Llama de la Deforestación, el primer jefe. Solo la Línea Cortafuegos de Bruma ataja la causa.
5. Sale la ola de purificación, el Bosque se cura y se abre el paso.
6. Al cruzar ese paso hacia la Cuenca, termina la demo con un mensaje que dice qué sigue en la historia.

Para que la demo funcione falta esto:

| Qué | Por qué | Quién |
|---|---|---|
| Cerrar la salida norte de Valdehoja hacia la Cripta | Hoy está abierta y se saltaría la historia | Diego |
| Terminar la demo al salir del Bosque hacia la Cuenca | Hoy esa salida lleva a la región siguiente | Diego |
| Pasar la caja de diálogo a `DialogBox` del sistema a 640 × 360 | Lo de la rama `parte-5/anexo` está hecho a 480 × 270 con otro diseño | Diego |
| Montar los tres diálogos ya escritos en esa rama (`yara_inicio`, `yara_ave_bosque`, `rasgo_bosque`) | Sin ellos no se entiende la historia | Diego |
| Hacer el mensaje de fin de demo en el papel del sistema | No hay una pantalla diseñada para esto y no vamos a inventar una | Diego |
| Exportar el `.exe` desde `master` y jugarlo completo | El que hay no tiene nada de lo de hoy | Juan José |

**Actualización del 2026-11-03, hecho en la rama `rediseno/demo-primer-jefe`:** las salidas cerradas, Rasgo después de Yara y el mensaje final, medidos con `tools/verify_demo.tscn`. Yara lleva retrato sacado de su sprite y Rasgo habla sin retrato hasta tener su original. Falta exportar el `.exe` y jugarlo completo. Nadie ha jugado aún el recorrido de punta a punta.

**Nota de Juan José para Diego, ya atendida:** Juan José adelantó parte
de esta tabla en el PR #48, a la vez que se escribía este plan, sin haberlo visto:

- **Ya está en `rediseno/terreno`, aún no en `master`:** la caja `DialogBox` a 640 × 360 y
  `yara_inicio` y `yara_ave_bosque` en marcha. La rama `parte-5/anexo` ya va integrada, así
  que no hace falta fusionarla otra vez.
- **Sin montar:** `rasgo_bosque`. El texto está en `data/dialogue/` y la prueba de su chapa
  existe, pero no sale en el juego.
- **Añadido fuera de este plan, para que lo veas:** al empezar, Yara llama a Ilan por el ave
  para que vaya al jardín (`yara_llamada.json`), porque aparece lejos de ella. Si no la
  quieres, basta con quitar `on_start` de `talk.json`.
- **Sin tocar:** la salida norte, el fin de demo, Bruma desde el Bosque y el mensaje final.

Desde ese PR, Juan José no cambia `src/` ni `data/` hasta que avises.

La demo no lleva título, guardado, menú fuera de combate ni puzzles. Tampoco el combate de acción, así que se presenta por turnos.

## 2. La historia que falta

Ilan quiere entender qué les pasó a sus padres y sanar Solmira, enferma por lo que dejó la Compañía Áurea del Barón Ezra Cendral. Cada región se cura atacando la causa de su daño, no golpeando más fuerte.

| Orden | Región | Monstruo | Habilidad que lo vence | Puzzle que la ensaya | Compañero |
|---|---|---|---|---|---|
| Demo | Bosque de las Cenizas | Llama de la Deforestación | Línea Cortafuegos | Cortafuegos | Bruma |
| 2 | Cuenca de Alquitrán | Devorador de Petróleo | Barrera Absorbente | Barreras absorbentes | Coral |
| 3 | Costa Quebrada | Gólem de Plástico | Separación en la Fuente | Fardos al contenedor | Nix |
| 4 | Llanura Marchita | Espectro del Monocultivo | Rotación de Cultivos | Rotar cultivos | Suri |
| 5 | Cumbre Menguante | Coloso del Deshielo | Escudo de Albedo | Manto sobre la roca | Grupo completo |
| Final | Cripta de la Avaricia | Sombra de la Avaricia | Combinar las habilidades, porque aprende a resistir la que se repite | No aplica | Grupo completo |

El Comandante Rasgo aparece en cada una de las cinco regiones y recuerda lo que hizo el jugador. Su historia termina en alianza, retirada o enemistad. Yara acompaña por el ave con pistas según cómo va jugando cada persona. Al final una última ola recorre el mundo y los créditos pasan por las siete zonas ya sanas.

## 3. Lo que falta después de la demo, en orden

1. **Combate de acción (R2), Diego, guía §4.5.** Va primero porque cambia cómo se vence cada monstruo y de ahí dependen los puzzles y el equilibrado. Si no alcanzamos, se queda el combate por turnos, y eso hay que decidirlo antes de seguir.
2. **Progresión, Juan José, guía §4.8.** Quién se une, con qué habilidad y qué región quedó purificada.
3. **Guardado, Juan José, guía §4.11.** Va después de la progresión porque guarda sus banderas. Al terminar se actualiza `docs/legal/privacidad.md`.
4. **Diálogos completos con pistas de Yara y memoria de Rasgo, Diego, guía §4.7.**
5. **Regiones con su composición de referencia, Diego.** Hoy tienen el arte nuevo sobre sus mapas, pero la Cripta y la Costa siguen lejos de sus imágenes `z_*`. Esto pide mapas nuevos con su colisión y sus pruebas, como se hizo con Valdehoja.
6. **HUD del mapa, interiores y vecinos (R3), Diego, guía §4.6.**
7. **Personajes en PixelLab, Diego.** Yara y las caminatas de Bruma, Coral, Nix y Suri.
8. **Puzzles, Diego, guía §4.9.**
9. **Menú fuera de combate, Diego, guía §4.10.**
10. **Título y opciones, Diego, guía §4.12.** El aviso de privacidad se muestra aquí dentro del juego.
11. **Audio definitivo, Diego, guía §4.13.** Hoy es provisional y le falta su anexo.
12. **Final y créditos, Diego, guía §4.14.** Faltan los nombres del equipo y `LICENCIAS.md`.
13. **Equilibrado, Juan José.** El Gólem no presiona y la fuerza bruta gana demasiado en la Llanura (100 %), la Cuenca (64 %) y el Bosque (41 %). Con R2 se vuelve a medir todo.
14. **Prueba con personas, los dos.** «¿Por qué pierdo?» se rehace con el combate definitivo.

## 4. Lo que Diego decidió para la demo (2026-11-03)

1. **Bruma.** La historia dice que se une después del Bosque, pero la pelea necesita su Línea Cortafuegos. Acompaña a Ilan desde la entrada del Bosque.
2. **Diálogos.** Se montan los tres ya escritos, porque sin ellos la demo es caminar y pelear. Si esta noche se complica, se presenta sin ellos y se explica la historia de palabra.
3. **Mensaje final.** «Aquí termina la demo. El Bosque de las Cenizas vuelve a respirar, pero Solmira sigue enferma. Ilan y Bruma siguen hacia la Cuenca de Alquitrán.»

Queda abierta para después de la presentación la prioridad entre el combate de acción y lo demás.
