# Continuar Ecos de la Tierra: turno de noche

Escrito el 2026-11-04 a las 00:20. Diego cambia de cuenta de Claude y quiere que el trabajo siga solo toda la noche, sesión tras sesión. Si estás leyendo esto al empezar una sesión, este archivo es tu encargo.

Palabras de Diego: «en el sistema de diseño ya quedó que las peleas iban a hacer en mundo abierto, que yo controlaba al jugador, no por turno», «ya inicié sesión con otra cuenta en pixellab, entonces puedes generar los personajes que faltan», «falta colocar música y demás, que esa demo sea chévere».

## 1. Cómo se trabaja esta noche

Cada sesión hace esto:

1. Lee este archivo entero y la bitácora del final. Lee `AGENTS.md` y `docs/guia-del-equipo.md` §2.
2. Confirma con `git status -sb` que estás en `noche/demo-accion`. Si hay cambios sin commit de una sesión cortada, revísalos antes de seguir.
3. Sigue el primer bloque sin terminar de la sección 3.
4. Haz commit y `git push` al terminar cada paso. Una sesión se puede cortar en cualquier momento por límite de uso.
5. Antes de cada commit anota en la bitácora qué quedó hecho, qué se midió y qué sigue.

**Permiso de Diego para esta noche.** No hay nadie para dar visto bueno, así que no se para a esperarlo en cada paso. Se deja captura y medida de cada paso para que Diego lo revise en la mañana. Lo que normalmente se le preguntaría se decide por la opción más conservadora y se escribe en «Preguntas para Diego». Este permiso vale solo para esta rama y esta noche.

**Lo que no se hace, aunque parezca buena idea:**

- No tocar `master` ni `rediseno/terreno`, y no fusionar ningún PR. Hoy 2026-11-04 es la presentación y `master` es la demo de respaldo. Juan José exporta el `.exe` desde ahí.
- No usar `git push --force`, no borrar ramas y no reescribir historia.
- No pagar nada, no comprar créditos y no aceptar términos en ninguna página. Si PixelLab pide pago, se anota y se sigue con otro bloque.
- No cambiar configuración de Claude, permisos ni cuentas.
- No escribir contraseñas ni datos de cuenta en ningún archivo.
- Si un comando se bloquea por permisos, no se le da la vuelta. Se anota y se sigue con lo demás.

**Terminar.** A la hora límite que te pasaron, deja todo con commit y push. Si no queda ningún bloque por hacer, crea el archivo `.noche-terminada` en la raíz del proyecto, sin commit, y el script deja de lanzar sesiones.

## 2. Lo que ya aprendimos a golpes

- **Las pruebas con captura se cuelgan con `--headless`.** `verify_terrain`, `verify_wave`, `verify_demo`, `verify_opening`, `verify_dialogue_states` y las capturas van con ventana. Esto dejó un agente quieto once minutos.
- **Todo comando de Godot lleva `timeout`.** Nunca se lanza sin límite, y nunca se espera un proceso sin límite.
- **La memoria es justa**, unos 2 GB libres de 12 GB, y una pasada ya murió por eso. Se corre una prueba a la vez.
- **Binario de Godot:** `C:\Users\Cisna\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe`.
- **Python en Windows:** con `PYTHONIOENCODING=utf-8`.
- **`--import` puede terminar con «Segmentation fault»,** y las texturas quedan bien igual. Después de cada PNG nuevo hay que importar.
- **Las pruebas dejan basura.** Se descarta con `git restore docs/balance docs/ux/capturas/2026-10-28-ola-bosque.png`, y se borran los `.png.import` sin versionar de `docs/ux/capturas`.
- **Pasar `verify_palette` no significa que se vea bien.** Valdehoja pasó todas las medidas y no se parecía en nada al sistema. Siempre se mira la captura junto a su referencia.
- **Quitar un respaldo puede romper el juego.** Al quitar el decorado viejo desapareció el monstruo de todas las regiones. Después de tocar el mundo se corre `verify_flow` y `verify_encounters`.
- **`docs/ux/sistema-de-diseno/project/assets/img/valdehoja-inicio.png` es una captura vieja,** no una referencia. Las buenas son `valdehoja_enfermo.png`, `valdehoja_sano.png` y `v_plaza.png`.
- **`verify_wave` puede fallar por duración** con la máquina cargada, 58 a 60 cuadros contra 54. El commit limpio también se pasó, así que no se afloja la prueba. Se anota.
- **El subagente `ux-designer`** es la regla de Diego para frontend. Si lo usas, pásale estas lecciones en el encargo y que no deje procesos en segundo plano.

