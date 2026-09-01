#!/usr/bin/env python3
"""Calcula el estado verificable de archivos administrados por el framework."""

from __future__ import annotations

import hashlib
from pathlib import Path


RUTAS_GESTIONADAS_BASE: tuple[str, ...] = (
    "configuracion_plantilla.json",
    "scripts/inicializar_proyecto.py",
    "scripts/inicializar_proyecto.sh",
    "scripts/verificar_memoria_proyecto.py",
)


def calcular_sha256(ruta: Path) -> str:
    """Calcula la huella SHA-256 de un archivo regular."""
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def descubrir_archivos_gestionados(raiz: Path) -> list[Path]:
    """Localiza Skills y scripts que pueden actualizarse sin renderizar documentos."""
    archivos: set[Path] = set()
    raiz_skills = raiz / ".agents" / "skills"
    if raiz_skills.is_dir():
        archivos.update(archivo for archivo in raiz_skills.rglob("*") if archivo.is_file())
    for relativa in RUTAS_GESTIONADAS_BASE:
        ruta = raiz / Path(relativa)
        if ruta.is_file():
            archivos.add(ruta)
    return sorted(archivos, key=lambda ruta: ruta.relative_to(raiz).as_posix())


def calcular_huellas_gestionadas(raiz: Path) -> dict[str, str]:
    """Relaciona cada archivo administrado con su contenido actual."""
    return {
        archivo.relative_to(raiz).as_posix(): calcular_sha256(archivo)
        for archivo in descubrir_archivos_gestionados(raiz)
    }
