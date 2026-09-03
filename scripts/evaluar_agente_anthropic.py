#!/usr/bin/env python3
"""Evalua una Skill mediante Claude Sonnet con la API de Anthropic."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import anthropic

if __package__:
    from .analizar_impacto import analizar_impacto
    from .evaluar_agente_gemini import (
        ESCENARIO,
        MAXIMO_CORRECCIONES,
        MAXIMO_REINTENTOS_CUOTA,
        MAXIMO_TURNOS,
        RAIZ,
        RUTA_SKILL,
        TERMINOS_IMPACTO,
        VARIANTES_EXPERIMENTO,
        construir_solicitud,
        ejecutar_herramienta,
        firma_consulta,
        registrar_rutas,
    )
    from .validar_resultado_agente import (
        RUTAS_ESENCIALES_MIGRACION,
        crear_indice_con_requisitos,
        crear_retroalimentacion,
        evaluar_auditoria,
    )
else:
    from analizar_impacto import analizar_impacto
    from evaluar_agente_gemini import (
        ESCENARIO,
        MAXIMO_CORRECCIONES,
        MAXIMO_REINTENTOS_CUOTA,
        MAXIMO_TURNOS,
        RAIZ,
        RUTA_SKILL,
        TERMINOS_IMPACTO,
        VARIANTES_EXPERIMENTO,
        construir_solicitud,
        ejecutar_herramienta,
        firma_consulta,
        registrar_rutas,
    )
    from validar_resultado_agente import (
        RUTAS_ESENCIALES_MIGRACION,
        crear_indice_con_requisitos,
        crear_retroalimentacion,
        evaluar_auditoria,
    )


MODELO_PREDETERMINADO = "claude-sonnet-4-6"
NOMBRE_SKILL = "optimizar-contexto"
VERSION_ADAPTADOR = 5
MAXIMO_TOKENS_SALIDA = 6000
MAXIMO_EJECUCIONES_HERRAMIENTAS = 12
MAXIMO_REPARACIONES_TRUNCAMIENTO = 1
HERRAMIENTAS: list[dict[str, object]] = [
    {
        "name": "listar_archivos",
        "description": "Lista hasta 40 archivos bajo un prefijo especifico; no admite la raiz.",
        "input_schema": {
            "type": "object",
            "properties": {"prefijo": {"type": "string"}},
            "required": ["prefijo"],
        },
    },
    {
        "name": "buscar_texto",
        "description": "Busca texto literal en archivos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patron": {"type": "string"},
                "prefijo": {"type": "string"},
            },
            "required": ["patron"],
        },
    },
    {
        "name": "leer_archivo",
        "description": "Lee lineas de un archivo del repositorio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string"},
                "inicio": {"type": "integer"},
                "limite": {"type": "integer"},
            },
            "required": ["ruta"],
        },
    },
]


def construir_instruccion(variante: str) -> str:
    """Construye instrucciones que separan descubrimiento, indice y Skill."""
    instruccion = (
        "Lee AGENTS.md antes de actuar, usa evidencia verificable y realiza como maximo "
        f"{MAXIMO_EJECUCIONES_HERRAMIENTAS} ejecuciones de herramientas. La respuesta "
        "JSON final debe ser compacta."
    )
    if variante == "control_puro":
        return (
            f"{instruccion} No recibes un indice previo ni debes aplicar el protocolo "
            "optimizar-contexto; descubre la evidencia necesaria mediante herramientas."
        )
    instruccion += (
        " El indice local adjunto ya cuenta como observacion de sus rutas y fragmentos; "
        "en el primer turno no tendras herramientas y debes emitir el JSON completo "
        "usando el indice, incluidas sus evidencias_disponibles. No repitas con "
        "buscar_texto los terminos que ya cubre. Si la rubrica rechaza ese JSON, "
        "las lecturas posteriores deben limitarse a los patrones rechazados."
    )
    if variante == "skill":
        protocolo = RUTA_SKILL.read_text(encoding="utf-8")
        return (
            f"{instruccion} La Skill {NOMBRE_SKILL} ya esta cargada a continuacion; "
            "aplicala sin volver a leer su archivo solo para descubrir sus instrucciones.\n\n"
            f"{protocolo}"
        )
    if variante == "indice":
        return f"{instruccion} No apliques el protocolo {NOMBRE_SKILL}."
    raise ValueError(f"Variante no soportada: {variante}")


def serializar_bloques(bloques: list[Any]) -> list[dict[str, object]]:
    """Convierte bloques del SDK en contenido reutilizable por la API."""
    resultado: list[dict[str, object]] = []
    for bloque in bloques:
        datos = bloque.model_dump(mode="json", exclude_none=True)
        if isinstance(datos, dict):
            resultado.append(datos)
    return resultado


def uso(respuesta: Any) -> tuple[int, int, int, int]:
    """Suma entradas sin cache, creaciones, lecturas de cache y salida."""
    datos = respuesta.usage
    entrada = int(getattr(datos, "input_tokens", 0) or 0)
    cache_creada = int(getattr(datos, "cache_creation_input_tokens", 0) or 0)
    cache_leida = int(getattr(datos, "cache_read_input_tokens", 0) or 0)
    salida = int(getattr(datos, "output_tokens", 0) or 0)
    return entrada + cache_creada + cache_leida, salida, cache_creada, cache_leida


def segundos_espera(error: anthropic.APIError, intento: int) -> int | None:
    """Determina una espera acotada para errores transitorios del proveedor."""
    transitorio = isinstance(
        error,
        (
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
            anthropic.RateLimitError,
        ),
    )
    if isinstance(error, anthropic.APIStatusError) and error.status_code >= 500:
        transitorio = True
    if not transitorio:
        return None
    respuesta = getattr(error, "response", None)
    cabecera = respuesta.headers.get("retry-after") if respuesta is not None else None
    try:
        return max(1, math.ceil(float(cabecera))) if cabecera else 5 * (2**intento)
    except (TypeError, ValueError):
        return 5 * (2**intento)


def solicitar(
    cliente: anthropic.Anthropic,
    modelo: str,
    sistema: str,
    mensajes: list[dict[str, object]],
    permitir_herramientas: bool = True,
) -> tuple[Any, int]:
    """Solicita una respuesta y contabiliza reintentos transitorios."""
    reintentos = 0
    for intento in range(MAXIMO_REINTENTOS_CUOTA + 1):
        try:
            parametros: dict[str, object] = {
                "model": modelo,
                "max_tokens": MAXIMO_TOKENS_SALIDA,
                "system": sistema,
                "messages": mensajes,
            }
            if permitir_herramientas:
                parametros["tools"] = HERRAMIENTAS
            respuesta = cliente.messages.create(**parametros)
            return respuesta, reintentos
        except anthropic.APIError as error:
            espera = segundos_espera(error, intento)
            if espera is None or intento == MAXIMO_REINTENTOS_CUOTA:
                raise
            reintentos += 1
            print(
                f"Error temporal de Anthropic; se reintentara en {espera} segundos "
                f"({reintentos}/{MAXIMO_REINTENTOS_CUOTA})."
            )
            time.sleep(espera)
    raise RuntimeError("No se obtuvo una respuesta de Anthropic")


def ejecutar_agente(
    cliente: anthropic.Anthropic,
    modelo: str,
    variante: str,
    indice_impacto: dict[str, object] | None,
) -> dict[str, object]:
    """Ejecuta el ciclo Sonnet con el mismo contrato factual de Gemini."""
    solicitud, indice_serializado = construir_solicitud(variante, indice_impacto)
    mensajes: list[dict[str, object]] = [
        {
            "role": "user",
            "content": solicitud,
        }
    ]
    entrada_total = salida_total = llamadas = reintentos = 0
    cache_creada_total = cache_leida_total = 0
    ejecuciones_herramientas = aciertos_cache = 0
    cache: dict[str, dict[str, object]] = {}
    rutas_observadas: set[str] = set()
    if indice_impacto is not None:
        registrar_rutas(indice_impacto, rutas_observadas)
    traza_herramientas: list[dict[str, object]] = []
    violaciones_protocolo: list[str] = []
    historial_rubrica: list[dict[str, object]] = []
    razones_detencion: list[str] = []
    correcciones = 0
    truncamientos = 0
    herramientas_rechazadas = 0
    cierre_solicitado = False
    texto_final = ""
    respuesta_estructurada: dict[str, object] | None = None
    fallos_finales: list[str] = []
    inicio = time.perf_counter()
    sistema = construir_instruccion(variante)

    for _ in range(MAXIMO_TURNOS):
        permitir_herramientas = (
            (variante == "control_puro" or correcciones > 0)
            and ejecuciones_herramientas < MAXIMO_EJECUCIONES_HERRAMIENTAS
        )
        respuesta, nuevos_reintentos = solicitar(
            cliente,
            modelo,
            sistema,
            mensajes,
            permitir_herramientas,
        )
        reintentos += nuevos_reintentos
        entrada, salida, cache_creada, cache_leida = uso(respuesta)
        entrada_total += entrada
        salida_total += salida
        cache_creada_total += cache_creada
        cache_leida_total += cache_leida
        bloques = serializar_bloques(list(respuesta.content))
        razon_detencion = str(getattr(respuesta, "stop_reason", "") or "desconocida")
        razones_detencion.append(razon_detencion)
        llamadas_turno = [
            bloque for bloque in bloques if bloque.get("type") == "tool_use"
        ]
        if not llamadas_turno:
            texto_candidato = "\n".join(
                str(bloque.get("text", ""))
                for bloque in bloques
                if bloque.get("type") == "text"
            )
            if razon_detencion == "max_tokens":
                truncamientos += 1
                if truncamientos <= MAXIMO_REPARACIONES_TRUNCAMIENTO:
                    mensajes.append({"role": "assistant", "content": bloques})
                    mensajes.append(
                        {
                            "role": "user",
                            "content": (
                                "La respuesta quedo truncada por el limite de salida. "
                                "Emite nuevamente el objeto JSON completo y valido, con "
                                "descripciones mas breves y sin explicaciones externas."
                            ),
                        }
                    )
                    continue
                texto_final = texto_candidato
                fallos_finales = [
                    "La respuesta final fue truncada por el limite de salida"
                ]
                historial_rubrica.append(
                    {"revision": correcciones, "fallos": fallos_finales}
                )
                break
            estructura_candidata, fallos = evaluar_auditoria(
                texto_candidato,
                RAIZ,
                rutas_observadas,
                RUTAS_ESENCIALES_MIGRACION,
                violaciones_protocolo,
            )
            historial_rubrica.append({"revision": correcciones, "fallos": fallos})
            if fallos and correcciones < MAXIMO_CORRECCIONES and not violaciones_protocolo:
                correcciones += 1
                mensajes.append({"role": "assistant", "content": bloques})
                mensajes.append(
                    {"role": "user", "content": crear_retroalimentacion(fallos)}
                )
                continue
            texto_final = texto_candidato
            respuesta_estructurada = estructura_candidata
            fallos_finales = fallos
            break

        mensajes.append({"role": "assistant", "content": bloques})
        resultados_herramientas: list[dict[str, object]] = []
        for llamada in llamadas_turno:
            nombre = str(llamada.get("name", ""))
            entrada_herramienta = llamada.get("input", {})
            argumentos = entrada_herramienta if isinstance(entrada_herramienta, dict) else {}
            firma = firma_consulta(nombre, argumentos)
            if nombre == "listar_archivos" and not str(argumentos.get("prefijo", "")).strip(" ./\\"):
                violaciones_protocolo.append("Se solicito un listado general de la raiz")
            if ejecuciones_herramientas >= MAXIMO_EJECUCIONES_HERRAMIENTAS:
                resultado = {
                    "error": (
                        "Presupuesto de lecturas agotado; debe resolverse con el indice "
                        "local y los resultados ya disponibles"
                    )
                }
                herramientas_rechazadas += 1
            elif firma in cache:
                resultado = {
                    "cache": True,
                    "firma": firma,
                    "mensaje": "El resultado completo ya esta disponible en el historial.",
                }
                aciertos_cache += 1
            else:
                resultado = ejecutar_herramienta(nombre, argumentos)
                cache[firma] = resultado
                registrar_rutas(resultado, rutas_observadas)
                ejecuciones_herramientas += 1
            traza_herramientas.append(
                {
                    "nombre": nombre,
                    "argumentos": argumentos,
                    "firma": firma,
                    "cache": resultado.get("cache") is True,
                    "error": resultado.get("error"),
                }
            )
            resultados_herramientas.append(
                {
                    "type": "tool_result",
                    "tool_use_id": str(llamada.get("id", "")),
                    "content": json.dumps(resultado, ensure_ascii=False),
                    "is_error": "error" in resultado,
                }
            )
            llamadas += 1
        if (
            ejecuciones_herramientas >= MAXIMO_EJECUCIONES_HERRAMIENTAS
            and not cierre_solicitado
        ):
            resultados_herramientas.append(
                {
                    "type": "text",
                    "text": (
                        "El presupuesto de lecturas se agoto. No habra mas "
                        "herramientas disponibles; emite ahora el objeto JSON final "
                        "con la evidencia ya obtenida."
                    ),
                }
            )
            cierre_solicitado = True
        mensajes.append({"role": "user", "content": resultados_herramientas})

    if not texto_final:
        fallos_finales = [
            "El agente Anthropic excedio el limite de turnos sin respuesta final"
        ]
        historial_rubrica.append(
            {"revision": correcciones, "fallos": fallos_finales}
        )
    return {
        "exito": bool(texto_final),
        "pruebas_aprobadas": not fallos_finales,
        "tokens_entrada": entrada_total,
        "tokens_salida": salida_total,
        "tokens_cache_creada": cache_creada_total,
        "tokens_cache_leida": cache_leida_total,
        "llamadas_herramientas": llamadas,
        "ejecuciones_herramientas": ejecuciones_herramientas,
        "aciertos_cache": aciertos_cache,
        "herramientas_rechazadas": herramientas_rechazadas,
        "duracion_segundos": round(time.perf_counter() - inicio, 3),
        "reintentos": reintentos,
        "analisis_local": {
            "indice_incluido": indice_impacto is not None,
            "terminos": indice_impacto.get("terminos", []) if indice_impacto else [],
            "archivos_examinados": indice_impacto.get("archivos_examinados", 0)
            if indice_impacto
            else 0,
            "archivos_con_coincidencias": indice_impacto.get(
                "archivos_con_coincidencias", 0
            ) if indice_impacto else 0,
            "coincidencias": indice_impacto.get("coincidencias", 0)
            if indice_impacto
            else 0,
            "caracteres_serializados": len(indice_serializado),
            "rutas_requeridas": len(RUTAS_ESENCIALES_MIGRACION),
        },
        "rutas_observadas": sorted(rutas_observadas),
        "traza_herramientas": traza_herramientas,
        "violaciones_protocolo": violaciones_protocolo,
        "correcciones": correcciones,
        "truncamientos": truncamientos,
        "razones_detencion": razones_detencion,
        "historial_rubrica": historial_rubrica,
        "rubrica_fallos": fallos_finales,
        "respuesta_estructurada": respuesta_estructurada,
        "respuesta": texto_final,
    }


def guardar_resultado(salida: Path, resultado: dict[str, object]) -> None:
    """Guarda cada avance de la medicion en JSON UTF-8."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="\n") as flujo:
        json.dump(resultado, flujo, ensure_ascii=False, indent=2)
        flujo.write("\n")


