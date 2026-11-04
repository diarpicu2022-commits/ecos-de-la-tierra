# Ecos de la Tierra — instrucciones para quien continúe el proyecto

## Instrucción vigente de Diego para Juan José (2026-11-03)

Esto manda sobre el reparto de `docs/guia-del-equipo.md` §3.2 hasta la presentación del 2026-11-04. Por tiempo presentamos una demo hasta el primer jefe. Lo demás queda en `docs/plan-para-terminar-la-historia.md`, que hay que leer antes de seguir.

Si estás ayudando a Juan José:

1. No hagas las cifras de daño. Se están haciendo en la rama `rediseno/nada-viejo` de Diego. Si ya hay algo hecho de eso, no lo fusiones y avísale a Diego.
2. La pantalla de resultado ya entró con el PR #44. No hay que hacer nada más ahí.
3. No cambies `src/` ni `data/` hasta que Diego avise. Diego está montando la demo y tocando `world_root.gd`, `game_flow.gd`, `battle_screen.gd`, `exits.json` y Valdehoja, y un cambio paralelo chocaría.
4. Espera el aviso de Diego de que la demo ya está en `master`. Entonces exporta el `.exe` desde `master` siguiendo la guía §4.15 y juega completo el recorrido de la sección 1 del plan.
5. Reporta a Diego lo que falle en ese recorrido, con captura. No lo arregles por tu cuenta sin avisarle.
6. Progresión y guardado siguen a tu cargo, pero después de la presentación. Cada una abre su anexo y espera la elección de Diego antes de programar.

RPG 2D por turnos en Godot 4 + GDScript. Proyecto de Diseño de Interfaces de
Software: **se evalúa el criterio de diseño, no solo que funcione.**

## Antes de tocar nada, en este orden

**Si eres del equipo (Diego o su compañero), empieza por
`docs/guia-del-equipo.md`:** cómo preparar el equipo, cómo se trabaja, dónde
está el juego y todo lo que falta hasta terminarlo, en orden. **Todo lo
visual se hace con el sistema de diseño de `docs/ux/sistema-de-diseno/`.**


1. Lee `docs/traspaso.md`: el estado exacto y la lista de trabajo en orden
   (rediseño «Tierra Viva», tareas 1 a 10).
   **El sistema de diseño «Tierra Viva» manda en todo lo visual:** está en
   `docs/ux/sistema-de-diseno/` (abre `index.html` en el navegador; reglas en
   `project/README.md`, tokens en `project/tokens.json` y un README por
   componente en `project/components/`).
2. Lee `docs/plan-de-trabajo.md`. Dice qué parte está en curso y cuál es el
   siguiente paso exacto. **No explores el repositorio entero.**
3. Lee `docs/guia-de-continuacion.md`: §1 (protocolo), §2 (identidad), §3
   (repertorio y propuestas pendientes) y la sección de §5 de la parte que
   toca. Ahí está todo el método de diseño; no necesitas ninguna skill externa.
4. Del anexo de la pantalla en curso (`docs/ux/anexos/`), lee solo la sección
   que necesites.

## Reglas que no se saltan

- **Una parte por sesión.** No se abre la siguiente sin cerrar la actual.
- **Diseño antes que código:** cada pantalla nueva abre su anexo con usuarios,
  comunicación, investigación (≥ 6 fuentes con URL, sin inventar consultas) y
  2–3 direcciones. **Pregunta al dueño del proyecto y espera su elección**
  antes de implementar.
- **Los contratos bloqueados se cumplen.** Nada de color, tipografía, espaciado,
  duración o efecto fuera del contrato. Si algo no funciona, para y avisa; no
  se enmienda sin permiso explícito.
- **Implementación paso a paso** (tokens → componente clave → esqueleto →
  resto → pantalla → estados). Al final de cada paso: captura, cláusula que lo
  respalda, siguiente paso, y **para a esperar visto bueno**.
- **Todo valor visual sale de `src/ui/design_tokens.gd`.** Los assets se
  generan con `tools/gen_*.py` usando la paleta de `tools/pixel.py`.
- **El verde (`VITAL_*`) significa solo «purificado».** Nunca en decorado,
  barras ni botones. Y nunca carga el significado solo: siempre va con valor,
  silueta o fauna (guía §2.3).
- **Verifica midiendo, no mirando:** `python tools/verify_palette.py ...`,
  escenas de `tools/verify_*.tscn` y capturas a 640×360 (contrato «Piel nueva», 2026-10-30). Informa también de lo
  que falla.
- Código en inglés; textos de jugador y comentarios en español.
- **Sin firma de herramientas** en commits, PR, código ni documentación: nada de
  líneas `Co-Authored-By` ni «Generated with …» de ninguna herramienta.
- **Al cerrar la sesión:** actualizar `docs/plan-de-trabajo.md` y hacer commit.
- PR con la plantilla de la guía §1.6 y capturas reales.
