# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-26 (rev 16)
**Estado general:** Skills endurecidas para uso personal; pilotos y procedencia pendientes
**Fase activa:** Fase 6 — validacion funcional de Skills y stacks

## 1. Objetivo

Framework agentico reutilizable extraido del proyecto "entrevoces". Provee una plantilla completa (core + stacks + domain-packs) que un proyecto nuevo puede consumir mediante la CLI Python de la raiz.

## 2. Estructura del repo

```
agent-framework/
├── PROJECT_STATE.md          ← Estado real de ESTE repo (este archivo)
├── analisis/                 ← Documentos de extraccion (historico, no operativo)
│   ├── a_clasificacion_capas.md
│   ├── b_conflictos_redundancias.md
│   ├── c_estructura_plantilla.md
│   └── d_plan_migracion.md
└── plantilla/                ← La plantilla consumible por proyectos nuevos
    ├── AGENTS.md             (template con {{placeholders}})
    ├── PROJECT_STATE.md      (template vacio — NO es el estado de este repo)
    ├── .agents/
    │   ├── skills/
    │   │   ├── cerrar-modulo/
    │   │   ├── evaluar-agente/
    │   │   ├── iniciar-proyecto/
    │   │   ├── lecciones-aprendidas/
    │   │   └── stacks/
    │   └── rules/
    │       ├── claude.md
    │       └── excepciones_nominales.md
    ├── documentacion/
    └── opcional/
        └── delegar-entre-agentes/
```

## 3. Stacks disponibles (completos)

| Stack | Skills | Origen |
|---|---|---|
| `backend-fastapi` | fastapi-setup | Creado para el framework (uv, SQLAlchemy, Alembic, pytest) |
| `firmware-esp32` | desarrollar-firmware, diagnosticar-hardware | Extraido de entrevoces |
| `frontend-nextjs` | nextjs-fullstack, typescript-react | Creado para el framework |
| `ia-llm` | rag-local, fine-tuning-llm, agentes-multiagent | Creado para el framework |
| `mobile-flutter` | flutter-state-management, flutter-performance, flutter-animations | Adaptado de spjoshis/claude-code-plugins (licencia pendiente de verificacion) |

Cada stack tiene LEEME.md con reglas adicionales, terminos tecnicos y procedimiento de instalacion.

## 4. Decisiones vigentes

