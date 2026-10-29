# Anexo de diseño — Parte 4: encuentros y paso mundo ↔ combate

Abierto el 2026-10-28. Sigue el protocolo de la guía §1.1: usuarios,
comunicación, investigación y direcciones. **Ninguna dirección está elegida:
se pregunta a Diego y se espera.** Hasta entonces no se escribe código de esta
parte.

Alcance (guía §5, parte 4): el monstruo en el mapa (IA-1), el contacto, la
entrada al combate, el fondo de batalla por región, el estado del grupo que
entra y sale, la huida con gracia y la vuelta al mapa con la ola de
purificación. IA-4 (bot de equilibrado) e IA-5 (sintonía del grupo) se diseñan
**después**, en este mismo anexo, porque dependen de cómo se entre al combate.

---

## Fase 1 — Usuarios

- **Primario:** quien juega un RPG 2D, de 14 a 30 años, hispanohablante, en PC
  con teclado, sin conocimiento previo del dominio ambiental. Ya sabe por
  convención que tocar a un enemigo visible abre un combate. **No** sabe que
  aquí el monstruo *es* la causa del daño de su zona, ni que hay un lado bueno
  y uno malo para acercarse.
- **Secundario:** el docente de Diseño de Interfaces, que evalúa si la
  transición y la lectura del monstruo están razonadas, no solo si funcionan.
- **Qué trae ya del juego:** sabe andar y correr (parte 2), que el verde es
  «purificado», que la brasa marca la causa activa y que el fundido a negro es
  cambiar de zona (repertorio §3.1).
- **Situación:** la pantalla mide 480 × 270 y el monstruo es una figura de
  16-32 px entre decorado vivo. La lectura es **periférica**: el jugador mira a
  Ilan y al camino, no al monstruo.

## Fase 2 — Comunicación

**Decisión dominante:** *¿me acerco ahora, y por dónde?* Cada región tiene un
solo monstruo de historia, la fuente del daño, y hay que vencerlo para abrir el
paso. La decisión no es si pelear, sino **cuándo y en qué condiciones**: con el
grupo curado o no, y por delante o por la espalda.

Información que la sostiene, en este orden:

1. **Dónde está el monstruo y hasta dónde llega:** su zona de daño, que el
   mapa ya dibuja con el gradiente (contrato «Rastro»).
2. **Si me ha visto:** su estado (patrulla, alerta, persecución, se rinde).
3. **Qué pasa si toco:** quién empieza el combate.
4. **Que el combate continúa el mundo:** la misma región, el mismo grupo con
   sus PV, la misma bolsa.

**Qué no va:**

- Signos de fábrica sobre la cabeza («!», «?») sin referente (guía §3.3, IA-1).
- Medidores de detección permanentes en el HUD: el HUD de exploración no
  existe, y no se abre por esto.
- Encuentros aleatorios invisibles: el alcance cerrado es un monstruo por
  región, visible.
- Color solo para el estado o para la ventaja (§2.3): cada señal va también
  en silueta, postura o movimiento.
- Una transición que repita el fundido (cambio de zona) o el tramado
  (purificación): cada una tiene su único trabajo.

---

## Fase 3 — Investigación

Consultas hechas el 2026-10-28. Formato:
`observación → decisión aplicable → límite que no copiaré`.

1. **Shadow Tactics, «Dynamic detection»** (Game Developer):
   https://www.gamedeveloper.com/design/game-design-deep-dive-dynamic-detection-in-i-shadow-tactics-i-
   → La detección no se anuncia cambiando de color: un relleno **avanza desde
   los ojos del guardia hacia el personaje**, y el jugador ve cuánto le queda.
   Bordes duros, sin degradados, y un solo cono visible a la vez. →
   **La alerta se lee como algo que avanza hacia Ilan, no como un icono que
   aparece.** Encaja con el pixel art sin subpíxel. → No copio el cono de
   visión permanente ni la cámara lenta: el juego no es de sigilo y la cámara
   lenta pide una regla de tiempo que no está en ningún contrato.
2. **Notas de diseño de batallas de *Ink*** (Pebble Version):
   https://www.pebbleversion.com/html/Ink/InkBattles.html
   → Con enemigos visibles, la emboscada vale en los dos sentidos: tocar por la
   espalda o fuera de su visión da ventaja a quien toca, y el autor lo exige
   por justicia. La cortinilla «no es necesaria; es una decisión de estilo». →
   **Ventaja simétrica:** Ilan por la espalda abre el combate; el monstruo por
   la espalda de Ilan, también. → No copio la batalla sobre el mismo mapa como
   regla: la pantalla «Ceniza y Brasa» ya está contratada con su composición.
3. **Guía de combate y enemigos de EarthBound** (CyricZ, GameFAQs, espejo):
   https://gopherproxy.meulie.net/tilde.pink/0/~bencollver/gamefaqs/text/gba/mother-12/Battle_Enemy-Guide-by--CyricZ.txt
   → Quien toca por la espalda gana un turno libre, y **la propia transición
   anuncia quién lleva ventaja** antes de que aparezca el menú. → **La
   transición lleva el dato de ventaja**: el jugador sabe quién empieza antes
   del primer turno. → No copio que lo diga solo el color del remolino
   (gris, verde, rojo): aquí sería verde para un trabajo que no es purificar.
   La ventaja va en la **dirección** de la transición.
4. **Game Accessibility Guidelines**, lista completa:
   https://gameaccessibilityguidelines.com/full-list/
   → «Ninguna información esencial solo por color», «evitar movimiento o
   sucesos repentinos e inesperados», «que la precisión de tiempo no sea
   esencial» y «opción para ocultar el movimiento de fondo». → **El contacto
   nunca es repentino:** hay alerta antes de la persecución, y la persecución
   va a velocidad de andar (IA-1), así que escapar no exige reflejos. Con
   movimiento reducido, la transición salta a su estado final y el parallax
   del fondo se queda quieto. → No añado una opción de velocidad del juego:
   no está en el alcance de esta parte. Se anota para la parte 10.
