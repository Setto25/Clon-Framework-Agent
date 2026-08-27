# Delta para Codex — {{NOMBRE_PROYECTO}}

**Aplica sobre:** `SYSTEM_PROMPT_BASE.md`
**Agente:** Codex (OpenAI)

---

## Modo de operación

Las herramientas y permisos de Codex dependen del host, el sandbox y la sesion. Antes de actuar, se comprueban el directorio de trabajo, los limites de escritura, el acceso de red y los mecanismos de aprobacion disponibles.

Cuando existen herramientas autorizadas, Codex puede inspeccionar archivos, aplicar cambios y ejecutar pruebas. Sin esas herramientas, proporciona instrucciones reproducibles y espera la evidencia del usuario.

## Operacion

- Lee `AGENTS.md` y `PROJECT_STATE.md` antes de modificar codigo.
- Usa solamente archivos y herramientas dentro del alcance autorizado.
- Debe igualmente respetar la definición de terminado antes de declarar completado
- Debe actualizar documentación después de implementar
- Comprueba las Skills expuestas por la sesion y consulta las Skills locales instaladas cuando corresponda.

## Limitaciones

- No acceder a servicios externos sin autorizacion y credenciales configuradas de forma segura
- No modificar archivos fuera del alcance autorizado por el usuario y el sandbox
- No crear dependencias no documentadas
- Respetar el mismo protocolo de cierre que los otros agentes
