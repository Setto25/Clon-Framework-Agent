#!/usr/bin/env python3
"""Prediagnostica fallos de pruebas para reducir la exploracion que necesita un agente."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import TypedDict


class Fallo(TypedDict, total=False):
    """Un fallo individual extraido de la salida de pruebas."""

    nombre: str
    archivo: str
    linea: int
    tipo: str
    esperado: str
    obtenido: str
    descripcion: str


class ResultadoEjecutor(TypedDict):
    """Salida de un ejecutor de pruebas."""

    ejecutor: str
    codigo: int
    salida: str
    fallos: list[Fallo]


class Diagnostico(TypedDict):
    """Diagnostico completo de un directorio."""

    directorio: str
    ejecutores: list[ResultadoEjecutor]
    todas_aprobadas: bool
    total_fallos: int
    archivos_candidatos: list[str]
    confianza: str
    contexto_agente: str


PATRON_FALLO_UNITTEST = re.compile(
    r"^(?:FAIL|ERROR): (\S+) \(([^)]+)\)\n(.*?)\n-{40,}\n(.*?)(?=\n(?:FAIL|ERROR|OK|FAILED|\Z))",
    re.MULTILINE | re.DOTALL,
)
PATRON_ASERCION_UNITTEST = re.compile(
    r"Assert\w+Error:\s*(.+?)$", re.MULTILINE
)
PATRON_LINEA_UNITTEST = re.compile(
    r'File "([^"]+)", line (\d+)',
)
PATRON_FALLO_NODE_DETALLE = re.compile(
    r"^[^\S\n]*✖ (.+?) \([\d.]+(?:ms|s)\)\n(\s+\S.*?)(?=\n[^\S\n]*✖|\ntest at |\Z)",
    re.MULTILINE | re.DOTALL,
)
PATRON_FALLO_NODE_SIMPLE = re.compile(
    r"^✖ (.+?) \([\d.]+(?:ms|s)\)\s*$",
    re.MULTILINE,
)
PATRON_ASERCION_NODE = re.compile(
    r"Assert\w+(?:Error)?\s*\[?[^\]]*\]?:\s*(.+?)(?:\.\s|$)", re.MULTILINE
)
PATRON_RUTA_PATRON = re.compile(
    r"""(?:/[\w{}.-]+){2,}""",
)
PATRON_CODIGO_HTTP = re.compile(
    r"(\d{3})\s*!=\s*(\d{3})",
)


def ejecutar_comando(directorio: Path, argumentos: list[str]) -> tuple[int, str]:
    """Ejecuta un comando con salida y tiempo acotados."""
    try:
        resultado = subprocess.run(
            argumentos,
            cwd=directorio,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
    except FileNotFoundError:
        return -1, ""
    except subprocess.TimeoutExpired:
        return 1, "Timeout al ejecutar pruebas"
    return resultado.returncode, (resultado.stdout + resultado.stderr).strip()


def analizar_fallos_unittest(salida: str) -> list[Fallo]:
    """Extrae fallos estructurados de la salida de unittest."""
    fallos: list[Fallo] = []
    for coincidencia in PATRON_FALLO_UNITTEST.finditer(salida):
        nombre = coincidencia.group(1)
        traza = coincidencia.group(4)
        fallo: Fallo = {"nombre": nombre, "tipo": "AssertionError"}
        linea_match = PATRON_LINEA_UNITTEST.search(traza)
        if linea_match:
            fallo["archivo"] = linea_match.group(1)
            fallo["linea"] = int(linea_match.group(2))
        asercion = PATRON_ASERCION_UNITTEST.search(traza)
        if asercion:
            fallo["descripcion"] = asercion.group(1).strip()
            codigos = PATRON_CODIGO_HTTP.search(asercion.group(1))
            if codigos:
                fallo["obtenido"] = codigos.group(1)
                fallo["esperado"] = codigos.group(2)
        fallos.append(fallo)
    return fallos


def analizar_fallos_node(salida: str) -> list[Fallo]:
    """Extrae fallos estructurados de la salida de node --test."""
    detalles: dict[str, str] = {}
    for coincidencia in PATRON_FALLO_NODE_DETALLE.finditer(salida):
        nombre = coincidencia.group(1)
        detalle = coincidencia.group(2)
        if nombre not in detalles:
            detalles[nombre] = detalle
    nombres_vistos: set[str] = set()
    fallos: list[Fallo] = []
    for coincidencia in PATRON_FALLO_NODE_SIMPLE.finditer(salida):
        nombre = coincidencia.group(1)
        if nombre in nombres_vistos:
            continue
        nombres_vistos.add(nombre)
        fallo: Fallo = {"nombre": nombre, "tipo": "AssertionError"}
        detalle = detalles.get(nombre, "")
        asercion = PATRON_ASERCION_NODE.search(detalle)
        if asercion:
            fallo["descripcion"] = asercion.group(1).strip()[:200]
        fallos.append(fallo)
    return fallos


def descubrir_ejecutores(directorio: Path) -> list[tuple[str, list[str]]]:
    """Detecta los ejecutores de pruebas disponibles en el directorio."""
    ejecutores: list[tuple[str, list[str]]] = []
    for nombre_carpeta in ("pruebas", "tests"):
        carpeta = directorio / nombre_carpeta
        pruebas_python = list(carpeta.rglob("prueba_*.py")) + list(carpeta.rglob("test_*.py")) if carpeta.is_dir() else []
        if pruebas_python:
            ejecutores.append(
                (
                    "unittest",
                    [
                        sys.executable,
                        "-m",
                        "unittest",
                        "discover",
                        "-s",
                        nombre_carpeta,
                        "-p",
                        "*.py",
                    ],
                )
            )
    pruebas_node = list(directorio.rglob("prueba_*.mjs")) + list(directorio.rglob("test_*.mjs"))
    if pruebas_node:
        ejecutores.append(
            ("node", ["node", "--test"] + [str(p.relative_to(directorio)) for p in pruebas_node])
        )
    return ejecutores


def buscar_candidatos(directorio: Path, fallos: list[Fallo]) -> list[str]:
    """Identifica archivos fuente candidatos que requieren confirmacion del agente."""
    candidatos: set[str] = set()
    archivos_fuente = [
        p for p in directorio.rglob("*")
        if p.is_file()
        and p.suffix in (".py", ".js", ".ts", ".html", ".css")
        and "prueba" not in p.name
        and "test" not in p.name
        and "__pycache__" not in p.parts
        and "node_modules" not in p.parts
    ]
    for fallo in fallos:
        rutas_api = PATRON_RUTA_PATRON.findall(fallo.get("descripcion", ""))
        for ruta_api in rutas_api:
            for archivo in archivos_fuente:
                try:
                    contenido = archivo.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if ruta_api in contenido:
                    candidatos.add(archivo.relative_to(directorio).as_posix())
        esperado = fallo.get("esperado", "")
        obtenido = fallo.get("obtenido", "")
        if esperado and obtenido:
            codigos_http = {int(esperado)} if esperado.isdigit() else set()
            if codigos_http:
                for archivo in archivos_fuente:
                    try:
                        contenido = archivo.read_text(encoding="utf-8", errors="ignore")
                    except OSError:
                        continue
                    if any(f"@app." in contenido or "router." in contenido or "app." in contenido
                           for _ in [1]):
                        if archivo.suffix == ".py":
                            candidatos.add(archivo.relative_to(directorio).as_posix())
    if not candidatos:
        for archivo in archivos_fuente:
            candidatos.add(archivo.relative_to(directorio).as_posix())
    return sorted(candidatos)


def diagnosticar(directorio: Path) -> Diagnostico:
    """Ejecuta pruebas, analiza fallos y genera un diagnostico estructurado."""
    directorio = directorio.resolve()
    ejecutores_descubiertos = descubrir_ejecutores(directorio)
    resultados: list[ResultadoEjecutor] = []
    todos_fallos: list[Fallo] = []
    for nombre_ejecutor, argumentos in ejecutores_descubiertos:
        codigo, salida = ejecutar_comando(directorio, argumentos)
        if nombre_ejecutor == "unittest":
            fallos = analizar_fallos_unittest(salida)
        elif nombre_ejecutor == "node":
            fallos = analizar_fallos_node(salida)
        else:
            fallos = []
        todos_fallos.extend(fallos)
        resultados.append({
            "ejecutor": nombre_ejecutor,
            "codigo": codigo,
            "salida": salida[-3000:],
            "fallos": fallos,
        })
    candidatos = buscar_candidatos(directorio, todos_fallos) if todos_fallos else []
    total = len(todos_fallos)
    todas_aprobadas = all(r["codigo"] == 0 for r in resultados) if resultados else False
    if todas_aprobadas:
        confianza = "alta"
    elif total > 0 and candidatos:
        confianza = "media"
    elif total > 0:
        confianza = "baja"
    else:
        confianza = "baja"
    contexto = formatear_contexto(
        todas_aprobadas, todos_fallos, candidatos, resultados
    )
    return {
        "directorio": str(directorio),
        "ejecutores": resultados,
        "todas_aprobadas": todas_aprobadas,
        "total_fallos": total,
        "archivos_candidatos": candidatos,
        "confianza": confianza,
        "contexto_agente": contexto,
    }


def formatear_contexto(
    aprobadas: bool,
    fallos: list[Fallo],
    candidatos: list[str],
    resultados: list[ResultadoEjecutor],
) -> str:
    """Genera un resumen compacto para inyectar como contexto inicial del agente."""
    if aprobadas:
        return "Todas las pruebas aprobaron. No se requiere correccion."
    lineas: list[str] = []
    lineas.append(f"FALLOS_DETECTADOS: {len(fallos)}")
    for fallo in fallos:
        partes = [f"- {fallo.get('nombre', 'desconocido')}"]
        if fallo.get("esperado") and fallo.get("obtenido"):
            partes.append(f"esperado={fallo['esperado']} obtenido={fallo['obtenido']}")
        if fallo.get("descripcion"):
            partes.append(fallo["descripcion"][:120])
        lineas.append(" | ".join(partes))
    if candidatos:
        lineas.append(f"\nARCHIVOS_CANDIDATOS: {', '.join(candidatos)}")
    lineas.append(
        "\nUsa los candidatos como punto de partida y confirma la causa antes de corregir. "
        "No repitas el diagnostico salvo contradiccion o cambios posteriores."
    )
    return "\n".join(lineas)


def main() -> int:
    """Diagnostica fallos de pruebas en un directorio."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directorio", type=Path, help="Directorio del proyecto a diagnosticar.")
    parser.add_argument(
        "--formato",
        choices=("json", "texto"),
        default="texto",
        help="Formato de salida: json completo o texto compacto para el agente.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=None,
        help="Archivo de salida. Si no se indica, imprime a stdout.",
    )
    argumentos = parser.parse_args()
    if not argumentos.directorio.is_dir():
        print(f"ERROR: {argumentos.directorio} no es un directorio", file=sys.stderr)
        return 1
    resultado = diagnosticar(argumentos.directorio)
    if argumentos.formato == "json":
        contenido = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    else:
        contenido = resultado["contexto_agente"] + "\n"
    if argumentos.salida:
        argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
        argumentos.salida.write_text(contenido, encoding="utf-8")
        print(f"Diagnostico guardado en: {argumentos.salida}")
    else:
        sys.stdout.buffer.write(contenido.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
