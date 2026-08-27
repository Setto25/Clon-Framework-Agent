#!/usr/bin/env python3
"""Crea un proyecto nuevo desde la plantilla mediante una operacion segura."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz del creador de proyectos."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("destino", type=Path, help="Directorio nuevo que recibira el proyecto")
    analizador.add_argument("nombre_proyecto", help="Nombre visible del proyecto")
    analizador.add_argument("--idioma", default="español", help="Idioma de nombres y documentacion")
    analizador.add_argument("--configuracion", type=Path, help="Archivo JSON con valores por placeholder")
    analizador.add_argument("--valor", action="append", default=[], metavar="CLAVE=VALOR")
    analizador.add_argument("--permitir-pendientes", action="store_true")
    analizador.add_argument("--sin-env", action="store_true")
    return analizador.parse_args()


def esta_dentro(ruta: Path, posible_contenedor: Path) -> bool:
    """Determina si una ruta queda dentro de otra ruta."""
    try:
        ruta.relative_to(posible_contenedor)
    except ValueError:
        return False
    return True


def validar_destino(destino: Path, raiz_framework: Path) -> tuple[Path, Path]:
    """Valida que el destino sea nuevo, externo al framework y tenga padre existente."""
    destino_absoluto = destino.expanduser().resolve()
    if destino_absoluto.exists():
        raise ValueError(f"El destino ya existe: {destino_absoluto}")
    padre = destino_absoluto.parent
    if not padre.is_dir():
        raise ValueError(f"El directorio padre no existe: {padre}")
    if esta_dentro(destino_absoluto, raiz_framework):
        raise ValueError("El destino no puede quedar dentro del repositorio agent-framework")
    return destino_absoluto, padre


def construir_comando_inicializador(
    destino_temporal: Path,
    argumentos: argparse.Namespace,
) -> list[str]:
    """Construye el comando del inicializador interno sin utilizar un shell."""
    comando = [
        sys.executable,
        str(destino_temporal / "scripts" / "inicializar_proyecto.py"),
        argumentos.nombre_proyecto,
        argumentos.idioma,
    ]
    if argumentos.configuracion is not None:
        comando.extend(["--configuracion", str(argumentos.configuracion.expanduser().resolve())])
    for valor in argumentos.valor:
        comando.extend(["--valor", valor])
    if argumentos.permitir_pendientes:
        comando.append("--permitir-pendientes")
    if argumentos.sin_env:
        comando.append("--sin-env")
    return comando


def eliminar_temporal(destino_temporal: Path, padre: Path) -> None:
    """Elimina solamente el temporal validado dentro de su padre previsto."""
    if not destino_temporal.exists():
        return
    temporal_resuelto = destino_temporal.resolve()
    if temporal_resuelto.parent != padre or not temporal_resuelto.name.startswith(".proyecto-temporal-"):
        raise ValueError(f"Se rechazo eliminar un temporal inesperado: {temporal_resuelto}")
    shutil.rmtree(temporal_resuelto)


def crear_proyecto(argumentos: argparse.Namespace) -> Path:
    """Copia, inicializa y publica localmente el proyecto de forma atomica."""
    raiz_framework = Path(__file__).resolve().parent.parent
    origen = raiz_framework / "plantilla"
    destino, padre = validar_destino(argumentos.destino, raiz_framework)
    destino_temporal = Path(tempfile.mkdtemp(prefix=".proyecto-temporal-", dir=padre))
    try:
        shutil.copytree(origen, destino_temporal, dirs_exist_ok=True, copy_function=shutil.copy2)
        comando = construir_comando_inicializador(destino_temporal, argumentos)
        subprocess.run(comando, cwd=destino_temporal, check=True)
        os.replace(destino_temporal, destino)
    except (OSError, subprocess.SubprocessError, ValueError):
        eliminar_temporal(destino_temporal, padre)
        raise
    return destino


def main() -> int:
    """Ejecuta la creacion y comunica el destino resultante."""
    argumentos = crear_argumentos()
    try:
        destino = crear_proyecto(argumentos)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Proyecto creado en: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
