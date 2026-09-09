# Arquitectura del código

Todo el código está en inglés (clases, métodos, variables y archivos). El
español queda para los textos que ve el jugador y para los comentarios.

```
src/
├── core/
│   └── enums.gd            Enumeraciones compartidas (EcoType, StatusType…).
├── actors/
│   ├── combatant.gd        Base común: PV, energía, estadísticas, estados.
│   ├── character.gd        Ilan y compañeros: niveles y Conocimiento Ambiental.
│   ├── party_library.gd    Constructores de los cinco personajes jugables.
│   ├── monster.gd          Debilidad ambiental, regeneración e IA por pesos.
│   └── monsters/           Un archivo por monstruo de región + jefe final.
├── skills/
│   ├── skill.gd            Base de las acciones.
│   ├── attack_skill.gd     Daño y estados alterados. Nunca purifica.
│   ├── eco_skill.gd        Habilidades Ecológicas: las únicas que purifican.
│   ├── summon_skill.gd     Multiplicación del Espectro del Monocultivo.
│   └── skill_library.gd    Catálogo con toda la configuración de habilidades.
├── status/
│   ├── status_effect.gd    Base de los estados alterados.
│   └── effects/            Veneno, quemadura, aturdimiento, ceguera, marchitez, lentitud.
├── items/
│   ├── item.gd             Base de los objetos.
│   ├── healing_item.gd     Consumibles de curación y antídotos.
│   ├── inventory.gd        Bolsa compartida del grupo.
│   └── item_library.gd     Catálogo de objetos.
├── battle/
│   ├── battle_manager.gd   Flujo del combate. Solo reglas, sin dibujar nada.
│   ├── turn_manager.gd     Orden de turnos por velocidad efectiva.
│   ├── battle_action.gd    Acción elegida en un turno.
│   └── battle_context.gd   Fotografía del combate que consulta la IA.
└── demo/
    └── battle_demo.gd      Prueba de concepto por consola, sin interfaz.
```

## Las dos reglas que sostienen el combate

1. **Debilidad ambiental.** `Monster.required_counter_type` se compara con
   `EcoSkill.weakness_type`. Mientras no coincidan, el monstruo resiste el daño
   y se regenera al llegar a 0 PV. La validación vive en `Monster`, no repartida
   por cada monstruo.
2. **El jefe final aprende.** `AdaptiveBoss` guarda una tabla Q
   (`Dictionary`: tipo de daño → resistencia aprendida) que se refuerza con cada
   repetición y se relaja con lo que el jugador deja de usar. Además exige cinco
   contramedidas distintas para purificarse.

## Interfaz

`BattleManager` no dibuja nada: comunica por señales (`turn_started`,
`player_input_required`, `action_resolved`, `battle_ended`…). La pantalla de
batalla se conecta a esas señales y responde con `submit_action()`.
