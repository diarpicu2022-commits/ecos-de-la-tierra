# Ecos de la Tierra

RPG 2D por turnos con estética pixel art y enfoque de concienciación ambiental.
Godot Engine 4 + GDScript, exportable a PC y Android desde el mismo proyecto.

La propuesta completa (historia, personajes, regiones y justificación técnica)
está en `EcosDeLaTierra Propuesta Videojuego.md`.

## Abrir el proyecto

1. Instalar **Godot Engine 4.3 o superior** (versión estándar, no la de .NET).
2. Abrir Godot → *Import* → seleccionar el archivo `project.godot` de esta
   carpeta.
3. Ejecutar con F5. La escena principal es `scenes/main.tscn`, que por ahora
   lanza la prueba de concepto del combate y escribe el registro en la consola
   de salida del editor.

## Qué hay implementado

- Clases base del combate por turnos, con la arquitectura descrita en `src/README.md`.
- **Sistema de debilidad ambiental**: los monstruos se regeneran mientras no se
  aplique la Habilidad Ecológica correcta.
- **IA de los monstruos** por pesos, y **tabla Q** del jefe final, que aumenta su
  resistencia a la habilidad que el jugador repite.
- Los cinco monstruos de región, el jefe final, los cinco personajes jugables,
  el catálogo de habilidades, los estados alterados y la Bolsa.

## Qué falta

- La interfaz de batalla y del mundo (menú, HUD, diálogos, inventario).
- Los sprites y tilemaps: `assets/` está preparado pero vacío.
- La exploración top-down y los puzzles ambientales de cada región.
- El guardado de partida.

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
