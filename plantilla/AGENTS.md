# Instrucciones permanentes de {{NOMBRE_PROYECTO}}

## 1. Estilo de código y documentación

- Todos los nombres creados para archivos, carpetas, módulos, clases, esquemas, modelos y routers deben escribirse en {{IDIOMA_NOMBRES}}, con dos excepciones:
  - **Nombres impuestos por herramientas** (no configurables): `AGENTS.md`, `PROJECT_STATE.md`, `.agents/skills`, `.agents/rules`, `SKILL.md` y los demas enumerados en `.agents/rules/excepciones_nominales.md`.
  - **Terminos tecnicos universales** reconocidos por la comunidad (ej: `endpoint`, `middleware`, `system_prompt`, `callback`): se conservan en ingles porque traducirlos dificulta busqueda y comunicacion. La lista completa y el criterio de inclusion estan en `.agents/rules/excepciones_nominales.md`.
- Se permite composicion mixta: termino universal + palabra en {{IDIOMA_NOMBRES}} (ej: `middleware_autenticacion`, `handler_pedidos`).
- Si una herramienta impone otro nombre tecnico no configurable, se debe documentar la excepcion antes de crearlo.
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

### Obligatorio para declarar el MVP

{{LISTA_OBLIGATORIOS}}

### Importante si el plazo lo permite

{{LISTA_DESEABLES}}

### Fuera del MVP inmediato

{{LISTA_EXCLUIDOS}}

## 5. Definición de terminado

Un módulo solo se considera terminado cuando el código está implementado, las pruebas pertinentes pasan, existe una forma reproducible de ejecutarlo y la documentación de estado, funcionamiento y cambios se encuentra actualizada.

## 6. Skills del proyecto

- Se deben consultar las Skills locales en `.agents/skills` cuando la tarea coincida con su descripción o el usuario las invoque explícitamente.
- Se debe leer completamente el `SKILL.md` seleccionado antes de actuar.
- Se deben resolver scripts y referencias desde el directorio de la Skill correspondiente.
- Se debe usar `$cerrar-modulo` después de completar y verificar un módulo.
- Se debe usar `$lecciones-aprendidas` antes de repetir una depuración difícil ya registrada.
- Se debe usar `$probar-e2e` cuando corresponda comprobar un flujo completo entre componentes.
- Solo se pueden invocar Skills cuyo `SKILL.md` exista en esta instancia. Las recomendaciones de otras Skills requieren confirmación antes de incorporarlas desde el framework fuente.

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
- Usar `documentacion/prompts/SYSTEM_PROMPT_BASE.md` + delta correspondiente
- Consultar `.agents/rules/claude.md` para reglas específicas

### Con Codex

- Aplicar todas las reglas de `AGENTS.md`
- Consultar documentación en `documentacion/`
- Seguir el protocolo de Skills como documentación
- Mantener compatibilidad con Antigravity

### Nota de compatibilidad

Estas reglas son agnósticas del agente. Cada agente las interpreta según sus capacidades. No hay conflicto entre agentes. Cada uno opera dentro de sus limitaciones.
