# Stack: firmware-esp32

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos con ESP32/MicroPython, Arduino y comunicacion IoT.

## Que ofrece el catalogo fuente

- Skills genericos de firmware: `desarrollar-firmware`, `diagnosticar-hardware`
- Reglas adicionales de implementacion (ver abajo)
- Secciones para inyectar en `AGENTS.md` §Arquitectura
- Domain-packs opcionales para dominios especificos (ej: `audio-embebido`)

Una instancia generada puede contener una o ambas Skills. Los `domain-packs` no se instalan automaticamente.

## Estructura en el catalogo fuente

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

## Como seleccionar

Desde la raiz de `agent-framework`, cada Skill se confirma por separado al crear la instancia:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill desarrollar-firmware --skill diagnosticar-hardware
```

No se mueven carpetas manualmente. La seleccion de un `domain-pack` requiere un flujo independiente que todavia no esta implementado.