## 3. El trabajo, en orden

La demo actual está en `docs/plan-para-terminar-la-historia.md` §1: Valdehoja, Bosque de las Cenizas y primer jefe. **Esta noche no se amplía a otras regiones.** Una demo corta y buena vale más que una larga a medias.

### Bloque A. Línea base

1. Importa y corre `verify_flow`, `verify_demo`, `verify_usability` y `verify_encounters`. Tienen que dar verde antes de tocar nada, y si no, se anota.
2. Graba el arranque real: `--path . --write-movie <dir>/x.png --fixed-fps 10 --quit-after 25 res://scenes/game.tscn`.

### Bloque B. Personajes en PixelLab

Diego dejó la sesión de PixelLab abierta en Chrome. Se usa con las herramientas de Claude in Chrome. **Si no están disponibles en esta sesión, se anota y se pasa al bloque C**, sin insistir más de dos intentos. Lee `assets/source/pixellab/README.md` y `docs/ux/sistema-de-diseno/project/components/Cast/README.md`. Los originales van en `assets/source/pixellab/<nombre>/`, y no se retoca nada a mano.

Se genera en este orden, porque los créditos pueden acabarse:

1. **Yara:** anciana curandera de Valdehoja, mentora. 48 px, 8 direcciones. Hoy es una variante de Toña.
2. **Rasgo:** Comandante de la Compañía Áurea, 48 px, 8 direcciones. Hoy no existe en el mapa.
3. **Bruma:** caminata de 4 cuadros en todas las direcciones. Va primero entre los compañeros porque es la que sale en la demo.
4. **Ataque de Ilan y de Bruma,** si PixelLab lo permite, para el combate del bloque C.
5. **Coral, Nix y Suri:** caminatas. Solo si sobran créditos.

El sistema no describe a Yara ni a Rasgo. Se toma lo que dice `EcosDeLaTierra Propuesta Videojuego.md` §2.3 y §2.4, con el estilo y las reglas de `Cast`, y lo que se decida se anota como pregunta para Diego. Después corre `tools/gen_tierra_viva_cast.py` y `tools/gen_tierra_viva_portraits.py`, y mide con `verify_palette.py image <png> --source assets/source/pixellab/<nombre>`. Con el original de Rasgo, ponlo en el Bosque como personaje y dale su retrato. Hoy solo habla.

### Bloque C. Combate de acción en el mapa (R2)

**Es lo más importante de la noche.** Es lo que Diego eligió el 2026-10-30, y la demo hoy lo presenta por turnos porque no alcanzó el tiempo.

La dirección no se vuelve a discutir porque ya la eligió Diego. Antes de programar, abre `docs/ux/anexos/2026-11-04-combate-accion.md` con usuarios, comunicación, las fuentes 4 a 7 que ya están en el anexo de Tierra Viva y el contrato. Las piezas salen de `components/ActionHUD/README.md`, `EnemyPlate`, `TypeBadge`, `docs/ux/tierra-viva/referencias/combate_accion.png` y `combate_purifica.png`, y del prototipo `tools/tierra_viva/combat_mock.py` y `hud.py`. El detalle está en `docs/guia-del-equipo.md` §4.5.

**Cómo debe jugarse:**

- Se pelea en el mismo mapa, sin pantalla aparte ni persiana. Manejas a un héroe con movimiento libre.
- **Z** ataca, **X** esquiva, **C** usa la habilidad eco y **V** usa el objeto. **Q** y **E** cambian de héroe al instante. **1 a 4** eligen en la bolsa.
- El golpe sin la causa correcta hace que el monstruo **se rehaga**, con el aviso en papel: «La llama se rehace. Su causa es FUEGO». Cifra con `~`.
- La habilidad eco del héroe correcto lo purifica. En el Bosque es la Línea Cortafuegos de Bruma. Cambia la forma del monstruo y sale la ola de `purify_wave`.
- La contramedida de dos rondas pasa a ser una **ventana de aturdimiento**. El compañero que no manejas actúa con la postura del grupo, que reemplaza a la orden de líder.
- La Llama necesita ataques con aviso que se puedan esquivar. Sus habilidades son Onda de Calor y Sofocación por Humo.
- Si pierdes, vuelves a la entrada de la zona. Se conserva lo que hace hoy `game_flow.gd`.
- Golpe: tajo en media luna de oro a blanco y chispa. Con `DesignTokens.reduced_motion`, todo salta al estado final. Solo se anima transform y opacidad.

