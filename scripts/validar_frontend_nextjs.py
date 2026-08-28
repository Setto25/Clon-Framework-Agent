#!/usr/bin/env python3
"""Valida los comandos obligatorios de un frontend Next.js ubicado en ``interfaz/``."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TypedDict


COMANDOS_OBLIGATORIOS: tuple[str, ...] = ("test", "lint", "build")
TIEMPO_MAXIMO_COMANDO_SEGUNDOS = 300


class PaqueteNpm(TypedDict):
    """Representa los campos necesarios del archivo package.json."""

    scripts: dict[str, str]


def cargar_paquete(ruta: Path) -> PaqueteNpm:
    """Carga y valida los scripts requeridos de un package.json."""
    try:
        datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer {ruta}: {error}") from error
    if not isinstance(datos, dict):
        raise ValueError("package.json debe contener un objeto JSON")
    scripts: object = datos.get("scripts")
    if not isinstance(scripts, dict):
        raise ValueError("package.json debe declarar el objeto scripts")
    resultado: dict[str, str] = {}
    for nombre in COMANDOS_OBLIGATORIOS:
        comando: object = scripts.get(nombre)
        if not isinstance(comando, str) or not comando.strip():
            raise ValueError(f"package.json no declara el script obligatorio: {nombre}")
        resultado[nombre] = comando
    return {"scripts": resultado}


def resolver_interfaz(proyecto: Path) -> Path:
    """Resuelve el directorio frontend esperado sin aceptar una ruta inexistente."""
    raiz = proyecto.expanduser().resolve()
    interfaz = raiz / "interfaz"
    if not raiz.is_dir():
        raise ValueError(f"El proyecto no existe o no es un directorio: {raiz}")
    if not interfaz.is_dir():
        raise ValueError(f"Falta el frontend Next.js esperado en: {interfaz}")
    cargar_paquete(interfaz / "package.json")
    return interfaz


def resolver_ejecutable_npm() -> str:
    """Resuelve npm con su extension ejecutable cuando Windows la requiere."""
    candidatos = ("npm.cmd", "npm") if sys.platform == "win32" else ("npm",)
    for candidato in candidatos:
        ruta = shutil.which(candidato)
        if ruta is not None:
            return ruta
    raise ValueError("No se encontro npm en PATH")


def ejecutar_comando(nombre: str, interfaz: Path, ejecutable_npm: str) -> None:
    """Ejecuta un script npm desde el subdirectorio frontend validado."""
    resultado = subprocess.run(
        [ejecutable_npm, "run", nombre],
        cwd=interfaz,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIEMPO_MAXIMO_COMANDO_SEGUNDOS,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"npm run {nombre} fallo con codigo {resultado.returncode}")


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz de linea de comandos del validador."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("proyecto", type=Path, help="Raiz del proyecto generado")
    analizador.add_argument(
        "--solo-verificar",
        action="store_true",
        help="Comprueba estructura y scripts sin ejecutar npm",
    )
    return analizador.parse_args()


def main() -> int:
    """Comprueba estructura y ejecuta pruebas reproducibles del frontend."""
    argumentos = crear_argumentos()
    try:
        interfaz = resolver_interfaz(argumentos.proyecto)
        if argumentos.solo_verificar:
            print(f"Frontend Next.js preparado: {interfaz}")
            return 0
        ejecutable_npm = resolver_ejecutable_npm()
        for nombre in COMANDOS_OBLIGATORIOS:
            print(f"Ejecutando: npm run {nombre}")
            ejecutar_comando(nombre, interfaz, ejecutable_npm)
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Frontend Next.js validado: test, lint y build aprobaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
