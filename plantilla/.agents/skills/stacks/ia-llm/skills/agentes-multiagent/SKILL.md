---
name: agentes-multiagent
description: Patrones de agentes autonomos y sistemas multi-agente. Cubre arquitecturas (ReAct, Plan-and-Execute, Reflection), tool-use, orquestacion multi-agente y guardrails de seguridad. Usar cuando se necesite que un LLM ejecute tareas multi-paso con herramientas o coordine multiples agentes.
---

# Agentes y Sistemas Multi-agente

## Cuando usar

- El LLM necesita ejecutar acciones multi-paso (buscar, calcular, escribir, validar).
- Se necesita descomponer tareas complejas en sub-tareas con herramientas.
- Se quiere coordinar multiples agentes especializados en un flujo.
- Se necesita un loop de razonamiento con auto-correccion.

## Cuando NO usar

- Una sola llamada al LLM resuelve la tarea — un agente agrega latencia y costo innecesarios.
- El flujo es determinista y fijo — mejor un pipeline clasico sin LLM en el loop.
- No se puede tolerar latencia variable (los agentes pueden tomar N iteraciones impredecibles).
- No se tienen guardrails de seguridad implementados — un agente sin limites es peligroso.

## Matriz de decision: patron de agente

| Patron | Iteraciones | Planifica? | Usa cuando |
|---|---|---|---|
| ReAct | Variable (3-15) | No — decide paso a paso | Tareas de busqueda/consulta con herramientas |
| Plan-and-Execute | Plan + N ejecuciones | Si — plan global primero | Tareas complejas descomponibles, requiere coherencia |
| Reflection | 2-3 (genera + critica + mejora) | No | Generacion de contenido que necesita auto-revision |
| Tool-only (router) | 1 | No | Clasificar intent y delegar a una herramienta |

## Matriz de decision: framework

| Framework | Complejidad | Multi-agente | Usar cuando |
|---|---|---|---|
| SDK nativo (Anthropic/OpenAI) | Baja | Manual | Maximo control, pocos tools, produccion |
| LangGraph | Media | Si (grafos) | Flujos complejos con estado, condicionales |
| CrewAI | Media | Si (roles) | Equipos de agentes con roles definidos |
| AutoGen | Alta | Si (conversacion) | Investigacion, prototipado multi-agente |
| Implementacion propia | Variable | Manual | Casos simples, sin dependencia externa |

## Patron 1: ReAct (Reasoning + Acting)

### Test primero

```python
def test_agente_react_usa_herramienta():
    herramientas = [HerramientaCalculadora()]
    agente = crear_agente_react(
        herramientas=herramientas,
        llm=llm_mock_con_respuestas([
            "Pensamiento: Necesito calcular 15 * 7\nAccion: calcular\nInput: 15 * 7",
            "Pensamiento: El resultado es 105. Tengo la respuesta.\nRespuesta final: 105",
        ]),
    )

    resultado = agente.ejecutar("Cuanto es 15 por 7?")
    assert resultado.respuesta_final == "105"
    assert len(resultado.pasos) == 2
    assert resultado.pasos[0].herramienta_usada == "calcular"


def test_agente_react_respeta_limite_iteraciones():
    agente = crear_agente_react(
        herramientas=[],
        llm=llm_mock_loop_infinito(),
        max_iteraciones=5,
    )

    resultado = agente.ejecutar("tarea imposible")
    assert len(resultado.pasos) <= 5
    assert resultado.detenido_por_limite is True
```

### Implementacion

