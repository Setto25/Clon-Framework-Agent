---
name: optimizar-contexto
description: Reduce el uso de tokens mediante lectura progresiva, busquedas dirigidas, salidas acotadas y resumen de evidencia. Usar al explorar repositorios, ejecutar herramientas verbosas o sostener tareas largas. No usar para omitir archivos obligatorios, controles de seguridad ni verificaciones necesarias.
---

# Optimizar contexto

## Objetivo

Reducir redundancia sin reducir cobertura, exactitud ni capacidad de verificacion. La economia se obtiene seleccionando mejor el contexto, no eliminando evidencia necesaria.

## Protocolo

1. Definir el resultado esperado, el alcance y las verificaciones que demostrarian que la tarea termino.
2. Leer completos los archivos obligatorios del proyecto y cualquier `SKILL.md` aplicable.
3. Localizar primero con busquedas por nombre, simbolo o patron. Abrir solo las secciones pertinentes y leer completo cada archivo antes de modificarlo.
4. Agrupar inspecciones independientes y acotar la salida de herramientas. Preferir rutas, coincidencias, conteos, resúmenes y diffs sobre volcados completos.
5. Mantener durante la tarea un registro compacto con hechos comprobados, decisiones, archivos afectados, pruebas ejecutadas y pendientes. No repetir resultados que no cambiaron.
6. Cuando el contexto crezca, condensar únicamente lo ya demostrado. Conservar nombres exactos, rutas, restricciones, errores relevantes y resultados de pruebas.
7. Antes de entregar, revisar el diff y ejecutar las verificaciones proporcionales al riesgo.

## Puertas de eficacia

- No se debe decidir a partir de una salida truncada si la parte omitida puede cambiar la conclusion.
- No se debe ahorrar contexto omitiendo seguridad, permisos, requisitos del usuario, pruebas de regresion o documentación obligatoria.
- Se debe ampliar la inspeccion cuando exista ambiguedad, una dependencia transversal o evidencia contradictoria.
- Se debe distinguir siempre entre hecho comprobado, inferencia y pendiente.
- Una respuesta breve no reemplaza una implementacion o verificacion solicitada.

## Criterio de salida

La tarea conserva el mismo criterio de aceptación que tendría sin esta Skill, pero usa menos lecturas repetidas, menos salida irrelevante y resúmenes trazables.