5. **Emil Kowalski, «Great animations»**:
   https://emilkowal.ski/ui/great-animations
   → Por debajo de 300 ms, `ease-out`, y lo que se repite muchas veces no se
   alarga. → **La entrada al combate ≤ 300 ms con `ease-out`**, el mismo techo
   del contrato de batalla. El jugador la verá en cada combate. → No copio sus
   curvas de web: aquí el movimiento va en franjas de píxel entero, sin
   interpolación subpíxel.
6. **Godot 4, `AStarGrid2D`**:
   https://docs.godotengine.org/en/stable/classes/class_astargrid2d.html
   → `region` y `fill_solid_region()` permiten encerrar la búsqueda de caminos
   en un rectángulo y marcar sólido todo lo que quede fuera, sin `update()`.
   `DIAGONAL_MODE_NEVER` da solo pasos ortogonales. → **El monstruo no puede
   salir de su zona de daño por construcción**: la rejilla solo tiene libres
   las casillas de esa zona. Pasos ortogonales, como Ilan. → No uso
   `allow_partial_path` contra objetivos sólidos: la documentación avisa de
   que es lento.
7. ***Tales of Zestiria*, transiciones** (RPG Site):
   https://www.rpgsite.net/news/3761-tales-of-zestiria-gameplay-footage-shows-new-battle-transitions-events
   → Se quita el salto a una arena: el combate empieza sobre el terreno donde
   se tocó. → Es la base de la **dirección B**. → No copio el combate en 3D
   en tiempo real: aquí es por turnos y con una composición contratada.

**Fuentes de pantalla de Diego, registradas:** `styles.refero.design`,
`motionsites.ai`, `mobbin.com`, Pinterest, `ui.aceternity.com` y
`tasteskill.dev` **no se consultaron para esta parte** el 2026-10-28. Son
catálogos de web y apps, y esta parte no tiene pantalla de interfaz nueva: es
un sistema de juego y una transición. No cuentan para las seis. Aceternity ya
dio, en el anexo de batalla, el fondo en tres capas que esta parte termina.

**Fuentes que no se pudieron abrir el 2026-10-28** (aparecieron en la
búsqueda, pero no se leyeron, así que no se usan):

- «A random battle draws near! Command?», Matchstick Eyes,
  https://www.matchstickeyes.com/2014/08/03/a-random-battle-draws-near-command/
  — error de certificado del sitio.
- «Fight Woosh», Tropedia, https://tropedia.fandom.com/wiki/Fight_Woosh
  — HTTP 402.
- Ensayo sobre la intro de combate de RPG Maker MZ,
  https://ava.ead.domalberto.edu.br/rpg-maker-mz-battle-intro — conexión
  rechazada.

### Design Read

```
Registro y audiencia: juego. El mapa y el contacto, como producto (lectura
  periférica, respuesta); la entrada al combate, como marca (un momento).
Escena de uso: PC, teclado, partida de sesiones medias; el jugador mira a Ilan.
Tesis: el monstruo es la causa que se ve; acercarse es elegir cómo enfrentarla.
Jerarquía: dónde está y si me ha visto → quién empieza → el combate.
Materiales: sprites del mundo, paleta ceniza y brasa; nada de color nuevo.
Repertorio: postura del monstruo = su estado; transición propia = entrada al
  combate y quién lleva ventaja; fondo regional = continuidad del lugar.
Puntos de entrada: durante la partida, la tarea. La transición es el único
  momento de marca.
Riesgo que se evita: el «!» flotante, el remolino de fábrica y el color como
  única señal.
```

---

## Fase 4 — Direcciones (pendiente de elección de Diego)

Las tres comparten lo que ya está aprobado y no se discute:

- el monstruo **nunca sale de su zona de daño**;
- persigue a **velocidad de andar** (60 px/s), así que corriendo siempre se escapa;
- el grupo entra y sale con su estado: PV, energía, bolsa y estados alterados;
- huir devuelve al mapa con **1 s de gracia**;
- al ganar, la **ola de purificación** sale del punto del combate.

Lo que cambia entre ellas es **cómo se juega el acercamiento y dónde ocurre el
combate**.

### A · «Persiana» — recomendada

- **En el mapa:** el monstruo patrulla una ruta corta dentro de su zona.
  - **Alerta:** se para y se gira hacia Ilan; su sombra se estira hacia él un
    tile por cada 120 ms. La señal es el avance, como en Shadow Tactics.
  - **Persecución:** anda hacia Ilan.
  - **Se rinde:** vuelve a su ruta.
  - Cada estado es una postura distinta, así que se lee sin color.
- **Contacto:** la pantalla se cierra en franjas horizontales de 8 px desde la
  fila del monstruo, en ≤ 300 ms (`ease-out`).
  - **El lado del que se cierra dice quién empieza.** Por la espalda del
    monstruo, las franjas avanzan desde el lado de Ilan y él actúa primero.
    Por la espalda de Ilan, avanzan desde el del monstruo. De frente, se
    cierran desde los dos lados a la vez.
  - Es la familia de transición que la guía §3.1 ya reservaba para esto.
- **Combate:** la pantalla «Ceniza y Brasa», sin cambios en su composición, con
  el **fondo de la región en tres capas** sacado de las rampas de su tileset.
- **Lo que gana:** la decisión «¿por dónde me acerco?» tiene consecuencia y se
  ve antes del primer turno. La pantalla de batalla ya está verificada (16/16).
- **Lo que cuesta:** IA-1 completa (cuatro estados y A* encerrado en la zona),
  las posturas de cada monstruo y los seis fondos.

### B · «En el sitio»

- **En el mapa:** igual que A.
- **Contacto:** no hay transición de pantalla.
  - La cámara se centra entre Ilan y el monstruo.
  - El resto del mundo baja a ceniza, solo en valor y sin tramado.
  - Los paneles de batalla entran por los bordes, sobre el terreno real.
