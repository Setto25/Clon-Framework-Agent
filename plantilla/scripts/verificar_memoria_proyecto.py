#!/usr/bin/env python3
"""Verifica la presencia y coherencia minima de la memoria del proyecto."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class ResultadoArchivo(TypedDict):
    """Representa el resultado de verificar un archivo obligatorio."""

    ruta: str
    existe: bool
    no_vacio: bool


class ResultadoVerificacion(TypedDict):
    """Representa el informe completo de memoria."""

    valido: bool
    raiz: str
    archivos: list[ResultadoArchivo]
    placeholders_configurables: dict[str, list[str]]


ARCHIVOS_OBLIGATORIOS: tuple[str, ...] = (
    "AGENTS.md",
    "PROJECT_STATE.md",
    "documentacion/INDICE_LECTURA_AGENTES.md",
    "documentacion/PLAN_DESARROLLO.md",
    "documentacion/DOCUMENTACION_TECNICA.md",
    "documentacion/GUIA_OPERACION.md",
    "documentacion/REGISTRO_CAMBIOS.md",
)
PATRON_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def crear_argumentos() -> argparse.Namespace:
    """Define los argumentos del verificador."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("raiz", nargs="?", type=Path, default=Path.cwd())
    analizador.add_argument("--json", action="store_true", dest="salida_json")
    return analizador.parse_args()


def verificar_archivo(raiz: Path, ruta_relativa: str) -> ResultadoArchivo:
    """Comprueba que un archivo exista y contenga texto."""
    ruta = raiz / ruta_relativa
    existe = ruta.is_file()
    no_vacio = existe and bool(ruta.read_text(encoding="utf-8").strip())
    return ResultadoArchivo(ruta=ruta_relativa, existe=existe, no_vacio=no_vacio)


def buscar_placeholders(raiz: Path, resultados: list[ResultadoArchivo]) -> dict[str, list[str]]:
    """Busca placeholders configurables en archivos existentes."""
    encontrados: dict[str, list[str]] = {}
    for resultado in resultados:
        if not resultado["existe"]:
            continue
        ruta_relativa = resultado["ruta"]
        contenido = (raiz / ruta_relativa).read_text(encoding="utf-8")
        for clave in PATRON_PLACEHOLDER.findall(contenido):
            encontrados.setdefault(clave, []).append(ruta_relativa)
    return encontrados


def verificar(raiz: Path) -> ResultadoVerificacion:
    """Construye el informe de memoria del proyecto."""
    raiz_resuelta = raiz.expanduser().resolve()
    resultados = [verificar_archivo(raiz_resuelta, ruta) for ruta in ARCHIVOS_OBLIGATORIOS]
    placeholders = buscar_placeholders(raiz_resuelta, resultados)
    valido = all(resultado["existe"] and resultado["no_vacio"] for resultado in resultados) and not placeholders
    return ResultadoVerificacion(
        valido=valido,
        raiz=str(raiz_resuelta),
        archivos=resultados,
        placeholders_configurables=placeholders,
    )


def imprimir_texto(resultado: ResultadoVerificacion) -> None:
    """Presenta el informe en formato legible."""
    for archivo in resultado["archivos"]:
        estado = "OK" if archivo["existe"] and archivo["no_vacio"] else "FALTA"
        print(f"[{estado}] {archivo['ruta']}")
    for clave, rutas in sorted(resultado["placeholders_configurables"].items()):
        print(f"[PENDIENTE] {clave}: {', '.join(rutas)}")
    print("Memoria valida." if resultado["valido"] else "Memoria incompleta.")


def main() -> int:
    """Ejecuta la verificacion y devuelve un codigo util para automatizacion."""
    argumentos = crear_argumentos()
    try:
        resultado = verificar(argumentos.raiz)
    except (OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if argumentos.salida_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        imprimir_texto(resultado)
    return 0 if resultado["valido"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
