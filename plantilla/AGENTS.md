# Instrucciones permanentes de {{NOMBRE_PROYECTO}}

## 1. Estilo de código y documentación

- Todos los nombres creados para archivos, carpetas, módulos, clases, esquemas, modelos y routers deben escribirse obligatoriamente en {{IDIOMA_NOMBRES}}.
- No se deben mezclar idiomas en nombres propios del proyecto.
- `AGENTS.md`, `PROJECT_STATE.md`, `.agents/skills`, `.agents/rules`, `SKILL.md` y los nombres enumerados en `.agents/rules/excepciones_nominales.md` se conservan como excepciones técnicas documentadas.
- Si una herramienta impone otro nombre técnico no configurable, se debe documentar la excepción antes de crearlo.
- Todo código Python debe usar type hints explícitos.
- Todo código TypeScript y Dart debe usar tipos explícitos; no se debe usar `any` o equivalentes sin una justificación documentada.
- Todos los comentarios y docstrings deben escribirse en {{IDIOMA_NOMBRES}} y siempre en tercera persona del singular.

## 2. Memoria y continuidad

- Se debe leer `PROJECT_STATE.md` antes de sugerir o modificar código.
- Después de terminar un módulo o recibir aprobación del usuario, se debe actualizar `PROJECT_STATE.md` con lo implementado, las tecnologías y versiones utilizadas, la ubicación, la forma de verificarlo y el siguiente paso lógico.
- Se debe agregar una entrada cronológica en `documentacion/REGISTRO_CAMBIOS.md` sin borrar entradas anteriores.
- Se debe actualizar el estado real de las tareas en `documentacion/PLAN_DESARROLLO.md`.
- Se debe mantener `documentacion/DOCUMENTACION_TECNICA.md` sincronizado con la implementación comprobada.
- Antes de cerrar un cambio material, se debe revisar `documentacion/GUIA_OPERACION.md` y actualizarla si aplica; si no aplica, el cierre debe indicarlo explícitamente.

## 3. Arquitectura y seguridad

{{REGLAS_ARQUITECTURA}}

## 4. Prioridad del MVP

Se protege este orden:

{{LISTA_PRIORIDADES}}

{{EXCLUSIONES_MVP}}

## 5. Definición de terminado

Un módulo solo se considera terminado cuando el código está implementado, las pruebas pertinentes pasan, existe una forma reproducible de ejecutarlo y la documentación de estado, funcionamiento y cambios se encuentra actualizada.

## 6. Skills del proyecto

- Se deben consultar las Skills locales en `.agents/skills` cuando la tarea coincida con su descripción o el usuario las invoque explícitamente.
- Se debe leer completamente el `SKILL.md` seleccionado antes de actuar.
- Se deben resolver scripts y referencias desde el directorio de la Skill correspondiente.
- Se debe usar `$cerrar-modulo` después de completar y verificar un módulo.

## 7. Operación con diferentes agentes

### Con Antigravity

- Las Skills se descubren automáticamente en `.agents/skills/`
- Las reglas en `.agents/rules/` se aplican automáticamente
- El agente invoca Skills mediante `$nombre-skill`
- Se consulta `AGENTS.md` como contexto permanente

### Con Claude

- Leer completamente `AGENTS.md` como contexto inicial
- Consultar Skills en `.agents/skills/` como documentación (no como herramientas automáticas)
- Seguir las reglas de `AGENTS.md` manualmente
- Usar `documentacion/prompts/PROMPT_SISTEMA_BASE.md` + delta correspondiente
- Consultar `.agents/rules/claude.md` para reglas específicas

### Con Codex

- Aplicar todas las reglas de `AGENTS.md`
- Consultar documentación en `documentacion/`
- Seguir el protocolo de Skills como documentación
- Mantener compatibilidad con Antigravity

### Nota de compatibilidad

Estas reglas son agnósticas del agente. Cada agente las interpreta según sus capacidades. No hay conflicto entre agentes. Cada uno opera dentro de sus limitaciones.
