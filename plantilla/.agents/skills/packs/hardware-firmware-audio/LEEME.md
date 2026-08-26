# Pack: hardware-firmware-audio

**Tipo:** Domain-pack (Capa 2)
**Para:** Proyectos con dispositivos embebidos, MicroPython/Arduino, audio digital y comunicación IoT.

## Qué agrega al core

- Skills: `desarrollar-firmware`, `diagnosticar-hardware`, `validar-audio`
- Reglas adicionales de implementación (ver abajo)
- Secciones para inyectar en `AGENTS.md` §Arquitectura

## Reglas adicionales de implementación

Estas reglas complementan la sección "Forma de implementación" del prompt base:

- Mantiene secretos fuera del firmware, la memoria flash y los logs del dispositivo.
- No fija el mapa de GPIO hasta inspeccionar etiquetas reales y probar conflictos.
- Prueba cada componente de audio de forma aislada antes de encadenar la señal.
- Separa máquina de estados y protocolo de los adaptadores físicos.
- Si una acción eléctrica presenta riesgo, se detiene y solicita mediciones o fotografías.

## Cómo instalar

```bash
cp -r .agents/skills/packs/hardware-firmware-audio/desarrollar-firmware/ .agents/skills/
cp -r .agents/skills/packs/hardware-firmware-audio/diagnosticar-hardware/ .agents/skills/
cp -r .agents/skills/packs/hardware-firmware-audio/validar-audio/ .agents/skills/
```

Luego agregar las reglas adicionales a la sección correspondiente del prompt de sistema o de `AGENTS.md`.
