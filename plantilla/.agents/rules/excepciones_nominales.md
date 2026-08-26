# Excepciones nominales documentadas

**Versión:** 1.0

## Propósito

Registra todos los nombres técnicos no configurables que se conservan como excepciones a la regla de "todos los nombres en {{IDIOMA_NOMBRES}}".

---

## Excepciones obligatorias por herramientas

### Antigravity / Codex

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `AGENTS.md` | Raíz | Antigravity exige este nombre para descubrimiento de reglas | Ninguna |
| `PROJECT_STATE.md` | Raíz | Antigravity exige este nombre para descubrimiento de estado | Ninguna |
| `.agents/skills` | Directorio | Antigravity exige esta ruta para descubrimiento de Skills | Ninguna |
| `.agents/rules` | Directorio | Antigravity exige esta ruta para descubrimiento de reglas | Ninguna |
| `SKILL.md` | Cada Skill | Antigravity exige este nombre en cada carpeta de Skill | Ninguna |

### Gestión de entorno

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `.env` | Raíz | Convención estándar para variables locales | Ninguna |
| `.env.ejemplo` | Raíz | Convención de proyecto para plantilla de `.env` | Ninguna |

{{EXCEPCIONES_ADICIONALES}}

---

## Regla de adición de nuevas excepciones

Si se necesita agregar una nueva excepción:

1. **Verificar que sea obligatoria** — ¿La herramienta exige específicamente este nombre? ¿No hay alternativa configurable?
2. **Documentar la razón** — Herramienta, versión, referencia oficial.
3. **Agregar a este archivo** — En la sección apropiada con razón y alternativa.
4. **Comunicar** — Agregar entrada en `REGISTRO_CAMBIOS.md`.

---

## Referencia rápida

**Excepciones obligatorias (NO traducir):**
- `AGENTS.md`, `PROJECT_STATE.md`
- `.agents/skills`, `.agents/rules`, `SKILL.md`
- `.env`, `.env.ejemplo`

**TODO LO DEMÁS:** Debe estar en {{IDIOMA_NOMBRES}}.
