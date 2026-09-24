# Plan de desarrollo — {{NOMBRE_PROYECTO}}

**Estado inicial:** {{ESTADO_BREVE}}
**Fase activa:** {{FASE_ACTIVA}}

## Objetivo vigente

{{DESCRIPCION_OBJETIVO}}

## Alcance obligatorio

{{LISTA_OBLIGATORIOS}}

## Alcance deseable

{{LISTA_DESEABLES}}

## Fuera del alcance inmediato

{{LISTA_EXCLUIDOS}}

## Hito activo

- [ ] {{SIGUIENTE_PASO}}

## Criterio de actualizacion

Solo se marca una tarea como completada después de que `scripts/validar_cierre_tarea.py . --solo-verificaciones` devuelva codigo cero. La puerta completa debe registrar después los comandos, directorios y codigos reales; una cobertura inferida o ausente se declara explícitamente.
La CI comprueba además memoria, contrato y actualizacion simultanea de estado, plan y registro mediante `scripts/validar_integridad_proyecto.py`.
