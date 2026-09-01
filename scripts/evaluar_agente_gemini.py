#!/usr/bin/env python3
"""Evalua una Skill mediante un agente Gemini con herramientas de solo lectura."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors, types


RAIZ = Path(__file__).resolve().parent.parent
MAXIMO_TURNOS = 16
MAXIMO_CARACTERES = 16000
MAXIMO_REINTENTOS_CUOTA = 4
TAREA = (
    "Audita, sin modificar archivos, que cambios exactos requeriria mover la Skill "
    "optimizar-contexto desde el core automatico hacia las Skills opcionales. Debe "
    "inspeccionar evidencia mediante herramientas antes de concluir. Entrega: rutas "
    "afectadas, cambio requerido por cada ruta, al menos seis evidencias con ruta y "
    "motivo, pruebas que deben ejecutarse y riesgos de compatibilidad. No invente "
    "archivos ni suponga que una lista se actualiza automaticamente."
)


def resolver(ruta_relativa: str) -> Path:
    """Resuelve una ruta regular dentro del repositorio autorizado."""
    ruta = (RAIZ / ruta_relativa).resolve()
    if (ruta != RAIZ and RAIZ not in ruta.parents) or not ruta.is_file():
        raise ValueError("La ruta solicitada no es un archivo regular autorizado")
    return ruta


def listar_archivos(prefijo: str = "") -> dict[str, object]:
    """Lista rutas regulares bajo un prefijo del repositorio."""
    base = (RAIZ / prefijo).resolve()
    if (base != RAIZ and RAIZ not in base.parents) or not base.exists():
        return {"error": "Prefijo no autorizado o inexistente"}
    rutas = [
        archivo.relative_to(RAIZ).as_posix()
        for archivo in sorted(base.rglob("*"))
        if archivo.is_file() and ".git" not in archivo.parts and "resultados" not in archivo.parts
    ]
    return {"rutas": rutas[:200], "truncado": len(rutas) > 200}


def buscar_texto(patron: str, prefijo: str = "") -> dict[str, object]:
    """Busca texto literal acotado en archivos UTF-8 del repositorio."""
    if not patron or len(patron) > 120:
        return {"error": "Patron invalido"}
    base = (RAIZ / prefijo).resolve()
    if (base != RAIZ and RAIZ not in base.parents) or not base.exists():
        return {"error": "Prefijo no autorizado o inexistente"}
    hallazgos: list[dict[str, object]] = []
    for archivo in sorted(base.rglob("*")):
        if not archivo.is_file() or ".git" in archivo.parts or "resultados" in archivo.parts:
            continue
        try:
            lineas = archivo.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for numero, linea in enumerate(lineas, start=1):
            if patron.casefold() in linea.casefold():
                hallazgos.append({"ruta": archivo.relative_to(RAIZ).as_posix(), "linea": numero, "texto": linea[:240]})
                if len(hallazgos) == 40:
                    return {"hallazgos": hallazgos, "truncado": True}
    return {"hallazgos": hallazgos, "truncado": False}


def leer_archivo(ruta: str, inicio: int = 1, limite: int = 300) -> dict[str, object]:
    """Lee un tramo acotado de un archivo autorizado."""
    if inicio < 1 or limite < 1 or limite > 500:
        return {"error": "Rango de lectura invalido"}
    try:
        lineas = resolver(ruta).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError, ValueError) as error:
        return {"error": str(error)}
    tramo = lineas[inicio - 1 : inicio - 1 + limite]
    texto = "\n".join(f"{numero}: {linea}" for numero, linea in enumerate(tramo, start=inicio))
    return {"ruta": ruta, "inicio": inicio, "texto": texto[:MAXIMO_CARACTERES], "truncado": len(tramo) < len(lineas) - inicio + 1}


HERRAMIENTAS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(name="listar_archivos", description="Lista archivos del repositorio.", parameters={"type": "object", "properties": {"prefijo": {"type": "string"}}}),
        types.FunctionDeclaration(name="buscar_texto", description="Busca texto literal en archivos.", parameters={"type": "object", "properties": {"patron": {"type": "string"}, "prefijo": {"type": "string"}}, "required": ["patron"]}),
        types.FunctionDeclaration(name="leer_archivo", description="Lee lineas de un archivo del repositorio.", parameters={"type": "object", "properties": {"ruta": {"type": "string"}, "inicio": {"type": "integer"}, "limite": {"type": "integer"}}, "required": ["ruta"]}),
    ]
)


def ejecutar_herramienta(nombre: str, argumentos: dict[str, Any]) -> dict[str, object]:
    """Ejecuta exclusivamente las herramientas declaradas y de solo lectura."""
    funciones = {"listar_archivos": listar_archivos, "buscar_texto": buscar_texto, "leer_archivo": leer_archivo}
    funcion = funciones.get(nombre)
    if funcion is None:
        return {"error": "Herramienta no autorizada"}
    try:
        return funcion(**argumentos)
    except TypeError:
        return {"error": "Argumentos invalidos"}


def uso(respuesta: Any) -> tuple[int, int, int]:
    """Extrae tokens de entrada, salida y razonamiento de una respuesta."""
    datos = respuesta.usage_metadata
    entrada = int(getattr(datos, "prompt_token_count", 0) or 0)
    salida = int(getattr(datos, "candidates_token_count", 0) or 0)
    razonamiento = int(getattr(datos, "thoughts_token_count", 0) or 0)
    return entrada, salida, razonamiento


def segundos_espera_cuota(error: errors.ClientError) -> int | None:
    """Extrae una espera segura cuando Gemini informa que excedio una cuota."""
    if getattr(error, "code", None) != 429:
        return None
    coincidencia = re.search(r"(?:retryDelay|retry in )[^0-9]*([0-9]+(?:\\.[0-9]+)?)s", str(error), re.IGNORECASE)
    if coincidencia is None:
        return 35
    return max(1, int(float(coincidencia.group(1))) + 1)


def ejecutar_agente(cliente: genai.Client, modelo: str, variante: str) -> dict[str, object]:
    """Ejecuta un ciclo de herramientas y agrega cada uso real del modelo."""
    instruccion = "Lee AGENTS.md antes de actuar y usa evidencia verificable."
    if variante == "skill":
        instruccion += " Aplica ademas plantilla/.agents/skills/optimizar-contexto/SKILL.md como protocolo activo."
    else:
        instruccion += " No apliques el protocolo optimizar-contexto durante esta evaluacion de control."
    configuracion = types.GenerateContentConfig(tools=[HERRAMIENTAS], system_instruction=instruccion, temperature=0, max_output_tokens=900)
    contenidos: list[Any] = [TAREA]
    entrada_total = salida_total = razonamiento_total = llamadas = reintentos = 0
    inicio = time.perf_counter()
    texto_final = ""
    for _ in range(MAXIMO_TURNOS):
        for intento in range(MAXIMO_REINTENTOS_CUOTA + 1):
            try:
                respuesta = cliente.models.generate_content(model=modelo, contents=contenidos, config=configuracion)
                break
            except errors.ServerError:
                if intento == MAXIMO_REINTENTOS_CUOTA:
                    raise
                reintentos += 1
                time.sleep(5 * (2**intento))
            except errors.ClientError as error:
                espera = segundos_espera_cuota(error)
                if espera is None or intento == MAXIMO_REINTENTOS_CUOTA:
                    raise
                reintentos += 1
                print(
                    f"Cuota temporal de Gemini para {variante}; se reintentara en "
                    f"{espera} segundos ({reintentos}/{MAXIMO_REINTENTOS_CUOTA})."
                )
                time.sleep(espera)
        entrada, salida, razonamiento = uso(respuesta)
        entrada_total += entrada
        salida_total += salida + razonamiento
        partes = respuesta.candidates[0].content.parts
        llamadas_turno = [parte.function_call for parte in partes if getattr(parte, "function_call", None)]
        if not llamadas_turno:
            texto_final = respuesta.text or ""
            break
        contenidos.append(respuesta.candidates[0].content)
        respuestas_herramientas: list[Any] = []
        for llamada in llamadas_turno:
            argumentos = dict(llamada.args or {})
            resultado = ejecutar_herramienta(llamada.name, argumentos)
            respuestas_herramientas.append(types.Part.from_function_response(name=llamada.name, response={"result": resultado}))
            llamadas += 1
        contenidos.append(types.Content(role="user", parts=respuestas_herramientas))
    if not texto_final:
        raise RuntimeError("El agente excedio el limite de turnos sin respuesta final")
    return {"exito": True, "pruebas_aprobadas": False, "tokens_entrada": entrada_total, "tokens_salida": salida_total, "llamadas_herramientas": llamadas, "duracion_segundos": round(time.perf_counter() - inicio, 3), "reintentos": reintentos, "respuesta": texto_final}


def guardar_resultado(salida: Path, resultado: dict[str, object]) -> None:
    """Guarda el avance de forma legible para permitir reanudar una medicion."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="\n") as flujo:
        json.dump(resultado, flujo, ensure_ascii=False, indent=2)
        flujo.write("\n")


