#!/usr/bin/env python3
"""Calcula el estado verificable de archivos administrados por el framework."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import cast


RUTAS_GESTIONADAS_CONTRATO_V2: tuple[str, ...] = (
    "configuracion_plantilla.json",
    "scripts/inicializar_proyecto.py",
    "scripts/inicializar_proyecto.sh",
    "scripts/verificar_memoria_proyecto.py",
)


def cargar_rutas_gestionadas(raiz: Path) -> list[str]:
    """Carga las rutas administradas desde el contrato unico del proyecto."""
    ruta_contrato = raiz / "configuracion_plantilla.json"
    datos: object = json.loads(ruta_contrato.read_text(encoding="utf-8"))
    if not isinstance(datos, dict):
        raise ValueError("configuracion_plantilla.json debe contener un objeto")
    contrato = cast(dict[str, object], datos)
    rutas = contrato.get("archivos_gestionados")
    if rutas is None and contrato.get("version_contrato") == 2:
        return list(RUTAS_GESTIONADAS_CONTRATO_V2)
    if not isinstance(rutas, list) or not all(isinstance(ruta, str) for ruta in rutas):
        raise ValueError("archivos_gestionados debe ser una lista de cadenas")
    rutas_tipeadas = cast(list[str], rutas)
    if not rutas_tipeadas or len(rutas_tipeadas) != len(set(rutas_tipeadas)):
        raise ValueError("archivos_gestionados debe contener rutas unicas")
    for relativa in rutas_tipeadas:
        ruta_pura = PurePosixPath(relativa)
        if (
            not relativa
            or "\\" in relativa
            or ruta_pura.is_absolute()
            or ".." in ruta_pura.parts
            or any(caracter in relativa for caracter in "*?[]")
        ):
            raise ValueError(f"Ruta administrada no portable o insegura: {relativa}")
    return rutas_tipeadas


def calcular_sha256(ruta: Path) -> str:
    """Calcula la huella SHA-256 de un archivo regular."""
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def descubrir_archivos_gestionados(raiz: Path) -> list[Path]:
    """Localiza Skills y scripts que pueden actualizarse sin renderizar documentos."""
    archivos: set[Path] = set()
    raiz_skills = raiz / ".agents" / "skills"
    if raiz_skills.is_dir():
        archivos.update(archivo for archivo in raiz_skills.rglob("*") if archivo.is_file())
    for relativa in cargar_rutas_gestionadas(raiz):
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