**Por fases, con commit en cada una:**

1. **Solo el bucle:** mover, atacar y esquivar contra la Llama, con vida y daño. Sin HUD.
2. **La regla de la causa:** rehacerse, el aviso de papel, la ventana de aturdimiento y la purificación con la ola.
3. **Cambio de héroe** con Q/E y el compañero con su postura.
4. **HUD** de `ActionHUD`: tarjeta del héroe, relevo, bolsa y mandos en rombo. Nunca tapa el centro de la pantalla.
5. **Estados:** derrota, victoria, sin energía, bolsa vacía y movimiento reducido.

**Cómo se conecta:** con un interruptor `action_combat` en `GameFlow`, igual que `demo`, y se enciende en `game.tscn` solo cuando pasen las fases 1 a 4. El combate por turnos **no se borra** esta noche. Si el nuevo no queda bien, se deja apagado y la rama sigue sirviendo. `verify_flow` y `verify_encounters` siguen probando el de turnos con el interruptor apagado.

**Cómo se mide:** `tools/verify_action_combat.gd` con teclas simuladas. Tiene que comprobar que el golpe común no purifica, que Bruma con C sí, que Q/E cambia al instante, que la esquiva evita un ataque avisado, que perder devuelve a la entrada, que al ganar sale la ola y se abre el paso, y que con movimiento reducido no se anima. Además, una pelea con fuerza bruta **no debe ganar**. Antes ganaba el 41 % de las veces. Graba capturas y míralas junto a `combate_accion.png`.

### Bloque D. Música y sonido

`tools/gen_audio.py` genera hoy 17 audios por código, y `src/core/game_audio.gd` los toca. Lee `docs/guia-del-equipo.md` §4.13.

1. Abre el anexo de la parte 11, que nunca se abrió.
2. Mejora la música de Valdehoja, del Bosque y del combate, sin muestras de terceros. Lo enfermo suena apagado y se abre con la ola.
3. Agrega sonidos para atacar, esquivar, cambiar de héroe, rehacerse y aturdir, y conéctalos.
4. Solo se usa audio generado por código o con licencia libre anotada en `docs/licencias-audio.md`. El conector de ElevenLabs de esta cuenta no hace música y gasta créditos, así que no se usa.
5. Mide niveles y que no haya recorte con `verify_audio`. **Claude no puede oír:** se anota que Diego tiene que escucharlo.

### Bloque E. Que la demo sea chévere

Solo lo que ayude al recorrido:

1. **El Bosque contra su referencia:** `assets/img/bosque_enfermo.png`, `bosque_sano.png` y `mapa_bosque_*.png`. Es la región que sale en la demo, y el mapa actual es distinto. Acerca el arte sin romper colisiones ni salidas.
2. **Vecinos de Valdehoja que hablan:** una línea cada uno, en `data/dialogue/`. Mismo tono de Yara.
3. **Cerrar la pelea con historia:** Bruma dice algo al purificar el Bosque, y Yara responde por el ave.
4. **Pantalla de título** desde `docs/ux/tierra-viva/titulo-y-creditos.md`, con Valdehoja real. Solo si todo lo anterior quedó bien.
5. Mostrar el aviso de privacidad de `docs/legal/privacidad.md` dentro del juego, en créditos u opciones.

### Bloque F. Cierre

1. Comprobación general de `docs/guia-del-equipo.md` §2, con `verify_demo`, `verify_opening`, `verify_numbers`, `verify_result` y `verify_action_combat`.
2. Si Godot tiene las plantillas instaladas, exporta el `.exe` de esta rama con la guía §4.15 a una carpeta fuera del repo y anota la ruta. Si no las tiene, no las descargues y anótalo.
3. Abre un PR de `noche/demo-accion` hacia `rediseno/terreno` con la plantilla de `docs/guia-del-equipo.md` §2, con **Dev:** Diego Armando Pinta Cuasquen y capturas reales. **No lo fusiones.** Diego decide en la mañana.
4. Escribe al final de este archivo el informe para Diego: qué quedó, qué falló, qué falta probar jugando y qué preguntas tiene que responder.

## 4. Preguntas para Diego

(Las sesiones agregan aquí lo que decidieron por él.)

