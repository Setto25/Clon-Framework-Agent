---
name: desarrollar-firmware
description: Guia la implementacion de firmware en ESP32/MicroPython siguiendo un ciclo seguro. Confirma hardware antes de escribir codigo, prueba cada componente aislado, estructura en maquina de estados y respeta limites de memoria. Usar cuando se implemente logica nueva en el microcontrolador.
---

# Desarrollar firmware

## Precondiciones

1. Confirmar que el hardware objetivo esta conectado y accesible.
2. Identificar pines/perifericos involucrados consultando esquematico o etiquetas fisicas.
3. Verificar que no haya conflictos de GPIO con perifericos existentes.

## Ciclo de implementacion

1. **Prueba aislada**: verificar el componente fisico con un script minimo independiente.
2. **Integracion**: incorporar a la maquina de estados principal.
3. **Limites de memoria**: verificar uso de RAM/PSRAM antes y despues del cambio.
4. **Persistencia**: si el cambio afecta flash/NVS, documentar el layout.

## Reglas estrictas

- No fijar GPIO sin inspeccion real del hardware.
- No usar bloques grandes de memoria sin verificar disponibilidad en PSRAM.
- Separar maquina de estados del protocolo de comunicacion.
- Si una accion electrica presenta riesgo, detenerse y solicitar mediciones o fotografias.
- Mantener secretos (WiFi, API keys) fuera del firmware — usar NVS cifrado o variables de entorno en el build.

## Estructura esperada del codigo

```
firmware/
├── main.py                 # Entry point, maquina de estados
├── componentes/            # Drivers de perifericos individuales
├── protocolos/             # MQTT, HTTP, BLE
├── configuracion/          # Pines, constantes, feature flags
└── pruebas/                # Scripts de verificacion por componente
```

## Salida

Entregar: componente implementado, prueba aislada ejecutada, integracion verificada, uso de memoria reportado, siguiente paso.
