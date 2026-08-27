---
name: typescript-react
description: Patrones de TypeScript estricto en React y Next.js. Cubre tipado de props, Server Components, hooks custom, generics, inferencia y configuracion estricta. Usar cuando se necesite definir tipos, crear hooks tipados, o resolver errores de tipos en un proyecto Next.js/React.
---

# TypeScript en React / Next.js

## Cuando usar

- Definir tipos para props, estado o respuestas de API.
- Crear hooks custom con tipos genericos.
- Tipar Server Components, Server Actions y Route Handlers.
- Resolver errores de tipos (TS2322, TS2345, etc.).
- Configurar `tsconfig.json` para maxima seguridad.

## Configuracion base estricta

```json
// tsconfig.json — opciones criticas
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

**Regla**: nunca usar `any`. Si no sabes el tipo, usar `unknown` y narrowing.

## Patron 1: Props de componente

```typescript
// Tipos explicitos — no inferir de defaultProps
interface PropsTarjetaProducto {
  producto: Producto;
  variante?: 'compacta' | 'completa';
  alClickear?: (id: string) => void;
}

export function TarjetaProducto({ producto, variante = 'compacta', alClickear }: PropsTarjetaProducto) {
  return (
    <article onClick={() => alClickear?.(producto.id)}>
      <h3>{producto.nombre}</h3>
      {variante === 'completa' && <p>{producto.descripcion}</p>}
      <span>${producto.precio}</span>
    </article>
  );
}
```

### Con children tipado

```typescript
interface PropsContenedor {
  children: React.ReactNode;
  className?: string;
}

// Para children especificos:
interface PropsLista<T> {
  items: T[];
  renderItem: (item: T, indice: number) => React.ReactNode;
}

export function Lista<T>({ items, renderItem }: PropsLista<T>) {
  return <ul>{items.map((item, i) => <li key={i}>{renderItem(item, i)}</li>)}</ul>;
}
```

## Patron 2: Server Components y Actions tipados

```typescript
// Server Component — el return type es JSX implicito, params si necesitan tipo
interface PropsDetalle {
  params: Promise<{ id: string }>;
}

export default async function PaginaDetalle({ params }: PropsDetalle) {
  const { id } = await params;
  const producto = await obtenerProductoPorId(id);
  if (!producto) notFound();
  return <DetalleProducto producto={producto} />;
}

// Server Action — tipar input Y output
interface ResultadoAccion {
  exito: boolean;
  errores?: Record<string, string[]>;
  datos?: { id: string };
}

export async function crearProducto(formData: FormData): Promise<ResultadoAccion> {
  const parsed = esquemaProducto.safeParse({
    nombre: formData.get('nombre'),
    precio: formData.get('precio'),
  });

  if (!parsed.success) {
    return { exito: false, errores: parsed.error.flatten().fieldErrors };
  }

  const nuevo = await repositorio.crear(parsed.data);
  revalidatePath('/productos');
  return { exito: true, datos: { id: nuevo.id } };
}
```

## Patron 3: Hooks custom tipados

### Test primero

```typescript
import { renderHook, act } from '@testing-library/react';
import { usarPaginacion } from '@/hooks/usar-paginacion';

describe('usarPaginacion', () => {
  it('inicia en pagina 1', () => {
    const { result } = renderHook(() => usarPaginacion({ total: 50, porPagina: 10 }));
    expect(result.current.paginaActual).toBe(1);
    expect(result.current.totalPaginas).toBe(5);
  });

  it('avanza a la siguiente pagina', () => {
    const { result } = renderHook(() => usarPaginacion({ total: 50, porPagina: 10 }));
    act(() => result.current.siguiente());
    expect(result.current.paginaActual).toBe(2);
  });

  it('no avanza mas alla del total', () => {
    const { result } = renderHook(() => usarPaginacion({ total: 10, porPagina: 10 }));
    act(() => result.current.siguiente());
    expect(result.current.paginaActual).toBe(1); // solo hay 1 pagina
  });
});
```

### Implementacion

```typescript
// hooks/usar-paginacion.ts
import { useState, useMemo, useCallback } from 'react';

interface OpcionesPaginacion {
  total: number;
  porPagina: number;
  paginaInicial?: number;
}

interface ResultadoPaginacion {
  paginaActual: number;
  totalPaginas: number;
  siguiente: () => void;
  anterior: () => void;
  irA: (pagina: number) => void;
  indiceInicio: number;
  indiceFin: number;
}

