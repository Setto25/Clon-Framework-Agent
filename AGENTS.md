# Instrucciones para agentes — agent-framework (meta-repo)

Este repositorio ES la plantilla agentica, no un proyecto que la consume.

## Distincion critica de archivos

- **`/PROJECT_STATE.md`** (raiz): Estado real de ESTE repo (el framework como proyecto). Leer siempre.
- **`plantilla/PROJECT_STATE.md`**: Template con placeholders para proyectos nuevos. Vacio por diseno. NO refleja el estado de este repo.
- **`plantilla/AGENTS.md`**: Template con placeholders para proyectos nuevos. NO son las reglas de este repo.

## Que es este repo

Un framework agentico reutilizable. Contiene:

1. `plantilla/` — Estructura completa lista para copiar a un proyecto nuevo (via skill iniciar-proyecto).
2. `analisis/` — Documentos historicos de la extraccion desde el proyecto origen (entrevoces). Solo para contexto arqueologico.

## Reglas para trabajar en este repo

1. **No instanciar placeholders.** Los `{{PLACEHOLDER}}` en plantilla/ deben permanecer como estan. Son para proyectos que consuman la plantilla, no para este repo.
2. **Actualizar /PROJECT_STATE.md** tras cambios materiales (nuevo stack, skill agregado o eliminado, decision arquitectonica).
3. **Mantener coherencia interna.** Si se agrega un skill a un stack, verificar que el LEEME.md del stack lo refleja.
4. **No duplicar entre stacks.** Si un skill aplica a multiples stacks, evaluar si pertenece al core.
5. **Atribuir fuentes externas.** Si un skill se adapta de un plugin externo, documentar la fuente y licencia en el LEEME.md del stack.

## Idioma

- Documentacion y nombres de archivo: espanol.
- Excepciones: nombres impuestos por herramientas (AGENTS.md, SKILL.md, etc.) y terminos tecnicos universales.
- Misma convencion que plantilla/.agents/rules/excepciones_nominales.md.