- **Combate:** sobre el propio mapa, como en *Tales of Zestiria*. El fondo
  regional sobra: el fondo es el sitio.
- **Lo que gana:** la continuidad más fuerte posible, porque se lucha donde está
  el daño. La ola de purificación sale de debajo del monstruo vencido, sin
  cortes.
- **Lo que cuesta:**
  - **Enmienda el contrato de batalla.** Su composición (monstruo arriba y grupo
    abajo, con el HUD bajo cada personaje) no cabe sobre un terreno de forma
    libre. Habría que rehacer los pasos 3 a 6 de aquel anexo.
  - Cada fuente necesita un claro de 30 × 17 tiles libre de decorado, así que
    hay que retocar las seis zonas aprobadas.
  - La ventaja se queda sin transición que la anuncie: la diría el registro.

### C · «Umbral de la causa»

- **En el mapa:** el monstruo no patrulla, se queda en su fuente.
  - Su zona de daño tiene un **umbral visible**: el borde donde el gradiente se
    vuelve denso.
  - Cruzarlo no inicia el combate. Ilan se detiene y el jugador **confirma**
    para entrar.
  - Antes de confirmar, un panel `ASH_800` muestra el nombre del monstruo y el
    estado del grupo, y se puede volver atrás para prepararse.
- **Contacto:** solo por decisión explícita. La entrada es la persiana de A,
  siempre desde los dos lados: no hay ventaja por la espalda.
- **Combate:** como A, con fondo regional.
- **Lo que gana:** cero sorpresas y cero reflejos. Es la más accesible y la más
  barata (IA-1 se reduce a una sola reacción del monstruo).
- **Lo que cuesta:**
  - El mapa pierde tensión: el monstruo es una estatua.
  - **Contradice IA-1, aprobada por Diego el 2026-09-30** (patrulla, alerta,
    persecución): elegir C es retirar esa aprobación.
  - El panel de confirmación es una pantalla de interfaz nueva con su propio
    contrato.

### Recomendación: A

1. **Es la única en la que la decisión dominante tiene dos ejes.** «Cuándo»
   y «por dónde»: el grupo curado o no, y por la espalda o de frente. B la
   tiene igual, pero rompe un contrato verificado y seis zonas aprobadas. C
   deja solo «cuándo».
2. **Cumple lo ya aprobado:** IA-1 tal como está, la persiana de §3.1 y el
   fondo de tres capas pendiente del anexo de batalla. No hace falta enmendar
   nada.
3. **La ventaja se lee sin color**, por la dirección de la persiana, y antes
   del primer turno, que es lo que hace bien el referente de EarthBound.
4. **Riesgo que se asume:** que la alerta por la sombra estirada no se lea a
   480 × 270. Se mide en el paso del componente clave. Si no se lee, se para y
   se pregunta; no se cambia por cuenta propia.

---

## Contrato «Persiana» — BLOQUEADO 2026-10-28

Diego eligió la **dirección A** el 2026-10-28. Desde aquí se cumple. Nada de
color, duración, velocidad ni efecto fuera de lo que sigue; si algo no
funciona, se para y se pregunta.

### 1. El monstruo en el mapa (IA-1)

| Estado | Qué hace | Cómo se lee sin color |
|---|---|---|
| Patrulla | Anda una ruta corta de su zona a `WALK_SPEED`, con pausas de `MONSTER_PATROL_PAUSE` en cada extremo | Postura de reposo, mirando hacia donde anda |
| Alerta | Se para, se gira hacia Ilan y su sombra se estira hacia él, 1 tile cada `DUR_MONSTER_ALERT_STEP`, hasta `MONSTER_ALERT_STEPS` tiles | La sombra que avanza hacia Ilan |
| Persecución | Anda hacia Ilan a `WALK_SPEED` por A*, sin diagonales | Postura de ataque, adelantada |
| Se rinde | Sin ver a Ilan durante `DUR_MONSTER_GIVE_UP`, vuelve a su ruta | Vuelve la postura de reposo; la sombra se recoge |

- **Ve a Ilan** si está a ≤ `MONSTER_SIGHT_TILES` tiles, en el semiplano hacia
  el que mira y sin muro entre los dos (línea de Bresenham sobre la rejilla).
- **La zona** es el conjunto de casillas pisables de la zona de daño. La rejilla
  `AStarGrid2D` tiene sólido todo lo de fuera, así que no puede salir.
- **Velocidad:** la persecución va a `WALK_SPEED` y correr va a `RUN_SPEED`.
  Corriendo en línea recta, el monstruo nunca alcanza a Ilan.
- **Señal de alerta:** banda `EMBER_400` con filo `ASH_950` (**enmienda 1**,
  abajo; la sombra `ASH_950` original no llegaba a 3:1). **No hay color nuevo
  ni signo sobre la cabeza.**

### 2. El contacto y la ventaja

- El contacto es el solape de las cajas de colisión.
- **Quién empieza** se decide por la dirección:
  - Ilan toca la espalda del monstruo: **ventaja de Ilan**, y el grupo actúa
    en la primera ronda antes que el monstruo.
  - El monstruo toca la espalda de Ilan: **ventaja del monstruo**, y actúa
    primero.
  - De frente o de lado: **sin ventaja**, y el orden lo da la velocidad, como
    hoy.
- En la ventaja, la espalda es el semiplano opuesto a donde se mira.

### 3. La persiana (entrada al combate)

- Franjas horizontales de `BLIND_STRIP` px (8) en `ASH_950` cubren la pantalla
  de 480 × 270 en `DUR_BATTLE_BLINDS` (300 ms) con `ease-out`. Cada franja
  avanza en píxeles enteros.
