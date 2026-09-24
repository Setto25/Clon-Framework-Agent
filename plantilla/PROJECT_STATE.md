# Estado del proyecto {{NOMBRE_PROYECTO}}

**Última actualización:** {{FECHA}}
**Zona horaria:** {{ZONA_HORARIA}}
**Estado general:** {{ESTADO_BREVE}}
**Fase activa:** {{FASE_ACTIVA}}

## 1. Objetivo vigente

{{DESCRIPCION_OBJETIVO}}

## 2. Alcance priorizado

### Obligatorio para declarar el MVP

{{LISTA_OBLIGATORIOS}}

### Importante si el plazo lo permite

{{LISTA_DESEABLES}}

### Fuera del MVP inmediato

{{LISTA_EXCLUIDOS}}

## 3. Infraestructura confirmada

{{HARDWARE_O_INFRA}}

## 4. Decisiones vigentes

{{LISTA_DECISIONES_NUMERADA}}

## 5. Artefactos de documentación

- `AGENTS.md`: reglas permanentes reconocibles por los agentes de desarrollo.
- `CLAUDE.md`: puente de Claude Code hacia las reglas y el estado canonicos.
- `.agents/skills/`: Skills reutilizables y locales del repositorio.
- `.claude/skills/`: wrappers generados para descubrir las mismas Skills en Claude Code.
- `documentacion/INDICE_LECTURA_AGENTES.md`: puerta de entrada a la documentación.
- `documentacion/PLAN_DESARROLLO.md`: hitos, tareas, prioridades y criterios de aceptación.
- `documentacion/DOCUMENTACION_TECNICA.md`: arquitectura, flujos, ubicación y contratos.
- `documentacion/REGISTRO_CAMBIOS.md`: historial cronológico inmutable.
- `documentacion/GUIA_OPERACION.md`: referencia integral de operación y diagnóstico.
- `contrato_validacion.json`: manifiesto opcional y versionado de modulos, comandos y puertas obligatorias; se crea desde `contrato_validacion.ejemplo.json`.
- `documentacion/EVIDENCIA_CIERRE.json`: ultima evidencia objetiva de cierre cuando se solicita su persistencia.
- `scripts/validar_integridad_proyecto.py`: puerta estatica para memoria, gestor, contrato y documentos del cambio.
- `.github/workflows/validacion-proyecto.yml`: ejecuta la puerta estatica en push y pull request cuando el proyecto usa GitHub.

## 6. Implementado hasta ahora

{{HISTORIAL_IMPLEMENTACION}}

## 7. Tecnologías decididas

{{LISTA_TECNOLOGIAS}}

## 8. Siguiente paso lógico

{{SIGUIENTE_PASO}}

## 9. Protocolo obligatorio de actualización

Después de completar cada módulo se actualiza este archivo con:

1. qué se implementó;
2. qué tecnologías y versiones se utilizaron;
3. dónde quedó cada componente;
4. cómo se ejecuta y cómo se verifica;
5. qué verificaciones pasaron, fallaron, no se ejecutaron o no estuvieron disponibles, con comando, directorio y codigo;
6. qué decisión cambió y por qué;
7. cuál es el siguiente paso lógico.

El detalle histórico se agrega, sin reescribir entradas anteriores, en `documentacion/REGISTRO_CAMBIOS.md`.

## 10. Bloqueos y datos pendientes

{{BLOQUEOS}}
