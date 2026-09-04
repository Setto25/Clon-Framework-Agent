# Excepciones nominales documentadas

**Versión:** 1.0

## Propósito

Registra todos los nombres técnicos no configurables que se conservan como excepciones a la regla de "todos los nombres en {{IDIOMA_NOMBRES}}".

---

## Categorias de excepcion

| Categoria | Criterio | Ejemplo |
|---|---|---|
| **Reservada para interoperabilidad** | Una herramienta o el contrato del framework usa ese nombre como interfaz estable | `AGENTS.md`, `SKILL.md`, `.env` |
| **Termino tecnico universal** | Concepto ampliamente reconocido en ingles por la comunidad; traducirlo dificulta busqueda, comunicacion o reconocimiento | `system_prompt`, `middleware`, `endpoint` |
| **Nombre de proyecto** | Todo lo demas: modulos, clases, variables, archivos, carpetas creados por el equipo | En {{IDIOMA_NOMBRES}} |

---

## Nombres reservados para interoperabilidad

### Memoria, reglas y Skills

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `AGENTS.md` | Raíz | Es la interfaz estable de instrucciones del repositorio y algunas herramientas la reconocen | Adjuntarlo como contexto cuando no exista descubrimiento verificable |
| `CLAUDE.md` | Raíz | Claude Code usa este nombre para cargar el contexto persistente del proyecto | Importar desde el los documentos canonicos en vez de duplicarlos |
| `PROJECT_STATE.md` | Raíz | Es la memoria persistente definida por el framework | Leerlo o adjuntarlo explicitamente al iniciar la sesion |
| `.agents/skills` | Directorio | Es el catalogo local neutral elegido por el framework | Instalar o adjuntar la Skill si la herramienta no descubre la ruta |
| `.agents/rules` | Directorio | Agrupa reglas compartidas sin ligarlas a un proveedor | Cargar manualmente las reglas relevantes |
| `.claude/skills` | Directorio | Claude Code descubre Skills de proyecto en esta ubicacion | Alojar wrappers generados que remiten a `.agents/skills` |
| `SKILL.md` | Cada Skill | Es el manifiesto estable usado para describir una Skill | Adaptar la integracion, sin renombrar la copia canonica |

### Gestión de entorno

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `.env` | Raíz | Convención estándar para variables locales | Ninguna |
| `.env.ejemplo` | Raíz | Convención de proyecto para plantilla de `.env` | Ninguna |

### Next.js y npm

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `package.json`, `package-lock.json` | Raiz del paquete | npm exige estos nombres para manifiesto y bloqueo reproducible | Ninguna |
| `tsconfig.json` | Raiz TypeScript | TypeScript y Next.js descubren este nombre por convencion | Ninguna |
| `next-env.d.ts` | Raiz Next.js | Next.js lo genera y puede incluir texto tecnico no editable | Mantenerlo generado e ignorado cuando las reglas de idioma impidan versionarlo |
| `layout.tsx`, `page.tsx` | Directorio `app/` | App Router usa estos nombres reservados para resolver rutas | Ninguna |
| `eslint.config.mjs` | Raiz del paquete | ESLint descubre este nombre de configuracion | Ninguna |

### Python, contenedores y despliegue

| Nombre | Ubicación | Razón | Alternativa |
|---|---|---|---|
| `pyproject.toml`, `uv.lock` | Raiz del paquete Python | Los gestores y estandares del ecosistema exigen o descubren estos nombres | Ninguna |
| `Dockerfile` | Raiz del contexto OCI | Docker y plataformas compatibles descubren este nombre por convencion | Indicar otro nombre explicitamente en cada comando de build |

{{EXCEPCIONES_ADICIONALES}}

---

## Terminos tecnicos universales (conservar en ingles)

Terminos que se mantienen en ingles porque traducirlos genera confusion, dificulta busquedas o rompe la comunicacion con documentacion externa.

### Criterio de inclusion

Un termino entra aqui si cumple AL MENOS DOS de estos:
1. La documentacion oficial del ecosistema lo usa exclusivamente en ingles.
2. Buscarlo en español no devuelve resultados utiles (ej: "indicador de estado" vs "endpoint").
3. El equipo lo usa en ingles al hablar, incluso en conversacion en español.
4. Traducirlo introduce ambiguedad (ej: "cola" puede ser queue o tail).

### Terminos aceptados

| Termino en ingles | NO usar | Donde aplica |
|---|---|---|
| `system_prompt` / `system prompt` | `prompt_del_sistema` | Archivos, variables, docs |
| `endpoint` | `punto_final` | URLs, rutas, docs |
| `middleware` | `software_intermedio` | Capas, archivos |
| `callback` | `retrollamada` | Codigo, docs |
| `handler` | `manejador` | Nombres de funciones |
| `token` | `ficha` | Auth, LLM |
| `webhook` | `gancho_web` | Integraciones |
| `payload` | `carga_util` | APIs, mensajes |
| `schema` | `esquema` | Bases de datos, validacion |
| `pipeline` | `tuberia` | CI/CD, procesamiento |
| `cache` | `almacen_temporal` | Codigo, infra |
| `runtime` | `tiempo_de_ejecucion` | Entorno, docs |
| `deploy` / `deployment` | `despliegue` | CI/CD, docs |
| `mock` | `simulacro` | Testing |
| `fixture` | `accesorio_de_prueba` | Testing |
| `plugin` | `complemento` | Extensiones |
| `driver` | `controlador` | Hardware, DB |
| `buffer` | `almacen_intermedio` | Audio, streams |
| `router` | `enrutador` | Backend, redes |
| `fallback` | `respaldo` | Logica de error |
| `log` / `logging` | `registro` (si es ambiguo) | Observabilidad |
| `MCP`, `tool`, `resource`, `prompt` | Traducciones que alteren el contrato | Model Context Protocol |
| `Streamable HTTP`, `JSON-RPC` | Traducciones del nombre protocolar | Transporte y mensajes MCP |
| `OAuth`, `bearer` | Traducciones del esquema | Autenticacion y autorizacion |
| `OCI`, `ASGI` | Traducciones de las siglas | Empaquetado y runtime de servidores |

### Regla de uso

- En **nombres de archivo y codigo** (variables, funciones, clases): usar el termino en ingles tal cual. Ej: `system_prompt.md`, `crear_endpoint()`, `middleware_auth`.
- En **documentacion narrativa**: se puede usar el termino en ingles inline sin traducir. Ej: "El middleware valida el token antes de pasar al handler."
- **Composicion mixta permitida**: combinar termino universal + palabra en {{IDIOMA_NOMBRES}}. Ej: `middleware_autenticacion`, `handler_pedidos`, `cache_sesiones`.

---

## Regla de adicion de nuevas excepciones

Si se necesita agregar una nueva excepción:

1. **Verificar que deba reservarse** — ¿Una herramienta o el contrato del framework usa específicamente este nombre? ¿Existe una alternativa configurable?
2. **Documentar la razón** — Herramienta, versión, referencia oficial.
3. **Agregar a este archivo** — En la sección apropiada con razón y alternativa.
4. **Comunicar** — Agregar entrada en `REGISTRO_CAMBIOS.md`.

---

## Referencia rápida

**Nombres reservados (NO traducir):**
- `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.md`
- `.agents/skills`, `.agents/rules`, `.claude/skills`, `SKILL.md`
- `.env`, `.env.ejemplo`

**TODO LO DEMÁS:** Debe estar en {{IDIOMA_NOMBRES}}.