- La primera franja que se cierra es **la de la fila del monstruo**. Las demás
  la siguen hacia arriba y hacia abajo. Entre la primera y la más lejana hay
  `BLIND_SPREAD` (100 ms), repartido por igual. Cada franja se cierra en los
  200 ms restantes, así que la última termina a los 300 ms, esté el monstruo
  donde esté.
- **El lado del que avanzan las franjas dice quién empieza:**
  - ventaja de Ilan: desde el borde del lado de Ilan;
  - ventaja del monstruo: desde el del monstruo;
  - sin ventaja: desde los dos bordes, que se juntan en el centro.
- Con la pantalla cubierta se carga el combate y la persiana **se abre** en el
  mismo tiempo y en el mismo sentido.
- **Movimiento reducido:** sin animación; corte directo con la pantalla
  cubierta durante `DUR_BATTLE_BLINDS`.
- **Exclusiva:** la persiana solo se usa para entrar al combate y salir de él
  (repertorio §3.1). El fundido sigue siendo solo para cambiar de zona.

### 4. El combate

- La pantalla «Ceniza y Brasa», sin cambios de composición.
- **El fondo de la región en tres capas** (la deuda pendiente del anexo de
  batalla), sacado de las rampas del tileset de esa región. El contraste baja
  bajo los paneles, como dice aquel contrato. El parallax es de
  `BATTLE_PARALLAX` px por capa, solo en la entrada. Con movimiento reducido,
  quieto.

### 5. La salida

- **Estado del grupo:** `GameState` guarda PV, energía, bolsa y estados
  alterados al entrar, y los actualiza al salir con el resultado exacto del
  combate.
- **Victoria:** persiana que se abre. Desde la casilla del combate sale la ola
  de purificación (`DUR_ZONE_PURIFY`, enmienda 3) y el paso cerrado se va.
- **Huida:** persiana que se abre. El monstruo sigue ahí y Ilan tiene
  `DUR_FLEE_GRACE` (1 s) sin contacto posible. El monstruo pasa a «se rinde».
- **Derrota:** fuera de alcance de esta parte. Hoy vuelve a la última llegada
  a la zona con el grupo a 1 PV; el guardado (parte 9) lo cambiará. Se anota.

### 6. Verificación que se escribe

- `tools/verify_encounters.gd`:
  - la ruta y la persecución nunca pisan fuera de la zona;
  - corriendo en línea recta, el monstruo no alcanza a Ilan;
  - cada transición de estado se fuerza y se comprueba;
  - la ventaja sale bien en los tres casos;
  - el estado del grupo antes y después coincide con el resultado;
  - la gracia de la huida dura 1 s.
- Hoja de la persiana cuadro a cuadro (patrón de `transition_sheet.gd`):
  duración medida, franjas en píxel entero, y el lado correcto en los tres
  casos.
- `verify_palette` sobre cada sprite nuevo: posturas, sombras y fondos.

### Orden de implementación

1. **Tokens.**
2. **Componente clave:** el monstruo con sus cuatro posturas y la sombra de
   alerta, medidos a 480 × 270.
3. **Esqueleto:** IA-1 en el mapa, contacto y ventaja.
4. **Resto:** la persiana, el paso de `GameState` y la vuelta con huida y
   ola.
5. **Pantalla completa:** fondos regionales en el combate.
6. **Estados:** huida, victoria, derrota y movimiento reducido.

### Registro

#### Paso 1 — Tokens · 2026-10-28

Tokens nuevos en `src/ui/design_tokens.gd`, sección «Encuentros». Ningún color
nuevo: la sombra y la persiana usan `ASH_950`. Las velocidades son las de
siempre (la regla de múltiplos de 60 px/s).

#### Paso 2 — Componente clave: el monstruo y la señal de alerta · 2026-10-28

**Cláusulas:** contrato §1 (cuatro estados que se leen sin color) y el riesgo
de la recomendación («que la alerta no se lea a 480 × 270: se mide»).

- **Posturas.** `posed()` en `tools/gen_world_decor.py` saca dos posturas del
  dibujo de reposo de cada monstruo: **alerta**, erguido 1 px, y
  **persecución**, adelantado 3 px en lo alto de su silueta y agachado 1 px.
  «Se rinde» vuelve al reposo. Lienzo de 20 × 24 y el mismo pie.
- **Medido** (`tools/verify_monster_poses.py`, solo la máscara, sin color):
  - persecución frente a reposo, solape entre 0,70 y 0,78 (tope 0,80) en los
    seis;
  - la alerta, más alta en los seis;
  - las tres posturas pisan la misma fila.
- **Primer fallo, y se dice:** con la inclinación medida sobre el lienzo, el
  Devorador de Petróleo, bajo y ancho, daba un solape de 0,83. Pasó a medirse
  sobre el alto real de cada silueta.
- **La señal de alerta, medida sobre el render** (`tools/monster_sheet.gd`:
  contraste de luminancia de la señal frente al mismo sitio en reposo):
  - **con la sombra `ASH_950` del contrato no llegaba al piso de 3:1 en
    ninguna región** (1,39-2,32:1), porque el suelo enfermo es oscuro;
  - se probó la brasa: `EMBER_400` pasa en cinco regiones (3,73-4,62:1) y no
    en la Cripta (2,61:1);
  - se paró y se preguntó.
- **Otro fallo de la propia hoja, y se dice:** la primera pasada daba 1,00:1
  en todo, porque la sombra se dibujaba debajo del suelo (`z_index -1`). Y la
  primera prueba con brasa daba cifras idénticas, porque Godot seguía usando la
  textura importada antes. Las dos se repitieron.

### Enmienda 1 — la señal de alerta, autorizada por Diego el 2026-10-28

- La sombra de alerta pasa a ser una **banda de 3 px en `EMBER_400`** (el
  aviso del repertorio §3.1) **con 1 px de filo `ASH_950`** debajo. En
  vertical, el filo va a la derecha. Sigue sin haber color nuevo. Avanza hacia
  Ilan, así que no se lee solo por el color.
