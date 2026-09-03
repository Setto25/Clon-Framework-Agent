#!/usr/bin/env python3
"""Evalua optimizacion de contexto web aislada mediante Qwen Model Studio."""

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

from openai import APIConnectionError, APIError, APIStatusError, OpenAI, RateLimitError

if __package__:
    from .analizar_impacto import analizar_impacto
    from .evaluar_desarrollo_web_gemini import (
        FIXTURE,
        MAXIMO_HERRAMIENTAS,
        MAXIMO_REINTENTOS,
        MAXIMO_TURNOS,
        RUTA_MODO_EXTENDIDO,
        RUTA_SKILL,
        RUTAS_EDITABLES,
        TERMINOS_INDICE,
        TAREA,
        construir_instruccion,
        construir_solicitud,
        ejecutar_herramienta,
        ejecutar_validacion,
    )
else:
    from analizar_impacto import analizar_impacto
    from evaluar_desarrollo_web_gemini import (
        FIXTURE,
        MAXIMO_HERRAMIENTAS,
        MAXIMO_REINTENTOS,
        MAXIMO_TURNOS,
        RUTA_MODO_EXTENDIDO,
        RUTA_SKILL,
        RUTAS_EDITABLES,
        TERMINOS_INDICE,
        TAREA,
        construir_instruccion,
        construir_solicitud,
        ejecutar_herramienta,
        ejecutar_validacion,
    )


URL_PREDETERMINADA = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
MODELO_PREDETERMINADO = "qwen3.7-plus"
VERSION_ADAPTADOR = 4
ESCENARIO = "desarrollo-web-tareas-v4"
MAXIMO_TOKENS_SALIDA = 3000
VARIANTES: tuple[str, ...] = (
    "control_puro",
    "indice_autoritativo",
    "skill_adaptativa",
    "skill_extendida",
    "extendido_compacto",
)
VARIANTES_SELECTOR_PYTHON: tuple[str, ...] = (
    "control_puro",
    "indice_autoritativo",
    "selector_python_compacto",
)
VARIANTES_HERRAMIENTAS_EFICIENTES: tuple[str, ...] = (
    "herramientas_actuales",
    "herramientas_eficientes",
)
VARIANTES_INDICE_EFICIENTES: tuple[str, ...] = (
    "herramientas_actuales",
    "indice_con_herramientas_eficientes",
)