def cargar_reanudacion(
    salida: Path,
    modelo: str,
    repeticiones: int,
) -> list[dict[str, object]]:
    """Carga solo ejecuciones Anthropic compatibles con el escenario vigente."""
    if not salida.is_file():
        return []
    datos = json.loads(salida.read_text(encoding="utf-8"))
    if (
        datos.get("skill") != NOMBRE_SKILL
        or datos.get("modelo") != modelo
        or datos.get("proveedor") != "anthropic-api"
        or datos.get("version_adaptador") != VERSION_ADAPTADOR
    ):
        raise ValueError("El resultado existente no corresponde a esta Skill, proveedor o modelo")
    ejecuciones = datos.get("ejecuciones")
    if not isinstance(ejecuciones, list):
        raise ValueError("El resultado existente no contiene ejecuciones validas")
    return [
        ejecucion
        for ejecucion in ejecuciones
        if isinstance(ejecucion, dict)
        and ejecucion.get("escenario") == ESCENARIO
        and isinstance(ejecucion.get("repeticion"), int)
        and 1 <= ejecucion["repeticion"] <= repeticiones
        and ejecucion.get("variante") in set(VARIANTES_EXPERIMENTO)
    ]


def main() -> int:
    """Ejecuta tres variantes comparables mediante la API de Anthropic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default=MODELO_PREDETERMINADO)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("resultados/evaluacion_sistema_anthropic_v8.json"),
    )
    parser.add_argument("--reanudar", action="store_true")
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("Se requiere ANTHROPIC_API_KEY y al menos una repeticion")

    cliente = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        max_retries=0,
    )
    indice_impacto = crear_indice_con_requisitos(
        analizar_impacto(RAIZ, TERMINOS_IMPACTO),
        RUTAS_ESENCIALES_MIGRACION,
        RAIZ,
    )
    ejecuciones = (
        cargar_reanudacion(argumentos.salida, argumentos.modelo, argumentos.repeticiones)
        if argumentos.reanudar
        else []
    )
    resultado: dict[str, object] = {
        "version": 1,
        "version_adaptador": VERSION_ADAPTADOR,
        "skill": NOMBRE_SKILL,
        "proveedor": "anthropic-api",
        "modelo": argumentos.modelo,
        "criterios": {"margen_no_inferioridad": 0.0, "ahorro_minimo_tokens": 0.2},
        "ejecuciones": ejecuciones,
    }
    completadas = {
        (ejecucion["repeticion"], ejecucion["variante"])
        for ejecucion in ejecuciones
    }
    for repeticion in range(1, argumentos.repeticiones + 1):
        for variante in VARIANTES_EXPERIMENTO:
            if (repeticion, variante) in completadas:
                print(f"Conservando {variante} {repeticion}/{argumentos.repeticiones} ya guardado.")
                continue
            print(f"Ejecutando {variante} {repeticion}/{argumentos.repeticiones}...")
            ejecucion = ejecutar_agente(
                cliente,
                argumentos.modelo,
                variante,
                None if variante == "control_puro" else indice_impacto,
            )
            ejecucion.update(
                {
                    "escenario": ESCENARIO,
                    "repeticion": repeticion,
                    "variante": variante,
                }
            )
            ejecuciones.append(ejecucion)
            guardar_resultado(argumentos.salida, resultado)
    print(f"Resultado guardado en: {argumentos.salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (anthropic.APIError, OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
