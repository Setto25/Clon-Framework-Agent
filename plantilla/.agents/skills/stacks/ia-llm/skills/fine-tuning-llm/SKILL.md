---
name: fine-tuning-llm
description: Fine-tuning de modelos de lenguaje con LoRA/QLoRA y PEFT. Cubre preparacion de datos, configuracion de entrenamiento, evaluacion y exportacion. Usar cuando se necesite especializar un modelo base en un dominio o tarea especifica.
---

# Fine-tuning de LLMs

## Cuando usar

- El modelo base no rinde lo suficiente en una tarea especifica despues de optimizar el prompt.
- Se necesita consistencia de formato/estilo que prompting no puede garantizar.
- Se tiene un dataset de >100 ejemplos de alta calidad del dominio.
- Se quiere reducir latencia/costo usando un modelo mas pequeno especializado.

## Cuando NO usar

- El prompt engineering con few-shot ya da resultados aceptables — fine-tuning es caro y fragil.
- El dataset tiene <50 ejemplos — overfitting garantizado.
- Los datos cambian frecuentemente — el modelo se desactualiza rapido.
- Se necesita conocimiento factual actualizado — mejor RAG.
- No se tiene GPU con >= 16GB VRAM (ni acceso a cloud con GPU).

## Matriz de decision: metodo de fine-tuning

| Metodo | VRAM minima | Parametros entrenados | Calidad | Usar cuando |
|---|---|---|---|---|
| LoRA | 16 GB | 0.1-1% | Alta | Default — mejor balance costo/calidad |
| QLoRA (4-bit) | 8 GB | 0.1-1% | Alta (-2% vs LoRA) | GPU limitada, modelos grandes (>13B) |
| Full fine-tune | 4× modelo | 100% | Maxima | Presupuesto ilimitado, dataset enorme (>100k) |
| Adapters (IA3) | 12 GB | <0.01% | Media-alta | Multiples tareas con un solo modelo base |

## Matriz de decision: modelo base

| Modelo | Parametros | Licencia | Usar cuando |
|---|---|---|---|
| Llama 3.1 8B | 8B | Meta (comercial) | Default para tareas generales |
| Mistral 7B | 7B | Apache 2.0 | Latencia critica, razonamiento medio |
| Phi-3 mini | 3.8B | MIT | Edge/movil, tareas simples |
| Gemma 2 9B | 9B | Google (comercial) | Multilingue, instrucciones |
| Qwen 2.5 7B | 7B | Apache 2.0 | Codigo, multilingue (CN/ES/EN) |

## Pipeline de fine-tuning (4 fases)

```
[1. Preparar datos] → [2. Configurar entrenamiento] → [3. Entrenar + evaluar] → [4. Exportar + servir]
```

## Fase 1: Preparacion de datos

### Test primero

```python
def test_formato_dataset_valido():
    ejemplos = cargar_dataset("datos/entrenamiento.jsonl")

    assert len(ejemplos) >= 50
    for ejemplo in ejemplos:
        assert "instruccion" in ejemplo
        assert "respuesta" in ejemplo
        assert len(ejemplo["respuesta"]) > 0
        assert len(ejemplo["instruccion"]) > 0


def test_split_entrenamiento_evaluacion():
    ejemplos = [{"instruccion": f"q{i}", "respuesta": f"a{i}"} for i in range(100)]
    train, eval_ = dividir_dataset(ejemplos, ratio_eval=0.1)

    assert len(train) == 90
    assert len(eval_) == 10
    assert not set(e["instruccion"] for e in train) & set(e["instruccion"] for e in eval_)
```

### Implementacion

```python
from dataclasses import dataclass
from typing import Protocol
import json
import random


@dataclass
class EjemploFineTune:
    instruccion: str
    respuesta: str
    sistema: str = ""
    contexto: str = ""


class FormateadorDataset(Protocol):
    def formatear(self, ejemplo: EjemploFineTune) -> dict: ...


class FormateadorChatML:
    """Formato ChatML (compatible con la mayoria de modelos)."""

    def formatear(self, ejemplo: EjemploFineTune) -> dict:
        mensajes = []
        if ejemplo.sistema:
            mensajes.append({"role": "system", "content": ejemplo.sistema})
        contenido_usuario = ejemplo.instruccion
        if ejemplo.contexto:
            contenido_usuario += f"\n\nContexto:\n{ejemplo.contexto}"
        mensajes.append({"role": "user", "content": contenido_usuario})
        mensajes.append({"role": "assistant", "content": ejemplo.respuesta})
        return {"messages": mensajes}


def cargar_dataset(ruta: str) -> list[EjemploFineTune]:
    ejemplos = []
    with open(ruta) as f:
        for linea in f:
            datos = json.loads(linea)
            ejemplos.append(EjemploFineTune(**datos))
    return ejemplos


def dividir_dataset(
    ejemplos: list[EjemploFineTune],
    ratio_eval: float = 0.1,
    semilla: int = 42,
) -> tuple[list[EjemploFineTune], list[EjemploFineTune]]:
    rng = random.Random(semilla)
    mezclados = ejemplos.copy()
    rng.shuffle(mezclados)
    corte = int(len(mezclados) * (1 - ratio_eval))
    return mezclados[:corte], mezclados[corte:]
```

## Fase 2: Configuracion de entrenamiento (LoRA)

### Test primero

