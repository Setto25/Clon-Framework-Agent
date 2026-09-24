# Documentacion tecnica — {{NOMBRE_PROYECTO}}

## Objetivo del sistema

{{DESCRIPCION_OBJETIVO}}

## Arquitectura vigente

{{REGLAS_ARQUITECTURA}}

## Tecnologias decididas

{{LISTA_TECNOLOGIAS}}

## Componentes implementados

{{HISTORIAL_IMPLEMENTACION}}

## Regla de mantenimiento

Este documento describe solo componentes comprobados. Cada cambio de arquitectura debe actualizar contratos, rutas, ejecucion y pruebas relacionadas. Las puertas por modulo se declaran en `contrato_validacion.json`; los contratos verticales propios del dominio se registran como comandos de tipo `integracion`, `e2e`, `schema` o `contrato`.
La integridad estatica del repositorio se comprueba con `scripts/validar_integridad_proyecto.py`; las pruebas ejecutables se comprueban con `scripts/validar_cierre_tarea.py`.
