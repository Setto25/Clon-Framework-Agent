---
name: fastapi-setup
description: Configura proyectos FastAPI con uv, SQLAlchemy, Alembic y pytest mediante una estructura tipada y verificable. Usar al iniciar un backend nuevo o migrar un proyecto existente despues de confirmar sus versiones y restricciones.
---

# FastAPI Setup (con uv)

## Cuando usar

- Iniciar un proyecto FastAPI desde cero.
- Migrar un proyecto pip+venv existente a uv.
- Incorporar Alembic al proyecto (migraciones de base de datos).
- Definir la estructura de carpetas antes de escribir el primer endpoint.

## Decidir antes de configurar

Respetar el gestor existente cuando el proyecto ya tenga uno y su migracion no forme parte de la tarea. Usar uv cuando se haya elegido explicitamente o cuando el proyecto sea nuevo.

Antes de ejecutar comandos, comprobar la version instalada de Python y uv, leer `pyproject.toml` si existe y revisar el diff que producira la migracion. En CI se prefiere `uv sync --locked`: valida que `uv.lock` siga alineado con `pyproject.toml`. `--frozen` omite esa comprobacion y se reserva para capas parciales donde faltan metadatos del workspace.

## Paso 1: Inicializar proyecto

```bash
# Proyecto nuevo desde cero
uv init nombre-proyecto
cd nombre-proyecto

# Agregar dependencias de produccion
uv add fastapi "uvicorn[standard]" sqlalchemy alembic pydantic-settings email-validator

# Agregar dependencias de desarrollo
uv add --dev pytest pytest-asyncio pytest-cov httpx

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
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    api_secret_key: SecretStr

    model_config = {"env_file": ".env"}

settings = Settings()
```

```python
# app/core/database.py
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Aplica el ajuste unicamente a conexiones SQLite.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
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
- `uv.lock` se versiona y CI ejecuta `uv lock --check` o `uv sync --locked` para detectar divergencias.
- Los secretos son obligatorios y no tienen valores predeterminados utilizables. La aplicacion debe fallar al iniciar si falta uno.
- `uv run <comando>` en vez de activar el venv manualmente. El entorno esta aislado por defecto.
- Para tests con DB: usar SQLite en memoria en `conftest.py` (override de `get_db` con fixture).
- Los nombres de negocio respetan el idioma declarado en `AGENTS.md`.