```python
from dataclasses import dataclass, field
from typing import Protocol


class Herramienta(Protocol):
    @property
    def nombre(self) -> str: ...
    @property
    def descripcion(self) -> str: ...
    def ejecutar(self, input: str) -> str: ...


class ClienteLLM(Protocol):
    def generar(self, mensajes: list[dict]) -> str: ...


@dataclass
class PasoAgente:
    pensamiento: str
    herramienta_usada: str | None = None
    input_herramienta: str | None = None
    resultado_herramienta: str | None = None


@dataclass
class ResultadoAgente:
    respuesta_final: str
    pasos: list[PasoAgente] = field(default_factory=list)
    detenido_por_limite: bool = False


class AgenteReact:
    def __init__(
        self,
        llm: ClienteLLM,
        herramientas: list[Herramienta],
        max_iteraciones: int = 10,
        prompt_sistema: str = "",
    ):
        self._llm = llm
        self._herramientas = {h.nombre: h for h in herramientas}
        self._max_iteraciones = max_iteraciones
        self._prompt_sistema = prompt_sistema or self._prompt_default()

    def ejecutar(self, consulta: str) -> ResultadoAgente:
        mensajes = [
            {"role": "system", "content": self._prompt_sistema},
            {"role": "user", "content": consulta},
        ]
        pasos = []

        for _ in range(self._max_iteraciones):
            respuesta = self._llm.generar(mensajes)
            paso = self._parsear_respuesta(respuesta)
            pasos.append(paso)

            if "Respuesta final:" in respuesta:
                final = respuesta.split("Respuesta final:")[-1].strip()
                return ResultadoAgente(respuesta_final=final, pasos=pasos)

            if paso.herramienta_usada and paso.herramienta_usada in self._herramientas:
                resultado = self._herramientas[paso.herramienta_usada].ejecutar(
                    paso.input_herramienta or ""
                )
                paso.resultado_herramienta = resultado
                mensajes.append({"role": "assistant", "content": respuesta})
                mensajes.append({"role": "user", "content": f"Observacion: {resultado}"})

        return ResultadoAgente(
            respuesta_final="",
            pasos=pasos,
            detenido_por_limite=True,
        )

    def _parsear_respuesta(self, texto: str) -> PasoAgente:
        pensamiento = ""
        herramienta = None
        input_h = None

        for linea in texto.split("\n"):
            if linea.startswith("Pensamiento:"):
                pensamiento = linea.split(":", 1)[1].strip()
            elif linea.startswith("Accion:"):
                herramienta = linea.split(":", 1)[1].strip()
            elif linea.startswith("Input:"):
                input_h = linea.split(":", 1)[1].strip()

        return PasoAgente(
            pensamiento=pensamiento,
            herramienta_usada=herramienta,
            input_herramienta=input_h,
        )

    def _prompt_default(self) -> str:
        nombres = ", ".join(self._herramientas.keys())
        descripciones = "\n".join(
            f"- {h.nombre}: {h.descripcion}" for h in self._herramientas.values()
        )
        return f"""Eres un agente que resuelve tareas paso a paso.

Herramientas disponibles: {nombres}
{descripciones}

Formato de respuesta:
Pensamiento: <razonamiento>
Accion: <nombre_herramienta>
Input: <input para la herramienta>

Cuando tengas la respuesta:
Pensamiento: <razonamiento final>
Respuesta final: <respuesta>"""


def crear_agente_react(
    herramientas: list[Herramienta],
    llm: ClienteLLM,
    max_iteraciones: int = 10,
) -> AgenteReact:
    return AgenteReact(llm=llm, herramientas=herramientas, max_iteraciones=max_iteraciones)
```

## Patron 2: Plan-and-Execute

### Test primero

```python
def test_planificador_genera_pasos():
    planificador = PlanificadorAgente(llm=llm_mock_plan())
    plan = planificador.planificar("Investiga precios de vuelos a Madrid y recomienda el mas barato")

    assert len(plan.pasos) >= 2
    assert all(p.descripcion for p in plan.pasos)
    assert plan.objetivo == "Investiga precios de vuelos a Madrid y recomienda el mas barato"


def test_ejecutor_sigue_plan():
    plan = Plan(
        objetivo="test",
        pasos=[
            PasoPlan(descripcion="Buscar vuelos", herramienta="buscar_vuelos"),
            PasoPlan(descripcion="Comparar precios", herramienta=None),
        ],
    )
    ejecutor = EjecutorPlan(llm=llm_mock_ejecutor(), herramientas=[mock_buscar_vuelos])
    resultado = ejecutor.ejecutar(plan)

    assert resultado.completado is True
    assert len(resultado.resultados_pasos) == 2
```

### Implementacion