1. **Stacks por tecnologia, no por dominio.** La reorganizacion packs/ → stacks/ ya se aplico.
2. **Domain-packs como stubs.** No son activables desde iniciar-proyecto. Se materializan manualmente cuando un proyecto los necesite. Ejemplo: `firmware-esp32/domain-packs/audio-embebido/`.
3. **delegar-entre-agentes en opcional/.** Sin evidencia de uso real en entrevoces. Aspiracional, no core.
4. **Candidatos de plugins externos: vetting cerrado.** flutter-development, nodejs-development, rag-cli y custom-plugin-ai-engineer fueron evaluados. Los aprovechables se distribuyeron en los 4 stacks actuales; los descartados no se incluyeron.
5. **Lecciones aprendidas como skill de core**, no como documento suelto. Vive en `.agents/skills/lecciones-aprendidas/` con archivos de referencia por stack.
6. **Superpowers formalizados** en rules/claude.md §2 (brainstorming, TDD, depuracion 4 fases) + §3 (eficiencia de contexto).
7. **Convencion de idioma en 3 categorias** documentada en excepciones_nominales.md. ~20 terminos universales limpios de contaminacion de stack.
8. **Renombrado PROMPT_SISTEMA → SYSTEM_PROMPT** completado, sin roturas de referencias.
9. **Plan de correcciones formalizado.** `ESTADO_CORRECCIONES.md` conserva el avance, las evidencias, los bloqueos y el siguiente paso del endurecimiento hasta `v1.0.0`.
10. **Rama de estabilizacion aislada.** Las correcciones se realizan en `codex/estabilizacion-framework` para preservar el arbol de trabajo preexistente sin resets ni eliminaciones.
11. **Linea base versionada por grupos.** El core y los stacks se registraron en `1aeed87`; el inicializador alfa se registro en `f845050`. La documentacion del meta-repositorio se mantiene separada para facilitar la revision.
12. **Fase 1 completada localmente.** La rama local `main` rastrea `origin/main` y se valido mediante un clon temporal limpio. La rama de estabilizacion contiene correcciones posteriores que se integraran por fast-forward al cerrar la revision. La publicacion remota se difiere hasta cerrar seguridad y licencia.
13. **Licencia externa pendiente de verificacion.** La fuente atribuida al stack `mobile-flutter` no mostro una licencia primaria en el arbol publico revisado; no se asumira MIT para una eventual redistribucion comercial sin evidencia adicional.
14. **Skills congeladas por procedencia.** Por decision del usuario no se modifican, agregan ni eliminan Skills hasta completar el inventario de fuentes, versiones y licencias. Los riesgos se documentan en `ATRIBUCIONES.md`.
15. **Protecciones Git instaladas.** La raiz y `plantilla/` incluyen `.gitignore` y `.gitattributes`; `.env` queda ignorado, `.env.ejemplo` permanece versionable y los archivos de texto principales usan finales LF.
16. **Licencia raiz diferida.** No se aplicara una licencia global hasta separar el contenido original de las adaptaciones con derechos pendientes. La correccion tecnica continua sin tocar Skills.
17. **Contrato unico de placeholders.** `plantilla/configuracion_plantilla.json` declara los campos configurables y `scripts/validar_contrato_plantilla.py` comprueba su uso. Los alias duplicados se eliminaron fuera de Skills.
18. **Limite de congelacion respetado.** El contrato excluye `.agents/skills`; los placeholders operativos de esas rutas no se modifican ni se validan como configuracion inicial.
19. **Inicializador interno reconstruido.** `plantilla/scripts/inicializar_proyecto.py` consume el contrato, protege `.env`, separa nombre visible e identificador tecnico, conserva procedencia y rechaza reinicializaciones.
20. **Inmutabilidad de Skills comprobada.** Una prueba temporal comparo SHA-256 antes y despues de inicializar; todas las Skills permanecieron identicas.
21. **Creacion de un comando verificada.** `scripts/crear_proyecto.py` copia hacia un temporal, ejecuta el inicializador contractual y publica el destino solo al terminar. Rechaza sobrescrituras y conserva las Skills byte por byte.
22. **Wizard temporalmente no soportado para correcciones.** La Skill `iniciar-proyecto` permanece congelada; hasta completar su auditoria, la CLI Python es la ruta soportada para crear proyectos.
23. **Memoria operativa completa.** La plantilla incorpora plan de desarrollo, documentacion tecnica y guia de operacion. `scripts/verificar_memoria_proyecto.py` comprueba la existencia, el contenido y la ausencia de placeholders configurables pendientes en los documentos obligatorios.
24. **Prueba documental reproducible.** Un proyecto temporal se genero con 14 archivos configurados y cero pendientes; sus siete documentos obligatorios pasaron el verificador y las 32 huellas de Skills coincidieron con la plantilla.
25. **Verificacion estricta de pendientes.** El verificador distingue placeholders sin resolver y marcadores TODO creados por `--permitir-pendientes`; solo una memoria completamente configurada obtiene salida valida.
26. **README alineado con la implementacion.** La guia principal presenta el creador atomico como ruta soportada, incluye una configuracion de ejemplo, relega la copia manual a contingencia y no promete seleccion automatica de stacks.
27. **Fase documental cerrada.** Todos los documentos prometidos fuera de Skills existen y el flujo descrito se probo de punta a punta. El wizard permanece congelado y excluido del flujo soportado.
28. **Suite permanente incorporada.** `pruebas/prueba_creacion_proyecto.py` cubre creacion completa, pendientes, limpieza tras fallo, rechazo de sobrescritura, proteccion de `.env` e inmutabilidad de Skills con `unittest` y sin dependencias externas.
29. **Matriz de CI definida.** `.github/workflows/validacion.yml` ejecuta el contrato y la suite en Windows y Ubuntu con Python 3.9 y 3.12. Su aprobacion remota queda pendiente hasta publicar la rama y ejecutar GitHub Actions.
30. **Skills preservadas por prueba.** La suite calcula y compara SHA-256 del arbol congelado; no escribe ni corrige contenido bajo `.agents/skills`.
31. **Reproducibilidad desde Git comprobada.** Se creo un clon temporal limpio del commit `864ba88`; el contrato y las cuatro pruebas aprobaron fuera del arbol de trabajo. El clon se elimino despues de la comprobacion.
32. **Integracion local lineal.** Se comprobo que `main` era ancestro directo de `codex/estabilizacion-framework`, con siete commits adicionales y sin cambios de Skills respecto de `main`. La rama local `main` se adelanto por fast-forward sin eliminar ramas ni publicar cambios.
33. **Inventario congelado reproducible.** `scripts/inventariar_skills.py` registra 32 archivos, 17 manifiestos `SKILL.md`, tamaños, SHA-256 y declaraciones locales de procedencia en `auditoria/inventario_skills.json`. Una quinta prueba impide que el inventario quede desactualizado.
34. **Declaracion local insuficiente.** El analisis mecanico detecto una sola declaracion explicita de procedencia, en `mobile-flutter`; afirma MIT, pero esa afirmacion continua sin evidencia primaria verificada.
35. **Modificacion autorizada para uso personal.** El usuario autorizo mejorar las Skills sin eliminarlas. La restriccion anterior de congelacion queda reemplazada por una politica de cambios probados, inventariados y sin redistribucion mientras la procedencia siga incompleta.
36. **Skills criticas reconstruidas.** `iniciar-proyecto` ahora delega en la CLI Python, no duplica placeholders y no mueve ni borra Skills. `agentes-multiagent` prioriza soluciones simples, autorizacion externa al modelo, aislamiento real y evaluaciones adversariales.
37. **Guias tecnicas endurecidas.** FastAPI exige secretos sin valor predeterminado y lock validado; Next.js usa cache explicita; RAG y fine-tuning eliminan precios, modelos, VRAM y umbrales universales. Los nombres de negocio leen el idioma desde `AGENTS.md` en vez de placeholders no procesados.
38. **Validacion estructural completa.** Las 17 Skills aprobaron `quick_validate.py`. La suite tiene ocho pruebas y controla cantidad, frontmatter, inventario, copia byte por byte y ausencia de instrucciones obsoletas o destructivas.

## 5. Que falta

- **Validacion con proyecto real.** Ningun proyecto ha consumido la plantilla todavia. El primer uso real revelara friccion en el wizard de iniciar-proyecto, gaps en las reglas, y skills que sobran o faltan.
- **Stack backend-fastapi.** Creado con skill `fastapi-setup`. Sin validacion en proyecto real todavia.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **Estabilizacion previa al piloto.** Antes de consumir la plantilla en un proyecto real se deben corregir la linea base Git, la seguridad de `.env`, el contrato de placeholders, el inicializador y las referencias ausentes. El avance detallado vive en `ESTADO_CORRECCIONES.md`.

## 6. Siguiente paso logico

Ejecutar pilotos aislados de `iniciar-proyecto`, `fastapi-setup` y `agentes-multiagent`, comparando resultado, tiempo, errores y seguridad frente a una ejecucion sin Skill. Mantener bloqueada la redistribucion hasta completar procedencia y licencia.
