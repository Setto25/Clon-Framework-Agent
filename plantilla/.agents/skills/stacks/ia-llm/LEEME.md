# Stack: ia-llm

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos que integran modelos de lenguaje (LLM), agentes, RAG, tool-use o procesamiento de lenguaje natural.

## Que ofrece el catalogo fuente

- Skills: `rag-local`, `fine-tuning-llm`, `agentes-multiagent`
- Reglas adicionales de implementacion (ver abajo)
- Terminos tecnicos del stack

Una instancia generada contiene solamente las Skills confirmadas de esta lista.

## Estructura en el catalogo fuente

```
stacks/ia-llm/
├── LEEME.md
├── skills/
│   ├── rag-local/              # Pipeline RAG: chunk, embed, store, retrieve, augment
│   ├── fine-tuning-llm/        # Fine-tuning con LoRA/QLoRA: datos, config, entrenamiento, export
│   └── agentes-multiagent/     # Agentes autonomos: ReAct, Plan-and-Execute, multi-agente
└── domain-packs/               # Extensiones futuras (ej: eval-llm, deployment-llm)
```

## Reglas adicionales de implementacion

Estas reglas complementan la seccion "Forma de implementacion" del prompt base:

- Desacoplar proveedor de LLM detras de una interfaz. Cambiar de Claude a GPT o local no debe requerir reescribir logica de negocio.
- No hardcodear model IDs en el codigo. Usar variables de entorno o configuracion.
- Registrar en logs: modelo usado, version, tokens consumidos, latencia. Nunca loguear el contenido del prompt ni la respuesta completa.
- Validar la salida del LLM con schema tipado (Zod, Pydantic) antes de confiar en ella.
- Implementar fallback para cuando el LLM falla (timeout, rate limit, respuesta malformada).
- No enviar datos sensibles del usuario al LLM sin consentimiento explicito.
- Usar embeddings locales (sentence-transformers, Ollama) para desarrollo. Embeddings remotos (OpenAI, Cohere) solo si el caso de uso lo justifica.
- Mantener el vector store como dependencia inyectable — no acoplar la logica de retrieval a un proveedor especifico.

## Terminos tecnicos del stack

Estos terminos se conservan en ingles dentro de proyectos que activen este stack:

| Termino | NO usar | Contexto |
|---|---|---|
| `embedding` | `incrustacion` | Representacion vectorial |
| `vector store` | `almacen_vectorial` | Base de datos de embeddings |
| `RAG` | — | Retrieval Augmented Generation |
| `chunk` / `chunking` | `trozo` | Division de documentos |
| `retrieval` | `recuperacion` (ambiguo) | Busqueda semantica |
| `prompt` | — | Ya esta en core |
| `token` | — | Ya esta en core |
| `fine-tuning` | `ajuste_fino` | Entrenamiento especializado |
| `inference` | `inferencia` (aceptable) | Ejecucion del modelo |
| `hallucination` | `alucinacion` (aceptable) | Salida no factual |
| `grounding` | `anclaje` | Vincular a fuentes |
| `reranking` | `reordenamiento` | Post-retrieval scoring |
| `HyDE` | — | Hypothetical Document Embeddings |
| `tool-use` / `function calling` | — | Capacidad del LLM |
| `context window` | `ventana_de_contexto` | Limite de tokens |
| `temperature` | — | Parametro de generacion |
| `top-k` / `top-p` | — | Parametros de sampling |

## Adaptacion al idioma del proyecto

Los nombres de APIs y parametros de modelos se conservan en ingles. Los nombres de negocio respetan el idioma declarado en `AGENTS.md`:

```python
# Correcto: terminos LLM en ingles + negocio en idioma del proyecto
class PipelineRag:
    def recuperar_contexto(self, consulta: str) -> list[Fragmento]: ...
    def generar_respuesta(self, consulta: str, contexto: list[Fragmento]) -> Respuesta: ...

class AlmacenVectorial(Protocol):
    def buscar_similares(self, embedding: list[float], top_k: int) -> list[Resultado]: ...
```

## Como seleccionar

Desde la raiz de `agent-framework`, cada Skill se confirma por separado al crear la instancia:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill rag-local --skill agentes-multiagent
```

No se mueven carpetas manualmente. Este `LEEME.md` no implica que `fine-tuning-llm` u otra Skill hermana este instalada.
