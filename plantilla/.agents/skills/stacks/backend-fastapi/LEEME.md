# Stack: backend-fastapi

**Tipo:** Stack tecnologico (Capa 2)
**Para:** APIs REST y servicios backend con FastAPI, SQLAlchemy y Alembic. Gestion de dependencias con uv.

## Que ofrece el catalogo fuente

- Skill del stack: `fastapi-setup`
- Skill core complementaria: `seguridad-backend` para modelar amenazas, autorizacion y pruebas negativas antes de exponer la API
- Patron router/schema/service como convencion de estructura
- uv como gestor de proyecto por defecto (en vez de pip+venv)

## Estructura en el catalogo fuente

```
stacks/backend-fastapi/
├── LEEME.md
└── skills/
    └── fastapi-setup/       # Setup, estructura, Alembic, pydantic-settings, TDD con pytest
```

`seguridad-backend` vive en el core porque tambien aplica a futuros stacks backend. Se selecciona por nombre y no se duplica dentro de este stack.

## Reglas adicionales de implementacion

- Separar responsabilidades: routers manejan HTTP, services manejan logica, schemas validan datos.
- No acceder a la DB directamente desde los routers — siempre via services.
- Validar input en el boundary del sistema (el router), nunca en el service.
- No retornar modelos SQLAlchemy al cliente — siempre serializar via schema Pydantic.
- Usar `uv run` para todos los comandos del proyecto (pytest, alembic, uvicorn). No activar el venv manualmente.
- Commitear `uv.lock` al repo. No commitear `.env`.

## Terminos tecnicos del stack

Estos terminos se conservan en ingles dentro de proyectos que activen este stack:

| Termino | NO usar | Contexto |
|---|---|---|
| `router` | `enrutador` | Agrupacion de endpoints FastAPI |
| `schema` | `esquema` | Pydantic model de entrada/salida |
| `model` | `modelo` | SQLAlchemy ORM class |
| `endpoint` | — | Ruta de la API |
| `middleware` | — | Ya esta en core |
| `migration` | `migracion` (ambiguo) | Cuando es tecnico de Alembic |
| `fixture` | — | pytest |
| `lock file` | — | uv.lock |

## Adaptacion al idioma del proyecto

Los nombres del framework (`BaseModel`, `APIRouter`, `Depends`) se conservan en ingles. Los nombres de negocio respetan el idioma declarado en `AGENTS.md`:

```python
# Correcto: API FastAPI en ingles + negocio en idioma del proyecto
class PedidoCrear(BaseModel): ...
router = APIRouter(prefix="/pedidos")

def crear_pedido(db: Session, datos: PedidoCrear): ...

# Incorrecto: todo en ingles cuando el proyecto usa español
class OrderCreate(BaseModel): ...
def create_order(db: Session, data: OrderCreate): ...
```

## Como seleccionar

Desde la raiz de `agent-framework`, la Skill se confirma al crear la instancia:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill fastapi-setup
```

Antes de exponer la API a red o procesar identidades y datos sensibles, se confirman ambas Skills:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill fastapi-setup --skill seguridad-backend
```

No se mueven carpetas manualmente. En una instancia generada, este `LEEME.md` acompaña exclusivamente a las Skills del stack que fueron confirmadas.
