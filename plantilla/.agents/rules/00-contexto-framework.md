---
trigger: always_on
description: Carga las reglas permanentes, la memoria y las puertas deterministas del framework.
---

# Contexto base del framework

Antes de modificar el proyecto, se deben leer `AGENTS.md` y `PROJECT_STATE.md`.
Las reglas permanentes, la definicion de terminado y el protocolo de cierre se toman
de esos archivos. Las Skills instaladas se descubren desde `.agents/skills/` y su
contenido completo solo se carga cuando la tarea coincide con su descripcion.

Antes de declarar una tarea terminada se ejecuta `scripts/validar_cierre_tarea.py . --solo-verificaciones`. Solo su codigo cero permite actualizar documentos de cierre; despues se ejecuta la puerta completa. Ninguna explicacion sustituye un codigo fallido o un estado `NO_EJECUTADO` o `NO_DISPONIBLE` bloqueante.