```python
@dataclass
class PasoPlan:
    descripcion: str
    herramienta: str | None = None
    completado: bool = False
    resultado: str = ""


@dataclass
class Plan:
    objetivo: str
    pasos: list[PasoPlan] = field(default_factory=list)


@dataclass
class ResultadoPlan:
    completado: bool
    respuesta_final: str
    resultados_pasos: list[str] = field(default_factory=list)


class PlanificadorAgente:
    def __init__(self, llm: ClienteLLM):
        self._llm = llm

    def planificar(self, objetivo: str) -> Plan:
        prompt = f"""Descompone esta tarea en pasos concretos y secuenciales.
Tarea: {objetivo}

Responde en formato:
1. [herramienta o "razonar"] Descripcion del paso
2. ..."""
        respuesta = self._llm.generar([{"role": "user", "content": prompt}])
        pasos = self._parsear_plan(respuesta)
        return Plan(objetivo=objetivo, pasos=pasos)

    def _parsear_plan(self, texto: str) -> list[PasoPlan]:
        pasos = []
        for linea in texto.strip().split("\n"):
            if not linea.strip():
                continue
            # Extraer herramienta entre corchetes si existe
            herramienta = None
            if "[" in linea and "]" in linea:
                herramienta = linea.split("[")[1].split("]")[0]
                if herramienta == "razonar":
                    herramienta = None
            descripcion = linea.split("]")[-1].strip() if "]" in linea else linea.strip()
            descripcion = descripcion.lstrip("0123456789. ")
            if descripcion:
                pasos.append(PasoPlan(descripcion=descripcion, herramienta=herramienta))
        return pasos


class EjecutorPlan:
    def __init__(self, llm: ClienteLLM, herramientas: list[Herramienta]):
        self._llm = llm
        self._herramientas = {h.nombre: h for h in herramientas}

    def ejecutar(self, plan: Plan) -> ResultadoPlan:
        contexto_acumulado = []

        for paso in plan.pasos:
            if paso.herramienta and paso.herramienta in self._herramientas:
                resultado = self._herramientas[paso.herramienta].ejecutar(paso.descripcion)
            else:
                prompt = f"""Objetivo: {plan.objetivo}
Paso actual: {paso.descripcion}
Contexto previo: {contexto_acumulado}

Ejecuta este paso y da el resultado."""
                resultado = self._llm.generar([{"role": "user", "content": prompt}])

            paso.completado = True
            paso.resultado = resultado
            contexto_acumulado.append(f"{paso.descripcion}: {resultado}")

        respuesta_final = self._sintetizar(plan, contexto_acumulado)
        return ResultadoPlan(
            completado=True,
            respuesta_final=respuesta_final,
            resultados_pasos=[p.resultado for p in plan.pasos],
        )

    def _sintetizar(self, plan: Plan, contexto: list[str]) -> str:
        prompt = f"""Objetivo original: {plan.objetivo}
Resultados de cada paso:
{chr(10).join(contexto)}

Sintetiza una respuesta final."""
        return self._llm.generar([{"role": "user", "content": prompt}])
```

## Patron 3: Multi-agente (orquestador + especialistas)

### Test primero

```python
def test_orquestador_delega_a_especialista():
    agentes = {
        "investigador": agente_mock(respuesta="Madrid tiene 3M habitantes"),
        "escritor": agente_mock(respuesta="Articulo sobre Madrid..."),
    }
    orquestador = OrquestadorAgentes(llm=llm_mock_router(), agentes=agentes)

    resultado = orquestador.ejecutar("Escribe un articulo corto sobre Madrid")
    assert any(a.fue_invocado for a in agentes.values())
    assert resultado.respuesta_final != ""


def test_orquestador_respeta_presupuesto_tokens():
    orquestador = OrquestadorAgentes(
        llm=llm_mock_router(),
        agentes={"a": agente_mock_caro()},
        presupuesto_tokens=1000,
    )

    resultado = orquestador.ejecutar("tarea costosa")
    assert resultado.tokens_usados <= 1000
```

### Implementacion

