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
2. **Actualizar la documentacion en el mismo cambio.** Todo cambio material (stack o Skill agregado, eliminado, renombrado o movido; cambio de core; decision arquitectonica; cambio de contrato o flujo soportado) debe actualizar `/PROJECT_STATE.md` y toda referencia afectada en `README.md`.
3. **Mantener coherencia interna verificable.** Si cambia una Skill, se debe actualizar el `LEEME.md` del stack cuando corresponda, el inventario, el catalogo narrativo y las pruebas de coherencia documental. El cambio no se considera cerrado mientras la suite detecte referencias o cantidades obsoletas.
4. **No duplicar entre stacks.** Si un skill aplica a multiples stacks, evaluar si pertenece al core.
5. **Atribuir fuentes externas.** Si un skill se adapta de un plugin externo, documentar la fuente y licencia en el LEEME.md del stack y en `ATRIBUCIONES.md`. Si es contenido original, se debe mantener esa procedencia coherente con la documentacion del catalogo.
6. **Ejecutar el cierre automatico.** Antes de declarar terminado cualquier cambio, se debe ejecutar `python scripts/validar_cierre_cambio.py`. Si falla, el cambio permanece incompleto. No se sustituye esta puerta por una revision visual ni por pruebas parciales.
7. **Registrar dependencias mediante el contrato.** Todo archivo de `plantilla/scripts/` consumido por una Skill debe existir y figurar en `archivos_gestionados` de `plantilla/configuracion_plantilla.json`. No se deben crear listas paralelas de rutas administradas.

## Matriz obligatoria de impacto

| Si cambia | Tambien se debe revisar |
|---|---|
| Una Skill | Inventario, catalogo narrativo, README, estado, dependencias citadas y pruebas |
| Un script de plantilla | Contrato, archivos administrados, creacion, actualizacion y huellas |
| Una CLI | README, ayuda, pruebas, compatibilidad Python y estado |
| Un adaptador de modelo | Dependencia, documentacion, simulacion sin API y medicion real separada |
| Arquitectura, nombre o ruta | Estado, README, historial afectado y todas las referencias mediante busqueda global |

La documentacion no basta como registro operativo. El cierre debe demostrar que los proyectos nuevos reciben los archivos y que los proyectos existentes pueden actualizarlos sin sobrescribir cambios locales.

## Idioma

- Documentacion y nombres de archivo: espanol.
- Excepciones: nombres impuestos por herramientas (AGENTS.md, SKILL.md, etc.) y terminos tecnicos universales.
- Misma convencion que plantilla/.agents/rules/excepciones_nominales.md.
