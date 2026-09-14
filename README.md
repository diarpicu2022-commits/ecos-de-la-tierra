# Ecos de la Tierra

RPG 2D por turnos con estética pixel art y enfoque de concienciación ambiental.
Godot Engine 4 + GDScript, exportable a PC y Android desde el mismo proyecto.

La propuesta completa (historia, personajes, regiones y justificación técnica)
está en `EcosDeLaTierra Propuesta Videojuego.md`.

El juego se construye **por partes, una por sesión**. Qué está hecho, qué toca
ahora y qué decisiones ya están cerradas: `docs/plan-de-trabajo.md`. Es lo
primero que conviene leer antes de tocar nada.

## Abrir el proyecto

1. Instalar **Godot Engine 4.3 o superior**, versión **estándar (no la .NET)**.
   La .NET solo añade soporte de C#, que este proyecto no usa —es todo GDScript—
   y encima exige instalar aparte el SDK de .NET.
   Verificado en 4.3 y en 4.7.2.
2. Abrir Godot → *Import* → seleccionar el archivo `project.godot` de esta
   carpeta.
3. Ejecutar con F5. La escena principal es `scenes/main.tscn`: abre el selector
   de región, desde el que se entra a cualquiera de los seis combates. Se juega
   con las flechas o WASD, Enter o Espacio para confirmar y Escape para volver
   atrás.
   La prueba de concepto por consola sigue disponible en
   `tools/console_demo.tscn` (F6 con esa escena abierta).

También se puede ejecutar sin abrir el editor, desde la carpeta del proyecto:

```
godot --headless --path . --quit-after 3
```

## La prueba de concepto

`scenes/main.tscn` ejecuta cuatro escenarios seguidos y los escribe por consola:

1. **Regla 1** — comprobación directa: se tira al monstruo a 0 PV sin la
   contramedida (se regenera) y después con ella aplicada (cae).
2. **Bosque de las Cenizas** — combate real: dos turnos de fuerza bruta y luego
   la Línea Cortafuegos. Termina en victoria.
3. **Llanura Marchita** — el Espectro del Monocultivo se multiplica y sus clones
   entran en la ronda en curso; hay que purificarlos uno a uno.
4. **Cripta de la Avaricia** — el mismo combate dos veces: repitiendo siempre la
   misma Habilidad Ecológica, el jefe aprende a resistirla (resistencia ~0,67 en
   su tabla Q) y el grupo tiene que retirarse; combinando las cinco, el jefe se
   purifica y el grupo gana.

## Qué hay implementado

- Clases base del combate por turnos, con la arquitectura descrita en `src/README.md`.
- **Sistema de debilidad ambiental**: los monstruos se regeneran mientras no se
  aplique la Habilidad Ecológica correcta.
- **IA de los monstruos** por pesos, y **tabla Q** del jefe final, que aumenta su
  resistencia a la habilidad que el jugador repite.
- Los cinco monstruos de región, el jefe final, los cinco personajes jugables,
  el catálogo de habilidades, los estados alterados y la Bolsa.
- Prueba de concepto por consola que verifica todo lo anterior sin interfaz.

## La interfaz de batalla

Diseñada siguiendo el proceso documentado en
`docs/ux/anexos/2026-09-13-pantalla-de-batalla.md`, bajo la dirección
«Ceniza y Brasa»: el mundo está apagado en grises y el único color saturado del
juego es el verde de la purificación, que vuelve a la pantalla cuando el jugador
ataja la causa del daño.

- `src/ui/design_tokens.gd` — paleta, espaciado, forma y duraciones. Ninguna
  escena escribe un color suelto.
- `src/ui/battle/` — la pantalla y sus componentes.
- `tools/gen_font.py`, `gen_sprites.py`, `gen_characters.py` — generan la fuente
  y todos los sprites. Los assets se pueden regenerar con
  `python tools/gen_sprites.py`.

## Qué falta

- La exploración top-down y los puzzles ambientales de cada región.
- Los diálogos, el inventario fuera de combate y el guardado de partida.
- Audio.

## Estructura

```
project.godot                Configuración del proyecto y mapa de entradas.
scenes/                      Escenas de Godot (main, batalla, mundo).
src/                         Todo el código. Ver src/README.md.
assets/                      Sprites, tilesets, audio y fuentes.
docs/ux/anexos/              Anexos de diseño de interfaz.
```

## Convenciones

- Código en inglés: clases, métodos, variables y nombres de archivo.
- Español solo en los textos que ve el jugador y en los comentarios.
- Archivos y carpetas en `snake_case`; clases en `PascalCase` con `class_name`.
- Programación orientada a objetos: la lógica compartida vive en la clase base
  (`Combatant`, `Monster`, `Skill`, `StatusEffect`, `Item`), no repetida en cada
  subclase.
