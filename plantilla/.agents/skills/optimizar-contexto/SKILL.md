---
name: optimizar-contexto
description: Conserva contexto verificable en auditorias, depuracion repetitiva y decisiones amplias. No se usa por defecto en cambios acotados ni promete ahorro sin medicion.
---

# Optimizar contexto

## Objetivo

Conservar requisitos y verificaciones con el menor contexto necesario. No atribuye ahorro sin medicion comparable.

## Seleccion del modo

No se activa para una implementacion acotada, aunque toque frontend y backend. Se usa solo ante auditoria, depuracion repetitiva, arquitectura o presion real de contexto.

Cuando aplica, usa el modo menos costoso:

1. **Directo:** si las rutas son conocidas y se esperan hasta 10 archivos. Lee, implementa, valida y termina si aprueba.
2. **Indice:** usalo solo si la exploracion ya es necesaria. Ejecuta `python scripts/generar_indice_contexto.py <terminos>`. Un indice fresco es evidencia inicial, no garantia de ahorro: no listes ni reconfirmes rutas incluidas; actualizalo solo ante ausencia, contradiccion o cambio externo.
3. **Extendido:** cargalo unicamente cuando exista al menos una señal observable de escalamiento:
   - mas de 10 rutas o dos ciclos fallidos;
   - una consulta repetida o presion real de contexto;
   - solicitud expresa del usuario.
4. **Arquitectonico:** cargalo solo para decisiones de arquitectura, migraciones profundas o cambios de contratos entre sistemas.

Tocar varios archivos, prever cuatro lecturas, cruzar frontend/backend o recibir un indice no activa esta Skill ni el modo extendido.

## Flujo base

1. Define el resultado y la comprobacion final.
2. Conserva rutas vigentes, cambios propios, ultimo resultado de prueba y pendiente inmediato; descarta lo demas.
3. Reutiliza `PROJECT_STATE.md`, pruebas e indice vigente. El indice autoritativo reemplaza el listado inicial, pero no se genera solo para ahorrar tokens.
4. No repitas lecturas vigentes ni reenvies archivos o historial si basta ese estado.
5. Implementa solo el alcance solicitado.
6. Ejecuta la validacion pertinente. Si aprueba, finaliza sin exploracion adicional.
7. Si falla, conserva solo el fallo necesario y escala ante una señal anterior.

## Carga progresiva

- Al escalar a extendido, lee `referencias/modo_extendido.md` y aplica solo ese protocolo.
- Al escalar a arquitectonico, lee primero `referencias/modo_extendido.md` y despues `referencias/modo_arquitectonico.md`.
- No cargues esas referencias en los modos directo o indice.

## Limites de seguridad

- No presentes rutas, lineas, comandos ni resultados como hechos sin evidencia observada.
- No reduzcas pruebas, seguridad, documentacion obligatoria ni criterios de aceptacion para ahorrar tokens.
- Si una salida estricta falla, vuelve a emitir el formato completo sin explicaciones intermedias.
- No informes metricas de ahorro salvo que el usuario las solicite o la tarea sea una evaluacion.
