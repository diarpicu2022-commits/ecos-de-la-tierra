# Título y créditos: concepto con el arte de Tierra Viva

Fecha: 2026-10-30. **Esto es un concepto, no un contrato.** Las partes 10
(título y opciones) y 12 (final y créditos) abren cada una su anexo con las
cuatro fases (guía §1.1) cuando les toque. El concepto sigue la dirección que
la guía ya recomienda para ambas (§5) y sirve como dirección A de esos anexos.

Generado por `tools/tierra_viva/title_credits.py`. Imágenes en `referencias/`.

## Pantalla de título (parte 10)

| Archivo | Estado de la partida |
|---|---|
| `titulo_nueva.png` | Partida nueva: Valdehoja enferma; solo el jardín de Yara está verde |
| `titulo_media.png` | Tres regiones devueltas: sus partes del pueblo verdes |
| `titulo_final.png` | Solmira entera devuelta |

- **Registro: marca.** La pantalla de título cambia a medida que el jugador devuelve el mundo, como recomienda la guía §5.
- **Frente de purificación:**
  - avanza en el tramado Bayer 4×4, que es su único trabajo en el repertorio (§3.1);
  - las formas son orgánicas, no círculos.
- **Punto de entrada único:** el nombre en «Brote». «Ecos de la» va a ×3 y «Tierra» a ×5.
  - «Tierra» va en `ASH_050` en partida nueva y pasa a `VITAL_500` en cuanto hay algo devuelto.
  - El verde aquí significa exactamente «purificado».
  - Debajo del nombre, la mitad izquierda del fondo baja de valor para que el nombre mande.
  - **Por medir:** que lo más contrastado de la pantalla sea el nombre (guía §5, parte 10).
- **Menú:** Continuar · Nueva partida · Opciones · Salir.
  - Panel `ASH_800` con borde `ASH_600` de 1 px, radio 0.
  - Cursor en `EMBER_300`, el foco ya contratado.
  - Sin «Continuar» si no hay partida guardada.
- **Abajo a la derecha:** el estado de la partida en `ASH_400` («Partida nueva», «Tres regiones devueltas»).
- **En el motor:**
  - es Valdehoja real con `purified_lookup` según `GameState`, y no una imagen fija;
  - la cámara se queda quieta y los vecinos y la fauna de lo purificado se mueven (enmienda 8);
  - `scenes/main.tscn` abre el título.

## Créditos (parte 12)

`creditos_hoja.png`, más un cuadro por zona (`creditos_<zona>.png`).

- **Registro: marca.** Tras purificar a la Sombra, los créditos son **un recorrido de cámara por las zonas ya sanas**, con los nombres en paneles. Enseñan lo que el jugador devolvió.
- **Orden del recorrido:**
  1. Valdehoja: título del proyecto.
  2. Costa: dirección, diseño y desarrollo.
  3. Cuenca: desarrollo e integración.
  4. Llanura: arte y mundo.
  5. Cumbre: fuentes y audio, con sus licencias.
  6. Cripta, ya en calma: «Gracias por devolverle el color a Solmira».
- **Panel:** el mismo del menú, abajo a la izquierda; el mundo ocupa el resto. La cámara avanza a velocidad de paseo y sin cortes; con movimiento reducido, un fundido por zona.
- **Pendiente de Diego:**
  - los **nombres completos reales** del equipo (en el concepto solo hay «Diego» y «Juan José Rueda»);
  - cómo acreditar el origen de los sprites hechos con PixelLab;
  - el archivo `LICENCIAS.md` con fuentes y audio de terceros.
  - Regla: sin firmas de herramientas (guía §1.6).
