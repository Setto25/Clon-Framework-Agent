#!/usr/bin/env python3
"""Genera un inventario determinista y de solo lectura del arbol de Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class ArchivoInventariado(TypedDict):
    """Representa un archivo inventariado mediante contenido canonico."""

    ruta: str
    bytes: int
    sha256: str


class SkillInventariada(ArchivoInventariado):
    """Representa un SKILL.md y su nombre declarado."""

    nombre: str


class DeclaracionProcedencia(TypedDict):
    """Representa una declaracion local que requiere verificacion externa."""

    ruta: str
    linea: int
    texto: str


class ResumenInventario(TypedDict):
    """Representa los conteos principales del inventario."""

    archivos: int
    skills: int
    declaraciones_procedencia: int


class InventarioSkills(TypedDict):
    """Representa el inventario completo del catalogo fuente."""

    version_inventario: int
    raiz: str
    huella_conjunto_sha256: str
    resumen: ResumenInventario
    skills: list[SkillInventariada]
    archivos_adicionales: list[ArchivoInventariado]
    declaraciones_procedencia: list[DeclaracionProcedencia]


PATRON_NOMBRE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
PATRON_PROCEDENCIA = re.compile(
    r"(?:basado\s+en|adaptad[oa]\s+de|licencia|license|copyright)",
    re.IGNORECASE,
)
PATRON_ENLACE = re.compile(r"https?://", re.IGNORECASE)
EXTENSIONES_TEXTO: set[str] = {".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}


def crear_argumentos() -> argparse.Namespace:
    """Define los argumentos del inventariador."""
    raiz_predeterminada = Path(__file__).resolve().parent.parent / "plantilla" / ".agents" / "skills"
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--raiz", type=Path, default=raiz_predeterminada)
    analizador.add_argument("--salida", type=Path)
    return analizador.parse_args()


def calcular_sha256(contenido: bytes) -> str:
    """Calcula la huella SHA-256 de un contenido."""
    return hashlib.sha256(contenido).hexdigest()


def normalizar_para_huella(archivo: Path, contenido: bytes) -> bytes:
    """Canoniza a UTF-8 con LF los formatos de texto conocidos."""
    if archivo.suffix.lower() not in EXTENSIONES_TEXTO:
        return contenido
    texto = contenido.decode("utf-8")
    return texto.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def extraer_nombre(contenido: str, ruta: Path) -> str:
    """Extrae el nombre declarado por un archivo SKILL.md."""
    coincidencia = PATRON_NOMBRE.search(contenido)
    if coincidencia is None:
        raise ValueError(f"No se encontro el campo name en {ruta}")
    return coincidencia.group(1).strip().strip('"\'')


def detectar_declaraciones(contenido: str, ruta: str) -> list[DeclaracionProcedencia]:
    """Detecta lineas que declaran una posible fuente o licencia externa."""
    declaraciones: list[DeclaracionProcedencia] = []
    for numero, linea in enumerate(contenido.splitlines(), start=1):
        if not PATRON_PROCEDENCIA.search(linea):
            continue
        if not PATRON_ENLACE.search(linea) and not ruta.endswith("LEEME.md"):
            continue
        declaraciones.append(
            DeclaracionProcedencia(ruta=ruta, linea=numero, texto=linea.strip())
        )
    return declaraciones


def crear_inventario(raiz: Path) -> InventarioSkills:
    """Lee el catalogo fuente y construye un inventario ordenado."""
    raiz_resuelta = raiz.expanduser().resolve()
    if not raiz_resuelta.is_dir():
        raise ValueError(f"No existe la raiz de Skills: {raiz_resuelta}")

    skills: list[SkillInventariada] = []
    adicionales: list[ArchivoInventariado] = []
    declaraciones: list[DeclaracionProcedencia] = []
    componentes_huella: list[bytes] = []

    for archivo in sorted(ruta for ruta in raiz_resuelta.rglob("*") if ruta.is_file()):
        ruta_relativa = archivo.relative_to(raiz_resuelta).as_posix()
        contenido_bytes = normalizar_para_huella(archivo, archivo.read_bytes())
        huella = calcular_sha256(contenido_bytes)
        componentes_huella.append(f"{ruta_relativa}\0{huella}\n".encode("utf-8"))
        base = ArchivoInventariado(ruta=ruta_relativa, bytes=len(contenido_bytes), sha256=huella)
        if archivo.name == "SKILL.md":
            contenido = contenido_bytes.decode("utf-8")
            skills.append(SkillInventariada(**base, nombre=extraer_nombre(contenido, archivo)))
            declaraciones.extend(detectar_declaraciones(contenido, ruta_relativa))
        else:
            adicionales.append(base)
            if archivo.suffix.lower() == ".md":
                declaraciones.extend(detectar_declaraciones(contenido_bytes.decode("utf-8"), ruta_relativa))

    huella_conjunto = calcular_sha256(b"".join(componentes_huella))
    return InventarioSkills(
        version_inventario=2,
        raiz="plantilla/.agents/skills",
        huella_conjunto_sha256=huella_conjunto,
        resumen=ResumenInventario(
            archivos=len(skills) + len(adicionales),
            skills=len(skills),
            declaraciones_procedencia=len(declaraciones),
        ),
        skills=skills,
        archivos_adicionales=adicionales,
        declaraciones_procedencia=declaraciones,
    )


def serializar(inventario: InventarioSkills) -> str:
    """Serializa el inventario con un formato estable."""
    return json.dumps(inventario, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    """Genera el inventario y lo escribe en archivo o salida estandar."""
    argumentos = crear_argumentos()
    try:
        contenido = serializar(crear_inventario(argumentos.raiz))
        if argumentos.salida is None:
            sys.stdout.write(contenido)
        else:
            argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
            with argumentos.salida.open("w", encoding="utf-8", newline="\n") as archivo_salida:
                archivo_salida.write(contenido)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
