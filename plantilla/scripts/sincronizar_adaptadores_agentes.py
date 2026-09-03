#!/usr/bin/env python3
"""Genera adaptadores livianos para agentes que usan otra raiz de Skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


PATRON_CAMPO = re.compile(r"^(name|description):\s*(.+?)\s*$")
MARCADOR_ADAPTADOR = "<!-- adaptador-generado-por-agent-framework -->"


def extraer_metadatos(ruta: Path) -> tuple[str, str]:
    """Extrae nombre y descripcion del frontmatter de una Skill canonica."""
    contenido = ruta.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    if not lineas or lineas[0].strip() != "---":
        raise ValueError(f"La Skill no contiene frontmatter valido: {ruta}")
    metadatos: dict[str, str] = {}
    for linea in lineas[1:]:
        if linea.strip() == "---":
            break
        coincidencia = PATRON_CAMPO.match(linea)
        if coincidencia:
            metadatos[coincidencia.group(1)] = coincidencia.group(2).strip(" \"'")
    nombre = metadatos.get("name", "")
    descripcion = metadatos.get("description", "")
    if not nombre or not descripcion:
        raise ValueError(f"La Skill debe declarar name y description: {ruta}")
    return nombre, descripcion


def descubrir_skills(raiz: Path) -> dict[str, Path]:
    """Localiza las Skills instaladas y rechaza nombres duplicados."""
    raiz_skills = raiz / ".agents" / "skills"
    if not raiz_skills.is_dir():
        raise ValueError("No existe el directorio .agents/skills")
    descubiertas: dict[str, Path] = {}
    for manifiesto in sorted(raiz_skills.rglob("SKILL.md")):
        if not manifiesto.is_file():
            continue
        nombre, _ = extraer_metadatos(manifiesto)
        if nombre in descubiertas:
            raise ValueError(f"Nombre de Skill duplicado: {nombre}")
        descubiertas[nombre] = manifiesto
    return descubiertas


def construir_adaptador(raiz: Path, manifiesto: Path) -> tuple[str, str]:
    """Construye un wrapper que mantiene la Skill original como fuente unica."""
    nombre, descripcion = extraer_metadatos(manifiesto)
    relativa = manifiesto.relative_to(raiz).as_posix()
    contenido = (
        f"---\nname: {nombre}\n"
        f"description: {json.dumps(descripcion, ensure_ascii=False)}\n---\n\n"
        f"{MARCADOR_ADAPTADOR}\n\n"
        f"# Adaptador de {nombre} para Claude Code\n\n"
        f"Lee y aplica completamente la Skill canonica "
        f"[`{relativa}`](../../../{relativa}) antes de actuar. "
        "Resuelve sus scripts, referencias y recursos desde el directorio de esa "
        "Skill canonica. Este archivo solo permite el descubrimiento nativo y no "
        "duplica sus instrucciones.\n"
    )
    return nombre, contenido


def escribir_adaptador(ruta: Path, contenido: str) -> None:
    """Publica un adaptador sin reemplazar contenido ajeno al framework."""
    if ruta.exists():
        existente = ruta.read_text(encoding="utf-8")
        if existente == contenido:
            return
        if MARCADOR_ADAPTADOR not in existente:
            raise ValueError(f"El adaptador contiene cambios locales: {ruta}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(f".{ruta.name}.temporal")
    if temporal.exists() or os.path.lexists(temporal):
        raise ValueError(f"Existe un temporal pendiente: {temporal}")
    try:
        with temporal.open("w", encoding="utf-8", newline="\n") as archivo:
            archivo.write(contenido)
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def sincronizar_adaptadores(
    raiz: Path,
    seleccionadas: Optional[set[str]] = None,
) -> list[Path]:
    """Crea adaptadores Claude para todas las Skills o para una seleccion."""
    raiz_resuelta = raiz.expanduser().resolve(strict=True)
    descubiertas = descubrir_skills(raiz_resuelta)
    nombres = set(descubiertas) if seleccionadas is None else seleccionadas
    desconocidas = sorted(nombres - set(descubiertas))
    if desconocidas:
        raise ValueError(f"Skills instaladas no encontradas: {', '.join(desconocidas)}")
    preparadas: list[tuple[Path, str]] = []
    for nombre in sorted(nombres):
        nombre_adaptador, contenido = construir_adaptador(
            raiz_resuelta, descubiertas[nombre]
        )
        destino = raiz_resuelta / ".claude" / "skills" / nombre_adaptador / "SKILL.md"
        if destino.exists():
            existente = destino.read_text(encoding="utf-8")
            if existente != contenido and MARCADOR_ADAPTADOR not in existente:
                raise ValueError(f"El adaptador contiene cambios locales: {destino}")
        preparadas.append((destino, contenido))
    generadas: list[Path] = []
    nuevas: list[Path] = []
    try:
        for destino, contenido in preparadas:
            if not destino.exists():
                nuevas.append(destino)
            escribir_adaptador(destino, contenido)
            generadas.append(destino)
    except (OSError, UnicodeError, ValueError):
        for ruta in reversed(nuevas):
            if ruta.exists():
                ruta.unlink()
            if ruta.parent.exists() and not any(ruta.parent.iterdir()):
                ruta.parent.rmdir()
        raise
    return generadas


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz del sincronizador."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("raiz", nargs="?", type=Path, default=Path.cwd())
    analizador.add_argument("--skill", action="append", default=[])
    return analizador.parse_args()


def main() -> int:
    """Sincroniza los adaptadores y comunica las rutas creadas."""
    argumentos = crear_argumentos()
    seleccionadas = set(argumentos.skill) if argumentos.skill else None
    try:
        generadas = sincronizar_adaptadores(argumentos.raiz, seleccionadas)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Adaptadores Claude sincronizados: {len(generadas)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