HERRAMIENTAS: list[dict[str, object]] = [
    {
        "type": "function",
        "function": {
            "name": "listar_archivos",
            "description": "Lista los archivos regulares del entorno web aislado.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "leer_archivo",
            "description": "Lee un archivo UTF-8 del entorno aislado.",
            "parameters": {
                "type": "object",
                "properties": {"ruta": {"type": "string"}},
                "required": ["ruta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escribir_archivo",
            "description": "Reemplaza un archivo editable dentro del entorno aislado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "contenido": {"type": "string"},
                },
                "required": ["ruta", "contenido"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_validacion",
            "description": "Ejecuta las pruebas reales de backend y frontend.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
HERRAMIENTAS_SIN_LISTADO: list[dict[str, object]] = [
    herramienta
    for herramienta in HERRAMIENTAS
    if herramienta["function"]["name"] != "listar_archivos"
]
HERRAMIENTAS_EFICIENTES: list[dict[str, object]] = json.loads(json.dumps(HERRAMIENTAS))
for herramienta in HERRAMIENTAS_EFICIENTES:
    funcion = herramienta["function"]
    if funcion["name"] == "leer_archivo":
        funcion["description"] = "Lee solo un rango de hasta 80 lineas del archivo."
        funcion["parameters"]["properties"].update({"inicio": {"type": "integer"}, "limite": {"type": "integer"}})
HERRAMIENTAS_EFICIENTES.extend(
    [
        {
            "type": "function",
            "function": {
                "name": "buscar_texto",
                "description": "Busca un texto literal y devuelve como maximo doce coincidencias con linea y fragmento.",
                "parameters": {
                    "type": "object",
                    "properties": {"ruta": {"type": "string"}, "texto": {"type": "string"}},
                    "required": ["ruta", "texto"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "leer_lote",
                "description": "Lee hasta cuatro rangos independientes en una sola llamada; cada rango admite ruta, inicio y limite de hasta 80 lineas.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lecturas": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ruta": {"type": "string"},
                                    "inicio": {"type": "integer"},
                                    "limite": {"type": "integer"},
                                },
                                "required": ["ruta"],
                            },
                        }
                    },
                    "required": ["lecturas"],
                },
            },
        },
    ]
)
HERRAMIENTAS_EFICIENTES_SIN_LISTADO: list[dict[str, object]] = [
    h for h in HERRAMIENTAS_EFICIENTES
    if h["function"]["name"] != "listar_archivos"
]


def usa_indice_autoritativo(variante: str) -> bool:
    """Determina si la variante recibe un indice fresco que sustituye el listado."""
    return variante != "control_puro"


def construir_instruccion_qwen(variante: str) -> str:
    """Refuerza el indice fresco sin cambiar los requisitos funcionales medidos."""
    if variante == "selector_python_compacto":
        return (
            "Trabajas dentro de un fixture temporal aislado. Las pruebas son inmutables. "
            f"Dispones de hasta {MAXIMO_HERRAMIENTAS} ejecuciones de herramientas. "
            "Python ya selecciono el modo indice y rutas iniciales. Lee solo las rutas "
            "indicadas o sus dependencias directas, edita fuentes, valida y entrega una "
            "respuesta final breve. No cargues ni apliques la Skill optimizar-contexto."
        )
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
    """Retira el listado general cuando un indice autoritativo ya lo reemplaza."""
    return HERRAMIENTAS_SIN_LISTADO if usa_indice_autoritativo(variante) else HERRAMIENTAS


def es_variante_eficiente(variante: str) -> bool:
    """Determina si la ejecucion aplica resultados acotados y cache local."""
    return variante == "herramientas_eficientes"


def es_variante_indice_eficiente(variante: str) -> bool:
    """Determina si la ejecucion combina indice autoritativo y herramientas eficientes."""
    return variante == "indice_con_herramientas_eficientes"


def construir_solicitud_indice_eficiente(indice: dict[str, object]) -> str:
    """Entrega una lista compacta de rutas junto con las busquedas obligatorias de contratos."""
    archivos = indice.get("archivos", [])
    rutas = sorted(set(
        str(a.get("ruta", ""))
        for a in archivos
        if isinstance(a, dict) and a.get("ruta")
    ))
    lista_rutas = "\n".join(f"- {r}" for r in rutas) or "No se detectaron archivos"
    return (
        f"{solicitud_herramientas_eficientes()}\n\n"
        f"ARCHIVOS_EN_ENTORNO:\n{lista_rutas}\n\n"
        "No ejecutes listar_archivos. Usa buscar_texto o leer_archivo para acceder al contenido."
    )


def preparar_contexto_herramientas_eficientes(entorno: Path) -> None:
    """Crea fuentes extensas solo dentro de la copia temporal para activar lecturas selectivas."""
    contenido_api = ["\"\"\"Conserva el contrato de consulta de API para la evaluacion.\"\"\"", ""]
    contenido_interfaz = ["// Conserva el contrato de consulta de interfaz para la evaluacion.", ""]
    for numero in range(1, 121):
        contenido_api.append(f"# Contexto auxiliar de API {numero:03d}.")
        contenido_interfaz.append(f"// Contexto auxiliar de interfaz {numero:03d}.")
    contenido_api.extend(
        [
            "",
            "MARCADOR_API = 'POST valida titulo y PATCH alterna completada'",
            "",
        ]
    )
    contenido_interfaz.extend(
        [
            "",
            "const MARCADOR_INTERFAZ = 'aria-live y filtros conservan accesibilidad';",
            "",
        ]
    )
    with (entorno / "backend" / "contrato_contexto.py").open(
        "w", encoding="utf-8", newline="\n"
    ) as flujo:
        flujo.write("\n".join(contenido_api))
    with (entorno / "interfaz" / "contrato_contexto.js").open(
        "w", encoding="utf-8", newline="\n"
    ) as flujo:
        flujo.write("\n".join(contenido_interfaz))


def solicitud_herramientas_eficientes() -> str:
    """Define una tarea que obliga a usar busquedas acotadas antes de editar."""
    return (
        f"{TAREA}\n\n"
        "Antes de editar ejecuta obligatoriamente estas dos llamadas en este orden:\n"
        "1. buscar_texto(ruta='backend/contrato_contexto.py', texto='MARCADOR_API')\n"
        "2. buscar_texto(ruta='interfaz/contrato_contexto.js', texto='MARCADOR_INTERFAZ')\n"
        "No leas esos archivos completos en ningun momento. Una vez obtenidos los marcadores, "
        "edita las fuentes autorizadas, ejecuta la validacion y en la respuesta final cita "
        "el valor literal de cada marcador observado."
    )


def limitar_lectura(resultado: dict[str, object], argumentos: dict[str, object]) -> tuple[dict[str, object], bool]:
    """Reduce una lectura a un rango seguro y declara si omite lineas del archivo."""
    contenido = resultado.get("contenido")
    if not isinstance(contenido, str):
        return resultado, False
    lineas = contenido.splitlines()
    inicio = max(1, int(argumentos.get("inicio", 1) or 1))
    limite = min(80, max(1, int(argumentos.get("limite", 80) or 80)))
    final = inicio - 1 + limite
    truncado = final < len(lineas)
    return {
        **resultado,
        "contenido": "\n".join(lineas[inicio - 1 : final]),
        "inicio": inicio,
        "limite": limite,
        "truncado": truncado,
    }, truncado


def ejecutar_herramienta_eficiente(
    entorno: Path, nombre: str, argumentos: dict[str, object]
) -> tuple[dict[str, object], int, int]:
    """Ejecuta busquedas, rangos y lotes confinados y devuelve sus contadores observables."""
    if nombre == "leer_archivo":
        resultado, truncado = limitar_lectura(
            ejecutar_herramienta(entorno, nombre, argumentos), argumentos
        )
        return resultado, int(truncado), 0
    if nombre == "buscar_texto":
        ruta = str(argumentos.get("ruta", ""))
        texto = str(argumentos.get("texto", ""))
        original = ejecutar_herramienta(entorno, "leer_archivo", {"ruta": ruta})
        contenido = original.get("contenido")
        if not texto or not isinstance(contenido, str):
            return {"error": original.get("error", "Texto de busqueda invalido")}, 0, 0
        coincidencias = [
            {"linea": numero, "fragmento": linea[:240]}
            for numero, linea in enumerate(contenido.splitlines(), start=1)
            if texto in linea
        ][:12]
        return {"ruta": ruta, "texto": texto, "coincidencias": coincidencias}, 0, 0
    if nombre == "leer_lote":
        lecturas = argumentos.get("lecturas")
        if not isinstance(lecturas, list) or not 1 <= len(lecturas) <= 4:
            return {"error": "lecturas debe contener entre una y cuatro lecturas"}, 0, 0
        resultados: list[dict[str, object]] = []
        truncadas = 0
        for lectura in lecturas:
            if not isinstance(lectura, dict):
                return {"error": "Cada lectura debe ser un objeto"}, 0, 0
            resultado, truncado = limitar_lectura(
                ejecutar_herramienta(entorno, "leer_archivo", lectura), lectura
            )
            resultados.append(resultado)
            truncadas += int(truncado)
        return {"lecturas": resultados}, truncadas, 1
    return ejecutar_herramienta(entorno, nombre, argumentos), 0, 0


def construir_solicitud_selector(indice: dict[str, object]) -> str:
    """Reduce el preanalisis a rutas editables que Python selecciona localmente."""
    archivos = indice.get("archivos", [])
    rutas = [
        str(archivo.get("ruta", ""))
        for archivo in archivos
        if isinstance(archivo, dict) and str(archivo.get("ruta", "")) in RUTAS_EDITABLES
    ]
    rutas_unicas = sorted(set(rutas))
    paquete = ", ".join(rutas_unicas) or "No se detectaron rutas editables"
    return (
        f"{TAREA}\n\nPLAN_LOCAL_AUTORITATIVO: modo=indice; rutas "
        f"iniciales={paquete}. No ejecutes listar_archivos. Lee estas rutas primero, "
        "edita solo fuentes autorizadas y ejecuta la validacion antes de finalizar."
    )


def uso(respuesta: object) -> tuple[int, int, int]:
    """Extrae tokens de entrada, salida y razonamiento sin asumir campos opcionales."""
    datos = getattr(respuesta, "usage", None)
    entrada = int(getattr(datos, "prompt_tokens", 0) or 0)
    salida = int(getattr(datos, "completion_tokens", 0) or 0)
    detalle = getattr(datos, "completion_tokens_details", None)
    razonamiento = int(
        getattr(detalle, "reasoning_tokens", 0)
        or getattr(datos, "reasoning_tokens", 0)
        or 0
    )
    return entrada, salida, razonamiento


def segundos_espera(error: APIError, intento: int) -> int | None:
    """Determina una espera acotada para errores transitorios del proveedor."""
    if isinstance(error, (APIConnectionError, RateLimitError)):
        return 5 * (2**intento)
    if isinstance(error, APIStatusError) and error.status_code >= 500:
        return 5 * (2**intento)
    return None


def solicitar(
    cliente: OpenAI,
    modelo: str,
    mensajes: list[dict[str, object]],
    herramientas: list[dict[str, object]] | None,
    con_razonamiento: bool,
) -> tuple[Any, int]:
    """Solicita una respuesta compatible con OpenAI y reintenta fallos temporales."""
    reintentos = 0
    for intento in range(MAXIMO_REINTENTOS + 1):
        try:
            parametros: dict[str, object] = {
                "model": modelo,
                "messages": mensajes,
                "temperature": 0,
                "max_completion_tokens": MAXIMO_TOKENS_SALIDA,
                "extra_body": {"enable_thinking": con_razonamiento},
            }
            if herramientas:
                parametros["tools"] = herramientas
            respuesta = cliente.chat.completions.create(**parametros)
            return respuesta, reintentos
        except APIError as error:
            espera = segundos_espera(error, intento)
            if espera is None or intento == MAXIMO_REINTENTOS:
                raise
            reintentos += 1
            print(
                f"Error temporal de Qwen; se reintentara en {espera} segundos "
                f"({reintentos}/{MAXIMO_REINTENTOS})."
            )
            time.sleep(espera)
    raise RuntimeError("No se obtuvo respuesta de Qwen")


def serializar_mensaje(mensaje: object) -> dict[str, object]:
    """Convierte un mensaje de SDK a la estructura reenviable de Chat Completions."""
    convertir = getattr(mensaje, "model_dump", None)
    if callable(convertir):
        datos = convertir(exclude_none=True)
        if isinstance(datos, dict):
            return datos
    return {
        "role": str(getattr(mensaje, "role", "assistant")),
        "content": getattr(mensaje, "content", None),
    }


def extraer_argumentos(llamada: object) -> dict[str, object]:
    """Decodifica argumentos JSON de una llamada sin ejecutar texto invalido."""
    funcion = getattr(llamada, "function", None)
    bruto = getattr(funcion, "arguments", "{}")
    try:
        datos: object = json.loads(str(bruto))
    except json.JSONDecodeError:
        return {"_error_argumentos": "La llamada contiene JSON invalido"}
    return datos if isinstance(datos, dict) else {"_error_argumentos": "Se esperaba un objeto"}


def ejecutar_agente(
    cliente: OpenAI,
    modelo: str,
    variante: str,
    entorno: Path,
    indice: dict[str, object],
    con_razonamiento: bool,
) -> dict[str, object]:
    """Ejecuta una variante en un fixture y conserva sus metricas comparables."""
    _variantes_con_herramientas = set(VARIANTES_HERRAMIENTAS_EFICIENTES) | set(VARIANTES_INDICE_EFICIENTES)
    variante_base = "control_puro" if variante in _variantes_con_herramientas else variante
    _instruccion_base = (
        "indice_autoritativo" if es_variante_indice_eficiente(variante) else variante_base
    )
    mensajes: list[dict[str, object]] = [
        {"role": "system", "content": construir_instruccion_qwen(_instruccion_base)},
        {
            "role": "user",
            "content": (
                construir_solicitud_indice_eficiente(indice)
                if es_variante_indice_eficiente(variante)
                else solicitud_herramientas_eficientes()
                if variante in _variantes_con_herramientas
                else (
                    construir_solicitud_selector(indice)
                    if variante == "selector_python_compacto"
                    else construir_solicitud(variante_base, indice)
                )
            ),
        },
    ]
    entrada_total = salida_total = razonamiento_total = 0
    llamadas = ejecuciones = reintentos = 0
    traza: list[dict[str, object]] = []
    cache: dict[str, dict[str, object]] = {}
    bytes_entregados = aciertos_cache = lecturas_truncadas = lecturas_lote = 0
    busquedas_texto = solicitudes_api = 0
    duracion_api_segundos = 0.0
    respuesta_final = ""
    inicio_medicion = time.perf_counter()
    inicio_pared = time.time()
    for _ in range(MAXIMO_TURNOS):
        inicio_solicitud = time.perf_counter()
        respuesta, nuevos_reintentos = solicitar(
            cliente,
            modelo,
            mensajes,
            (
                HERRAMIENTAS_EFICIENTES_SIN_LISTADO if es_variante_indice_eficiente(variante)
                else HERRAMIENTAS_EFICIENTES if es_variante_eficiente(variante)
                else herramientas_disponibles(variante_base)
            )
            if ejecuciones < MAXIMO_HERRAMIENTAS
            else None,
            con_razonamiento,
        )
        duracion_api_segundos += time.perf_counter() - inicio_solicitud
        solicitudes_api += 1
        reintentos += nuevos_reintentos
        entrada, salida, razonamiento = uso(respuesta)
        entrada_total += entrada
        salida_total += salida
        razonamiento_total += razonamiento
        mensaje = respuesta.choices[0].message
        solicitudes = list(getattr(mensaje, "tool_calls", None) or [])
        if not solicitudes:
            respuesta_final = str(getattr(mensaje, "content", "") or "")
            break
        mensajes.append(serializar_mensaje(mensaje))
        for solicitud in solicitudes:
            funcion = getattr(solicitud, "function", None)
            nombre = str(getattr(funcion, "name", ""))
            argumentos = extraer_argumentos(solicitud)
            if "_error_argumentos" in argumentos:
                resultado = {"error": str(argumentos["_error_argumentos"])}
            elif ejecuciones >= MAXIMO_HERRAMIENTAS:
                resultado = {"error": "Presupuesto de herramientas agotado; debe finalizar"}
            else:
                firma = json.dumps({"nombre": nombre, "argumentos": argumentos}, sort_keys=True)
                resultado = cache.get(firma)
                if resultado is None:
                    if es_variante_eficiente(variante) or es_variante_indice_eficiente(variante):
                        resultado, nuevas_truncadas, nuevos_lotes = ejecutar_herramienta_eficiente(
                            entorno, nombre, argumentos
                        )
                        lecturas_truncadas += nuevas_truncadas
                        lecturas_lote += nuevos_lotes
                        busquedas_texto += int(nombre == "buscar_texto")
                    else:
                        resultado = ejecutar_herramienta(entorno, nombre, argumentos)
                    cache[firma] = resultado
                else:
                    aciertos_cache += 1
                if nombre == "escribir_archivo":
                    cache.clear()
                bytes_entregados += len(json.dumps(resultado, ensure_ascii=False).encode("utf-8"))
                ejecuciones += 1
            llamadas += 1
            traza.append(
                {
                    "nombre": nombre,
                    "argumentos": (
                        argumentos
                        if nombre != "escribir_archivo"
                        else {"ruta": argumentos.get("ruta", "")}
                    ),
                    "error": resultado.get("error"),
                }
            )
            mensajes.append(
                {
                    "role": "tool",
                    "tool_call_id": str(getattr(solicitud, "id", "")),
                    "content": json.dumps(resultado, ensure_ascii=False),
                }
            )
    inicio_validacion = time.perf_counter()
    validacion = ejecutar_validacion(entorno)
    duracion_validacion_segundos = time.perf_counter() - inicio_validacion
    duracion_segundos = time.perf_counter() - inicio_medicion
    duracion_pared = time.time() - inicio_pared
    duracion_anomala = (
        duracion_segundos > (duracion_api_segundos + duracion_validacion_segundos + 60)
        or duracion_pared > 300
    )
    return {
        "exito": bool(respuesta_final),
        "pruebas_aprobadas": bool(validacion["aprobada"]),
        "tokens_entrada": entrada_total,
        "tokens_salida": salida_total,
        "tokens_razonamiento": razonamiento_total,
        "llamadas_herramientas": llamadas,
        "ejecuciones_herramientas": ejecuciones,
        "duracion_segundos": round(duracion_segundos, 3),
        "duracion_api_segundos": round(duracion_api_segundos, 3),
        "duracion_validacion_segundos": round(duracion_validacion_segundos, 3),
        "duracion_anomala": duracion_anomala,
        "solicitudes_api": solicitudes_api,
        "reintentos": reintentos,
        "bytes_herramientas_entregados": bytes_entregados,
        "aciertos_cache": aciertos_cache,
        "lecturas_truncadas": lecturas_truncadas,
        "lecturas_lote": lecturas_lote,
        "busquedas_texto": busquedas_texto,
        "mecanismos_activados": bool(
            lecturas_truncadas or lecturas_lote or busquedas_texto or aciertos_cache
        ),
        "validacion_final": validacion,
        "traza_herramientas": traza,
        "respuesta": respuesta_final,
    }


def guardar(salida: Path, resultado: dict[str, object]) -> None:
    """Guarda cada avance de medicion sin incluir secretos ni directorios temporales."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Ejecuta cinco tratamientos aislados mediante una API Qwen compatible."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default=MODELO_PREDETERMINADO)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument(
        "--url",
        default=os.environ.get("QWEN_BASE_URL", URL_PREDETERMINADA),
        help="URL base compatible con OpenAI de Model Studio.",
    )
    parser.add_argument("--herramientas-eficientes", action="store_true")
    parser.add_argument(
        "--indice-eficiente",
        action="store_true",
        help="Combina indice autoritativo y herramientas eficientes frente al control.",
    )
    parser.add_argument(
        "--selector-python",
        action="store_true",
        help="Compara control, indice completo y selector local compacto.",
    )
    parser.add_argument(
        "--con-razonamiento",
        action="store_true",
        help="Activa enable_thinking en todas las variantes.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("resultados/evaluacion_desarrollo_web_qwen_v2.json"),
    )
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("DASHSCOPE_API_KEY"):
        raise ValueError("Se requiere DASHSCOPE_API_KEY y al menos una repeticion")
    if not FIXTURE.is_dir() or not RUTA_SKILL.is_file() or not RUTA_MODO_EXTENDIDO.is_file():
        raise ValueError("No se encuentra el fixture, la Skill o su modo extendido")

    cliente = OpenAI(api_key=os.environ["DASHSCOPE_API_KEY"], base_url=argumentos.url)
    indice = analizar_impacto(FIXTURE, TERMINOS_INDICE, maximo_archivos=30, maximo_fragmentos=2)
    variantes = (
        VARIANTES_HERRAMIENTAS_EFICIENTES if argumentos.herramientas_eficientes
        else VARIANTES_INDICE_EFICIENTES if argumentos.indice_eficiente
        else VARIANTES_SELECTOR_PYTHON if argumentos.selector_python
        else VARIANTES
    )
    escenario = (
        "desarrollo-web-herramientas-eficientes-v2" if argumentos.herramientas_eficientes
        else "desarrollo-web-indice-eficiente-v1" if argumentos.indice_eficiente
        else "desarrollo-web-selector-python-v1" if argumentos.selector_python
        else ESCENARIO
    )
    resultado: dict[str, object] = {
        "version": 1,
        "version_adaptador": VERSION_ADAPTADOR,
        "skill": "optimizar-contexto",
        "proveedor": "qwen-model-studio",
        "modelo": argumentos.modelo,
        "escenario": escenario,
        "razonamiento_habilitado": argumentos.con_razonamiento,
        "criterios": {"margen_no_inferioridad": 0.0, "ahorro_minimo_tokens": 0.2},
        "ejecuciones": [],
    }
    ejecuciones_resultado = resultado["ejecuciones"]
    if not isinstance(ejecuciones_resultado, list):
        raise RuntimeError("No se pudo inicializar la coleccion de ejecuciones")
    for repeticion in range(1, argumentos.repeticiones + 1):
        for variante in variantes:
            print(f"Ejecutando {variante} {repeticion}/{argumentos.repeticiones}...")
            with tempfile.TemporaryDirectory(prefix=f"web-qwen-{variante}-") as temporal:
                entorno = Path(temporal) / "aplicacion"
                shutil.copytree(FIXTURE, entorno)
                if argumentos.herramientas_eficientes or argumentos.indice_eficiente:
                    preparar_contexto_herramientas_eficientes(entorno)
                ejecucion = ejecutar_agente(
                    cliente,
                    argumentos.modelo,
                    variante,
                    entorno,
                    indice,
                    argumentos.con_razonamiento,
                )
            ejecucion.update(
                {"escenario": escenario, "repeticion": repeticion, "variante": variante}
            )
            ejecuciones_resultado.append(ejecucion)
            guardar(argumentos.salida, resultado)
    print(f"Resultado guardado en: {argumentos.salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (APIError, OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
