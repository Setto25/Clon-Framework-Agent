# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-28 (rev 51)
**Estado general:** main publicada y reproducible mediante GitHub; uso conversacional y pilotos validados
**Fase activa:** Fase 7 — cierre de validacion local y preparacion de CI

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
│   ├── d_plan_migracion.md
│   └── historial_decisiones.md  ← 102 decisiones cronologicas extraidas de §4
└── plantilla/                ← La plantilla consumible por proyectos nuevos
    ├── AGENTS.md             (template con {{placeholders}})
    ├── PROJECT_STATE.md      (template vacio — NO es el estado de este repo)
    ├── .agents/
    │   ├── skills/
    │   │   ├── cerrar-modulo/
    │   │   ├── evaluar-agente/
    │   │   ├── iniciar-proyecto/
    │   │   ├── lecciones-aprendidas/
    │   │   ├── seguridad-backend/
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
| `backend-fastapi` | fastapi-setup; seguridad-backend como core complementaria | Creado para el framework (uv, SQLAlchemy, Alembic, pytest, OWASP) |
| `firmware-esp32` | desarrollar-firmware, diagnosticar-hardware | Extraido de entrevoces |
| `frontend-nextjs` | nextjs-fullstack, typescript-react | Creado para el framework |
| `ia-llm` | rag-local, fine-tuning-llm, agentes-multiagent | Creado para el framework |
| `mobile-flutter` | flutter-state-management, flutter-performance, flutter-animations | Adaptado de spjoshis/claude-code-plugins (licencia pendiente de verificacion) |

Cada stack tiene LEEME.md con reglas adicionales, terminos tecnicos y procedimiento de instalacion.

## 4. Decisiones vigentes

> Historial completo de las 102 decisiones cronologicas: `analisis/historial_decisiones.md`

### Arquitectura

- **Stacks por tecnologia, no por dominio.** Cada stack agrupa Skills por plataforma (FastAPI, Flutter, Next.js, ESP32, LLM).
- **Domain-packs como stubs.** No son activables desde `iniciar-proyecto`. Se materializan manualmente cuando un proyecto los necesite.
- **Core automatico minimo.** Todo proyecto recibe `cerrar-modulo`, `lecciones-aprendidas` y `probar-e2e`. Las demas se instalan con `--skill NOMBRE`.
- **`delegar-entre-agentes` en opcional.** Formaliza traspasos entre agentes (Claude, Antigravity, Codex). Se instala con `--skill delegar-entre-agentes`.
- **Recomendacion sin autorizacion implicita.** El agente puede proponer Skills, pero debe obtener confirmacion de nombres exactos antes de instalarlas.

### CLI y contrato

- **Contrato unico de placeholders.** `configuracion_plantilla.json` declara los campos; `validar_contrato_plantilla.py` comprueba su uso. Version de contrato: `2`.
- **Creacion atomica.** `crear_proyecto.py` copia a temporal, inicializa, valida y publica solo al terminar. Rechaza sobrescrituras, enlaces, artefactos generados y arboles no regulares.
- **Instalacion posterior transaccional.** `agregar_skills.py` incorpora Skills confirmadas sin reinicializar. Conserva existentes y actualiza `.estado-plantilla.json` atomicamente.
- **Piso Python 3.9.** Se evitan APIs posteriores; una prueba AST lo vigila. CI aprobada en 3.9 y 3.12.

### Seguridad y protecciones

- **Protecciones Git.** `.gitignore` y `.gitattributes` en raiz y `plantilla/`; `.env` ignorado; finales LF.
- **Convenciones sin proveedor supuesto.** Cada agente comprueba herramientas, sandbox y permisos observables en vez de asumir capacidades por marca.
- **Capacidades verificables por agente.** Los deltas de Antigravity, Claude y Codex no atribuyen acceso ni descubrimiento por suposicion.

### Procedencia y licencia

- **Licencia raiz diferida.** No se aplicara una licencia global hasta separar contenido original de adaptaciones con derechos pendientes.
- **Licencia externa `mobile-flutter` pendiente.** La fuente `spjoshis/claude-code-plugins` no mostro licencia verificable. Uso personal permitido; redistribucion bloqueada.
- **Modificacion autorizada para uso personal.** Se pueden mejorar Skills sin eliminarlas, conservando procedencia, inventario y pruebas. No redistribuir mientras la procedencia siga incompleta.

### Validacion

- **CI aprobada.** Matriz remota aprobo Windows y Ubuntu con Python 3.9 y 3.12. Version de plantilla: `0.2.0-alpha.10`.
- **Dos pilotos cerrados.** `piloto-inventario-api` (FastAPI + PostgreSQL) y `piloto-inventario-web` (Next.js). Fricciones sintetizadas en `auditoria/sintesis_pilotos.md`.
- **Main publicada.** 43 commits publicados por avance lineal hasta `aa55f03` en `origin/main`.

## 5. Que falta

- **Validacion con proyecto real.** Dos pilotos independientes completaron sus flujos locales, sus fricciones fueron sintetizadas y el validador frontend se ejecuto de extremo a extremo. Falta validar en CI remota.
- **Stack backend-fastapi.** El piloto uso `fastapi-setup` y valido setup, configuracion tipada, rutas, esquemas, servicio, migraciones, persistencia PostgreSQL y pruebas. Quedan autenticacion y autorizacion fuera de alcance hasta confirmar actores y exposicion.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **CI remota.** La matriz aprobo Windows y Ubuntu con Python 3.9 y 3.12 en la rama de estabilizacion.

## 6. Siguiente paso logico

Clonar o actualizar `main` desde GitHub en los equipos autorizados y usarla para instanciar proyectos. Si en el futuro se amplia la redistribucion, primero identificar el commit de origen o conseguir autorizacion del autor para `mobile-flutter`. Toda exposicion futura requiere definir actores, autenticacion y autorizacion.