```python
def test_config_lora_valida():
    config = crear_config_lora(rango=16, alpha=32, dropout=0.05)

    assert config.r == 16
    assert config.lora_alpha == 32
    assert config.lora_dropout == 0.05
    assert "q_proj" in config.target_modules
    assert "v_proj" in config.target_modules


def test_config_entrenamiento_defaults():
    config = crear_config_entrenamiento(
        nombre_run="prueba-clasificacion",
        epocas=3,
        batch_size=4,
    )

    assert config.num_train_epochs == 3
    assert config.per_device_train_batch_size == 4
    assert config.learning_rate == 2e-4  # default LoRA
    assert config.bf16 is True
```

### Implementacion

```python
from peft import LoraConfig, TaskType
from transformers import TrainingArguments


def crear_config_lora(
    rango: int = 16,
    alpha: int = 32,
    dropout: float = 0.05,
    modulos_target: list[str] | None = None,
) -> LoraConfig:
    return LoraConfig(
        r=rango,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=modulos_target or ["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )


def crear_config_entrenamiento(
    nombre_run: str,
    epocas: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4,
    warmup_ratio: float = 0.03,
    directorio_salida: str = "output",
) -> TrainingArguments:
    return TrainingArguments(
        output_dir=f"{directorio_salida}/{nombre_run}",
        num_train_epochs=epocas,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        warmup_ratio=warmup_ratio,
        bf16=True,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )
```

## Fase 3: Entrenamiento y evaluacion

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer


def entrenar(
    modelo_base: str,
    dataset_train,
    dataset_eval,
    config_lora: LoraConfig,
    config_entrenamiento: TrainingArguments,
    quantizar_4bit: bool = False,
) -> str:
    """Entrena y retorna la ruta del modelo guardado."""
    kwargs_modelo = {}
    if quantizar_4bit:
        from transformers import BitsAndBytesConfig
        kwargs_modelo["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype="bfloat16",
        )

    modelo = AutoModelForCausalLM.from_pretrained(modelo_base, **kwargs_modelo)
    tokenizer = AutoTokenizer.from_pretrained(modelo_base)

    if quantizar_4bit:
        modelo = prepare_model_for_kbit_training(modelo)

    modelo = get_peft_model(modelo, config_lora)

    trainer = SFTTrainer(
        model=modelo,
        args=config_entrenamiento,
        train_dataset=dataset_train,
        eval_dataset=dataset_eval,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model()
    return config_entrenamiento.output_dir
```

### Metricas de evaluacion

| Metrica | Que mide | Umbral aceptable |
|---|---|---|
| `eval_loss` | Divergencia del modelo vs respuestas esperadas | < train_loss × 1.2 (no overfit) |
| Exactitud en eval set | % respuestas correctas en formato esperado | Depende de tarea (>80% para clasificacion) |
| Coherencia manual (10 samples) | Calidad subjetiva en casos reales | Sin degradacion vs base + prompt |

## Fase 4: Exportacion

```python
from peft import PeftModel


def exportar_modelo_merged(
    modelo_base: str,
    ruta_adapter: str,
    ruta_salida: str,
) -> None:
    """Merge LoRA adapter con modelo base para inference sin PEFT."""
    modelo = AutoModelForCausalLM.from_pretrained(modelo_base)
    modelo = PeftModel.from_pretrained(modelo, ruta_adapter)
    modelo_merged = modelo.merge_and_unload()

    modelo_merged.save_pretrained(ruta_salida)
    tokenizer = AutoTokenizer.from_pretrained(modelo_base)
    tokenizer.save_pretrained(ruta_salida)
```

## Estructura de archivos recomendada

```
lib/
├── fine_tuning/
│   ├── __init__.py
│   ├── tipos.py              # EjemploFineTune, FormateadorDataset Protocol
│   ├── datos.py              # cargar_dataset(), dividir_dataset()
│   ├── config.py             # crear_config_lora(), crear_config_entrenamiento()
│   ├── entrenamiento.py      # entrenar()
│   └── exportar.py           # exportar_modelo_merged()
datos/
├── entrenamiento.jsonl       # Dataset (gitignore si es sensible)
├── evaluacion.jsonl
output/                       # Checkpoints y modelo final (gitignore)
```

## Reglas

- No fine-tunear sin antes agotar prompt engineering + few-shot. Fine-tuning es el ultimo recurso, no el primero.
- Dataset minimo: 50 ejemplos para clasificacion, 200+ para generacion abierta.
- Siempre separar eval set ANTES de entrenar. Nunca evaluar con datos de entrenamiento.
- Monitorear `eval_loss` — si diverge de `train_loss` por >20%, hay overfitting.
- No subir modelos fine-tuneados a repos publicos sin verificar que no memorizaron datos sensibles del dataset.
- Guardar config exacta de entrenamiento (hiperparametros, modelo base, commit del dataset) — reproducibilidad.
- Preferir LoRA sobre full fine-tune. Solo escalar si LoRA no alcanza la calidad necesaria con datos suficientes.
- `trust_remote_code: false` siempre al cargar modelos de HuggingFace, a menos que se haya auditado el codigo.
- Gitignore: checkpoints, modelo merged, dataset si contiene datos sensibles.
- Validar formato de salida del modelo fine-tuneado con el mismo schema que se usaria en produccion (Zod/Pydantic).
