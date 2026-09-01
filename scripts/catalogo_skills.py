#!/usr/bin/env python3
"""Descubre el catalogo de Skills y distingue el core automatico."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Literal, TypedDict


CategoriaSkill = Literal["core", "opcional", "stack"]
CORE_AUTOMATICO: tuple[str, ...] = (
    "cerrar-modulo",
    "lecciones-aprendidas",
    "optimizar-contexto",
    "probar-e2e",
)
PATRON_NOMBRE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
PATRON_DESCRIPCION = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


class RegistroSkill(TypedDict):
    """Representa una Skill disponible en la plantilla fuente."""

    nombre: str
    descripcion: str
    categoria: CategoriaSkill
    stack: str | None
    ruta: str
    automatica: bool


class CatalogoSkills(TypedDict):
    """Representa el catalogo completo y su politica de seleccion."""

    core_automatico: list[str]
    skills: list[RegistroSkill]


def limpiar_valor_yaml(valor: str) -> str:
    """Retira comillas exteriores de un valor simple de frontmatter."""
    limpio = valor.strip()
    if len(limpio) >= 2 and limpio[0] == limpio[-1] and limpio[0] in {'"', "'"}:
        return limpio[1:-1]
    return limpio


def clasificar(ruta_relativa: Path) -> tuple[CategoriaSkill, str | None]:
    """Clasifica una Skill por su ubicacion dentro del catalogo."""
    partes = ruta_relativa.parts
    if len(partes) >= 4 and partes[0] == "stacks" and partes[2] == "skills":
        return "stack", partes[1]
    if partes[0] == "opcional":
        return "opcional", None
    return "core", None


def descubrir_skills(raiz_skills: Path) -> list[RegistroSkill]:
    """Descubre y valida todos los manifiestos SKILL.md de la fuente."""
    raiz_resuelta = raiz_skills.expanduser().resolve()
    if not raiz_resuelta.is_dir():
        raise ValueError(f"No existe el catalogo de Skills: {raiz_resuelta}")

    registros: list[RegistroSkill] = []
    nombres: set[str] = set()
    for manifiesto in sorted(raiz_resuelta.rglob("SKILL.md")):
        contenido = manifiesto.read_text(encoding="utf-8")
        nombre_encontrado = PATRON_NOMBRE.search(contenido)
        descripcion_encontrada = PATRON_DESCRIPCION.search(contenido)
        if nombre_encontrado is None or descripcion_encontrada is None:
            raise ValueError(f"Frontmatter incompleto: {manifiesto}")
        nombre = limpiar_valor_yaml(nombre_encontrado.group(1))
        if nombre in nombres:
            raise ValueError(f"Nombre de Skill duplicado: {nombre}")
        if nombre != manifiesto.parent.name:
            raise ValueError(f"La Skill {nombre} no coincide con su carpeta {manifiesto.parent.name}")
        nombres.add(nombre)
        ruta_relativa = manifiesto.parent.relative_to(raiz_resuelta)
        categoria, stack = clasificar(ruta_relativa)
        registros.append(
            RegistroSkill(
                nombre=nombre,
                descripcion=limpiar_valor_yaml(descripcion_encontrada.group(1)),
                categoria=categoria,
                stack=stack,
                ruta=ruta_relativa.as_posix(),
                automatica=nombre in CORE_AUTOMATICO,
            )
        )

    faltantes = sorted(set(CORE_AUTOMATICO) - nombres)
    if faltantes:
        raise ValueError(f"Faltan Skills core automaticas: {', '.join(faltantes)}")
    return registros


def crear_catalogo(raiz_skills: Path) -> CatalogoSkills:
    """Construye el catalogo serializable."""
    return CatalogoSkills(
        core_automatico=list(CORE_AUTOMATICO),
        skills=descubrir_skills(raiz_skills),
    )


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz del catalogo."""
    raiz_predeterminada = Path(__file__).resolve().parent.parent / "plantilla" / ".agents" / "skills"
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--raiz", type=Path, default=raiz_predeterminada)
    analizador.add_argument("--json", action="store_true", dest="salida_json")
    return analizador.parse_args()


def main() -> int:
    """Imprime el catalogo para una persona o un agente recomendador."""
    argumentos = crear_argumentos()
    try:
        catalogo = crear_catalogo(argumentos.raiz)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if argumentos.salida_json:
        print(json.dumps(catalogo, ensure_ascii=False, indent=2))
        return 0
    print("Core automatico: " + ", ".join(catalogo["core_automatico"]))
    for skill in catalogo["skills"]:
        if skill["automatica"]:
            continue
        grupo = f"stack:{skill['stack']}" if skill["stack"] else skill["categoria"]
        print(f"- {skill['nombre']} [{grupo}]: {skill['descripcion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
