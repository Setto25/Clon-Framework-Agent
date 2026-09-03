# Instrucciones permanentes de {{NOMBRE_PROYECTO}}

## 1. Estilo de código y documentación

- Todos los nombres creados para archivos, carpetas, módulos, clases, esquemas, modelos y routers deben escribirse en {{IDIOMA_NOMBRES}}, con dos excepciones:
  - **Nombres reservados por herramientas o por la convencion interoperable del framework** (no configurables dentro de la plantilla): `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.md`, `.agents/skills`, `.agents/rules`, `.claude/skills`, `SKILL.md` y los demas enumerados en `.agents/rules/excepciones_nominales.md`.
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

Un módulo solo se considera terminado cuando el código está implementado, las pruebas pertinentes pasan, existe una forma reproducible de ejecutarlo y la documentación de estado, funcionamiento y cambios se encuentra actualizada. Antes de declararlo terminado se debe ejecutar `scripts/validar_cierre_tarea.py` con las pruebas y archivos reales de la tarea; un código distinto de cero significa que el trabajo permanece incompleto.

## 6. Skills del proyecto

- Se deben consultar las Skills locales en `.agents/skills` cuando la tarea coincida con su descripción o el usuario las invoque explícitamente.
- Se debe leer completamente el `SKILL.md` seleccionado antes de actuar.
- Se deben resolver scripts y referencias desde el directorio de la Skill correspondiente.
- Se debe usar `$cerrar-modulo` después de completar y verificar un módulo.
- Se debe usar `$lecciones-aprendidas` antes de repetir una depuración difícil ya registrada.
- Se debe considerar `$optimizar-contexto` solo ante auditoría solicitada, exploración repetida, más de diez rutas relevantes, dos ciclos fallidos o presión observable de contexto. No se activa por defecto en una implementación acotada, aunque cruce frontend y backend. El índice local se usa solo cuando la exploración ya es necesaria; si es fresco, reemplaza el listado inicial y se actualiza solo ante ausencia, contradicción o cambio externo.
- Se debe usar `$probar-e2e` cuando corresponda comprobar un flujo completo entre componentes.
- Se debe considerar `$diagnosticar-tarea` antes de invocar al agente en tareas con pruebas fallidas o errores reproducibles. Ejecutar `python scripts/diagnosticar_tarea.py <directorio>` y entregar el diagnostico como contexto inicial si la confianza es alta o media.
- Solo se pueden invocar Skills cuyo `SKILL.md` exista en esta instancia. Las recomendaciones de otras Skills requieren confirmación antes de incorporarlas desde el framework fuente.

## 7. Operación con diferentes agentes

### Con Antigravity

- Se deben usar `.agents/rules/` y `.agents/skills/` como mecanismos nativos del proyecto.
- La regla `00-contexto-framework.md` exige leer `AGENTS.md` y `PROJECT_STATE.md`.
- Solo se deben invocar Skills instaladas en la instancia.

### Con Claude

- Se deben comprobar las herramientas y permisos de la sesion antes de asumir acceso a archivos o terminal.
- `CLAUDE.md` importa `AGENTS.md`, `PROJECT_STATE.md` y las reglas especificas.
- `.claude/skills/` contiene adaptadores generados que remiten a la unica copia canonica en `.agents/skills/`.
- Se debe usar `documentacion/prompts/SYSTEM_PROMPT_BASE.md` junto con el delta correspondiente cuando la configuracion lo requiera.
- Se debe consultar `.agents/rules/claude.md` para reglas especificas.

### Con Cursor

- Se deben usar `AGENTS.md` y `.agents/skills/` mediante su descubrimiento nativo.
- Se debe leer `PROJECT_STATE.md` antes de modificar codigo.
- Se deben comprobar las Skills visibles y los permisos de la sesion antes de actuar.

### Con Codex

- Se deben comprobar el sandbox, las rutas autorizadas, la red y las herramientas disponibles.
- Se deben aplicar todas las reglas de `AGENTS.md` y consultar la documentacion pertinente.
- Se deben usar solamente las Skills instaladas y expuestas en la sesion.

### Nota de compatibilidad

Estas reglas son agnosticas del agente. Si una capacidad declarada por la plataforma contradice este documento, prevalece la capacidad observable y se actualiza la documentacion del proyecto.