- **Excepción de la Cripta**, autorizada el mismo día: sobre su losa de valor
  medio, ninguna tinta autorizada llega a 3:1. Lleva **filo de 2 px**. Se mide
  y se imprime como «EXCEPCIÓN», no como OK.

**Medido con la enmienda** (brasa · filo):

| Región | Brasa | Filo |
|---|---|---|
| Bosque | 4,54:1 | 1,57:1 |
| Cuenca | 3,49:1 | 1,73:1 |
| Costa | 3,78:1 | 1,56:1 |
| Llanura | 3,77:1 | 1,47:1 |
| Cumbre | 3,88:1 | 1,57:1 |
| Cripta | 2,51:1 | 2,18:1 — **excepción, bajo el piso** |

- En la Cripta, el filo de 2 px **midió menos que el de 1 px** (2,18 frente a
  2,63:1). La fila de más cae sobre juntas más claras. No mejora el contraste,
  solo el peso de la señal. Se deja dicho.
- `verify_palette --world` sobre los 16 sprites nuevos: todo píxel es un token.

**Capturas:** `docs/ux/capturas/2026-10-28-<región>-monstruo-reposo.png`,
`-alerta.png` y `-persecucion.png`, de las seis regiones.

**Siguiente:** paso 3, el esqueleto. IA-1 en el mapa (patrulla, alerta,
persecución y rendición con A* encerrado en la zona), el contacto y la
ventaja, con `tools/verify_encounters.gd`.

#### Paso 3 — Esqueleto: IA-1 en el mapa, contacto y ventaja · 2026-10-28

**Cláusulas:** contrato §1 (estados, visión, zona y velocidad) y §2 (contacto
y ventaja).

- **`src/world/map_monster.gd`** (`MapMonster`):
  - máquina de cuatro estados;
  - `AStarGrid2D` con todo sólido salvo su territorio, sin diagonales;
  - 1 px por cuadro, eje a eje;
  - visión por distancia, semiplano y línea de Bresenham sin sólidos;
  - contacto por cajas que se tocan, y ventaja por la espalda.
- **`WorldRoot`:** mientras la zona está enferma, cambia el sprite fijo del
  monstruo por el `MapMonster`, que lleva su cuerpo entre los sólidos. Al
  tocarlo, Ilan se para y el mundo emite `encounter(ventaja)`. La persiana va
  en el paso 4.
- **Decisión de la sesión, pendiente del visto bueno de Diego:** el contrato
  no fija cuánto mide el territorio. Para no inventar un valor, usa
  `MONSTER_SIGHT_TILES`: las casillas libres a ≤ 6 pasos ortogonales del
  puesto. Mide entre 42 casillas (Cuenca) y 79 (Cripta).
- **Ruta de patrulla:** del puesto a 2 tiles en la primera dirección libre,
  ida y vuelta.

**Medido** — `tools/verify_encounters.gd`: **82 de 82**.

- Ventaja en los tres casos, más el de lado.
- En las seis regiones:
  - territorio pisable y ruta dentro de él;
  - 900 cuadros con Ilan rondando, sin salir nunca del territorio;
  - patrulla → alerta de frente, y nada a la espalda;
  - alerta → persecución en **28 cuadros** (4 × 7);
  - persecución → se rinde en **120 cuadros** sin verlo;
  - se rinde → patrulla al llegar a su ruta;
  - Ilan corriendo en línea recta (82-178 px) sin que la distancia baje nunca;
  - contacto real por la espalda del monstruo, que da ventaja a Ilan;
  - con gracia, sin contacto.
- **La primera pasada dio 68 de 82, y los tres errores eran de la prueba:**
  - Ilan corría más allá de la línea libre, chocaba y se paraba;
  - el contacto se probaba a 13 px, y con un monstruo sólido no se llega a
    menos de 12;
  - la línea de la Cuenca tenía un barril sólido que la prueba no miraba.
- **Regresión en verde:** `verify_zone` en las siete zonas, `verify_movement`
  99/99, `verify_usability` 16/16 y `verify_camera` 37/37.
- **`tools/monster_sheet.gd`** mide ahora el componente real y no una
  maqueta. Brasa: 4,61 · 3,49 · 4,13 · 3,75 · 4,91:1. Cripta 2,60:1, la
  excepción ya autorizada. Las capturas `-monstruo-*.png` se regeneraron con
  él.

**Siguiente:** paso 4. La persiana con su ventaja, el paso a «Ceniza y
Brasa» con el grupo en `GameState`, y la vuelta al mapa con huida (1 s de
gracia) y victoria (la ola).

Diego aprobó el paso 3 el 2026-10-28, **territorio de 6 tiles incluido**.

#### Paso 4 — La persiana, el grupo y la vuelta · 2026-10-28

**Cláusulas:** contrato §2 (ventaja), §3 (persiana) y §5 (salida).

- **`src/world/battle_blinds.gd`** (`BattleBlinds`):
  - 34 franjas de 8 px en `ASH_950`;
  - empieza la de la fila del monstruo y las demás la siguen, repartidas en
    `BLIND_SPREAD`;
  - cada franja va con `ease-out` y en píxeles enteros;
  - entra desde el lado de Ilan, desde el del monstruo o desde los dos;
  - al abrir, se recoge hacia el mismo borde;
  - se cuenta en cuadros de física.
- **`src/core/game_flow.gd`** (`GameFlow`):
  - contacto → persiana → mundo parado y oculto → «Ceniza y Brasa» con el
    grupo y la bolsa de `GameState` y el monstruo de la región → persiana
    abierta;
  - al confirmar el desenlace, el camino inverso.
- **La ventaja llega al combate.** `BattleManager.opening_team` y
  `TurnManager.prioritize()` adelantan al equipo entero en la primera ronda,
  sin romper su orden por velocidad. La composición de «Ceniza y Brasa» no
  cambia, solo el orden.