```python
@dataclass
class ResultadoOrquestacion:
    respuesta_final: str
    agentes_invocados: list[str] = field(default_factory=list)
    tokens_usados: int = 0


class AgenteEspecialista(Protocol):
    @property
    def nombre(self) -> str: ...
    @property
    def descripcion(self) -> str: ...
    def ejecutar(self, tarea: str, contexto: str = "") -> str: ...


class OrquestadorAgentes:
    def __init__(
        self,
        llm: ClienteLLM,
        agentes: dict[str, AgenteEspecialista],
        presupuesto_tokens: int = 50_000,
        max_delegaciones: int = 5,
    ):
        self._llm = llm
        self._agentes = agentes
        self._presupuesto = presupuesto_tokens
        self._max_delegaciones = max_delegaciones
        self._tokens_usados = 0

    def ejecutar(self, tarea: str) -> ResultadoOrquestacion:
        invocados = []
        contexto_acumulado = []

        for _ in range(self._max_delegaciones):
            if self._tokens_usados >= self._presupuesto:
                break

            siguiente = self._decidir_siguiente(tarea, contexto_acumulado)

            if siguiente == "FINALIZAR":
                break

            if siguiente in self._agentes:
                resultado = self._agentes[siguiente].ejecutar(
                    tarea, contexto="\n".join(contexto_acumulado)
                )
                invocados.append(siguiente)
                contexto_acumulado.append(f"[{siguiente}]: {resultado}")

        respuesta = self._sintetizar(tarea, contexto_acumulado)
        return ResultadoOrquestacion(
            respuesta_final=respuesta,
            agentes_invocados=invocados,
            tokens_usados=self._tokens_usados,
        )

    def _decidir_siguiente(self, tarea: str, contexto: list[str]) -> str:
        disponibles = "\n".join(
            f"- {n}: {a.descripcion}" for n, a in self._agentes.items()
        )
        prompt = f"""Tarea: {tarea}
Trabajo completado: {contexto or 'Ninguno'}
Agentes disponibles:
{disponibles}

Responde SOLO con el nombre del siguiente agente a invocar, o "FINALIZAR" si ya tienes suficiente."""
        return self._llm.generar([{"role": "user", "content": prompt}]).strip()

    def _sintetizar(self, tarea: str, contexto: list[str]) -> str:
        prompt = f"""Tarea original: {tarea}
Resultados recopilados:
{chr(10).join(contexto)}

Genera la respuesta final integrando todos los resultados."""
        return self._llm.generar([{"role": "user", "content": prompt}])
```

## Guardrails de seguridad

| Control | Implementacion | Por que |
|---|---|---|
| Max iteraciones | `max_iteraciones=10` (configurable) | Evitar loops infinitos que consumen tokens |
| Presupuesto de tokens | Cortar ejecucion al alcanzar limite | Control de costos |
| Whitelist de herramientas | Solo herramientas registradas explicitamente | Evitar ejecucion arbitraria |
| Sandbox de codigo | Nunca `exec()` directo — usar subprocess con timeout | Codigo generado por LLM no es confiable |
| Aprobacion humana | Para acciones destructivas (borrar, enviar, publicar) | El agente puede equivocarse |
| Logging de pasos | Registrar cada paso/herramienta/resultado | Auditabilidad y debugging |

## Estructura de archivos recomendada

```
lib/
├── agentes/
│   ├── __init__.py
│   ├── tipos.py              # Herramienta, ClienteLLM, PasoAgente (Protocols)
│   ├── react.py              # AgenteReact
│   ├── plan_execute.py       # PlanificadorAgente, EjecutorPlan
│   ├── orquestador.py        # OrquestadorAgentes
│   └── herramientas/         # Implementaciones de Herramienta
│       ├── __init__.py
│       ├── busqueda.py
│       ├── calculadora.py
│       └── archivo.py
```

## Reglas

- Siempre definir `max_iteraciones`. Un agente sin limite es un riesgo de costo y seguridad.
- Desacoplar el LLM detras de `ClienteLLM` Protocol. Cambiar de Claude a GPT no debe reescribir la logica del agente.
- Las herramientas son inyectables — el agente recibe una lista, no importa internamente.
- No dar al agente acceso a herramientas que no necesita. Principio de minimo privilegio.
- Logging obligatorio: cada paso del agente debe quedar registrado (pensamiento, accion, resultado).
- No ejecutar codigo generado por el LLM sin sandbox. `exec()` directo es una vulnerabilidad critica.
- Para multi-agente: definir presupuesto global de tokens y max delegaciones.
- Preferir agente simple (ReAct con pocas herramientas) sobre orquestacion compleja. Escalar solo si la tarea lo requiere.
- Si el agente falla 3 veces consecutivas en la misma accion, abortar y reportar — no reintentar infinitamente.
- Test de integracion minimo: dar al agente una tarea conocida con herramientas mock, verificar que llega a la respuesta correcta en <=N pasos.
