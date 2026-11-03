> **Tierra Viva.** Solmira está enferma, pero nunca gris: el daño tiene su propio color —ceniza, crudo, plástico, óxido— y la purificación devuelve el del bosque, el río y las flores. El jugador ve el mundo sanar.

*Ecos de la Tierra* es un RPG de acción en pixel art con exploración cenital: se pelea en el mismo mapa, en tiempo real. Este sistema fija cómo se ve todo: mundo, personajes, monstruos e interfaz. Sus referencias son **The Legend of Zelda: The Minish Cap** y **Link's Awakening** (mundo legible, copas de árbol en racimos, caminos con borde de hierba), **CrossCode** y **Moonlighter** (personajes con volumen y caminata viva), y **Pokémon Negro/Blanco, Negro 2/Blanco 2 y HeartGold/SoulSilver** (caja de diálogo de papel, cartel de lugar, color de los pueblos). El combate **no** es por turnos ni en pantalla aparte: es de acción en el mapa, como Minish Cap.

## Retícula

- Lienzo lógico de **640×360**, escalado solo por enteros (2× = 1280×720, 3× = 1920×1080), filtro *Nearest*.
- Terreno en losetas de **16 px** (`tile`), escrito casilla a casilla. Cada material se vuelve una máscara de píxeles con esquinas redondeadas (camino radio ~6, agua curvas amplias): bordes rectos limpios y curvas suaves, nunca escalones ni ruido. Cada loseta depende solo de sus 8 vecinas, así que se traslada tal cual a un autotile de Godot.
- Personajes en lienzo de **48 px** (`character`), unos 46 px de alto, en 8 direcciones. Monstruos de combate en **128 px** (`monster`).
- Un píxel de arte = un píxel de pantalla, sin excepciones. Los monstruos de zona (128 px) son más grandes que el héroe a propósito: se leen como jefes de la zona.

## Color

- Paleta por **rampas**, de oscuro a claro (`grass-1` … `grass-7`). Las sombras viran a azul o violeta y las luces a amarillo: nunca se oscurece añadiendo negro.
- Todo sprite se contornea con **contorno selectivo**: el borde toma el tono más oscuro de su propio material, no un negro plano. El contorno exterior de la interfaz es `ink-1`.
- **Mundo sano**: `grass`, `leaf`, `dirt`, `sand`, `water`, `wood`, `roofr`, `roofb`, `wall`, `flower`.
- **Mundo enfermo**, uno por región, con su propio color: incendio `ash` + `fire` (Bosque de las Cenizas), crudo `oil` + `sheen` (Cuenca de Alquitrán), residuos `plastic` (Costa Quebrada), agotamiento `drygrass` + `sludge` (Llanura Marchita), hollín sobre `ice` (Cumbre Menguante), `gold` + `smog` (Cripta de la Avaricia).
- **`eco`** es el acento de la purificación: la chapa PURIFICADO, el mando ECO, la barra de energía y la luz de las habilidades. No se usa como decorado.
- Las barras de vida: `hp-high` (verde), `hp-mid` (oro), `hp-low` (rojo), con la cifra al lado en la tarjeta del héroe.

## Tipografía

- Una familia, **Brote**: pixel proporcional, mayúsculas de 7 px, minúsculas de 5, descendentes de 2, tildes, ñ, `¿¡«»` y los símbolos ▶ ▼ ✓ ✖ ♥ ★.
- `texto` (11 px) para todo; `titular` (22 px) solo para títulos y desenlaces. Sin tamaños intermedios.
- Sobre papel, el texto va en `text-on-paper` con sombra de 1 px `text-shadow-paper` abajo a la derecha, como en Pokémon. Sobre pizarra, `text-on-slate` con sombra `ui-1`.

## Interfaz

- **Caja de diálogo** (`DialogBox`): papel `paper` con marco de madera de 2 px (`paper-edge`), esquina 3, hoja `eco` en la esquina superior izquierda, chapa con el nombre de quien habla y retrato opcional. `▼` cuando hay más texto.
- **HUD de acción** (`ActionHUD`), siempre a la vista y sin pausar el juego:
  - *Tarjeta del héroe* arriba a la izquierda: retrato, nombre, la causa que sabe atajar (chapa de tipo), PV y energía.
  - *Relevo* debajo: los otros cuatro con su PV y un punto del color de su causa. **Q / E** cambian de héroe al momento.
  - *Bolsa* abajo a la izquierda: cuatro huecos con icono, cantidad y tecla **1–4**. Usar un objeto no abre ningún menú.
  - *Mandos* abajo a la derecha, en rombo y de color fijo: **Z** atacar (`rust`), **X** esquivar (`roofb`), **C** habilidad eco con su coste (`eco`), **V** objeto elegido (`gold`).
  - *Placa flotante* sobre el monstruo: nombre, chapa de tipo, SE REHACE / PURIFICADO y barra de PV.
  - *Aviso* en papel abajo en el centro: la regla dicha con el hecho («La llama se rehace. Su causa es FUEGO»).
