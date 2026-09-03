#!/usr/bin/env python3
"""Evalua optimizacion de contexto durante un desarrollo web aislado."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors, types

if __package__:
    from .analizar_impacto import analizar_impacto
    from .evaluar_agente_gemini import segundos_espera_cuota, uso
else:
    from analizar_impacto import analizar_impacto
    from evaluar_agente_gemini import segundos_espera_cuota, uso


RAIZ = Path(__file__).resolve().parent.parent
FIXTURE = RAIZ / "pruebas" / "fixtures" / "desarrollo-web"
RUTA_SKILL = RAIZ / "plantilla" / ".agents" / "skills" / "optimizar-contexto" / "SKILL.md"
RUTA_MODO_EXTENDIDO = RUTA_SKILL.parent / "referencias" / "modo_extendido.md"
VARIANTES: tuple[str, ...] = (
    "control_puro",
    "indice",
    "skill_adaptativa",
    "skill_extendida",
    "extendido_compacto",
)
VARIANTES_INDICE_EFICIENTES: tuple[str, ...] = (
    "herramientas_actuales",
    "indice_con_herramientas_eficientes",
)
VERSION_ADAPTADOR = 4
ESCENARIO = "desarrollo-web-tareas-v3"
ESCENARIO_INDICE_EFICIENTE = "desarrollo-web-indice-eficiente-v2"
MODELO_PREDETERMINADO = "gemini-3.1-flash-lite"
MAXIMO_TURNOS = 24
MAXIMO_HERRAMIENTAS = 24
MAXIMO_REINTENTOS = 4
MAXIMO_CORRECCIONES_CIERRE = 2
MAXIMO_CARACTERES_ARCHIVO = 24000
RUTAS_EDITABLES: frozenset[str] = frozenset(
    {
        "backend/__init__.py",
        "backend/aplicacion.py",
        "backend/modelos.py",
        "interfaz/interfaz.html",
        "interfaz/aplicacion.js",
        "interfaz/estilos.css",
        "LEEME.md",
    }
)
TERMINOS_INDICE: list[str] = [
    "tarea",
    "/api/tareas",
    "completada",
    "filtro",
    "formulario",
]

TAREA = """Completa la aplicacion aislada de tablero de tareas.

Requisitos funcionales:
- La API FastAPI conserva GET /api/tareas.
- POST /api/tareas recibe un titulo, elimina espacios externos, rechaza titulos vacios con 422, asigna un id incremental y responde 201.
- PATCH /api/tareas/{id} alterna completada y responde 404 para un id desconocido.
- La interfaz permite crear tareas sin recargar la pagina, alternar su estado y filtrar todas, pendientes y completadas.
- El formulario conserva label asociado, la interfaz anuncia cambios con aria-live="polite" y los controles resultan utilizables con teclado.
- Se mantienen tipado explicito, nombres y comentarios en espanol.

