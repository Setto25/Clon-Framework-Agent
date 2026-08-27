---
name: nextjs-fullstack
description: Implementa flujos fullstack con Next.js App Router, Server Components, acciones, Route Handlers y cache explicita. Usar despues de confirmar la version instalada porque los valores predeterminados del framework cambian entre versiones mayores.
---

# Next.js Fullstack (App Router)

## Cuando usar

- Crear una pagina nueva con fetch de datos del servidor.
- Implementar una mutacion (crear, actualizar, eliminar).
- Definir API routes para consumo externo o integracion.
- Configurar caching, revalidacion o streaming.
- Estructurar layouts, loading states y error boundaries.

## Criterio de decision: donde poner la logica

| Necesidad | Solucion | NO usar |
|---|---|---|
| Mostrar datos | Server Component con fetch directo | `useEffect` + `useState` |
| Mutacion del propio frontend | Server Action | API route (innecesario) |
| API para consumo externo | Route Handler (`route.ts`) | Server Action (no es invocable externamente) |
| Estado interactivo (formulario, toggle) | Client Component con `'use client'` | Server Component |
| Logica de negocio reutilizable | `lib/servicios/` | Dentro del componente |

## Patron 1: Server Component con datos

### Test primero

```typescript
// __tests__/pagina-productos.test.tsx
import { render, screen } from '@testing-library/react';
import PaginaProductos from '@/app/productos/page';

// Mock del servicio
jest.mock('@/lib/servicios/productos', () => ({
  obtenerProductos: jest.fn().mockResolvedValue([
    { id: '1', nombre: 'Producto A', precio: 100 },
  ]),
}));

describe('PaginaProductos', () => {
  it('muestra la lista de productos', async () => {
    const Componente = await PaginaProductos();
    render(Componente);
    expect(screen.getByText('Producto A')).toBeInTheDocument();
  });
});
```

### Implementacion

```typescript
// app/productos/page.tsx
import { obtenerProductos } from '@/lib/servicios/productos';
import { TarjetaProducto } from '@/components/tarjeta-producto';

export default async function PaginaProductos() {
  const productos = await obtenerProductos();

  return (
    <section>
      <h1>Productos</h1>
      <div className="grid grid-cols-3 gap-4">
        {productos.map((producto) => (
          <TarjetaProducto key={producto.id} producto={producto} />
        ))}
      </div>
    </section>
  );
}
```

```typescript
// lib/servicios/productos.ts
import { Producto } from '@/lib/tipos';

export async function obtenerProductos(): Promise<Producto[]> {
  const res = await fetch(`${process.env.API_URL}/productos`, {
    next: { revalidate: 60 }, // ISR: revalida cada 60s
  });

  if (!res.ok) throw new Error('Error al obtener productos');
  return res.json();
}
```

## Patron 2: Server Action (mutacion)

### Test primero

```typescript
// __tests__/acciones/crear-pedido.test.ts
import { crearPedido } from '@/app/pedidos/acciones';
import { repositorioPedidos } from '@/lib/repositorios/pedidos';

jest.mock('@/lib/repositorios/pedidos');

describe('crearPedido', () => {
  it('crea un pedido con datos validos', async () => {
    const formData = new FormData();
    formData.set('productoId', '123');
    formData.set('cantidad', '2');

    (repositorioPedidos.crear as jest.Mock).mockResolvedValue({ id: 'nuevo-1' });

    const resultado = await crearPedido(formData);
    expect(resultado.exito).toBe(true);
    expect(repositorioPedidos.crear).toHaveBeenCalledWith({
      productoId: '123',
      cantidad: 2,
    });
  });

  it('rechaza datos invalidos', async () => {
    const formData = new FormData();
    formData.set('cantidad', '-1');

    const resultado = await crearPedido(formData);
    expect(resultado.exito).toBe(false);
    expect(resultado.errores).toBeDefined();
  });
});
```

### Implementacion

```typescript
// app/pedidos/acciones.ts
'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';
import { repositorioPedidos } from '@/lib/repositorios/pedidos';

const esquemaPedido = z.object({
  productoId: z.string().min(1),
  cantidad: z.coerce.number().int().positive(),
});

export async function crearPedido(formData: FormData) {
  const resultado = esquemaPedido.safeParse({
    productoId: formData.get('productoId'),
    cantidad: formData.get('cantidad'),
  });

  if (!resultado.success) {
    return { exito: false, errores: resultado.error.flatten().fieldErrors };
  }

  await repositorioPedidos.crear(resultado.data);
  revalidatePath('/pedidos');
  return { exito: true };
}
```

