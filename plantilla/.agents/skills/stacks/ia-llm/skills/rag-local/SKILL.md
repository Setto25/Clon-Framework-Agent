---
name: rag-local
description: Pipeline de Retrieval Augmented Generation local. Cubre chunking, embeddings, vector store, retrieval y augmentation del prompt. Agnostico de proveedor con matriz de decision para elegir componentes. Usar cuando se necesite que un LLM responda con conocimiento de documentos propios.
---

# RAG Local

## Cuando usar

- El LLM necesita responder con informacion de documentos propios (no en su entrenamiento).
- Se quiere reducir alucinaciones anclando respuestas a fuentes verificables.
- Se tiene un corpus de documentos (PDFs, markdown, codigo, wikis) que cambia con el tiempo.
- Se necesita busqueda semantica sobre contenido propio.

## Cuando NO usar

- El corpus cabe completo en el context window del modelo (< 100k tokens) — pasar directo es mas simple.
- Se necesita razonamiento sobre relaciones entre documentos (mejor: grafos de conocimiento).
- Los documentos cambian cada minuto (mejor: busqueda en tiempo real, no indexacion batch).

## Pipeline RAG (5 fases)

```
Documentos → [1. Chunk] → [2. Embed] → [3. Store] → ...
                                                        ↓
Consulta → [2. Embed] → [4. Retrieve] → [5. Augment + Generate] → Respuesta
```

## Fase 1: Chunking (division de documentos)

### Criterio de seleccion

| Estrategia | Usar cuando | Chunk size tipico |
|---|---|---|
| Por parrafos | Documentos narrativos (blogs, manuales) | 500-1000 tokens |
| Por secciones (headers) | Docs con estructura clara (markdown, wikis) | Variable |
| Por ventana deslizante + overlap | Texto sin estructura | 500 tokens, 50 overlap |
| Por unidad semantica | Codigo fuente (funciones, clases) | 1 funcion/clase |

### Implementacion (ejemplo con langchain)

```python
# Test primero
def test_chunking_respeta_limites():
    texto = "palabra " * 2000  # ~2000 tokens
    fragmentos = fragmentar_documento(texto, tamano=500, overlap=50)

    assert all(len(f.contenido.split()) <= 550 for f in fragmentos)
    assert len(fragmentos) > 1
    # Verificar overlap
    assert fragmentos[0].contenido[-50:] in fragmentos[1].contenido[:100]


# Implementacion
from dataclasses import dataclass

@dataclass
class Fragmento:
    contenido: str
    metadata: dict  # origen, pagina, seccion, etc.

def fragmentar_documento(
    texto: str,
    tamano: int = 500,
    overlap: int = 50,
) -> list[Fragmento]:
    """Divide texto en fragmentos con overlap."""
    palabras = texto.split()
    fragmentos = []
    inicio = 0

    while inicio < len(palabras):
        fin = inicio + tamano
        contenido = " ".join(palabras[inicio:fin])
        fragmentos.append(Fragmento(
            contenido=contenido,
            metadata={"inicio": inicio, "fin": min(fin, len(palabras))},
        ))
        inicio += tamano - overlap

    return fragmentos
```

## Fase 2: Embeddings

### Matriz de decision

| Proveedor | Local | Costo | Calidad | Dimensiones | Usar cuando |
|---|---|---|---|---|---|
| `sentence-transformers` (all-MiniLM-L6-v2) | Si | Gratis | Buena | 384 | Desarrollo, corpus < 100k docs |
| `sentence-transformers` (multilingual-e5-large) | Si | Gratis | Alta | 1024 | Corpus multilingue |
| Ollama (nomic-embed-text) | Si | Gratis | Alta | 768 | Produccion local, GPU disponible |
| OpenAI (text-embedding-3-small) | No | $0.02/1M tokens | Alta | 1536 | Produccion cloud, presupuesto disponible |
| Cohere (embed-v3) | No | $0.1/1M tokens | Muy alta | 1024 | Maxima calidad, multilingue |

### Implementacion (interfaz desacoplada)

