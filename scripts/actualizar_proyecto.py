#!/usr/bin/env python3
"""Actualiza archivos administrados sin sobrescribir cambios locales del proyecto."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import TypedDict, cast

from catalogo_skills import CORE_AUTOMATICO, RegistroSkill, descubrir_skills
from crear_proyecto import (
    es_enlace_o_reparse,
    instalar_skills,
    normalizar_permisos_arbol,
    validar_arbol_sin_enlaces,
)
from estado_proyecto import (
    calcular_huellas_gestionadas,
    calcular_sha256,
    cargar_rutas_gestionadas,
)


PATRON_HUELLA = re.compile(r"^[0-9a-f]{64}$")


class EstadoProyecto(TypedDict, total=False):
    """Representa el estado necesario para una actualizacion verificable."""

    version_framework: str
    version_contrato: int
    skills_instaladas: list[str]
    huellas_gestionadas: dict[str, str]
    actualizaciones_framework: list[dict[str, object]]


class PlanActualizacion(TypedDict):
    """Resume cambios y conflictos antes de escribir en el proyecto."""

    version_origen: str
    version_destino: str
    archivos_actualizados: list[str]
    archivos_agregados: list[str]
    skills_agregadas: list[str]
    conflictos: list[str]


def cargar_objeto_json(ruta: Path, descripcion: str) -> dict[str, object]:
    """Carga un objeto JSON regular y acotado."""
    if not ruta.is_file() or ruta.stat().st_size > 1024 * 1024:
        raise ValueError(f"{descripcion} no existe o supera 1 MiB")
    try:
        datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer {descripcion}: {error}") from error
    if not isinstance(datos, dict):
        raise ValueError(f"{descripcion} debe ser un objeto JSON")
    return cast(dict[str, object], datos)


def validar_relativa(texto: str) -> str:
    """Rechaza rutas absolutas, ambiguas o que escapen del proyecto."""
    ruta = PurePosixPath(texto)
    if not texto or ruta.is_absolute() or ".." in ruta.parts or "." in ruta.parts or "\\" in texto:
        raise ValueError(f"Ruta administrada invalida: {texto}")
    return ruta.as_posix()


def cargar_estado(ruta: Path) -> EstadoProyecto:
    """Valida el estado persistente y sus huellas administradas."""
    datos = cargar_objeto_json(ruta, "el estado de plantilla")
    version = datos.get("version_framework")
    instaladas = datos.get("skills_instaladas")
    if not isinstance(version, str) or not version:
        raise ValueError("El estado no declara version_framework")
    if not isinstance(instaladas, list) or not all(isinstance(nombre, str) for nombre in instaladas):
        raise ValueError("El estado no declara una lista valida de Skills")
    if len(instaladas) != len(set(instaladas)):
        raise ValueError("El estado declara Skills duplicadas")
    huellas = datos.get("huellas_gestionadas")
    if huellas is not None:
        if not isinstance(huellas, dict):
            raise ValueError("huellas_gestionadas debe ser un objeto")
        for ruta_cruda, huella in huellas.items():
            if not isinstance(ruta_cruda, str) or not isinstance(huella, str):
                raise ValueError("huellas_gestionadas contiene una entrada invalida")
            validar_relativa(ruta_cruda)
            if PATRON_HUELLA.fullmatch(huella) is None:
                raise ValueError(f"Huella invalida para {ruta_cruda}")
    return EstadoProyecto(datos)


def escribir_estado(ruta: Path, estado: EstadoProyecto) -> None:
    """Publica el estado mediante reemplazo atomico."""
    temporal = ruta.with_name(f".{ruta.name}.actualizacion-temporal")
    if temporal.exists() or os.path.lexists(temporal):
        raise ValueError("Existe un estado temporal de actualizacion pendiente")
    try:
        with temporal.open("w", encoding="utf-8", newline="\n") as flujo:
            json.dump(estado, flujo, ensure_ascii=False, indent=2)
            flujo.write("\n")
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def preparar_fuente(raiz_framework: Path, instaladas: list[str], temporal: Path) -> tuple[Path, list[str]]:
    """Construye el arbol deseado con Skills instaladas y nuevo core automatico."""
    raiz_plantilla = raiz_framework / "plantilla"
    raiz_skills = raiz_plantilla / ".agents" / "skills"
    catalogo = descubrir_skills(raiz_skills)
    por_nombre = {registro["nombre"]: registro for registro in catalogo}
    nombres = sorted(set(instaladas) | set(CORE_AUTOMATICO))
    desconocidas = sorted(set(nombres) - set(por_nombre))
    if desconocidas:
        raise ValueError(f"El framework ya no contiene Skills instaladas: {', '.join(desconocidas)}")
    seleccionadas = [cast(RegistroSkill, por_nombre[nombre]) for nombre in nombres]
    destino_skills = temporal / ".agents" / "skills"
    instalar_skills(raiz_skills, destino_skills, seleccionadas)
    for relativa in cargar_rutas_gestionadas(raiz_plantilla):
        origen = raiz_plantilla / Path(relativa)
        destino = temporal / Path(relativa)
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)
    normalizar_permisos_arbol(temporal)
    return temporal, nombres


def construir_plan(
    proyecto: Path,
    fuente: Path,
    estado: EstadoProyecto,
    version_destino: str,
    skills_destino: list[str],
) -> PlanActualizacion:
    """Detecta cambios seguros, incorporaciones y conflictos antes de escribir."""
    registradas = estado.get("huellas_gestionadas")
    if not isinstance(registradas, dict):
        raise ValueError(
            "El proyecto no registra huellas administradas; requiere --adoptar-estado-actual y revision previa"
        )
    huellas_deseadas = calcular_huellas_gestionadas(fuente)
    actualizados: list[str] = []
    agregados: list[str] = []
    conflictos: list[str] = []
    for relativa, huella_deseada in huellas_deseadas.items():
        destino = proyecto / Path(relativa)
        huella_registrada = registradas.get(relativa)
        if os.path.lexists(destino) and es_enlace_o_reparse(destino):
            conflictos.append(f"{relativa}: es un enlace o reparse point")
        elif destino.exists():
            if not destino.is_file():
                conflictos.append(f"{relativa}: no es un archivo regular")
                continue
            huella_actual = calcular_sha256(destino)
            if huella_registrada is None and huella_actual != huella_deseada:
                conflictos.append(f"{relativa}: existe sin huella administrada")
            elif huella_registrada is not None and huella_actual not in {
                huella_registrada,
                huella_deseada,
            }:
                conflictos.append(f"{relativa}: contiene cambios locales")
            elif huella_actual != huella_deseada:
                actualizados.append(relativa)
        elif huella_registrada is not None:
            conflictos.append(f"{relativa}: fue eliminado localmente")
        else:
            agregados.append(relativa)
    instaladas = cast(list[str], estado["skills_instaladas"])
    return PlanActualizacion(
        version_origen=cast(str, estado["version_framework"]),
        version_destino=version_destino,
        archivos_actualizados=actualizados,
        archivos_agregados=agregados,
        skills_agregadas=sorted(set(skills_destino) - set(instaladas)),
        conflictos=conflictos,
    )


def adoptar_estado_actual(proyecto: Path, ruta_estado: Path, estado: EstadoProyecto) -> None:
    """Registra una base heredada sin reemplazar ningun archivo."""
    if isinstance(estado.get("huellas_gestionadas"), dict):
        raise ValueError("El proyecto ya contiene huellas administradas")
    actualizado = EstadoProyecto(estado)
    actualizado["huellas_gestionadas"] = calcular_huellas_gestionadas(proyecto)
    escribir_estado(ruta_estado, actualizado)


def aplicar_plan(
    proyecto: Path,
    fuente: Path,
    ruta_estado: Path,
    estado: EstadoProyecto,
    plan: PlanActualizacion,
    skills_destino: list[str],
) -> None:
    """Aplica todos los reemplazos con respaldo y revierte ante cualquier fallo."""
    if plan["conflictos"]:
        raise ValueError("La actualizacion contiene conflictos")
    cambios = [*plan["archivos_actualizados"], *plan["archivos_agregados"]]
    estado_anterior = ruta_estado.read_bytes()
    directorios_creados: set[Path] = set()
    with tempfile.TemporaryDirectory(prefix="respaldo-actualizacion-") as temporal:
        respaldo = Path(temporal)
        existentes: set[str] = set()
        try:
            for relativa in cambios:
                destino = proyecto / Path(relativa)
                if destino.is_file():
                    copia = respaldo / Path(relativa)
                    copia.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(destino, copia)
                    existentes.add(relativa)
                faltantes: list[Path] = []
                directorio = destino.parent
                while directorio != proyecto and not directorio.exists():
                    faltantes.append(directorio)
                    directorio = directorio.parent
                destino.parent.mkdir(parents=True, exist_ok=True)
                directorios_creados.update(faltantes)
                temporal_archivo = destino.with_name(f".{destino.name}.actualizacion-temporal")
                shutil.copy2(fuente / Path(relativa), temporal_archivo)
                os.replace(temporal_archivo, destino)

            actualizado = EstadoProyecto(estado)
            actualizado["version_framework"] = plan["version_destino"]
            contrato = cargar_objeto_json(
                proyecto / "configuracion_plantilla.json", "el contrato actualizado"
            )
            version_contrato = contrato.get("version_contrato")
            if not isinstance(version_contrato, int):
                raise ValueError("El contrato actualizado no declara version_contrato")
            actualizado["version_contrato"] = version_contrato
            actualizado["skills_instaladas"] = skills_destino
            actualizado["huellas_gestionadas"] = calcular_huellas_gestionadas(proyecto)
            historial = actualizado.get("actualizaciones_framework", [])
            if not isinstance(historial, list):
                raise ValueError("actualizaciones_framework debe ser una lista")
            historial.append(
                {
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "version_origen": plan["version_origen"],
                    "version_destino": plan["version_destino"],
                    "archivos_actualizados": cambios,
                    "skills_agregadas": plan["skills_agregadas"],
                }
            )
            actualizado["actualizaciones_framework"] = historial
            escribir_estado(ruta_estado, actualizado)
        except (OSError, UnicodeError, ValueError):
            for relativa in reversed(cambios):
                destino = proyecto / Path(relativa)
                if relativa in existentes:
                    shutil.copy2(respaldo / Path(relativa), destino)
                elif destino.exists():
                    destino.unlink()
            for directorio in sorted(directorios_creados, key=lambda ruta: len(ruta.parts), reverse=True):
                if directorio.exists():
                    directorio.rmdir()
            ruta_estado.write_bytes(estado_anterior)
            raise


def actualizar(
    proyecto_crudo: Path,
    solo_verificar: bool,
    adoptar: bool,
) -> PlanActualizacion:
    """Prepara y aplica una actualizacion desde el framework actual."""
    raiz_framework = Path(__file__).resolve().parent.parent
    proyecto = proyecto_crudo.expanduser().resolve(strict=True)
    if not proyecto.is_dir() or proyecto == raiz_framework.resolve():
        raise ValueError("El destino debe ser un proyecto generado distinto del framework")
    ruta_estado = proyecto / ".estado-plantilla.json"
    estado = cargar_estado(ruta_estado)
    if adoptar:
        if not solo_verificar:
            raise ValueError("--adoptar-estado-actual requiere --solo-verificar")
        adoptar_estado_actual(proyecto, ruta_estado, estado)
        estado = cargar_estado(ruta_estado)
    validar_arbol_sin_enlaces(raiz_framework / "plantilla" / ".agents" / "skills")
    contrato = cargar_objeto_json(
        raiz_framework / "plantilla" / "configuracion_plantilla.json", "el contrato fuente"
    )
    version_destino = contrato.get("version_framework")
    if not isinstance(version_destino, str):
        raise ValueError("El contrato fuente no declara version_framework")
    with tempfile.TemporaryDirectory(prefix="fuente-actualizacion-") as temporal:
        fuente, skills_destino = preparar_fuente(
            raiz_framework,
            cast(list[str], estado["skills_instaladas"]),
            Path(temporal),
        )
        plan = construir_plan(proyecto, fuente, estado, version_destino, skills_destino)
        hay_cambios = bool(
            plan["archivos_actualizados"]
            or plan["archivos_agregados"]
            or plan["skills_agregadas"]
            or plan["version_origen"] != plan["version_destino"]
        )
        if not solo_verificar and not plan["conflictos"] and hay_cambios:
            aplicar_plan(proyecto, fuente, ruta_estado, estado, plan, skills_destino)
    return plan


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz segura del actualizador."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("proyecto", type=Path)
    analizador.add_argument("--solo-verificar", action="store_true")
    analizador.add_argument(
        "--adoptar-estado-actual",
        action="store_true",
        help="Registra huellas de una instancia heredada sin actualizar archivos",
    )
    return analizador.parse_args()


def main() -> int:
    """Informa el plan y usa codigo distinto cuando existen conflictos."""
    argumentos = crear_argumentos()
    try:
        plan = actualizar(
            argumentos.proyecto,
            argumentos.solo_verificar,
            argumentos.adoptar_estado_actual,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 2 if plan["conflictos"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
