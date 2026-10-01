# Hoja de pruebas con personas — 2026-10-01

Dos pruebas pendientes, hechas en **una sola sentada por persona**, con las
mismas **tres personas**. La guía (§4) pide la primera **antes de la parte 3**:
si falla, cambia cómo se diseñan las siete zonas. La segunda cierra la parte 1.

| | Prueba | Qué decide | Dónde se registra |
|---|---|---|---|
| A | «¿Por qué pierdo?» en el combate del Bosque | Si la pantalla de batalla enseña sola que hay que atajar la causa. Si no, las zonas de la parte 3 tienen que enseñarlo antes. | Anexo de batalla, fase 6, fila «¿Por qué pierdo?» |
| B | Nombrar el material de 10 recortes | Si la separación dE 9,2 entre suelo, camino, agua y follaje basta, o hace falta la enmienda 6 | Anexo de exploración, fase 5, paso 2b |

**Orden: primero A, luego B.** La A necesita a alguien que no sepa nada del
juego. La B no revela nada del combate, pero el combate sí podría contaminar la
B si se hiciera al revés: el tileset sale en el fondo del combate.

---

## Quién vale

- Personas que **no hayan visto el juego** ni hablado de él con el equipo.
- Que jueguen o hayan jugado algún RPG o videojuego con teclado; no hace falta
  que sean del perfil exacto (14–30 años), pero anota la edad aproximada.
- **No** vale nadie del equipo, ni quien haya visto capturas en los PR.

## Antes de empezar (una vez)

1. Abre el proyecto en Godot 4.7.2 y comprueba que **F5** abre el selector de
   región.
2. Ten a mano esta hoja impresa o en otra pantalla **que la persona no vea**.
3. Cronómetro (el del móvil vale).
4. Si `project.godot` aparece modificado después de abrir el editor, descártalo
   antes de cualquier commit (`git checkout project.godot`).

---

## Prueba A — «¿Por qué pierdo?»

### Qué se dice a la persona (literal, y nada más)

> «Es un juego de rol por turnos. Muévete con las flechas, confirma con Enter y
> vuelve atrás con Escape. Elige la primera región. Juega como quieras; yo no
> puedo ayudarte. Si quieres, piensa en voz alta.»

**No expliques** qué es la purificación, qué significa el verde, quién es Bruma
ni qué hace ninguna habilidad. Si pregunta, responde: «Haz lo que harías tú».

### Qué haces tú

1. F5 → la persona elige **Bosque de las Cenizas** (la primera opción).
2. Pon el cronómetro en marcha cuando aparezca el combate.
3. Anota mientras juega, sin intervenir.
4. Para la prueba cuando el combate acabe (victoria, derrota o huida) o a los
   **10 minutos**.
5. Al final, una sola pregunta: **«¿Por qué crees que ganaste / perdiste?»**
   Anota la respuesta literal.

### Qué tiene que descubrir (no se lo digas)

La Llama de la Deforestación **se rehace** mientras no se ataje la causa: el
ataque normal casi no le hace nada. Solo la **Línea Cortafuegos** de **Bruma**
(una Habilidad Ecológica) la purifica. Ilan no la tiene; Bruma sí.

### Hoja por persona

| Dato | Persona 1 | Persona 2 | Persona 3 |
|---|---|---|---|
| Edad aproximada / juega RPG (sí/no) | | | |
| ¿Usó la Línea Cortafuegos? (sí/no) | | | |
| Turno en que la usó por primera vez | | | |
| ¿La usó **antes** de ver la pantalla de derrota? | | | |
| Desenlace (victoria / derrota / huida / 10 min) | | | |
| Veces que el monstruo se rehízo (lo dice la pantalla final) | | | |
| Tiempo total | | | |
| Lo que dijo en voz alta (literal, lo más relevante) | | | |
| Respuesta a «¿Por qué crees que ganaste / perdiste?» | | | |

### Criterio

- **Llega** si al menos **2 de 3** usan la Línea Cortafuegos **antes de perder
  por primera vez** y su respuesta final menciona la causa (el fuego, la tala,
  «había que cortar el fuego», «se curaba»).
- **No llega** en cualquier otro caso. Entonces las zonas de la parte 3 tienen
  que enseñar la causa **antes** del combate (el paisaje del Bosque, los
  tocones, el humo), y eso se decide en la fase 4 de su anexo.

---

## Prueba B — Nombrar el material

### Qué se dice a la persona (literal)

> «Te voy a enseñar diez cuadraditos de un mapa. En cada uno, dime de qué es el
> centro: **suelo, camino, agua o follaje**. Una palabra, lo primero que veas.»

Enséñale los recortes **en orden**, de `docs/ux/prueba-materiales/recorte-01.png`
a `recorte-10.png`, a pantalla completa y **sin la clave a la vista**.

### Hoja por persona

| Recorte | Persona 1 | Persona 2 | Persona 3 |
|---|---|---|---|
| 01 | | | |
| 02 | | | |
| 03 | | | |
| 04 | | | |
| 05 | | | |
| 06 | | | |
| 07 | | | |
| 08 | | | |
| 09 | | | |
| 10 | | | |
| Aciertos | /10 | /10 | /10 |

La clave está en el anexo de exploración (fase 5, paso 2b). **Corrígelo
después**, no delante de la persona.

### Criterio (enmienda 1 del anexo de exploración)

- **Basta** si las **tres** aciertan los 10.
- **No basta** con un solo fallo. Anota qué materiales confundió y en qué
  estado (enfermo o purificado). Diego decide la enmienda 6.

---

## Después

Pásale los resultados a quien continúe la sesión (o pégalos en el chat). Se
registran en los anexos con fecha, **incluidos los fallos**, y la prueba A
decide la fase 4 del anexo de la parte 3.
