---
name: probar-e2e
description: Ejecuta y documenta pruebas de extremo a extremo del MVP. Usar al verificar flujos completos entre componentes (cliente, servidor, dispositivo, proveedor externo). No usar para marcar un flujo como aprobado sin evidencia observable de cada etapa.
---

# Probar E2E

## Preparación

1. Leer `referencias/guion_e2e.md`.
2. Leer `PROJECT_STATE.md` y detectar qué hitos están realmente implementados.
3. Identificar ambiente, versión, servicios, proveedor simulado o real y datos de prueba.
4. Evitar datos reales de usuarios y evitar cambios en producción sin autorización explícita.
5. Definir identificadores de correlación para seguir cada turno.

## Ejecución

1. Preparar datos controlados mediante el mecanismo de prueba del proyecto.
2. Ejecutar primero el recorrido obligatorio (camino feliz).
3. Ejecutar recorridos opcionales solo cuando los hitos necesarios estén implementados.
4. Incluir fallos esperados (autenticación, validación, servicio caído, timeout).
5. Capturar solicitudes, estados, registros y resultados sin exponer secretos.
6. Repetir dos veces el guion destinado a demostración.

## Criterios

- Verificar resultados persistidos y no solo respuestas de transporte.
- Verificar que los datos correctos lleguen al destinatario correcto.
- Verificar que contenido bloqueado no aparezca en vistas públicas.
- Verificar que un error permita regresar al estado inicial.
- Marcar como no ejecutada cualquier etapa ausente; no simular evidencia.

## Informe

Entregar una tabla con caso, precondición, acción, evidencia, resultado esperado, resultado observado y estado. Terminar con bloqueos, regresiones y decisión `APROBADO` o `NO_APROBADO` para el alcance evaluado.
