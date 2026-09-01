#!/usr/bin/env python3
"""Evalua una Skill mediante un agente Gemini con herramientas de solo lectura."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors, types

if __package__:
    from .analizar_impacto import analizar_impacto
    from .validar_resultado_agente import (
        RUTAS_ESENCIALES_MIGRACION,
        crear_indice_con_requisitos,
        crear_retroalimentacion,
        evaluar_auditoria,
    )
else:
    from analizar_impacto import analizar_impacto
    from validar_resultado_agente import (
        RUTAS_ESENCIALES_MIGRACION,
        crear_indice_con_requisitos,
        crear_retroalimentacion,
        evaluar_auditoria,
    )


RAIZ = Path(__file__).resolve().parent.parent
RUTA_SKILL = RAIZ / "plantilla" / ".agents" / "skills" / "optimizar-contexto" / "SKILL.md"
MAXIMO_TURNOS = 16
MAXIMO_CARACTERES = 16000
MAXIMO_REINTENTOS_CUOTA = 4
MAXIMO_CORRECCIONES = 1
MAXIMO_RUTAS_LISTADO = 40
DIRECTORIOS_EXCLUIDOS: set[str] = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "resultados",
    "venv",
}
ESCENARIO = "migracion-core-a-opcional-v6"
TERMINOS_IMPACTO: list[str] = [
    "optimizar-contexto",
    "CORE_AUTOMATICO",
    "core automatico",
    "Skills opcionales",
]
TAREA = (
    "Audita, sin modificar archivos, que cambios exactos requeriria mover la Skill "
    "optimizar-contexto desde el core automatico hacia las Skills opcionales. Debe "
    "usar primero el indice local determinista adjunto y reservar las herramientas "
    "para lecturas puntuales que completen impactos indirectos. Responda solo "
    "con un objeto JSON que contenga: rutas_afectadas como objetos ruta/cambio, al "
    "menos seis evidencias como objetos ruta/patron/motivo, pruebas como objetos "
    "comando/motivo y riesgos como cadenas. Las rutas declaradas deben existir y "
    "haber sido observadas en el indice o mediante herramientas; patron debe ser un "
    "fragmento literal exacto de hasta 160 caracteres copiado del indice o del archivo. "
    "rutas_afectadas debe contener un objeto para cada ruta enumerada en el campo "
    "rutas_requeridas_en_rutas_afectadas del indice, aunque la ruta tambien aparezca "
    "en evidencias; puede agregar otras rutas justificadas. No repita con buscar_texto "
    "los terminos ya cubiertos por el indice, no solicite un listado de la raiz, no "
    "invente archivos ni suponga que una lista se actualiza automaticamente."
)


def resolver(ruta_relativa: str) -> Path:
    """Resuelve una ruta regular dentro del repositorio autorizado."""
    ruta = (RAIZ / ruta_relativa).resolve()
    if (
        (ruta != RAIZ and RAIZ not in ruta.parents)
        or any(parte in DIRECTORIOS_EXCLUIDOS for parte in ruta.parts)
        or ruta.suffix.casefold() == ".pyc"
        or not ruta.is_file()
    ):
        raise ValueError("La ruta solicitada no es un archivo regular autorizado")
    return ruta


def archivo_incluido(archivo: Path) -> bool:
    """Excluye metadatos, dependencias, caches y resultados generados."""
    return (
        archivo.is_file()
        and not any(parte in DIRECTORIOS_EXCLUIDOS for parte in archivo.parts)
        and archivo.suffix.casefold() != ".pyc"
    )


def listar_archivos(prefijo: str) -> dict[str, object]:
    """Lista rutas regulares bajo un prefijo del repositorio."""
    prefijo_limpio = prefijo.strip().replace("\\", "/").strip("/")
    if not prefijo_limpio or prefijo_limpio == ".":
        return {"error": "Se requiere un prefijo especifico; no se permite listar la raiz"}
    base = (RAIZ / prefijo_limpio).resolve()
    if (base != RAIZ and RAIZ not in base.parents) or not base.is_dir():
        return {"error": "Prefijo no autorizado o inexistente"}
    rutas = [
        archivo.relative_to(RAIZ).as_posix()
        for archivo in sorted(base.rglob("*"))
        if archivo_incluido(archivo)
    ]
    return {"rutas": rutas[:MAXIMO_RUTAS_LISTADO], "truncado": len(rutas) > MAXIMO_RUTAS_LISTADO}


def buscar_texto(patron: str, prefijo: str = "") -> dict[str, object]:
    """Busca texto literal acotado en archivos UTF-8 del repositorio."""
    if not patron or len(patron) > 120:
        return {"error": "Patron invalido"}
    base = (RAIZ / prefijo).resolve()
    if (base != RAIZ and RAIZ not in base.parents) or not base.exists():
        return {"error": "Prefijo no autorizado o inexistente"}
    hallazgos: list[dict[str, object]] = []
    for archivo in sorted(base.rglob("*")):
        if not archivo_incluido(archivo):
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
        types.FunctionDeclaration(name="listar_archivos", description="Lista hasta 40 archivos bajo un prefijo especifico; no admite la raiz.", parameters={"type": "object", "properties": {"prefijo": {"type": "string"}}, "required": ["prefijo"]}),
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


def firma_consulta(nombre: str, argumentos: dict[str, Any]) -> str:
    """Calcula una firma estable para detectar herramientas repetidas."""
    serializado = json.dumps(
        {"nombre": nombre, "argumentos": argumentos},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()[:16]


def registrar_rutas(resultado: dict[str, object], observadas: set[str]) -> None:
    """Registra las rutas que una herramienta devolvio realmente al agente."""
    ruta = resultado.get("ruta")
    if isinstance(ruta, str):
        observadas.add(ruta.replace("\\", "/"))
    rutas = resultado.get("rutas")
    if isinstance(rutas, list):
        observadas.update(
            ruta.replace("\\", "/") for ruta in rutas if isinstance(ruta, str)
        )
    hallazgos = resultado.get("hallazgos")
    if isinstance(hallazgos, list):
        for hallazgo in hallazgos:
            if isinstance(hallazgo, dict) and isinstance(hallazgo.get("ruta"), str):
                observadas.add(str(hallazgo["ruta"]).replace("\\", "/"))
    archivos = resultado.get("archivos")
    if isinstance(archivos, list):
        for archivo in archivos:
            if isinstance(archivo, dict) and isinstance(archivo.get("ruta"), str):
                observadas.add(str(archivo["ruta"]).replace("\\", "/"))


def segundos_espera_cuota(error: errors.ClientError) -> int | None:
    """Extrae una espera segura cuando Gemini informa que excedio una cuota."""
    if getattr(error, "code", None) != 429:
        return None
    coincidencia = re.search(r"(?:retryDelay|retry in )[^0-9]*([0-9]+(?:\\.[0-9]+)?)s", str(error), re.IGNORECASE)
    if coincidencia is None:
        return 35
    return max(1, int(float(coincidencia.group(1))) + 1)


def ejecutar_agente(
    cliente: genai.Client,
    modelo: str,
    variante: str,
    indice_impacto: dict[str, object],
) -> dict[str, object]:
    """Ejecuta un ciclo de herramientas y agrega cada uso real del modelo."""
    instruccion = "Lee AGENTS.md antes de actuar y usa evidencia verificable."
    if variante == "skill":
        protocolo = RUTA_SKILL.read_text(encoding="utf-8")
        instruccion += (
            " La Skill optimizar-contexto ya esta cargada a continuacion; aplicala "
            "sin volver a leer su archivo solo para descubrir sus instrucciones.\n\n"
            f"{protocolo}"
        )
    else:
        instruccion += " No apliques el protocolo optimizar-contexto durante esta evaluacion de control."
    configuracion = types.GenerateContentConfig(tools=[HERRAMIENTAS], system_instruction=instruccion, temperature=0, max_output_tokens=2000)
    indice_serializado = json.dumps(
        indice_impacto,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    contenidos: list[Any] = [
        f"{TAREA}\n\nINDICE_LOCAL_DE_IMPACTO:\n{indice_serializado}"
    ]
    entrada_total = salida_total = razonamiento_total = llamadas = reintentos = 0
    ejecuciones_herramientas = aciertos_cache = 0
    cache: dict[str, dict[str, object]] = {}
    rutas_observadas: set[str] = set()
    registrar_rutas(indice_impacto, rutas_observadas)
    traza_herramientas: list[dict[str, object]] = []
    violaciones_protocolo: list[str] = []
    historial_rubrica: list[dict[str, object]] = []
    correcciones = 0
    inicio = time.perf_counter()
    texto_final = ""
    respuesta_estructurada: dict[str, object] | None = None
    fallos_finales: list[str] = []
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
            texto_candidato = respuesta.text or ""
            estructura_candidata, fallos = evaluar_auditoria(
                texto_candidato,
                RAIZ,
                rutas_observadas,
                RUTAS_ESENCIALES_MIGRACION,
                violaciones_protocolo,
            )
            historial_rubrica.append(
                {"revision": correcciones, "fallos": fallos}
            )
            if fallos and correcciones < MAXIMO_CORRECCIONES and not violaciones_protocolo:
                correcciones += 1
                contenidos.append(respuesta.candidates[0].content)
                contenidos.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=crear_retroalimentacion(fallos))],
                    )
                )
                continue
            texto_final = texto_candidato
            respuesta_estructurada = estructura_candidata
            fallos_finales = fallos
            break
        contenidos.append(respuesta.candidates[0].content)
        respuestas_herramientas: list[Any] = []
        for llamada in llamadas_turno:
            argumentos = dict(llamada.args or {})
            firma = firma_consulta(llamada.name, argumentos)
            if llamada.name == "listar_archivos" and not str(argumentos.get("prefijo", "")).strip(" ./\\"):
                violaciones_protocolo.append("Se solicito un listado general de la raiz")
            if firma in cache:
                resultado = {
                    "cache": True,
                    "firma": firma,
                    "mensaje": "El resultado completo ya esta disponible en el historial.",
                }
                aciertos_cache += 1
            else:
                resultado = ejecutar_herramienta(llamada.name, argumentos)
                cache[firma] = resultado
                registrar_rutas(resultado, rutas_observadas)
                ejecuciones_herramientas += 1
            traza_herramientas.append(
                {
                    "nombre": llamada.name,
                    "argumentos": argumentos,
                    "firma": firma,
                    "cache": firma in cache and resultado.get("cache") is True,
                    "error": resultado.get("error"),
                }
            )
            respuestas_herramientas.append(types.Part.from_function_response(name=llamada.name, response={"result": resultado}))
            llamadas += 1
        contenidos.append(types.Content(role="user", parts=respuestas_herramientas))
    if not texto_final:
        raise RuntimeError("El agente excedio el limite de turnos sin respuesta final")
    return {
        "exito": True,
        "pruebas_aprobadas": not fallos_finales,
        "tokens_entrada": entrada_total,
        "tokens_salida": salida_total,
        "llamadas_herramientas": llamadas,
        "ejecuciones_herramientas": ejecuciones_herramientas,
        "aciertos_cache": aciertos_cache,
        "duracion_segundos": round(time.perf_counter() - inicio, 3),
        "reintentos": reintentos,
        "analisis_local": {
            "terminos": indice_impacto.get("terminos", []),
            "archivos_examinados": indice_impacto.get("archivos_examinados", 0),
            "archivos_con_coincidencias": indice_impacto.get(
                "archivos_con_coincidencias", 0
            ),
            "coincidencias": indice_impacto.get("coincidencias", 0),
            "caracteres_serializados": len(indice_serializado),
            "rutas_requeridas": len(RUTAS_ESENCIALES_MIGRACION),
        },
        "rutas_observadas": sorted(rutas_observadas),
        "traza_herramientas": traza_herramientas,
        "violaciones_protocolo": violaciones_protocolo,
        "correcciones": correcciones,
        "historial_rubrica": historial_rubrica,
        "rubrica_fallos": fallos_finales,
        "respuesta_estructurada": respuesta_estructurada,
        "respuesta": texto_final,
    }


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
        and ejecucion.get("escenario") == ESCENARIO
        and isinstance(ejecucion.get("repeticion"), int)
        and 1 <= ejecucion["repeticion"] <= repeticiones
        and ejecucion.get("variante") in {"control", "skill"}
    ]


def main() -> int:
    """Ejecuta pares y guarda observaciones pendientes de revision humana."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default="gemini-3.1-flash-lite")
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument("--salida", type=Path, default=Path("resultados/evaluacion_agente_gemini.json"))
    parser.add_argument("--reanudar", action="store_true", help="Reanuda las ejecuciones ya guardadas en --salida.")
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("Se requiere GEMINI_API_KEY y al menos una repeticion")
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    indice_impacto = crear_indice_con_requisitos(
        analizar_impacto(RAIZ, TERMINOS_IMPACTO),
        RUTAS_ESENCIALES_MIGRACION,
    )
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
            ejecucion = ejecutar_agente(
                cliente,
                argumentos.modelo,
                variante,
                indice_impacto,
            )
            ejecucion.update({"escenario": ESCENARIO, "repeticion": repeticion, "variante": variante})
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
