# Stack: backend-fastapi

**Tipo:** Stack tecnologico (Capa 2)
**Para:** APIs REST y servicios backend con FastAPI, SQLAlchemy y Alembic. Gestion de dependencias con uv.

## Que agrega al core

- Skills: `fastapi-setup`
- Patron router/schema/service como convencion de estructura
- uv como gestor de proyecto por defecto (en vez de pip+venv)

## Estructura

```
stacks/backend-fastapi/
├── LEEME.md
└── skills/
    └── fastapi-setup/       # Setup, estructura, Alembic, pydantic-settings, TDD con pytest
```

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

## Adaptacion a {{IDIOMA_NOMBRES}}

Los nombres del framework (`BaseModel`, `APIRouter`, `Depends`) se conservan en ingles. Los nombres de **negocio** del proyecto SI se escriben en {{IDIOMA_NOMBRES}}:

```python
# Correcto: API FastAPI en ingles + negocio en idioma del proyecto
class PedidoCrear(BaseModel): ...
router = APIRouter(prefix="/pedidos")

def crear_pedido(db: Session, datos: PedidoCrear): ...

# Incorrecto: todo en ingles cuando el proyecto usa español
class OrderCreate(BaseModel): ...
def create_order(db: Session, data: OrderCreate): ...
```

## Como instalar

La instalacion es automatica via `$iniciar-proyecto`. Si necesitas hacerlo manualmente:

```bash
mv .agents/skills/stacks/backend-fastapi/skills/fastapi-setup/ .agents/skills/
```

Luego agregar las reglas adicionales a la seccion correspondiente de `AGENTS.md`.