def cargar_reanudacion(salida: Path, modelo: str, repeticiones: int) -> list[dict[str, object]]:
    """Carga solo ejecuciones compatibles de un avance anterior validado."""
    if not salida.is_file():
        return []
    try:
        datos = json.loads(salida.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo reanudar desde {salida}: {error}") from error
    if datos.get("skill") != "optimizar-contexto" or datos.get("modelo") != modelo:
        raise ValueError("El resultado existente no corresponde a esta Skill o modelo")
    ejecuciones = datos.get("ejecuciones")
    if not isinstance(ejecuciones, list):
        raise ValueError("El resultado existente no contiene ejecuciones validas")
    return [
        ejecucion
        for ejecucion in ejecuciones
        if isinstance(ejecucion, dict)
        and ejecucion.get("escenario") == "migracion-core-a-opcional"
        and isinstance(ejecucion.get("repeticion"), int)
        and 1 <= ejecucion["repeticion"] <= repeticiones
        and ejecucion.get("variante") in {"control", "skill"}
    ]


def main() -> int:
    """Ejecuta pares y guarda observaciones pendientes de revision humana."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default="gemini-3.1-flash-lite")
    parser.add_argument("--repeticiones", type=int, default=3)
    parser.add_argument("--salida", type=Path, default=Path("resultados/evaluacion_agente_gemini.json"))
    parser.add_argument("--reanudar", action="store_true", help="Reanuda las ejecuciones ya guardadas en --salida.")
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("Se requiere GEMINI_API_KEY y al menos una repeticion")
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    ejecuciones = cargar_reanudacion(argumentos.salida, argumentos.modelo, argumentos.repeticiones) if argumentos.reanudar else []
    resultado: dict[str, object] = {
        "version": 1,
        "skill": "optimizar-contexto",
        "proveedor": "gemini-api",
        "modelo": argumentos.modelo,
        "criterios": {"margen_no_inferioridad": 0.0, "ahorro_minimo_tokens": 0.2},
        "ejecuciones": ejecuciones,
    }
    completadas = {(ejecucion["repeticion"], ejecucion["variante"]) for ejecucion in ejecuciones}
    for repeticion in range(1, argumentos.repeticiones + 1):
        for variante in ("control", "skill"):
            if (repeticion, variante) in completadas:
                print(f"Conservando {variante} {repeticion}/{argumentos.repeticiones} ya guardado.")
                continue
            print(f"Ejecutando {variante} {repeticion}/{argumentos.repeticiones}...")
            ejecucion = ejecutar_agente(cliente, argumentos.modelo, variante)
            ejecucion.update({"escenario": "migracion-core-a-opcional", "repeticion": repeticion, "variante": variante})
            ejecuciones.append(ejecucion)
            guardar_resultado(argumentos.salida, resultado)
    print(f"Resultado guardado en: {argumentos.salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
