#!/usr/bin/env python3
"""Agrega Skills confirmadas a un proyecto ya inicializado de forma transaccional."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from catalogo_skills import RegistroSkill, descubrir_skills
from crear_proyecto import instalar_skills, normalizar_permisos_arbol, validar_arbol_sin_enlaces
from estado_proyecto import calcular_huellas_gestionadas


class EstadoPlantilla(TypedDict, total=False):
    """Representa el estado persistente de una instancia de plantilla."""

    skills_instaladas: list[str]
    actualizaciones_skills: list[dict[str, object]]
    huellas_gestionadas: dict[str, str]


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz de instalacion posterior de Skills."""

    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("proyecto", type=Path, help="Proyecto ya inicializado que recibira las Skills")
    analizador.add_argument(
        "--skill",
        action="append",
        default=[],
        metavar="NOMBRE",
        help="Skill confirmada que se agregara; se puede repetir",
    )
    return analizador.parse_args()


def cargar_estado(ruta_estado: Path) -> EstadoPlantilla:
    """Carga y valida el estado de una instancia inicializada."""

    try:
        datos: object = json.loads(ruta_estado.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer el estado de plantilla: {error}") from error
    if not isinstance(datos, dict):
        raise ValueError("El estado de plantilla debe ser un objeto JSON")
    instaladas = datos.get("skills_instaladas")
    if not isinstance(instaladas, list) or not all(isinstance(nombre, str) for nombre in instaladas):
        raise ValueError("El estado de plantilla no contiene una lista valida de Skills")
    if len(instaladas) != len(set(instaladas)):
        raise ValueError("El estado de plantilla contiene Skills duplicadas")
    return EstadoPlantilla(datos)


def descubrir_skills_instaladas(raiz_skills: Path) -> set[str]:
    """Obtiene los nombres instalados despues de validar su arbol local."""

    validar_arbol_sin_enlaces(raiz_skills)
    return {registro["nombre"] for registro in descubrir_skills(raiz_skills)}


def seleccionar_nuevas_skills(
    catalogo: list[RegistroSkill],
    solicitadas: list[str],
    instaladas: set[str],
) -> list[RegistroSkill]:
    """Rechaza nombres ambiguos, desconocidos o ya presentes."""

    nombres = [nombre.strip() for nombre in solicitadas if nombre.strip()]
    if not nombres:
        raise ValueError("Se debe confirmar al menos una Skill mediante --skill")
    if len(nombres) != len(set(nombres)):
        raise ValueError("Una Skill no puede repetirse en la misma instalacion")
    por_nombre = {registro["nombre"]: registro for registro in catalogo}
    desconocidas = sorted(set(nombres) - set(por_nombre))
    if desconocidas:
        raise ValueError(f"Skills desconocidas: {', '.join(desconocidas)}")
    existentes = sorted(set(nombres) & instaladas)
    if existentes:
        raise ValueError(f"Skills ya instaladas: {', '.join(existentes)}")
    return [por_nombre[nombre] for nombre in sorted(nombres)]


def publicar_skills_preparadas(
    temporal: Path,
    destino: Path,
    seleccionadas: list[RegistroSkill],
) -> list[Path]:
    """Publica Skills nuevas sin reemplazar rutas presentes en el proyecto."""

    publicadas: list[Path] = []
    stacks_publicados: set[str] = set()
    try:
        for registro in seleccionadas:
            if registro["categoria"] == "stack":
                stack = registro["stack"]
                if stack is None:
                    raise ValueError(f"La Skill {registro['nombre']} no declara stack")
                if stack in stacks_publicados:
                    continue
                origen = temporal / "stacks" / stack / "skills" / registro["nombre"]
                destino_stack = destino / "stacks" / stack
                destino_skill = destino_stack / "skills" / registro["nombre"]
                if destino_skill.exists() or os.path.lexists(destino_skill):
                    raise ValueError(f"La Skill ya existe en el destino: {registro['nombre']}")
                if destino_stack.exists():
                    if not (destino_stack / "LEEME.md").is_file():
                        raise ValueError(f"El stack instalado no contiene LEEME.md: {stack}")
                    destino_skill.parent.mkdir(exist_ok=True)
                    os.replace(origen, destino_skill)
                    publicadas.append(destino_skill)
                else:
                    origen_stack = temporal / "stacks" / stack
                    destino_stack.parent.mkdir(exist_ok=True)
                    os.replace(origen_stack, destino_stack)
                    publicadas.append(destino_stack)
                    stacks_publicados.add(stack)
            else:
                origen = temporal / registro["nombre"]
                destino_skill = destino / registro["nombre"]
                if destino_skill.exists() or os.path.lexists(destino_skill):
                    raise ValueError(f"La Skill ya existe en el destino: {registro['nombre']}")
                os.replace(origen, destino_skill)
                publicadas.append(destino_skill)
    except (OSError, ValueError):
        for ruta in reversed(publicadas):
            if ruta.is_dir() and ruta.exists():
                shutil.rmtree(ruta)
        raise
    return publicadas


def escribir_estado(
    ruta_estado: Path,
    estado: EstadoPlantilla,
    nombres: list[str],
    huellas_gestionadas: dict[str, str],
) -> None:
    """Actualiza el estado mediante reemplazo atomico despues de publicar Skills."""

    actualizado = EstadoPlantilla(estado)
    instaladas = actualizado["skills_instaladas"]
    actualizado["skills_instaladas"] = [*instaladas, *nombres]
    historial = actualizado.get("actualizaciones_skills", [])
    if not isinstance(historial, list):
        raise ValueError("El historial de Skills debe ser una lista")
    historial.append(
        {
            "fecha": datetime.now(timezone.utc).isoformat(),
            "skills_agregadas": nombres,
        }
    )
    actualizado["actualizaciones_skills"] = historial
    actualizado["huellas_gestionadas"] = huellas_gestionadas
    temporal = ruta_estado.with_name(f".{ruta_estado.name}.temporal")
    if temporal.exists() or os.path.lexists(temporal):
        raise ValueError("Existe un estado temporal pendiente; se rechaza sobrescribirlo")
    try:
        with temporal.open("w", encoding="utf-8", newline="\n") as archivo:
            json.dump(actualizado, archivo, ensure_ascii=False, indent=2)
            archivo.write("\n")
        os.replace(temporal, ruta_estado)
    finally:
        if temporal.exists():
            temporal.unlink()


def agregar_skills(proyecto: Path, solicitadas: list[str]) -> list[str]:
    """Instala Skills seleccionadas y actualiza su trazabilidad en una transaccion."""

    raiz_framework = Path(__file__).resolve().parent.parent
    raiz_origen = raiz_framework / "plantilla" / ".agents" / "skills"
    raiz_proyecto = proyecto.expanduser().resolve(strict=True)
    ruta_estado = raiz_proyecto / ".estado-plantilla.json"
    raiz_destino = raiz_proyecto / ".agents" / "skills"
    if not ruta_estado.is_file() or (raiz_proyecto / ".plantilla-framework").exists():
        raise ValueError("El destino debe ser un proyecto inicializado una sola vez")
    validar_arbol_sin_enlaces(raiz_origen)
    estado = cargar_estado(ruta_estado)
    instaladas = descubrir_skills_instaladas(raiz_destino)
    if instaladas != set(estado["skills_instaladas"]):
        raise ValueError("El estado no coincide con las Skills instaladas")
    seleccionadas = seleccionar_nuevas_skills(descubrir_skills(raiz_origen), solicitadas, instaladas)
    nombres = [registro["nombre"] for registro in seleccionadas]

    temporal = Path(tempfile.mkdtemp(prefix=".skills-temporal-", dir=raiz_destino.parent))
    publicadas: list[Path] = []
    try:
        instalar_skills(raiz_origen, temporal, seleccionadas)
        normalizar_permisos_arbol(temporal)
        publicadas = publicar_skills_preparadas(temporal, raiz_destino, seleccionadas)
        escribir_estado(ruta_estado, estado, nombres, calcular_huellas_gestionadas(raiz_proyecto))
    except (OSError, ValueError):
        for ruta in reversed(publicadas):
            if ruta.is_dir() and ruta.exists():
                shutil.rmtree(ruta)
        raise
    finally:
        if temporal.exists():
            shutil.rmtree(temporal)
    return nombres


def main() -> int:
    """Ejecuta la instalacion y comunica las Skills agregadas."""

    argumentos = crear_argumentos()
    try:
        agregadas = agregar_skills(argumentos.proyecto, argumentos.skill)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Skills agregadas: " + ", ".join(agregadas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
