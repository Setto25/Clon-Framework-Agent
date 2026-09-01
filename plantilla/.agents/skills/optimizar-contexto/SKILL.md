---
name: optimizar-contexto
description: Reduce lecturas y contexto repetidos en tareas transversales, repositorios desconocidos o sesiones prolongadas mediante busqueda dirigida, deduplicacion y evidencia trazable. No activar automaticamente en tareas simples que puedan resolverse con menos de cuatro lecturas ni para omitir verificaciones necesarias.
---

# Optimizar contexto

## Resultado

Conservar el criterio de aceptacion y la exactitud con menos contexto reenviado. La economia debe provenir de evitar exploracion y repeticion, no de retirar evidencia necesaria.

## Activacion y modo (4 Niveles)

Si la invocacion es explicita, aplicar la Skill. Si es automatica, la Skill determina condicionalmente el nivel de analisis necesario:

- **Sin analisis:** Tarea corta y archivo conocido. Modificacion local donde se conocen las dependencias. No ejecutar escaneos generales; modificar o leer directamente.
- **Modo ligero:** 1–2 terminos, maximo 10 rutas y fragmentos minimos. Usar por defecto en exploraciones iniciales si se desconoce la ruta exacta.
- **Modo extendido:** Cambios transversales (3–8 terminos, hasta 30 rutas). Ejecuta `python scripts/generar_indice_contexto.py <terminos>` en la terminal para obtener un mapa determinista del proyecto y evitar gastar lecturas a ciegas.
- **Modo arquitectonico:** Analisis extendido mas revision semantica del agente, pruebas y documentacion. Requerido para migraciones profundas o diseno de arquitectura.

*Limitaciones del script:* `generar_indice_contexto.py` solo busca referencias literales. No puede determinar dependencias semanticas, comportamientos en tiempo de ejecucion ni decisiones implicitas. Debes complementar su resultado con razonamiento y revision de pruebas/logs.

## Protocolo

1. Definir el entregable, el alcance y las verificaciones que demuestran la finalizacion.
2. Mantener un registro compacto interno (en tu razonamiento, nunca rompiendo formatos estrictos de salida) con: rutas consultadas, hechos y pendientes. Consultarlo antes de usar otra herramienta.
3. Si recibe un indice generado sobre la raiz y el estado actuales, se debe usar como evidencia observada. Si no se puede comprobar su procedencia o vigencia, se debe regenerar antes de confiar en el. **No se gastan lecturas ni busquedas** para reconfirmar evidencia vigente ya incluida.
4. Buscar primero por nombre, simbolo o patron. Evitar listar o volcar el repositorio completo.
5. Seleccionar los resultados pertinentes y agrupar inspecciones independientes.
6. No repetir una consulta con los mismos argumentos si su evidencia permanece vigente.
7. Antes de concluir, comprobar internamente que cada ruta y linea citada fue observada.
8. Si se te exige un formato estricto (ej. JSON) y fallas, **corrige y emite de nuevo el formato completo**, sin conversar ni explicar lo que vas a hacer.

## Puertas de eficacia

- Una salida truncada no sustenta una conclusion sobre la parte omitida.
- Una ruta, linea o comando no se presenta como hecho si no fue comprobado.
- La brevedad no reemplaza una implementacion, revision o prueba solicitada.
- La optimizacion se considera fallida si reduce tokens pero pierde cobertura o exactitud.

## Cierre trazable

Al finalizar, si la tarea permite conversacion, emite un resumen de metricas (llamadas realizadas, repeticiones evitadas). **Excepcion critica:** Si la tarea exige un formato estructurado (como JSON), todas estas metricas y resumenes deben quedar estrictamente en tu razonamiento interno; la salida publica debe ser unicamente el formato solicitado.