- Pizarra `slate` con contorno `slate-edge` para todo el HUD; papel solo para lo que se lee como frase.
- **Cartel de lugar** (`LocationSign`): tabla de madera con clavos, el nombre de la zona y, debajo, su estado.
- **Chapas** (`TypeBadge`): tipo de daño en su color (FUEGO, PETRÓLEO, PLÁSTICO, MONOCULTIVO, DESHIELO, AVARICIA) y estado (CORRUPTO / PURIFICADO). Texto blanco o claro, siempre ≥ 4,5:1.
- Esquinas recortadas en escalera (`corner-1/2/3`), nunca curvas suavizadas. Sin degradados ni sombras difusas en la interfaz.

## Mundo

- **Hierba**: textura propia de 32×32 con matas en V regulares pero no mecánicas, más matas sueltas y flores. Nada de manchas de color: la variedad la ponen los objetos.
- **Caminos**: tierra con borde oscuro de 1 px, sombra de la hierba en el borde norte y briznas que lo pisan. Curvas amplias en los quiebros.
- **Agua hundida**: la profundidad sale de la distancia a la orilla (bajío claro, medio, fondo oscuro, transiciones tramadas); en la orilla norte se ve el talud de tierra; destellos solo en agua abierta; nenúfares, juncos y piedras.
- **Desniveles**: mesetas con cara de roca de una loseta hecha de bloques (no ladrillos), flecos de hierba colgando, labio de luz arriba, sombra al pie y escaleras de piedra. Donde un río cruza una cara, cascada.
- **Objetos**: árboles en racimos con sombra, arbustos con los mismos racimos, tocones, troncos caídos, carteles, vallas, setas.
- **Regla de colocación**: el pie de un árbol solo va sobre hierba libre y su copa no tapa más del 8 % de agua o camino. La escena no se genera si alguno lo incumple, y la posición vale a la vez para el árbol sano y el quemado.
- Los bosques se cierran con filas de árboles solapados (muro de árboles), como en Pokémon y Minish Cap.
- La hierba alta va en matas densas con forma (no rectángulos), cortables.
- Lo enfermo y lo sano son el mismo mapa con otra paleta y otros objetos: el árbol quemado vuelve a tener copa, el agua turbia vuelve a ser azul, la hierba seca vuelve a ser verde y aparecen flores y fauna.
- En lo enfermo **todo** se asienta en el mismo daño: los árboles quemados llevan cerco de ceniza y sombra, la madera de tocones y troncos está carbonizada, y casas y vallas se apagan hacia el gris ceniza. Nada conserva el color sano encima de un suelo quemado.

## Personajes y monstruos

- Personajes de 48 px, vista cenital baja, contorno selectivo, 8 rotaciones y caminata de 4 cuadros a `dur-walk-frame` (200 ms por cuadro).
- Cada monstruo tiene **dos formas** que comparten silueta de base: la corrupta (agresiva, con el material del daño) y la purificada (amable, con el material sano). Purificar cambia forma, paleta y expresión a la vez.
- En el mapa, el monstruo de zona patrulla y se enfrenta en el sitio. Golpearlo sin la causa correcta lo hace rehacerse; la habilidad eco del héroe adecuado lo purifica.

## Voz

- Todo en español, frases cortas, sin marketing. Menús y mandos en MAYÚSCULAS; diálogos en tipo oración.
- La pantalla enseña el hecho, no da consejos: «La Llama se regeneró: la causa sigue activa.»

## Movimiento

- Caminata de 4 cuadros; texto que se escribe letra a letra (`dur-text-char`), Enter lo completa; barras de PV que bajan en `dur-hp`.
- La purificación (`dur-purify`) es el momento grande: el monstruo cambia de forma y el color vuelve al mapa en una ola circular tramada (Bayer 4×4) que sale de él.
- Golpe: tajo en media luna de oro a blanco y chispa; cifras a doble tamaño; `~` delante si el monstruo se lo quita de encima.
- Con movimiento reducido, todo salta al estado final.

## Activos

- Personajes y monstruos generados con PixelLab a partir de descripciones de este sistema; terreno, interfaz y fuente hechos a mano en código.
- Los grupos de Activos muestran copias ampliadas por entero (3× o 2×) para verlas nítidas; los originales están a 1× en el proyecto.