```typescript
// app/pedidos/formulario-pedido.tsx
'use client';

import { useActionState } from 'react';
import { crearPedido } from './acciones';

export function FormularioPedido({ productoId }: { productoId: string }) {
  const [estado, accion, pendiente] = useActionState(crearPedido, null);

  return (
    <form action={accion}>
      <input type="hidden" name="productoId" value={productoId} />
      <input type="number" name="cantidad" min="1" defaultValue="1" />
      <button type="submit" disabled={pendiente}>
        {pendiente ? 'Creando...' : 'Crear pedido'}
      </button>
      {estado?.errores && <p className="text-red-500">{JSON.stringify(estado.errores)}</p>}
    </form>
  );
}
```

## Patron 3: Route Handler (API para consumo externo)

```typescript
// app/api/productos/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { obtenerProductos, crearProducto } from '@/lib/servicios/productos';

export async function GET() {
  const productos = await obtenerProductos();
  return NextResponse.json(productos);
}

const esquemaCrear = z.object({
  nombre: z.string().min(2).max(100),
  precio: z.number().positive(),
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const resultado = esquemaCrear.safeParse(body);

  if (!resultado.success) {
    return NextResponse.json(
      { errores: resultado.error.flatten().fieldErrors },
      { status: 400 }
    );
  }

  const producto = await crearProducto(resultado.data);
  return NextResponse.json(producto, { status: 201 });
}
```

## Patron 4: Layout + Loading + Error

```typescript
// app/productos/layout.tsx
export default function LayoutProductos({ children }: { children: React.ReactNode }) {
  return (
    <div className="container mx-auto p-4">
      <nav>{/* navegacion de productos */}</nav>
      <main>{children}</main>
    </div>
  );
}

// app/productos/loading.tsx
export default function CargandoProductos() {
  return <div className="animate-pulse">Cargando productos...</div>;
}

// app/productos/error.tsx
'use client';

export default function ErrorProductos({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Error al cargar productos</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Reintentar</button>
    </div>
  );
}

// app/productos/not-found.tsx
export default function ProductoNoEncontrado() {
  return <h2>Producto no encontrado</h2>;
}
```

## Patron 5: Caching y revalidacion

```typescript
// Solicita cache persistente de forma explicita.
const datos = await fetch(url, { cache: 'force-cache' });

// Fetch con revalidacion por tiempo (ISR)
const datos = await fetch(url, { next: { revalidate: 60 } });

// Solicita datos nuevos en cada renderizado del servidor.
const datos = await fetch(url, { cache: 'no-store' });

// Revalidar por tag (on-demand)
// En el fetch:
const datos = await fetch(url, { next: { tags: ['productos'] } });
// En el Server Action tras mutacion:
import { revalidateTag } from 'next/cache';
revalidateTag('productos');

// Revalidar por path
import { revalidatePath } from 'next/cache';
revalidatePath('/productos');
```

No inferir cache a partir de ejemplos de otra version de Next.js. Comprobar la version del proyecto y la documentacion oficial de `fetch`, Route Handlers y revalidacion antes de elegir el comportamiento.

## Estructura de archivos recomendada

```
app/
├── layout.tsx                # Layout raiz
├── page.tsx                  # Pagina principal
├── productos/
│   ├── page.tsx              # Server Component — lista
│   ├── [id]/page.tsx         # Server Component — detalle
│   ├── loading.tsx           # Skeleton/spinner
│   ├── error.tsx             # Error boundary
│   └── acciones.ts           # Server Actions de este modulo
├── api/
│   └── productos/route.ts    # Solo si hay consumidores externos
lib/
├── tipos.ts                  # Tipos compartidos
├── servicios/                # Logica de negocio
│   └── productos.ts
├── repositorios/             # Acceso a datos (DB, API externa)
│   └── pedidos.ts
└── validaciones/             # Schemas Zod reutilizables
    └── pedido.ts
components/
├── ui/                       # Componentes genericos (Button, Card)
└── tarjeta-producto.tsx      # Componentes de dominio
```

## Reglas

- Server Component por defecto. `'use client'` solo con justificacion.
- Server Actions para mutaciones propias. API routes solo para consumo externo.
- Validar con Zod en el boundary (Server Action o Route Handler), no en el componente.
- Fetch de datos en Server Components, no en Client Components con `useEffect`.
- Usar los archivos convencionales del App Router (`loading.tsx`, `error.tsx`) en vez de logica manual.
- Los nombres de archivos, rutas y acciones de negocio respetan el idioma declarado en `AGENTS.md`.