- **`GameState.ensure_party()`:** el grupo vive en `GameState` entre combates.
  Los que ya viajaban conservan PV, energía y estados, y la bolsa se llena la
  primera vez. Quién se une dónde sigue siendo de la parte 6.
- **La vuelta al mapa:**
  - **huida:** el monstruo se rinde y hay 1 s de gracia;
  - **victoria:** `purified_<zona>` y la zona repintada, sin monstruo;
  - **derrota:** a `arrival_cell` con el grupo a 1 PV.

**Medido** — `tools/verify_flow.gd`: **23 de 23**.

- **Persiana, en los tres lados:**
  - cerrar y abrir en **18 cuadros** (300 ms);
  - cubre las 34 franjas a 480 px;
  - la fila del monstruo va siempre por delante y nada retrocede.
- **Con movimiento reducido:** cubierta en el primer cuadro y 18 de espera.
- **Ventaja:** abre el equipo con ventaja aunque sea más lento.
- **Paso completo:** el mundo parado y oculto, y el grupo de `GameState`.
  - Huida: monstruo rendido, **60 cuadros de gracia** y PV conservados.
  - Derrota: vuelta a la casilla de llegada con 1 PV.
  - Victoria: zona purificada y sin monstruo.
- **Un fallo real, y se dice:** la gracia de la huida empezaba a contar con la
  persiana aún abriéndose; se perdían 18 de los 60 cuadros tras la cortina.
  Ahora el monstruo se suelta cuando el mundo se ve entero.
- **Regresión en verde:** `verify_encounters` 82/82, `verify_movement`
  99/99, `verify_usability` 16/16, `verify_camera` 37/37 y `verify_zone` en
  Valdehoja, Bosque y Cripta. `battle_demo` sin errores.

**Capturas** (`tools/blinds_sheet.gd`): `2026-10-28-persiana-ventaja-ilan.png`,
`-ventaja-monstruo.png` y `-sin-ventaja.png`, en el cuadro 9 de 18, y
`2026-10-28-combate-desde-el-mapa.png`. En esta última, la tira de turnos ya
abre con Ilan.

**Pendiente, y se dice:**

- **La ola de purificación animada.** Hoy la victoria repinta la zona entera
  de golpe. La ola (tramado 4 × 4 desde el punto del combate, 900 ms,
  enmienda 3) va en el paso 6, con los estados.
- **La escena principal** sigue abriendo el selector de región de pruebas.
  Arrancar el juego en el mundo con `GameFlow` es de la parte 10 (título),
  como ya decía la guía. Para jugarlo hoy: `GameFlow` en una escena con
  `start_zone`.

**Siguiente:** paso 5, el fondo de cada región en tres capas dentro de
«Ceniza y Brasa».

Diego aprobó el paso 4 el 2026-10-28.

#### Paso 5 — El fondo de cada región en el combate · 2026-10-28

**Cláusula:** contrato §4. Es la deuda del anexo de batalla, que dejaba el
campo en dos bandas planas.

- **`BattleScreen.region`:** con región, el campo se pinta en tres capas, siempre
  en el estado enfermo de la región (se lucha contra la causa):
  - **lejos:** la silueta propia de la región en `ASH_700` contra el cielo de
    ceniza: troncos quemados con ramas (Bosque), torres y tubería (Cuenca),
    montones de basura (Costa), silo e hileras (Llanura), picos con la cima en
    `ASH_600` (Cumbre) y columnas bajo un dintel (Cripta);
  - **medio:** la franja de su material: tierra, crudo, orilla, cultivo seco,
    roca o losa;
  - **cerca:** el material en su tono más oscuro, con vetas `ASH_950`, para
    que el contraste baje junto a los paneles.
- Sin región, el fondo genérico de antes: la demo y las pruebas viejas no
  cambian.
- **Parallax de entrada:** la capa *k* entra desplazada *k* ×
  `BATTLE_PARALLAX` px y llega a su sitio con `ease-out` mientras se abre la
  persiana. Con movimiento reducido, quieta.
- `GameFlow` pasa la zona del combate, y la demo del selector, la de su
  región.

**Medido** — `tools/battle_bg_sheet.gd`:

- **Parallax:** la capa cercana sale a 6 px y llega a 0 en 12 cuadros (≤ 18),
  sin retroceder. Con movimiento reducido, 0 desde el primer cuadro.
- **El monstruo se lee sobre su fondo:** borde `EMBER_300` frente al tono más
  claro del campo junto a él: Bosque 5,04 · Cuenca 5,58 · Costa 4,18 ·
  Llanura 4,44 · Cumbre 5,58 · Cripta 5,58:1 (piso 3:1).
- `verify_palette image` sobre las seis capturas: todo píxel es un token.
- **Regresión:** `verify_usability` 16/16, `verify_flow` 23/23 y
  `battle_demo` sin errores.

**Capturas:** `docs/ux/capturas/2026-10-28-combate-fondo-<región>.png`, las
seis.

**Siguiente:** paso 6, los estados. La ola de purificación animada al ganar
(tramado 4 × 4 desde el punto del combate, 900 ms, enmienda 3), y un repaso
de huida, derrota y movimiento reducido con capturas.

Diego aprobó el paso 5 el 2026-10-28.

#### Paso 6 — Estados: la ola de purificación y el repaso · 2026-10-28

**Cláusulas:** contrato §5 (victoria → ola desde el punto del combate) y la
enmienda 3 del contrato de exploración (tramado 4 × 4, 900 ms, exclusivo).

- **`WorldRoot.purify_wave(celda)`:**
  - el suelo purificado se pinta en una capa encima del enfermo;
  - `src/world/purify_wave.gdshader` lo descubre píxel a píxel: cuando el
    frente toca un píxel, pasa en el paso ⌊Bayer/2⌋ de los ocho
    (`PURIFY_DITHER_STEPS`) de una banda de medio tile;
  - la matriz `BAYER_4X4` y los pasos llegan desde `DesignTokens` como
    uniformes;
  - el frente recorre la pantalla visible en `DUR_ZONE_PURIFY`;
  - al terminar, `purified_<zona>` y la zona se monta entera, con decorado y
    fauna purificados;
  - con movimiento reducido, de golpe.
