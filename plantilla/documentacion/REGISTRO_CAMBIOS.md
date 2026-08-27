# Registro de cambios — {{NOMBRE_PROYECTO}}

Formato: una entrada por sesion de trabajo. Mas reciente primero.

---

## 2026-08-26 (rev 2) — Claude — Stack backend-fastapi + skill fastapi-setup

**Hito:** Nuevo stack disponible

**Archivos creados:**
- `.agents/skills/stacks/backend-fastapi/LEEME.md` — Descripcion del stack, reglas adicionales, terminos tecnicos, instrucciones de instalacion
- `.agents/skills/stacks/backend-fastapi/skills/fastapi-setup/SKILL.md` — Skill con uv como gestor por defecto, estructura router/schema/service, Alembic, pydantic-settings, TDD con pytest

**Archivos modificados:**
- `README.md` (raiz) — backend-fastapi agregado a tablas de inventario de skills y cobertura tecnologica; FastAPI/SQLAlchemy removido de "sin skill dedicado"
- `/PROJECT_STATE.md` — backend-fastapi agregado a tabla de stacks disponibles; item "falta" actualizado
- `documentacion/REGISTRO_CAMBIOS.md` — esta entrada

**Decisiones tomadas:**
- uv como gestor de proyecto/dependencias por defecto (no pip/poetry): velocidad, uv.lock confiable, sin dependencias extra en produccion.
- Un solo skill `fastapi-setup` cubre setup + estructura + Alembic + config. Patron unico, no dividir en skills separados hasta que un proyecto real lo justifique.
- `sessionmaker(autocommit=False, autoflush=False, bind=engine)` en lugar de solo `bind=engine` para compatibilidad SQLAlchemy 2.0.
- `connect_args={"check_same_thread": False}` solo para SQLite (detectado dinamicamente en database.py).

**Pendiente para siguiente sesion:**
- Validar plantilla con un proyecto real (primer uso del wizard iniciar-proyecto)

---

## 2026-08-26 — Claude — Skill lecciones-aprendidas + actualizacion INDICE_LECTURA_AGENTES

**Hito:** Consolidacion del framework

**Archivos creados:**
- `.agents/skills/lecciones-aprendidas/SKILL.md` — Skill de memoria persistente de errores resueltos con dificultad
- `.agents/skills/lecciones-aprendidas/referencias/backend-fastapi.md` — Archivo de referencia (vacio)
- `.agents/skills/lecciones-aprendidas/referencias/mobile-flutter.md` — Archivo de referencia (vacio)
- `.agents/skills/lecciones-aprendidas/referencias/frontend-nextjs.md` — Archivo de referencia (vacio)
- `.agents/skills/lecciones-aprendidas/referencias/firmware-esp32.md` — Archivo de referencia (vacio)
- `.agents/skills/lecciones-aprendidas/referencias/ia-llm.md` — Archivo de referencia (vacio)

**Archivos modificados:**
- `.agents/rules/claude.md` — Nueva §9 "Lecciones aprendidas": regla de registro obligatorio tras 2+ intentos fallidos. §9 anterior renumerada a §10.
- `documentacion/INDICE_LECTURA_AGENTES.md` — Reescrito: rules/claude.md agregado a lectura obligatoria, seccion condicional expandida (excepciones_nominales, lecciones-aprendidas), nota sobre mecanismo propio de descubrimiento de skills.

**Decisiones tomadas:**
- Lecciones-aprendidas es un skill de core (no un documento suelto) porque necesita protocolo de consulta/registro y archivos de referencia por stack.
- Se registra solo cuando la causa raiz no era deducible del mensaje de error (evita ruido con errores triviales).
- INDICE_LECTURA_AGENTES no lista skills exhaustivamente — tienen su propio mecanismo via metadata en SKILL.md.

**Pendiente para siguiente sesion:**
- Validar plantilla con un proyecto real (primer uso del wizard iniciar-proyecto)
- Evaluar si se necesita stack backend-fastapi

---

## [Fecha] — Agente — Resumen de 1 linea

**Hito:** Hx  
**Archivos modificados:**
- `ruta/archivo.ext` — que cambio

**Decisiones tomadas:**
- Decision y razon breve

**Pendiente para siguiente sesion:**
- Tarea concreta