export function usarPaginacion({
  total,
  porPagina,
  paginaInicial = 1,
}: OpcionesPaginacion): ResultadoPaginacion {
  const [paginaActual, setPaginaActual] = useState(paginaInicial);
  const totalPaginas = useMemo(() => Math.ceil(total / porPagina), [total, porPagina]);

  const siguiente = useCallback(() => {
    setPaginaActual((p) => Math.min(p + 1, totalPaginas));
  }, [totalPaginas]);

  const anterior = useCallback(() => {
    setPaginaActual((p) => Math.max(p - 1, 1));
  }, []);

  const irA = useCallback((pagina: number) => {
    setPaginaActual(Math.max(1, Math.min(pagina, totalPaginas)));
  }, [totalPaginas]);

  return {
    paginaActual,
    totalPaginas,
    siguiente,
    anterior,
    irA,
    indiceInicio: (paginaActual - 1) * porPagina,
    indiceFin: Math.min(paginaActual * porPagina, total),
  };
}
```

## Patron 4: Generics reutilizables

```typescript
// Respuesta de API generica
interface RespuestaApi<T> {
  datos: T;
  meta?: { total: number; pagina: number };
}

// Fetch tipado
async function fetchApi<T>(ruta: string): Promise<RespuestaApi<T>> {
  const res = await fetch(`${process.env.API_URL}${ruta}`);
  if (!res.ok) throw new Error(`Error ${res.status}: ${ruta}`);
  return res.json();
}

// Uso
const { datos: productos } = await fetchApi<Producto[]>('/productos');
const { datos: usuario } = await fetchApi<Usuario>('/usuarios/123');
```

```typescript
// Componente generico de lista con seleccion
interface PropsListaSeleccionable<T> {
  items: T[];
  obtenerClave: (item: T) => string;
  renderItem: (item: T, seleccionado: boolean) => React.ReactNode;
  alSeleccionar: (item: T) => void;
  seleccionActual?: string;
}

export function ListaSeleccionable<T>({
  items,
  obtenerClave,
  renderItem,
  alSeleccionar,
  seleccionActual,
}: PropsListaSeleccionable<T>) {
  return (
    <ul>
      {items.map((item) => {
        const clave = obtenerClave(item);
        return (
          <li key={clave} onClick={() => alSeleccionar(item)}>
            {renderItem(item, clave === seleccionActual)}
          </li>
        );
      })}
    </ul>
  );
}
```

## Patron 5: Discriminated unions para estado

```typescript
// En vez de { loading: boolean; error: string | null; data: T | null }
type EstadoAsync<T> =
  | { tipo: 'inactivo' }
  | { tipo: 'cargando' }
  | { tipo: 'exito'; datos: T }
  | { tipo: 'error'; mensaje: string };

// El switch exhaustivo garantiza que se manejen todos los casos
function renderEstado<T>(estado: EstadoAsync<T>, renderDatos: (datos: T) => React.ReactNode) {
  switch (estado.tipo) {
    case 'inactivo':
      return null;
    case 'cargando':
      return <Spinner />;
    case 'exito':
      return renderDatos(estado.datos);
    case 'error':
      return <MensajeError mensaje={estado.mensaje} />;
  }
}
```

## Errores comunes y solucion

| Error | Causa | Solucion |
|---|---|---|
| `Type 'X' is not assignable to 'Y'` | Props mal tipadas o datos de API sin validar | Validar con Zod + inferir tipo: `z.infer<typeof esquema>` |
| `'children' is missing` | Falta `React.ReactNode` en interface | Agregar `children: React.ReactNode` a las props |
| `Parameter implicitly has 'any' type` | `strict: true` sin tipo explicito | Agregar tipo al parametro |
| Async component error | Falta `async` o tipo incorrecto de params | En Next.js 15+: `params` es `Promise<{...}>`, usar `await` |

## Reglas

- `strict: true` siempre. Ningun proyecto sin modo estricto.
- No usar `any` — usar `unknown` + type narrowing, o `z.infer<>` para datos externos.
- Tipar explicitamente: props de componentes, return de hooks, respuestas de API.
- No tipar lo que TS infiere correctamente (variables locales simples, return de funciones puras obvias).
- Nombres de tipos/interfaces en {{IDIOMA_NOMBRES}}: `PropsTarjetaProducto`, `EstadoAsync`, `ResultadoAccion`.
- Nombres de tipos del framework en ingles: `React.ReactNode`, `NextRequest`, `FormData`.
- Preferir `interface` para props y objetos de dominio. Usar `type` para unions y utilidades.
