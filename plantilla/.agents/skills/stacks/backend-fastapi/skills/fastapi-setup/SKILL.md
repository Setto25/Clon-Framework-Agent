---
name: fastapi-setup
description: Setup y estructura de proyectos FastAPI con uv como gestor de dependencias. Cubre estructura de directorios, integracion con Alembic, patrones de router/schema/service y TDD con pytest. Usar al iniciar un proyecto FastAPI nuevo o al migrar de pip+venv a uv.
---

# FastAPI Setup (con uv)

## Cuando usar

- Iniciar un proyecto FastAPI desde cero.
- Migrar un proyecto pip+venv existente a uv.
- Incorporar Alembic al proyecto (migraciones de base de datos).
- Definir la estructura de carpetas antes de escribir el primer endpoint.

## Por que uv y no pip/poetry

| Criterio | pip + venv | poetry | uv |
|---|---|---|---|
| Velocidad de instalacion | Lenta (resolucion serial) | Media | **10-100x mas rapido** (escrito en Rust, paralelo) |
| Lock file confiable | No (requirements.txt manual) | Si (poetry.lock) | **Si (uv.lock)** — reproducible en CI |
| pyproject.toml nativo | Requiere setup.py extra | Si | **Si** — compatible con proyectos existentes |
| Sin herramienta extra en produccion | No (pip en imagen) | Requiere poetry | **Solo Python** — `uv sync --frozen` basta |
| Gestion de version de Python | No | Parcial | **Si** — `uv python install 3.12` |

Si el proyecto ya tiene `pyproject.toml`, uv lo adopta: `uv add` agrega dependencias al `[project.dependencies]` existente sin reescribir el archivo. No es necesario correr `uv init` en un proyecto ya inicializado.

## Paso 1: Inicializar proyecto

```bash
# Proyecto nuevo desde cero
uv init nombre-proyecto
cd nombre-proyecto

# Agregar dependencias de produccion
uv add fastapi "uvicorn[standard]" sqlalchemy alembic pydantic-settings email-validator

# Agregar dependencias de desarrollo
uv add --dev pytest pytest-asyncio httpx

# Instalar todo (genera uv.lock — commitear al repo)
uv sync
```

### Test de humo primero

```python
# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

### Implementacion minima

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

Correr tests: `uv run pytest`

## Estructura de proyecto recomendada

```
nombre-proyecto/
├── pyproject.toml          # Dependencias y metadata del proyecto
├── uv.lock                 # Lock file — commitear al repo
├── .python-version         # Version de Python fijada (ej: 3.12)
├── .env                    # Variables de entorno (no commitear)
├── alembic.ini             # Configuracion de Alembic
├── alembic/
│   ├── env.py              # Conecta Alembic con los modelos SQLAlchemy
│   └── versions/           # Migraciones generadas
├── app/
│   ├── main.py             # FastAPI app + inclusion de routers
│   ├── core/
│   │   ├── config.py       # Settings via pydantic-settings (lee .env)
│   │   └── database.py     # Engine, SessionLocal, Base
│   ├── routers/            # Un archivo por dominio (usuarios.py, productos.py)
│   ├── schemas/            # Pydantic models: entrada/salida de la API
│   ├── models/             # SQLAlchemy ORM models
│   └── services/           # Logica de negocio (sin dependencia de FastAPI)
└── tests/
    ├── conftest.py         # Fixtures: db en memoria, client de prueba
    └── test_*.py           # Un archivo de tests por router/servicio
```

## Patron 2: Router con schema y service

### Test primero

```python
# tests/test_usuarios.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_crear_usuario():
    response = client.post("/usuarios/", json={"nombre": "Ana", "email": "ana@ejemplo.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ana@ejemplo.com"
    assert "id" in data

def test_crear_usuario_email_invalido():
    response = client.post("/usuarios/", json={"nombre": "Ana", "email": "no-es-un-email"})
    assert response.status_code == 422
```

### Implementacion

```python
# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr

class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = {"from_attributes": True}  # Pydantic v2: permite construir desde ORM
```

```python
# app/services/usuario_service.py
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCrear

def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    usuario = Usuario(nombre=datos.nombre, email=datos.email)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
```

```python
# app/routers/usuarios.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.usuario import UsuarioCrear, UsuarioRespuesta
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    return usuario_service.crear_usuario(db, datos)
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import usuarios

app = FastAPI()
app.include_router(usuarios.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

## Patron 3: Alembic + migraciones

```bash
# Inicializar Alembic (solo una vez por proyecto)
uv run alembic init alembic

# Generar migracion desde cambios en modelos SQLAlchemy
uv run alembic revision --autogenerate -m "crear_tabla_usuarios"

# Aplicar migraciones pendientes
uv run alembic upgrade head

# Revertir ultima migracion
uv run alembic downgrade -1
```

`alembic/env.py` debe importar `Base` de los modelos para que `--autogenerate` los detecte:

```python
# alembic/env.py (fragmento clave — reemplazar target_metadata)
from app.core.database import Base
from app.models import usuario  # importar todos los modulos de modelos para registrarlos en Base

target_metadata = Base.metadata
```

## Patron 4: Config y base de datos

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    api_secret_key: str = "cambiar-en-produccion"

    model_config = {"env_file": ".env"}

settings = Settings()
```

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# connect_args solo necesario para SQLite (no thread-safe por defecto)
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Correr el proyecto

```bash
# Servidor de desarrollo (uv activa el venv automaticamente)
uv run uvicorn app.main:app --reload

# Tests (TestClient requiere httpx instalado como dev dependency)
uv run pytest

# Tests con cobertura
uv run pytest --cov=app --cov-report=term-missing
```

## Reglas

- Toda logica de negocio en `services/`, no en los routers. Los routers solo traducen HTTP ↔ dominio.
- Schemas Pydantic para entrada y salida. Nunca retornar modelos SQLAlchemy directamente al cliente.
- `uv.lock` se commitea al repo — garantiza reproducibilidad en CI y otros equipos.
- `uv run <comando>` en vez de activar el venv manualmente. El entorno esta aislado por defecto.
- Para tests con DB: usar SQLite en memoria en `conftest.py` (override de `get_db` con fixture).
- Nombres de variables, funciones y rutas en `{{IDIOMA_NOMBRES}}`.
