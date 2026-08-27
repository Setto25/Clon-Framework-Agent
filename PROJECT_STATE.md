# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-26 (rev 10)
**Estado general:** Plantilla funcional con memoria operativa verificable
**Fase activa:** Fase 5 — documentos y referencias externas a Skills

## 1. Objetivo

Framework agentico reutilizable extraido del proyecto "entrevoces". Provee una plantilla completa (core + stacks + domain-packs) que cualquier proyecto nuevo puede consumir via el skill `iniciar-proyecto`.

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

## 5. Que falta

- **Validacion con proyecto real.** Ningun proyecto ha consumido la plantilla todavia. El primer uso real revelara friccion en el wizard de iniciar-proyecto, gaps en las reglas, y skills que sobran o faltan.
- **Stack backend-fastapi.** Creado con skill `fastapi-setup`. Sin validacion en proyecto real todavia.
- **Automatizacion del wizard.** `iniciar-proyecto` existe como SKILL.md pero no como script ejecutable. Es manual (el agente sigue los pasos).
- **Estabilizacion previa al piloto.** Antes de consumir la plantilla en un proyecto real se deben corregir la linea base Git, la seguridad de `.env`, el contrato de placeholders, el inicializador y las referencias ausentes. El avance detallado vive en `ESTADO_CORRECCIONES.md`.

## 6. Siguiente paso logico

Corregir el README para documentar la CLI Python como ruta soportada, eliminar inventarios contradictorios y señalar expresamente el estado congelado del wizard.