```python
# Test primero
def test_embedding_genera_vector_correcto():
    generador = crear_generador_embeddings("sentence-transformers")
    vector = generador.generar("Hola mundo")

    assert isinstance(vector, list)
    assert len(vector) == 384  # dimensiones de all-MiniLM-L6-v2
    assert all(isinstance(v, float) for v in vector)


# Interfaz
from typing import Protocol

class GeneradorEmbeddings(Protocol):
    def generar(self, texto: str) -> list[float]: ...
    def generar_batch(self, textos: list[str]) -> list[list[float]]: ...
    @property
    def dimensiones(self) -> int: ...


# Implementacion con sentence-transformers (local)
from sentence_transformers import SentenceTransformer

class EmbeddingsSentenceTransformers:
    def __init__(self, modelo: str = "all-MiniLM-L6-v2"):
        self._modelo = SentenceTransformer(modelo)
        self._dimensiones = self._modelo.get_sentence_embedding_dimension()

    @property
    def dimensiones(self) -> int:
        return self._dimensiones

    def generar(self, texto: str) -> list[float]:
        return self._modelo.encode(texto).tolist()

    def generar_batch(self, textos: list[str]) -> list[list[float]]:
        return self._modelo.encode(textos).tolist()


# Factory
def crear_generador_embeddings(tipo: str = "sentence-transformers") -> GeneradorEmbeddings:
    match tipo:
        case "sentence-transformers":
            return EmbeddingsSentenceTransformers()
        case _:
            raise ValueError(f"Generador no soportado: {tipo}")
```

## Fase 3: Vector Store

### Matriz de decision

| Store | Modo | Persistencia | Filtros metadata | Client TS | Usar cuando |
|---|---|---|---|---|---|
| ChromaDB | Embedded | Disco | Si | No (REST) | Prototipos, Python-only, < 1M docs |
| Qdrant | Embedded/Server | Disco/Docker | Avanzados | Si (nativo) | Produccion, filtros complejos, Next.js |
| LanceDB | Embedded | Disco (columnar) | Si | Si (nativo) | Zero-infra, datasets grandes |
| FAISS | Libreria | Manual (pickle) | No | No | Maxima velocidad, sin filtros |
| pgvector | Extension PG | PostgreSQL | Via SQL | Via driver | Ya usas PostgreSQL |

### Implementacion (interfaz desacoplada + ejemplo ChromaDB)

```python
# Test primero
def test_almacenar_y_buscar():
    store = crear_vector_store("chromadb", ruta="/tmp/test_vectors")
    store.agregar(
        ids=["doc1"],
        embeddings=[[0.1] * 384],
        metadatas=[{"origen": "test.md"}],
        documentos=["Contenido de prueba"],
    )

    resultados = store.buscar(embedding=[0.1] * 384, top_k=1)
    assert len(resultados) == 1
    assert resultados[0].id == "doc1"
    assert resultados[0].documento == "Contenido de prueba"


# Interfaz
@dataclass
class ResultadoBusqueda:
    id: str
    documento: str
    metadata: dict
    distancia: float

class AlmacenVectorial(Protocol):
    def agregar(self, ids: list[str], embeddings: list[list[float]],
                metadatas: list[dict], documentos: list[str]) -> None: ...
    def buscar(self, embedding: list[float], top_k: int = 5,
               filtro: dict | None = None) -> list[ResultadoBusqueda]: ...
    def eliminar(self, ids: list[str]) -> None: ...


# Implementacion ChromaDB
import chromadb

class AlmacenChromaDB:
    def __init__(self, ruta: str, coleccion: str = "documentos"):
        self._client = chromadb.PersistentClient(path=ruta)
        self._coleccion = self._client.get_or_create_collection(coleccion)

    def agregar(self, ids, embeddings, metadatas, documentos):
        self._coleccion.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documentos,
        )

    def buscar(self, embedding, top_k=5, filtro=None):
        kwargs = {"query_embeddings": [embedding], "n_results": top_k}
        if filtro:
            kwargs["where"] = filtro

        resultados = self._coleccion.query(**kwargs)
        return [
            ResultadoBusqueda(
                id=resultados["ids"][0][i],
                documento=resultados["documents"][0][i],
                metadata=resultados["metadatas"][0][i],
                distancia=resultados["distances"][0][i],
            )
            for i in range(len(resultados["ids"][0]))
        ]

    def eliminar(self, ids):
        self._coleccion.delete(ids=ids)
```