- **Esquiva de 48 px y no de 32.** Con 32 no se salía de la zona de aviso de 40 px de radio. Se cambió midiendo.
- **El ataque de la Llama hace daño sin quemadura ni humo.** Los estados del combate por turnos cuentan por turnos y aquí no hay turnos. ¿Se agregan con duración en segundos?
- **El claro del Bosque sin muro ni cartel.** La referencia tiene una meseta con muro de piedra y escalera, pero el mapa del juego no tiene alturas. Tampoco hay cartel en el catálogo del Bosque. ¿Se agregan después?
- **Textos nuevos para revisar:** `data/dialogue/bosque_purificado.json` y los cinco `vecino_*.json`. La pescadora no tiene nombre en el sistema y sale como «Pescadora».
- **La segunda contramedida no hace daño, purifica directamente.** Así no se rehace en el mismo golpe que la purifica.

## 5. Bitácora

Una línea por paso: fecha y hora, qué se hizo, qué se midió, commit y qué sigue.

- 2026-11-04 00:20. Plan escrito desde `master` (`ec75dc3`). Sigue el bloque A.
- 2026-11-04 00:30. Bloque A hecho: `verify_flow` 34/34, `verify_usability` 28/28, `verify_encounters` 82/82 y `verify_demo` 15/15. Diego pausó el turno de noche y sigue en la mañana. Falta grabar el arranque real (A.2). Sigue el bloque B.
- 2026-11-04 05:40. A.2 hecho (40 cuadros del arranque, sin errores). Se trajeron a esta rama los arreglos de Juan José de `master` (PR #52 a #55).
- 2026-11-04 05:45. Bloque B saltado: la extensión de Chrome no conecta, seguramente porque está con la cuenta de Claude anterior. Para generar en PixelLab, Diego tiene que iniciar sesión en claude.ai desde Chrome con la cuenta nueva.
- 2026-11-04 06:40. Bloque C, fases 1, 2 y 4 hechas, con el registro en `docs/ux/anexos/2026-11-04-combate-accion.md`. `verify_action_combat` 21/21 y las demás pruebas sin cambios. El interruptor `action_combat` sigue apagado en `game.tscn`. Sigue la fase 3, el compañero en el mapa, y después encenderlo.
- 2026-11-04 07:30. Fases 3 y 5 hechas: Bruma sigue a Ilan en el mapa y cambian de sitio con Q/E; avisos largos partidos dentro del papel; sin energía y bolsa vacía con su aviso. `verify_action_combat` 29/29. **El combate de acción queda encendido en `game.tscn`.** Comprobación general sin fallos. Sigue el bloque D, música y sonido.
- 2026-11-04 07:50. Bloque D, primera parte: cuatro sonidos del combate de acción (`slash`, `dodge`, `swap`, `stun`) generados por código con semilla aparte, así que los 17 audios de antes salen con los mismos bytes. `verify_audio` 35/35 y `verify_action_combat` 29/29. **No se tocó la música:** Claude no puede oír y cambiarla a ciegas puede empeorarla. Diego tiene que escuchar los cuatro sonidos nuevos. Sigue el bloque E.
- 2026-11-04 08:20. Bloque E.3 hecho: tras la ola hablan Bruma, Ilan y Yara por el ave (`bosque_purificado.json`) y Yara manda hacia la Cuenca, donde termina la demo. Al acabar la pelea se vuelve a andar con Ilan. Bloque E.2 hecho: Doña Rosa, Don Aurelio, Tito, el padre Julián y la pescadora dicen una línea, sin retrato viejo. `verify_demo` 21/21, `verify_action_combat` 32/32 y `verify_opening` 11/11. Los textos son nuevos y Diego tiene que revisarlos. Sigue E.1, el Bosque contra su referencia.
- 2026-11-04 09:30. Bloque E.1 hecho: `tools/stamp_forest_clearing.py` pone la escena de la referencia (`maps2.bosque()`) en el mapa del Bosque, con su río alineado al del mapa y su camino unido a la llegada. Estanque, cruce, puente, hierba seca, tocones, rocas, tronco caído, arbustos (nuevos en el catálogo del Bosque) y árboles en el borde. `verify_zone` 46/46, `verify_terrain` 8/8, valor 2,49 a 2,70 y las pruebas del juego sin cambios. Captura junto a la referencia en `docs/ux/capturas/2026-11-04-claro-junto-a-la-referencia.png`. Sigue E.4, el título.
