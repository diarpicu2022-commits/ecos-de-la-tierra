# Ecos de la Tierra — instrucciones para Claude

RPG 2D por turnos en Godot 4 + GDScript. Proyecto de Diseño de Interfaces de
Software: **se evalúa el criterio de diseño, no solo que funcione.**

## Antes de tocar nada, en este orden

1. Lee `docs/plan-de-trabajo.md`. Dice qué parte está en curso y cuál es el
   siguiente paso exacto. **No explores el repositorio entero.**
2. Lee `docs/guia-de-continuacion.md`: §1 (protocolo), §2 (identidad), §3
   (repertorio y propuestas pendientes) y la sección de §5 de la parte que
   toca. Ahí está todo el método de diseño; no necesitas ninguna skill externa.
3. Del anexo de la pantalla en curso (`docs/ux/anexos/`), lee solo la sección
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
  escenas de `tools/verify_*.tscn` y capturas a 480×270. Informa también de lo
  que falla.
- Código en inglés; textos de jugador y comentarios en español.
- **Sin firma de herramientas** en commits, PR, código ni documentación: nada de
  `Co-Authored-By: Claude` ni «Generated with Claude Code».
- **Al cerrar la sesión:** actualizar `docs/plan-de-trabajo.md` y hacer commit.
- PR con la plantilla de la guía §1.6 y capturas reales.