- **`GameFlow`, al ganar:** el monstruo desaparece con el combate, la persiana
  se abre sobre la zona aún enferma y la ola sale de la casilla donde se le
  tocó.

**Medido** — `tools/verify_wave.gd`: **6 de 6** (7 de 7 con el decorado pieza a pieza, abajo).

- Dura **54 cuadros de física** (900 ms).
- **Ningún píxel mezclado:** en cada cuadro, todo píxel del suelo es el
  enfermo o el purificado de su sitio (0 fuera).
- Lo purificado crece y nunca vuelve atrás.
- A media ola: 100 % purificado cerca del origen y 0 % lejos.
- Al terminar, la zona queda purificada y montada.
- Con movimiento reducido, de golpe (0 cuadros).

**Dos fallos de la prueba, y se dicen:**

- contaba cuadros de render, que dependen del refresco de la ventana, y no de
  física (dio 67);
- la referencia purificada incluía el decorado purificado, así que bajo cada
  copa contaba como «mezcla» lo que era suelo correcto (39 528 píxeles). Se
  mide sin decorado ni agua animada, y la captura se saca aparte, con todo
  visible.

**Repaso de estados.** Huida (gracia y rendición), derrota (llegada y 1 PV),
victoria (ola) y movimiento reducido (persiana, parallax y ola) están medidos
en `verify_flow` (23/23), `battle_bg_sheet` y `verify_wave`.

**Regresión en verde:**

| Prueba | Resultado |
|---|---|
| `verify_encounters` | 82/82 |
| `verify_movement` | 99/99 |
| `verify_usability` | 16/16 |
| `verify_camera` | 37/37 |
| `verify_zone`, siete zonas | 55 · 46 · 45 · 46 · 45 · 45 · 48 |

**Captura:** `docs/ux/capturas/2026-10-28-ola-bosque.png`, a media ola.

**Pendiente, y se dice:**

- ~~El decorado no cambia con el frente.~~ **Resuelto el mismo día, a
  petición de Diego («pieza a pieza»):** cada árbol, mata o roca pasa a
  purificado (o desaparece, si es daño) en el cuadro en que el frente llega a
  su pie. `verify_wave` lo mide: **0 desfases en 46 644 comprobaciones**,
  7 de 7. La captura `2026-10-28-ola-bosque.png` lo muestra a media ola: copas
  verdes dentro del frente y troncos quemados fuera.
- **La fauna en bandada al purificar (IA-2)** no está: es de la parte 3
  según la guía y quedó sin hacer. Se anota como deuda.

Diego aprobó el paso 6 el 2026-10-28 y pidió seguir con IA-4 e IA-5.

---

## IA-4 · Bot de equilibrado — 2026-10-28

Herramienta de desarrollo, sin interfaz: no lleva dirección de diseño, solo
criterio medido (guía §3.3).

- **`tools/balance_bot.gd`**, sin ventana y con semilla fija `20261028`:
  - 300 combates por región y por política;
  - un CSV por región en `docs/balance/2026-10-28-<región>.csv`, una fila por
    combate (resultado, rondas y habilidades usadas);
  - la tabla Q de la Sombra, entrenada encadenando sus combates, en
    `data/balance/sombra_q.json`.
- **Políticas:**
  - **aleatoria:** cualquier acción;
  - **voraz:** el grupo repite solo la contramedida del fuego;
  - **experta:** cura bajo el 45 %, ataja la causa y, contra la Sombra,
    combina las que no ha usado.
- **Un error mío, y se dice:** la primera voraz usaba la primera habilidad
  ofensiva *de cada personaje*. Con cinco personajes eso suma cinco
  contramedidas, justo lo que la Sombra exige, y ganaba 300 de 300. Se
  corrigió a «el grupo repite una sola», que es lo que dice la guía.

**Medido** (victorias de 300 · rondas de media):

| Región | Aleatoria | Voraz | Experta |
|---|---|---|---|
| Bosque | 298 · 12,4 | 299 · 6,6 | **300** · 9,1 |
| Cuenca | 300 · 9,9 | 0 · 20,5 | **300** · 5,9 |
| Costa | 300 · 9,9 | 0 · 25,9 | **300** · 7,6 |
| Llanura | 290 · 10,5 | 0 · 13,4 | **300** · 6,0 |
| Cumbre | 297 · 8,7 | 0 · 11,6 | **300** · 6,9 |
| Cripta | 299 · 12,3 | **0** · 28,1 | **300** · 9,2 |

- **Criterio 1, la experta gana siempre:** OK en las seis regiones.
- **Criterio 2, la voraz pierde contra la Sombra:** OK, 0 de 300.
- En el Bosque, la voraz es la experta: el fuego *es* la contramedida.

**Hallazgo, y se le lleva a Diego:** **la aleatoria gana entre el 97 y el
100 % en todas las regiones, también contra la Sombra.** Pulsar al azar
termina usando la contramedida, porque las acciones posibles son pocas. El
mensaje «hay que atajar la causa» no se impone a quien juega sin pensar. Solo
lo nota en las rondas: tarda entre 1,4 y 2 veces más que la experta.

---

## IA-5 · Sintonía del grupo — fases 1 a 3 · 2026-10-28

**Comunicación.** Hoy el jugador elige la acción de cada personaje. IA-5
(guía §3.3, aprobada el 2026-09-30) quiere que sea **el líder**: los
compañeros actúan por su cuenta según lo que vean hacer a Ilan, aprendido con
una red pequeña, y la *sintonía* (de 0 a 1) mide la calidad del liderazgo.

- **Decisión dominante del jugador:** *¿cómo llevo al grupo esta ronda?*
- **Lo que no puede faltar:** que se vea que es él quien arrastra al grupo
  (regla 1 de IA-5: «un castigo que no se entiende es un error»).

