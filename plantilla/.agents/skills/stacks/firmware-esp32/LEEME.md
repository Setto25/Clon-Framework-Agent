# Stack: firmware-esp32

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos con ESP32/MicroPython, Arduino y comunicacion IoT.

## Que agrega al core

- Skills genericos de firmware: `desarrollar-firmware`, `diagnosticar-hardware`
- Reglas adicionales de implementacion (ver abajo)
- Secciones para inyectar en `AGENTS.md` §Arquitectura
- Domain-packs opcionales para dominios especificos (ej: `audio-embebido`)

## Estructura

```
stacks/firmware-esp32/
├── LEEME.md                          # Este archivo
├── skills/
│   ├── desarrollar-firmware/         # Generico: cualquier proyecto ESP32
│   │   └── SKILL.md
│   └── diagnosticar-hardware/        # Generico: cualquier proyecto ESP32
│       └── SKILL.md
└── domain-packs/
    └── audio-embebido/               # Solo proyectos ESP32 + audio
        └── LEEME.md                  # Stub: skill validar-audio pendiente
```

## Reglas adicionales de implementacion

Estas reglas complementan la seccion "Forma de implementacion" del prompt base:

- Mantiene secretos fuera del firmware, la memoria flash y los logs del dispositivo.
- No fija el mapa de GPIO hasta inspeccionar etiquetas reales y probar conflictos.
- Separa maquina de estados y protocolo de los adaptadores fisicos.
- Si una accion electrica presenta riesgo, se detiene y solicita mediciones o fotografias.
- Verifica uso de RAM/PSRAM antes de integrar componentes nuevos.

## Terminos tecnicos del stack

Estos terminos se conservan en ingles dentro de proyectos que activen este stack:

| Termino | NO usar | Contexto |
|---|---|---|
| `GPIO` | — | Universal en embebidos |
| `SPI` / `I2C` / `UART` | — | Protocolos de bus |
| `bootloader` | `cargador_de_arranque` | Firmware |
| `watchdog` | `perro_guardian` | Hardware timer |
| `DMA` | — | Direct Memory Access |
| `ISR` | — | Interrupt Service Routine |
| `PSRAM` | — | Memoria externa ESP32 |
| `NVS` | — | Non-Volatile Storage |

## Como instalar

La instalacion es automatica via `$iniciar-proyecto`. Si necesitas hacerlo manualmente:

```bash
# Skills genericos del stack
mv .agents/skills/stacks/firmware-esp32/skills/desarrollar-firmware/ .agents/skills/
mv .agents/skills/stacks/firmware-esp32/skills/diagnosticar-hardware/ .agents/skills/
```

Para domain-packs (ej: audio), ver el LEEME.md dentro de `domain-packs/audio-embebido/`.

Luego agregar las reglas adicionales a la seccion correspondiente de `AGENTS.md`.
