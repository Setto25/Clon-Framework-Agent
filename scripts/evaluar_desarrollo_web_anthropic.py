#!/usr/bin/env python3
"""Evalua optimizacion de contexto web aislada mediante Claude API."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import anthropic

if __package__:
    from .analizar_impacto import analizar_impacto
    from .evaluar_agente_anthropic import segundos_espera
    from .evaluar_desarrollo_web_gemini import (
        FIXTURE,
        MAXIMO_HERRAMIENTAS,
        MAXIMO_REINTENTOS,
        MAXIMO_TURNOS,
        RUTA_MODO_EXTENDIDO,
        RUTA_SKILL,
        TERMINOS_INDICE,
        construir_instruccion,
        construir_solicitud,
        ejecutar_herramienta,
        ejecutar_validacion,
    )
else:
    from analizar_impacto import analizar_impacto
    from evaluar_agente_anthropic import segundos_espera
    from evaluar_desarrollo_web_gemini import (
        FIXTURE,
        MAXIMO_HERRAMIENTAS,
        MAXIMO_REINTENTOS,
        MAXIMO_TURNOS,
        RUTA_MODO_EXTENDIDO,
        RUTA_SKILL,
        TERMINOS_INDICE,
        construir_instruccion,
        construir_solicitud,
        ejecutar_herramienta,
        ejecutar_validacion,
    )


MODELO_PREDETERMINADO = "claude-sonnet-5"
VERSION_ADAPTADOR = 1
ESCENARIO = "desarrollo-web-tareas-v4"
MAXIMO_TOKENS_SALIDA = 3000
VARIANTES: tuple[str, ...] = (
    "control_puro",
    "indice_autoritativo",
    "skill_adaptativa",
    "skill_extendida",
    "extendido_compacto",
)
HERRAMIENTAS: list[dict[str, object]] = [
    {
        "name": "listar_archivos",
        "description": "Lista los archivos regulares del entorno web aislado.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "leer_archivo",
        "description": "Lee un archivo UTF-8 del entorno aislado.",
        "input_schema": {
            "type": "object",
            "properties": {"ruta": {"type": "string"}},
            "required": ["ruta"],
        },
    },
    {
        "name": "escribir_archivo",
        "description": "Reemplaza un archivo editable dentro del entorno aislado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string"},
                "contenido": {"type": "string"},
            },
            "required": ["ruta", "contenido"],
        },
    },
    {
        "name": "ejecutar_validacion",
        "description": "Ejecuta las pruebas reales de backend y frontend.",
        "input_schema": {"type": "object", "properties": {}},
    },
]
HERRAMIENTAS_SIN_LISTADO: list[dict[str, object]] = [
    herramienta for herramienta in HERRAMIENTAS if herramienta["name"] != "listar_archivos"
]


def usa_indice_autoritativo(variante: str) -> bool:
    """Determina si una variante recibe el preanalisis local verificable."""
    return variante != "control_puro"


def construir_instruccion_anthropic(variante: str) -> str:
    """Refuerza la vigencia del indice sin alterar los requisitos funcionales."""
    variante_base = "indice" if variante == "indice_autoritativo" else variante
    instruccion = construir_instruccion(variante_base)
    if usa_indice_autoritativo(variante):
        return (
            f"{instruccion}\n\n"
            "El INDICE_LOCAL_INICIAL fue generado inmediatamente antes de esta tarea "
            "sobre esta misma raiz. Es evidencia autoritativa del estado inicial: no "
            "ejecutes listar_archivos ni reconfirmes rutas ya incluidas. Solo solicita "
            "una lectura adicional si falta una ruta necesaria o una evidencia observada "
            "contradice el indice."
        )
    return instruccion


def herramientas_disponibles(variante: str) -> list[dict[str, object]]:
    """Retira el listado general cuando un indice autoritativo lo sustituye."""
    return HERRAMIENTAS_SIN_LISTADO if usa_indice_autoritativo(variante) else HERRAMIENTAS


def uso(respuesta: object) -> tuple[int, int, int, int]:
    """Extrae entrada, salida y desglose de cache de una respuesta Anthropic."""
    datos = getattr(respuesta, "usage", None)
    entrada = int(getattr(datos, "input_tokens", 0) or 0)
    salida = int(getattr(datos, "output_tokens", 0) or 0)
    cache_creada = int(getattr(datos, "cache_creation_input_tokens", 0) or 0)
    cache_leida = int(getattr(datos, "cache_read_input_tokens", 0) or 0)
    return entrada + cache_creada + cache_leida, salida, cache_creada, cache_leida


def solicitar(
    cliente: anthropic.Anthropic,
    modelo: str,
    sistema: str,
    mensajes: list[dict[str, object]],
    herramientas: list[dict[str, object]] | None,
) -> tuple[Any, int]:
    """Solicita Claude y reintenta solamente errores temporales observables."""
    reintentos = 0
    for intento in range(MAXIMO_REINTENTOS + 1):
        try:
            parametros: dict[str, object] = {
                "model": modelo,
                "max_tokens": MAXIMO_TOKENS_SALIDA,
                "system": sistema,
                "messages": mensajes,
            }
            if herramientas:
                parametros["tools"] = herramientas
            return cliente.messages.create(**parametros), reintentos
        except anthropic.APIError as error:
            espera = segundos_espera(error, intento)
            if espera is None or intento == MAXIMO_REINTENTOS:
                raise
            reintentos += 1
            print(
                f"Error temporal de Anthropic; se reintentara en {espera} segundos "
                f"({reintentos}/{MAXIMO_REINTENTOS})."
            )
            time.sleep(espera)
    raise RuntimeError("No se obtuvo respuesta de Anthropic")


def serializar_bloques(bloques: list[object]) -> list[dict[str, object]]:
    """Convierte bloques del SDK en contenido reutilizable de Anthropic."""
    resultado: list[dict[str, object]] = []
    for bloque in bloques:
        convertir = getattr(bloque, "model_dump", None)
        if callable(convertir):
            datos = convertir(mode="json", exclude_none=True)
            if isinstance(datos, dict):
                resultado.append(datos)
    return resultado


def ejecutar_agente(
    cliente: anthropic.Anthropic,
    modelo: str,
    variante: str,
    entorno: Path,
    indice: dict[str, object],
) -> dict[str, object]:
    """Ejecuta una variante aislada y conserva metricas comparables del proveedor."""
    mensajes: list[dict[str, object]] = [
        {"role": "user", "content": construir_solicitud("indice" if usa_indice_autoritativo(variante) else variante, indice)}
    ]
    entrada_total = salida_total = cache_creada_total = cache_leida_total = 0
    llamadas = ejecuciones = reintentos = 0
    traza: list[dict[str, object]] = []
    respuesta_final = ""
    inicio = time.perf_counter()
    for _ in range(MAXIMO_TURNOS):
        respuesta, nuevos_reintentos = solicitar(
            cliente,
            modelo,
            construir_instruccion_anthropic(variante),
            mensajes,
            herramientas_disponibles(variante) if ejecuciones < MAXIMO_HERRAMIENTAS else None,
        )
        reintentos += nuevos_reintentos
        entrada, salida, cache_creada, cache_leida = uso(respuesta)
        entrada_total += entrada
        salida_total += salida
        cache_creada_total += cache_creada
        cache_leida_total += cache_leida
        bloques = list(getattr(respuesta, "content", []) or [])
        llamadas_turno = [
            bloque for bloque in bloques if getattr(bloque, "type", "") == "tool_use"
        ]
        if not llamadas_turno:
            respuesta_final = "\n".join(
                str(getattr(bloque, "text", ""))
                for bloque in bloques
                if getattr(bloque, "type", "") == "text"
            )
            break
        mensajes.append({"role": "assistant", "content": serializar_bloques(bloques)})
        resultados: list[dict[str, object]] = []
        for llamada in llamadas_turno:
            nombre = str(getattr(llamada, "name", ""))
            argumentos_crudos = getattr(llamada, "input", {})
            argumentos = argumentos_crudos if isinstance(argumentos_crudos, dict) else {}
            if ejecuciones >= MAXIMO_HERRAMIENTAS:
                resultado = {"error": "Presupuesto de herramientas agotado; debe finalizar"}
            else:
                resultado = ejecutar_herramienta(entorno, nombre, argumentos)
                ejecuciones += 1
            llamadas += 1
            traza.append(
                {
                    "nombre": nombre,
                    "argumentos": argumentos if nombre != "escribir_archivo" else {"ruta": argumentos.get("ruta", "")},
                    "error": resultado.get("error"),
                }
            )
            resultados.append(
                {
                    "type": "tool_result",
                    "tool_use_id": str(getattr(llamada, "id", "")),
                    "content": json.dumps(resultado, ensure_ascii=False),
                    "is_error": "error" in resultado,
                }
            )
        mensajes.append({"role": "user", "content": resultados})
    validacion = ejecutar_validacion(entorno)
    return {
        "exito": bool(respuesta_final),
        "pruebas_aprobadas": bool(validacion["aprobada"]),
        "tokens_entrada": entrada_total,
        "tokens_salida": salida_total,
        "tokens_cache_creada": cache_creada_total,
        "tokens_cache_leida": cache_leida_total,
        "llamadas_herramientas": llamadas,
        "ejecuciones_herramientas": ejecuciones,
        "duracion_segundos": round(time.perf_counter() - inicio, 3),
        "reintentos": reintentos,
        "validacion_final": validacion,
        "traza_herramientas": traza,
        "respuesta": respuesta_final,
    }


def guardar(salida: Path, resultado: dict[str, object]) -> None:
    """Guarda cada avance sin conservar secretos ni directorios temporales."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    """Ejecuta cinco tratamientos comparables con la API de Anthropic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default=MODELO_PREDETERMINADO)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("resultados/evaluacion_desarrollo_web_anthropic_v1.json"),
    )
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("Se requiere ANTHROPIC_API_KEY y al menos una repeticion")
    if not FIXTURE.is_dir() or not RUTA_SKILL.is_file() or not RUTA_MODO_EXTENDIDO.is_file():
        raise ValueError("No se encuentra el fixture, la Skill o su modo extendido")

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=0)
    indice = analizar_impacto(FIXTURE, TERMINOS_INDICE, maximo_archivos=30, maximo_fragmentos=2)
    resultado: dict[str, object] = {
        "version": 1,
        "version_adaptador": VERSION_ADAPTADOR,
        "skill": "optimizar-contexto",
        "proveedor": "anthropic-api",
        "modelo": argumentos.modelo,
        "escenario": ESCENARIO,
        "criterios": {"margen_no_inferioridad": 0.0, "ahorro_minimo_tokens": 0.2},
        "ejecuciones": [],
    }
    ejecuciones_resultado = resultado["ejecuciones"]
    if not isinstance(ejecuciones_resultado, list):
        raise RuntimeError("No se pudo inicializar la coleccion de ejecuciones")
    for repeticion in range(1, argumentos.repeticiones + 1):
        for variante in VARIANTES:
            print(f"Ejecutando {variante} {repeticion}/{argumentos.repeticiones}...")
            with tempfile.TemporaryDirectory(prefix=f"web-anthropic-{variante}-") as temporal:
                entorno = Path(temporal) / "aplicacion"
                shutil.copytree(FIXTURE, entorno)
                ejecucion = ejecutar_agente(cliente, argumentos.modelo, variante, entorno, indice)
            ejecucion.update({"escenario": ESCENARIO, "repeticion": repeticion, "variante": variante})
            ejecuciones_resultado.append(ejecucion)
            guardar(argumentos.salida, resultado)
    print(f"Resultado guardado en: {argumentos.salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (anthropic.APIError, OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
