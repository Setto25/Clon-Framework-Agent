# Domain-pack: audio-embebido

**Tipo:** Extension de dominio sobre stack `firmware-esp32`
**Para:** Proyectos ESP32 que incluyen captura, procesamiento o reproduccion de audio digital.

## Que agrega al stack base

- Skill: `validar-audio` (no materializado aun)
- Reglas adicionales especificas de audio (ver abajo)
- Terminos tecnicos de audio

## Skill pendiente: validar-audio

**Proposito:** Verificar la cadena completa de audio (captura → procesamiento → salida) con señales controladas.

**Alcance esperado:**
- Validar formato de audio (WAV, PCM, sample rate, bit depth)
- Verificar calidad de señal (SNR, clipping, latencia)
- Probar cadena completa end-to-end con señal conocida
- Confirmar que el buffer de audio no produce underruns/overruns

**Estado:** Stub. Materializar como SKILL.md cuando un proyecto lo necesite.

## Reglas adicionales (solo proyectos con audio)

- Probar cada componente de audio de forma aislada antes de encadenar la señal.
- Documentar sample rate, bit depth y formato en cada punto de la cadena.
- Verificar que el tamaño de buffer es suficiente para la latencia objetivo.
- No asumir que la captura funciona sin reproducir una grabacion de prueba.

## Terminos tecnicos del dominio

| Termino | Contexto |
|---|---|
| `sample rate` | Frecuencia de muestreo |
| `bit depth` | Resolucion por muestra |
| `PCM` | Pulse Code Modulation |
| `I2S` | Protocolo de audio digital |
| `codec` | Codificador/decodificador de audio |
| `DAC` / `ADC` | Conversion analogica-digital |
| `buffer underrun` / `overrun` | Fallos de flujo de audio |
| `SNR` | Signal-to-Noise Ratio |
| `clipping` | Distorsion por saturacion |

## Como activar

Cuando un proyecto ESP32 necesite audio:

1. Materializar `validar-audio/SKILL.md` en este directorio o en `stacks/firmware-esp32/skills/`.
2. Agregar las reglas adicionales a `AGENTS.md` §Arquitectura.
3. Agregar los terminos tecnicos a las excepciones nominales del proyecto.
