# Stack: frontend-nextjs

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos fullstack con Next.js (App Router) o Next.js como frontend con backend separado (ej: FastAPI).

## Que ofrece el catalogo fuente

- Skills: `nextjs-fullstack`, `typescript-react`
- Reglas adicionales de implementacion (ver abajo)
- Terminos tecnicos del stack

Una instancia generada puede contener una o ambas Skills, segun la seleccion confirmada.

## Estructura en el catalogo fuente

```
stacks/frontend-nextjs/
├── LEEME.md
├── skills/
│   ├── nextjs-fullstack/       # App Router, Server Components, Server Actions, API routes
│   └── typescript-react/       # TypeScript estricto en React/Next: tipos, generics, hooks
└── domain-packs/               # Extensiones futuras (ej: auth-nextauth, cms-headless)
```

## Reglas adicionales de implementacion

Estas reglas complementan la seccion "Forma de implementacion" del prompt base:

- Preferir Server Components por defecto. Usar `'use client'` solo cuando se necesite interactividad (estado, efectos, event handlers).
- No pasar datos serializables del servidor al cliente innecesariamente — fetch en el Server Component directamente.
- Usar Server Actions para mutaciones. No crear API routes para operaciones que solo consume el propio frontend.
- Colocar logica de negocio en `lib/` o `services/`, no en componentes ni en route handlers.
- Validar input en el boundary del sistema (Server Actions, API routes) con Zod u equivalente.
- No exponer secretos al cliente: `NEXT_PUBLIC_` solo para valores no sensibles.
- Usar `loading.tsx`, `error.tsx` y `not-found.tsx` del App Router en vez de estados manuales.
- Preferir `fetch` nativo con cache/revalidacion de Next.js sobre librerias de fetching del lado cliente.
- Tipar explicitamente props, return types de Server Actions, y schemas de validacion — no usar `any`.

## Terminos tecnicos del stack

Estos terminos se conservan en ingles dentro de proyectos que activen este stack:

| Termino | NO usar | Contexto |
|---|---|---|
| `Server Component` | `componente_servidor` | Arquitectura Next.js |
| `Client Component` | `componente_cliente` | Arquitectura Next.js |
| `Server Action` | `accion_servidor` | Mutaciones Next.js |
| `App Router` | `enrutador_app` | Sistema de rutas |
| `layout` | `disposicion` | Archivo de estructura |
| `middleware` | — | Ya esta en core |
| `hook` | `gancho` | Patron React |
| `props` | — | API de React |
| `state` | `estado` (ambiguo) | Cuando es tecnico de React |
| `context` | — | API de React |
| `SSR` / `SSG` / `ISR` | — | Estrategias de rendering |
| `RSC` | — | React Server Components |
| `hydration` | `hidratacion` | Proceso de activacion |
| `suspense` | — | API de React |
| `streaming` | — | Rendering incremental |
| `revalidate` | — | Cache de Next.js |
| `slug` | — | Parametro de ruta dinamica |

## Adaptacion al idioma del proyecto

Los nombres del framework (`useEffect`, `ServerComponent`, `revalidatePath`) se conservan en ingles. Los nombres de negocio respetan el idioma declarado en `AGENTS.md`:

```typescript
// Correcto: API Next.js en ingles + negocio en idioma del proyecto
export default function PaginaPedidos() { ... }
export async function crearPedido(datos: FormData) { ... }  // Server Action
function usarCarrito() { ... }  // hook custom

// Incorrecto: todo en ingles cuando el proyecto usa español
export default function OrdersPage() { ... }
export async function createOrder(data: FormData) { ... }
```

## Como seleccionar

Desde la raiz de `agent-framework`, cada Skill se confirma por separado al crear la instancia:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill nextjs-fullstack --skill typescript-react
```

No se mueven carpetas manualmente. Este `LEEME.md` no implica que todas las Skills del stack esten instaladas.
