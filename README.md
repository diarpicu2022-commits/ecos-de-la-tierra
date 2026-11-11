# Ecos de la Tierra

Ecos de la Tierra es un RPG 2D en pixel art sobre el cuidado del medio ambiente. Ilan sale de Valdehoja a recorrer las regiones dañadas, y cada una tiene un monstruo que nace de un problema real, como la deforestación o el monocultivo. El monstruo no cae a punta de golpes. Se regenera hasta que el jugador usa la habilidad ecológica que ataja la causa del daño, y ahí la región se cura.

Lo hicimos Juan José Rueda y yo como proyecto final de Diseño de Interfaces de Software (5.º semestre, Universidad Cooperativa de Colombia). Está hecho en Godot 4 con GDScript y se puede exportar a PC y a Android desde el mismo proyecto.

## Para qué sirve

La idea es que el jugador aprenda jugando que los problemas ambientales se resuelven atacando su causa y no sus síntomas. Esa regla está metida en el combate, no en un texto que se lee. La historia completa, los personajes y las regiones están en `EcosDeLaTierra Propuesta Videojuego.md`.

## Qué se puede jugar hoy

La versión de `master` es la **demo hasta el primer jefe**, la que presentamos el 4 de noviembre de 2026.

1. Ilan empieza en Valdehoja y habla con Yara junto al semillero.
2. Sale por el este al Bosque de las Cenizas y se encuentra con el Comandante Rasgo.
3. Pelea contra la Llama de la Deforestación. Solo la Línea Cortafuegos de Bruma ataja la causa.
4. El bosque se cura, se abre el paso y la demo termina con un mensaje de lo que sigue en la historia.

El combate es de acción en el mismo mapa. Manejas a un héroe, cambias entre los del grupo, golpeas, esquivas y usas las habilidades y la bolsa, que siempre están a la vista.

## Controles

| Acción | Tecla |
|---|---|
| Moverse | Flechas o W A S D |
| Correr | Shift |
| Hablar o confirmar | Enter o Espacio |
| Volver | Esc |
| Golpear | Z |
| Esquivar | X |
| Habilidad ecológica | C |
| Usar objeto | V |
| Cambiar de héroe | Q y E |
| Orden al grupo | Tab |

## Cómo jugarlo

1. Instala **Godot 4.3 o superior**, la versión estándar (no la .NET, porque el proyecto no usa C#). Lo probamos en 4.3 y en 4.7.2.
2. En Godot entra a *Import* y elige el `project.godot` de esta carpeta.
3. Dale F5. La escena principal es `scenes/game.tscn`.

En Windows también está `Jugar.bat`, que abre el juego sin el editor. Busca Godot 4.7.2 en la carpeta de Descargas, así que si lo tienes en otra parte toca cambiar la ruta dentro del archivo.

El juego no necesita cuenta ni internet.

## Cómo está hecho

- **Combate.** Las clases base (`Combatant`, `Monster`, `Skill`, `StatusEffect`, `Item`) viven en `src/` y su arquitectura está en `src/README.md`. Los monstruos deciden por pesos y el jefe final aprende con una tabla Q, así que si repites siempre la misma habilidad la empieza a resistir y toca combinarlas.
- **Diseño.** Todo lo visual sigue el sistema de diseño «Tierra Viva», en `docs/ux/sistema-de-diseno/` (abre su `index.html`). Los anexos de cada pantalla, con sus referencias y su verificación, están en `docs/ux/anexos/`.
- **Arte.** Los personajes y monstruos del mapa se hicieron con PixelLab y el resto lo generan los scripts de `tools/`.
- **Pruebas.** Las verificaciones de movimiento, combate, flujo y usabilidad están en `tools/` y corren sin interfaz.

| Carpeta | Qué hay |
|---|---|
| `scenes/` | Escenas de Godot (juego, batalla, mundo) |
| `src/` | Todo el código |
| `assets/` | Sprites, mapas, audio y fuentes |
| `data/` | Mapas de las regiones, salidas y datos de combate |
| `docs/` | Plan de trabajo, guía del equipo, diseño y aviso legal |
| `tools/` | Generadores de arte y pruebas |

Para seguir el desarrollo se lee primero `docs/plan-para-terminar-la-historia.md` y después `docs/guia-del-equipo.md`.

## Convenciones

- Código en inglés (clases, métodos, variables y archivos) y español en los textos que ve el jugador y en los comentarios.
- Archivos y carpetas en `snake_case` y clases en `PascalCase` con `class_name`.
- La lógica compartida va en la clase base y no se repite en cada subclase.

## Privacidad

El juego no recoge datos de nadie ni se conecta a internet. El detalle está en [`docs/legal/privacidad.md`](docs/legal/privacidad.md).

## Lo que falta

El plan para acabar la historia, con las regiones que siguen y el jefe final, está en `docs/plan-para-terminar-la-historia.md`.

## Equipo

Diego Armando Pinta Cuasquen · Juan José Rueda