Usa exclusivamente las herramientas declaradas. No modifiques pruebas. Ejecuta la validacion antes de finalizar y corrige hasta que backend y frontend aprueben. La respuesta final resume cambios, pruebas y riesgos pendientes de forma breve."""

HERRAMIENTAS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="listar_archivos",
            description="Lista los archivos regulares del entorno web aislado.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="leer_archivo",
            description="Lee un archivo UTF-8 del entorno aislado.",
            parameters={
                "type": "object",
                "properties": {"ruta": {"type": "string"}},
                "required": ["ruta"],
            },
        ),
        types.FunctionDeclaration(
            name="escribir_archivo",
            description="Reemplaza un archivo editable dentro del entorno aislado.",
            parameters={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "contenido": {"type": "string"},
                },
                "required": ["ruta", "contenido"],
            },
        ),
        types.FunctionDeclaration(
            name="ejecutar_validacion",
            description="Ejecuta las pruebas reales de backend y frontend.",
            parameters={"type": "object", "properties": {}},
        ),
    ]
)

HERRAMIENTAS_EFICIENTES = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="leer_archivo",
            description="Lee solo un rango de hasta 80 lineas del archivo.",
            parameters={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "inicio": {"type": "integer"},
                    "limite": {"type": "integer"},
                },
                "required": ["ruta"],
            },
        ),
        types.FunctionDeclaration(
            name="escribir_archivo",
            description="Reemplaza un archivo editable dentro del entorno aislado.",
            parameters={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "contenido": {"type": "string"},
                },
                "required": ["ruta", "contenido"],
            },
        ),
        types.FunctionDeclaration(
            name="ejecutar_validacion",
            description="Ejecuta las pruebas reales de backend y frontend.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="buscar_texto",
            description="Busca un texto literal y devuelve como maximo doce coincidencias con linea y fragmento.",
            parameters={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "texto": {"type": "string"},
                },
                "required": ["ruta", "texto"],
            },
        ),
        types.FunctionDeclaration(
            name="leer_lote",
            description="Lee hasta cuatro rangos independientes en una sola llamada; cada rango admite ruta, inicio y limite de hasta 80 lineas.",
            parameters={
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
        ),
    ]
)


def normalizar_ruta(ruta: str) -> str:
    """Normaliza una ruta relativa sin permitir escapes del entorno."""
    return ruta.strip().replace("\\", "/").removeprefix("./")


def resolver(entorno: Path, ruta: str) -> Path:
    """Resuelve una ruta confinada dentro del entorno temporal."""
    relativa = normalizar_ruta(ruta)
    candidata = (entorno / relativa).resolve()
    raiz = entorno.resolve()
    if not relativa or (candidata != raiz and raiz not in candidata.parents):
        raise ValueError("Ruta no autorizada")
    return candidata


def listar_archivos(entorno: Path) -> dict[str, object]:
    """Enumera el fixture sin incluir caches generadas por las pruebas."""
    rutas = [
        archivo.relative_to(entorno).as_posix()
        for archivo in sorted(entorno.rglob("*"))
        if archivo.is_file() and "__pycache__" not in archivo.parts
    ]
    return {"rutas": rutas}


def leer_archivo(entorno: Path, ruta: str) -> dict[str, object]:
    """Devuelve el contenido completo de un archivo acotado."""
    try:
        archivo = resolver(entorno, ruta)
        if not archivo.is_file() or archivo.stat().st_size > MAXIMO_CARACTERES_ARCHIVO:
            raise ValueError("El archivo no existe o supera el limite")
        contenido = archivo.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        return {"error": str(error)}
    return {"ruta": normalizar_ruta(ruta), "contenido": contenido}


def escribir_archivo(entorno: Path, ruta: str, contenido: str) -> dict[str, object]:
    """Escribe solo fuentes autorizadas y conserva las pruebas inmutables."""
    relativa = normalizar_ruta(ruta)
    if relativa not in RUTAS_EDITABLES or len(contenido) > MAXIMO_CARACTERES_ARCHIVO:
        return {"error": "La ruta no es editable o el contenido supera el limite"}
    try:
        archivo = resolver(entorno, relativa)
        with archivo.open("w", encoding="utf-8", newline="\n") as flujo:
            flujo.write(contenido)
    except (OSError, UnicodeError, ValueError) as error:
        return {"error": str(error)}
    huella = hashlib.sha256(contenido.encode("utf-8")).hexdigest()[:12]
    return {"ruta": relativa, "bytes": len(contenido.encode("utf-8")), "sha256": huella}


def ejecutar_comando(entorno: Path, argumentos: list[str]) -> dict[str, object]:
    """Ejecuta una validacion fija con salida y tiempo acotados."""
    try:
        resultado = subprocess.run(
            argumentos,
            cwd=entorno,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=45,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"codigo": 1, "salida": str(error)}
    salida = (resultado.stdout + resultado.stderr).strip()
    return {"codigo": resultado.returncode, "salida": salida[-6000:]}


def ejecutar_validacion(entorno: Path) -> dict[str, object]:
    """Ejecuta las pruebas funcionales de ambas capas sin aceptar comandos libres."""
    backend = ejecutar_comando(
        entorno,
        [sys.executable, "-m", "unittest", "discover", "-s", "pruebas", "-p", "prueba_*.py"],
    )
    frontend = ejecutar_comando(
        entorno,
        ["node", "--test", "pruebas/prueba_frontend.mjs"],
    )
    return {
        "aprobada": backend["codigo"] == 0 and frontend["codigo"] == 0,
        "backend": backend,
        "frontend": frontend,
    }


def ejecutar_herramienta(
    entorno: Path,
    nombre: str,
    argumentos: dict[str, Any],
) -> dict[str, object]:
    """Despacha una herramienta limitada al fixture de la ejecucion."""
    if nombre == "listar_archivos":
        return listar_archivos(entorno)
    if nombre == "leer_archivo":
        return leer_archivo(entorno, str(argumentos.get("ruta", "")))
    if nombre == "escribir_archivo":
        return escribir_archivo(
            entorno,
            str(argumentos.get("ruta", "")),
            str(argumentos.get("contenido", "")),
        )
    if nombre == "ejecutar_validacion":
        return ejecutar_validacion(entorno)
    return {"error": "Herramienta no autorizada"}


def limitar_lectura(
    resultado: dict[str, object], argumentos: dict[str, object]
) -> tuple[dict[str, object], bool]:
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
    entorno: Path, nombre: str, argumentos: dict[str, Any]
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


def preparar_contexto_herramientas_eficientes(entorno: Path) -> None:
    """Crea fuentes extensas solo dentro de la copia temporal para activar lecturas selectivas."""
    contenido_api = ["\"\"\"Conserva el contrato de consulta de API para la evaluacion.\"\"\"", ""]
    contenido_interfaz = ["// Conserva el contrato de consulta de interfaz para la evaluacion.", ""]
    for numero in range(1, 121):
        contenido_api.append(f"# Contexto auxiliar de API {numero:03d}.")
        contenido_interfaz.append(f"// Contexto auxiliar de interfaz {numero:03d}.")
    contenido_api.extend(["", "MARCADOR_API = 'POST valida titulo y PATCH alterna completada'", ""])
    contenido_interfaz.extend(["", "const MARCADOR_INTERFAZ = 'aria-live y filtros conservan accesibilidad';", ""])
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


def construir_instruccion(variante: str) -> str:
    """Construye el tratamiento de contexto sin cambiar los requisitos funcionales."""
    base = (
        "Trabajas dentro de un fixture temporal aislado. Las pruebas son inmutables. "
        f"Dispones de hasta {MAXIMO_HERRAMIENTAS} ejecuciones de herramientas. "
        "Lee lo necesario, edita fuentes, valida y entrega una respuesta final breve."
    )
    if variante == "control_puro":
        return f"{base} No recibes indice local ni la Skill optimizar-contexto."
    if variante == "indice":
        return (
            f"{base} Recibes un indice local inicial; usalo para orientar lecturas sin "
            "asumir que refleja cambios posteriores. No apliques la Skill optimizar-contexto."
        )
    if variante == "skill_adaptativa":
        protocolo = RUTA_SKILL.read_text(encoding="utf-8")
        return (
            f"{base} Recibes un indice local inicial y la Skill optimizar-contexto. "
            "Selecciona y aplica el modo menos costoso segun sus señales observables.\n\n"
            f"{protocolo}"
        )
    if variante == "skill_extendida":
        protocolo = RUTA_SKILL.read_text(encoding="utf-8")
        modo_extendido = RUTA_MODO_EXTENDIDO.read_text(encoding="utf-8")
        return (
            f"{base} Recibes un indice local inicial y la Skill optimizar-contexto. "
            "Usa obligatoriamente el modo extendido desde el inicio; no agregues "
            "revision arquitectonica.\n\n"
            f"{protocolo}\n\n{modo_extendido}"
        )
    if variante == "extendido_compacto":
        modo_extendido = RUTA_MODO_EXTENDIDO.read_text(encoding="utf-8")
        return (
            f"{base} Recibes un indice local inicial. Aplica exclusivamente el modo "
            "extendido sin cargar el selector ni la referencia arquitectonica.\n\n"
            f"{modo_extendido}"
        )
    raise ValueError(f"Variante no soportada: {variante}")


def construir_solicitud(variante: str, indice: dict[str, object]) -> str:
    """Adjunta el indice solo a las variantes que lo reciben."""
    if variante == "control_puro":
        return TAREA
    serializado = json.dumps(indice, ensure_ascii=False, separators=(",", ":"))
    return f"{TAREA}\n\nINDICE_LOCAL_INICIAL:\n{serializado}"


def solicitar(
    cliente: genai.Client,
    modelo: str,
    contenidos: list[Any],
    instruccion: str,
    herramientas: types.Tool | None,
) -> tuple[Any, int]:
    """Realiza una solicitud manual y reintenta solo errores temporales."""
    parametros: dict[str, Any] = {
        "system_instruction": instruccion,
        "temperature": 0,
        "max_output_tokens": 3000,
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
    }
    if herramientas is not None:
        parametros["tools"] = [herramientas]
    configuracion = types.GenerateContentConfig(**parametros)
    reintentos = 0
    for intento in range(MAXIMO_REINTENTOS + 1):
        try:
            return cliente.models.generate_content(
                model=modelo,
                contents=contenidos,
                config=configuracion,
            ), reintentos
        except errors.ServerError:
            if intento == MAXIMO_REINTENTOS:
                raise
            espera = 5 * (2**intento)
        except errors.ClientError as error:
            espera_cuota = segundos_espera_cuota(error)
            if espera_cuota is None or intento == MAXIMO_REINTENTOS:
                raise
            espera = espera_cuota
        reintentos += 1
        print(f"Error temporal; se reintentara en {espera} segundos ({reintentos}/{MAXIMO_REINTENTOS}).")
        time.sleep(espera)
    raise RuntimeError("No se obtuvo respuesta de Gemini")


def requiere_correccion_cierre(validacion: dict[str, object], correcciones: int) -> bool:
    """Determina si el agente debe continuar al intentar cerrar con pruebas fallidas."""
    return not bool(validacion["aprobada"]) and correcciones < MAXIMO_CORRECCIONES_CIERRE


def instruccion_correccion_cierre(validacion: dict[str, object]) -> str:
    """Construye una orden breve para impedir un cierre textual sin tarea resuelta."""
    backend = validacion["backend"]
    frontend = validacion["frontend"]
    if not isinstance(backend, dict) or not isinstance(frontend, dict):
        return "La validacion sigue fallando. No finalices; usa las herramientas para implementar y validar."
    return (
        "La validacion final sigue fallando. No puedes finalizar con una explicacion. "
        "Continua usando herramientas, implementa los requisitos pendientes y ejecuta otra validacion. "
        f"Backend codigo={backend.get('codigo')}; frontend codigo={frontend.get('codigo')}."
    )


def ejecutar_agente(
    cliente: genai.Client,
    modelo: str,
    variante: str,
    entorno: Path,
    indice: dict[str, object],
) -> dict[str, object]:
    """Ejecuta un ciclo completo de desarrollo y valida el estado final localmente."""
    es_eficiente = variante == "indice_con_herramientas_eficientes"
    es_variante_indice = variante in VARIANTES_INDICE_EFICIENTES
    if es_eficiente:
        instruccion = (
            construir_instruccion("indice") + "\n\n"
            "ARCHIVOS_EN_ENTORNO es evidencia autoritativa del estado inicial. "
            "No ejecutes listar_archivos ni reconfirmes rutas ya incluidas en el."
        )
        solicitud_inicial = construir_solicitud_indice_eficiente(indice)
        herramientas_variante: types.Tool | None = HERRAMIENTAS_EFICIENTES
    elif es_variante_indice:
        instruccion = construir_instruccion("control_puro")
        solicitud_inicial = solicitud_herramientas_eficientes()
        herramientas_variante = HERRAMIENTAS
    else:
        instruccion = construir_instruccion(variante)
        solicitud_inicial = construir_solicitud(variante, indice)
        herramientas_variante = HERRAMIENTAS
    contenidos: list[Any] = [solicitud_inicial]
    entrada_total = salida_total = razonamiento_total = 0
    llamadas = ejecuciones = reintentos = 0
    traza: list[dict[str, object]] = []
    cache: dict[str, dict[str, object]] = {}
    bytes_entregados = aciertos_cache = lecturas_truncadas = lecturas_lote = 0
    busquedas_texto = solicitudes_api = 0
    duracion_api_segundos = 0.0
    respuesta_final = ""
    correcciones_cierre = 0
    inicio_medicion = time.perf_counter()
    inicio_pared = time.time()
    for _ in range(MAXIMO_TURNOS):
        inicio_solicitud = time.perf_counter()
        respuesta, nuevos_reintentos = solicitar(
            cliente,
            modelo,
            contenidos,
            instruccion,
            herramientas_variante if ejecuciones < MAXIMO_HERRAMIENTAS else None,
        )
        duracion_api_segundos += time.perf_counter() - inicio_solicitud
        solicitudes_api += 1
        reintentos += nuevos_reintentos
        entrada, salida, razonamiento = uso(respuesta)
        entrada_total += entrada
        salida_total += salida
        razonamiento_total += razonamiento
        partes = respuesta.candidates[0].content.parts
        solicitudes = [
            parte.function_call
            for parte in partes
            if getattr(parte, "function_call", None)
        ]
        if not solicitudes:
            validacion_intermedia = ejecutar_validacion(entorno)
            if bool(validacion_intermedia["aprobada"]):
                respuesta_final = respuesta.text or ""
                break
            if requiere_correccion_cierre(validacion_intermedia, correcciones_cierre):
                correcciones_cierre += 1
                contenidos.append(respuesta.candidates[0].content)
                contenidos.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                text=instruccion_correccion_cierre(validacion_intermedia)
                            )
                        ],
                    )
                )
                continue
            respuesta_final = respuesta.text or ""
            break
        contenidos.append(respuesta.candidates[0].content)
        resultados: list[Any] = []
        for solicitud in solicitudes:
            nombre = solicitud.name
            argumentos = dict(solicitud.args or {})
            if ejecuciones >= MAXIMO_HERRAMIENTAS:
                resultado: dict[str, object] = {"error": "Presupuesto de herramientas agotado; debe finalizar"}
            else:
                if es_variante_indice:
                    firma = json.dumps({"nombre": nombre, "argumentos": argumentos}, sort_keys=True)
                    resultado = cache.get(firma)
                    if resultado is None:
                        if es_eficiente:
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
                types.Part.from_function_response(
                    name=nombre,
                    response={"result": resultado},
                )
            )
        contenidos.append(types.Content(role="user", parts=resultados))
    inicio_validacion = time.perf_counter()
    validacion = ejecutar_validacion(entorno)
    duracion_validacion_segundos = time.perf_counter() - inicio_validacion
    duracion_segundos = time.perf_counter() - inicio_medicion
    duracion_pared = time.time() - inicio_pared
    duracion_anomala = (
        duracion_segundos > (duracion_api_segundos + duracion_validacion_segundos + 60)
        or duracion_pared > 300
    )
    resultado_base: dict[str, object] = {
        "exito": bool(respuesta_final) and bool(validacion["aprobada"]),
        "pruebas_aprobadas": bool(validacion["aprobada"]),
        "tokens_entrada": entrada_total,
        "tokens_salida": salida_total + razonamiento_total,
        "tokens_razonamiento": razonamiento_total,
        "llamadas_herramientas": llamadas,
        "ejecuciones_herramientas": ejecuciones,
        "duracion_segundos": round(duracion_segundos, 3),
        "duracion_anomala": duracion_anomala,
        "reintentos": reintentos,
        "validacion_final": validacion,
        "traza_herramientas": traza,
        "respuesta": respuesta_final,
        "correcciones_cierre": correcciones_cierre,
    }
    if es_variante_indice:
        resultado_base.update({
            "duracion_api_segundos": round(duracion_api_segundos, 3),
            "duracion_validacion_segundos": round(duracion_validacion_segundos, 3),
            "solicitudes_api": solicitudes_api,
            "bytes_herramientas_entregados": bytes_entregados,
            "aciertos_cache": aciertos_cache,
            "lecturas_truncadas": lecturas_truncadas,
            "lecturas_lote": lecturas_lote,
            "busquedas_texto": busquedas_texto,
            "mecanismos_activados": bool(
                lecturas_truncadas or lecturas_lote or busquedas_texto or aciertos_cache
            ),
        })
    return resultado_base


def guardar(salida: Path, resultado: dict[str, object]) -> None:
    """Guarda cada avance sin incluir secretos ni copias temporales."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Ejecuta variantes sobre fixtures independientes y comparables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default=MODELO_PREDETERMINADO)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument(
        "--indice-eficiente",
        action="store_true",
        help="Combina indice autoritativo y herramientas eficientes frente al control.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("resultados/evaluacion_desarrollo_web_gemini_v3.json"),
    )
    argumentos = parser.parse_args()
    if argumentos.repeticiones < 1 or not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("Se requiere GEMINI_API_KEY y al menos una repeticion")
    if not FIXTURE.is_dir() or not RUTA_SKILL.is_file() or not RUTA_MODO_EXTENDIDO.is_file():
        raise ValueError("No se encuentra el fixture, la Skill o su modo extendido")

    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    indice = analizar_impacto(FIXTURE, TERMINOS_INDICE, maximo_archivos=30, maximo_fragmentos=2)
    variantes = VARIANTES_INDICE_EFICIENTES if argumentos.indice_eficiente else VARIANTES
    escenario = ESCENARIO_INDICE_EFICIENTE if argumentos.indice_eficiente else ESCENARIO
    resultado: dict[str, object] = {
        "version": 1,
        "version_adaptador": VERSION_ADAPTADOR,
        "skill": "optimizar-contexto",
        "proveedor": "gemini-api",
        "modelo": argumentos.modelo,
        "escenario": escenario,
        "criterios": {"margen_no_inferioridad": 0.0, "ahorro_minimo_tokens": 0.2},
        "ejecuciones": [],
    }
    ejecuciones_resultado = resultado["ejecuciones"]
    if not isinstance(ejecuciones_resultado, list):
        raise RuntimeError("No se pudo inicializar la coleccion de ejecuciones")
    for repeticion in range(1, argumentos.repeticiones + 1):
        for variante in variantes:
            print(f"Ejecutando {variante} {repeticion}/{argumentos.repeticiones}...")
            with tempfile.TemporaryDirectory(prefix=f"web-{variante}-") as temporal:
                entorno = Path(temporal) / "aplicacion"
                shutil.copytree(FIXTURE, entorno)
                if argumentos.indice_eficiente:
                    preparar_contexto_herramientas_eficientes(entorno)
                ejecucion = ejecutar_agente(cliente, argumentos.modelo, variante, entorno, indice)
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
    except (errors.APIError, OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
