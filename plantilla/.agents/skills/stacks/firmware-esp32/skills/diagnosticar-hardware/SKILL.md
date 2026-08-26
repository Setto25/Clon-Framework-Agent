---
name: diagnosticar-hardware
description: Protocolo sistematico para diagnosticar fallos de hardware en proyectos ESP32. Secuencia de pruebas desde alimentacion hasta perifericos, aislando el componente defectuoso. Usar cuando un comportamiento inesperado podria tener origen electrico o de conexion fisica.
---

# Diagnosticar hardware

## Cuando usar

- Un componente no responde o se comporta de forma erratica.
- El firmware funciona en simulacion pero falla en hardware real.
- Hay un cambio fisico reciente (nueva placa, nuevo cableado, nuevo periferico).

## Secuencia de diagnostico

### Nivel 1: Alimentacion

1. Medir voltaje en el pin de alimentacion del ESP32 (3.3V nominal).
2. Verificar que la fuente soporta el consumo pico (WiFi: ~300mA).
3. Buscar caidas de tension bajo carga.

### Nivel 2: Conexion

1. Verificar continuidad entre pines y perifericos.
2. Confirmar que no hay cortocircuitos entre pines adyacentes.
3. Revisar soldaduras frias o conectores flojos.

### Nivel 3: Comunicacion

1. Probar bus I2C/SPI con scanner generico.
2. Verificar pull-ups en I2C (4.7k tipico).
3. Confirmar frecuencia de reloj compatible con el periferico.

### Nivel 4: Periferico

1. Probar el periferico con script minimo aislado.
2. Comparar comportamiento con datasheet (timings, voltajes logicos).
3. Si el periferico tiene LED/indicador, verificar estado visual.

## Reglas

- NUNCA asumir que el hardware funciona sin evidencia.
- Solicitar fotografias o mediciones si no se puede verificar remotamente.
- Documentar cada prueba y su resultado en la tabla de evidencia.
- Escalar al usuario si el diagnostico requiere instrumentacion (osciloscopio, analizador logico).

## Tabla de evidencia

| Nivel | Prueba | Resultado | Accion |
|---|---|---|---|
| 1 | Voltaje 3.3V | ___V | |
| 2 | Continuidad pin X | OK/FALLO | |
| 3 | I2C scan | Dispositivos: ___ | |
| 4 | Script aislado | OK/FALLO | |

## Salida

Entregar: componente diagnosticado, causa raiz identificada o hipotesis ordenadas por probabilidad, siguiente accion concreta.
