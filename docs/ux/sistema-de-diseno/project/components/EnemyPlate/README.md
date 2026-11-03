# EnemyPlate

Placa del monstruo enemigo, en la esquina superior izquierda del combate (10, 10).

## Qué aporta quien la usa
- Nombre, tipo de daño, si está purificado y sus PV.

## Anatomía (184 px de ancho)
- Marco `f-plate`: pizarra `slate` con contorno `slate-edge`, esquina `corner-3`.
- Nombre en `text-on-slate` con sombra `ui-1`.
- Fila de chapas: tipo (`TypeBadge`) y estado CORRUPTO / PURIFICADO.
- «PV» en `text-highlight`, barra de 5 px y la cifra `actual/máx` en `text-muted-slate`. La barra pasa de `hp-high` a `hp-mid` (≤ 50 %) y `hp-low` (≤ 20 %).

## No
- No se oculta la cifra: la barra sola obliga a estimar.