**Investigación** (`observación → decisión → límite`):

1. **Dragon Quest, IA del grupo** (Dragon Quest Wiki):
   https://dragon-quest.org/wiki/Artificial_Intelligence
   → Tácticas por personaje («Lucha con cabeza», «Sin piedad», «Cura
   primero»…); la IA decide al empezar el turno de cada uno; «Sigue mis
   órdenes» devuelve el control. → Una orden con nombre, elegida de una lista
   corta, es legible. La decisión al inicio del turno usa el estado real. →
   No copio la lista larga ni la opción de volver al control total en cada
   combate: anularía la idea del líder.
2. **«Dragon Quest's Tactics system…»** (Boss Rush, 2026-02-19):
   https://bossrush.net/2026/02/19/boss-rush-banter-dragon-quests-tactics-system-is-the-secret-to-grander-immersion-and-faster-combat
   → Llevar solo al protagonista se siente «más cerca de la acción», como
   luchar junto a los compañeros y no mirarlos desde arriba, y el combate va
   más rápido. → Apoya que el jugador lleve solo a Ilan. → El autor no recoge
   frustraciones porque la serie es indulgente; aquí la sintonía sí castiga, y
   por eso la influencia tiene que verse.
3. **Katano sobre los gambits de FFXII** (Game Developer):
   https://www.gamedeveloper.com/design/why-i-final-fantasy-iv-i-was-key-to-i-ffxii-i-s-ai-driven-gambit-system
   → Elegir cada comando de 3-4 personajes «habría estropeado la diversión»:
   se cede el control a una IA con condiciones asignadas. → Con cinco
   personajes, el menú por personaje de hoy es la carga que el referente
   evita. → No copio los gambits: programar condiciones es otro juego y otra
   interfaz entera.
4. **Reseña de FFXII: The Zodiac Age** (RPG Site):
   https://www.rpgsite.net/review/5777-final-fantasy-xii-the-zodiac-age-review
   → «Casi como si el jugador programara el combate a distancia»: divide a
   los jugadores, porque no se controla al personaje ni se elige del menú. →
   El riesgo es la distancia. Mantener a Ilan en mano directa evita que el
   jugador quede solo como espectador. → No copio el modelo de distancia
   total.
5. **Game Accessibility Guidelines** (ya en la fase 3 de este anexo): nada
   esencial solo por color, y que la precisión no sea esencial. → La reacción
   de un compañero («Coral duda») va en texto, en el registro. Y el modo de
   sintonía neutra de opciones (regla 3 de IA-5) se mantiene.

**Fuentes de pantalla de Diego:** como en la fase 3, son catálogos web y no
aplican a un sistema de combate. La de FFXII en Fandom
(https://finalfantasy.fandom.com/wiki/Gambit) **no se pudo abrir el
2026-10-28** (HTTP 402).

## IA-5 — fase 4: direcciones (pendiente de elección de Diego)

Las tres respetan las reglas de IA-5: la red aprende de Ilan, la sintonía
existe, la influencia se ve en texto y hay un modo neutro en opciones.

- **A · «El líder»** (literal de la guía). El jugador maneja **solo a
  Ilan**. Cada compañero decide con su red, que imita a Ilan, y la sintonía
  le da precisión. Cada acción de compañero deja en el registro su motivo
  corto («Coral sigue a Ilan: Barrera Absorbente»).
  - *Gana:* es la idea de Diego tal cual, y es el combate más rápido.
  - *Cuesta:* la única palanca del jugador es su propio turno. La influencia
    llega lenta, y con la sintonía baja puede sentirse opaca.
  - *Enmienda:* el menú de acción solo para Ilan.
- **B · «Líder con orden»** — recomendada. Como A, y además, en el turno de
  Ilan, **una orden de grupo** de tres: *Seguidme* (imitan a Ilan), *Atajad
  la causa* (prioridad a la contramedida) y *Cubríos* (curar y defender).
  - La orden sesga la red; la sintonía decide cuánto aciertan al cumplirla.
  - Es una fila más en el menú de Ilan, con el mismo estilo: no hay
    componente nuevo.
  - *Gana:* el jugador orquesta en cada ronda y ve el efecto en esa misma
    ronda, sin volver a manejar a cinco (Dragon Quest con lista corta, FFXII
    sin programar).
  - *Cuesta:* una decisión más por ronda.
  - *Enmienda:* el menú de acción solo para Ilan, más la fila de orden.
- **C · «Propuesta del compañero»** (sin enmienda). El jugador sigue
  manejando a los cinco, pero el menú de cada compañero se abre con el cursor
  en lo que propone su red. La sintonía se ve en lo buenas que son las
  propuestas.
  - *Gana:* no toca el contrato y no hay pérdida de control.
  - *Cuesta:* el jugador deja de ser el líder y la IA pasa a ser una
    sugerencia. Además, no resuelve la carga de elegir cinco menús por ronda.

**Recomendación: B.** Es la única en la que la decisión dominante («cómo
llevo al grupo esta ronda») tiene una palanca inmediata y legible. A deja esa
palanca en un efecto lento que la regla 1 de IA-5 teme. C renuncia a la idea
de Diego.

---

## Lo que queda abierto en esta parte (se decide después de la dirección)

- **IA-5, primera mitad:** enmienda del contrato de batalla para que el
  jugador maneje solo a Ilan, comparada con la «orden de líder» por ronda
  (guía §3.3). Va en su propia pregunta, con su fase de comunicación.
- **IA-4:** bot de equilibrado en `tools/balance_bot.gd`. Es una herramienta
  sin interfaz: no necesita dirección, solo criterio medido.
- **Tokens nuevos** que pedirá cualquier dirección: velocidad y radios de
  IA-1, duración de la persiana y de la gracia. Van a `DesignTokens` con la
  dirección elegida.