## Fase 4: Retrieval (busqueda)

```python
# Test primero
def test_recuperar_contexto_relevante():
    pipeline = PipelineRetrieval(
        generador=crear_generador_embeddings("sentence-transformers"),
        store=crear_vector_store("chromadb", ruta="/tmp/test"),
    )
    # Pre-cargar documentos
    pipeline.indexar_documentos([
        Fragmento("Python es un lenguaje de programacion", {"origen": "intro.md"}),
        Fragmento("La receta de paella lleva arroz", {"origen": "cocina.md"}),
    ])

    resultados = pipeline.recuperar("que es Python", top_k=1)
    assert "Python" in resultados[0].documento
    assert "paella" not in resultados[0].documento


# Implementacion
class PipelineRetrieval:
    def __init__(self, generador: GeneradorEmbeddings, store: AlmacenVectorial):
        self._generador = generador
        self._store = store

    def indexar_documentos(self, fragmentos: list[Fragmento]) -> None:
        embeddings = self._generador.generar_batch([f.contenido for f in fragmentos])
        self._store.agregar(
            ids=[f"frag_{i}" for i in range(len(fragmentos))],
            embeddings=embeddings,
            metadatas=[f.metadata for f in fragmentos],
            documentos=[f.contenido for f in fragmentos],
        )

    def recuperar(self, consulta: str, top_k: int = 5, filtro: dict | None = None) -> list[ResultadoBusqueda]:
        embedding_consulta = self._generador.generar(consulta)
        return self._store.buscar(embedding_consulta, top_k=top_k, filtro=filtro)
```

## Fase 5: Augmentation (enriquecer el prompt)

```python
def construir_prompt_rag(
    consulta: str,
    contexto: list[ResultadoBusqueda],
    instruccion_sistema: str = "",
) -> str:
    """Construye el prompt enriquecido con contexto recuperado."""
    fragmentos_texto = "\n\n---\n\n".join(
        f"[Fuente: {r.metadata.get('origen', 'desconocido')}]\n{r.documento}"
        for r in contexto
    )

    return f"""{instruccion_sistema}

Usa UNICAMENTE la siguiente informacion para responder. Si la respuesta no esta en el contexto, di que no tienes informacion suficiente.

## Contexto recuperado

{fragmentos_texto}

## Consulta del usuario

{consulta}"""
```

## Estructura de archivos recomendada

```
lib/
├── rag/
│   ├── __init__.py
│   ├── tipos.py                # Fragmento, ResultadoBusqueda, interfaces Protocol
│   ├── chunking.py             # fragmentar_documento()
│   ├── embeddings.py           # GeneradorEmbeddings + implementaciones
│   ├── vector_store.py         # AlmacenVectorial + implementaciones
│   ├── retrieval.py            # PipelineRetrieval
│   └── prompt_builder.py       # construir_prompt_rag()
data/
├── documentos/                 # Fuentes originales (PDFs, .md, etc.)
└── vectores/                   # Persistencia del vector store (gitignore)
```

## Reglas

- Desacoplar cada fase detras de una interfaz (Protocol). Cambiar de ChromaDB a Qdrant no debe tocar la logica de retrieval.
- Embeddings locales para desarrollo (sentence-transformers). Remotos solo si la calidad lo justifica y el presupuesto lo permite.
- No indexar datos sensibles sin consentimiento. El vector store puede ser leido por cualquiera con acceso al disco.
- Incluir metadata de origen en cada fragmento — sin ella no hay citacion posible.
- Validar que el chunking no corte a mitad de oracion o de bloque de codigo.
- No confiar ciegamente en la distancia del vector — un resultado "cercano" puede ser irrelevante. Considerar reranking si la precision importa.
- El prompt de augmentation debe instruir al LLM a NO inventar fuera del contexto proporcionado.
- Gitignore la carpeta de vectores — son derivados, no fuente.
- Test de integracion minimo: indexar 3 documentos conocidos, buscar, verificar que el correcto aparece primero.
