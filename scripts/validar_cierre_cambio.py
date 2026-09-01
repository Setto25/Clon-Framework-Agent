#!/usr/bin/env python3
"""Valida que un cambio material quede completo y coherente antes de cerrarse."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

if __package__:
    from .validar_contrato_plantilla import cargar_configuracion, validar
else:
    from validar_contrato_plantilla import cargar_configuracion, validar


RAIZ = Path(__file__).resolve().parent.parent
PATRON_SCRIPT = re.compile(r"(?<![A-Za-z0-9_.-])(scripts/[A-Za-z0-9_./-]+\.py)")
RUTAS_DOCUMENTACION_OBLIGATORIA: frozenset[str] = frozenset(
    {"PROJECT_STATE.md", "README.md"}
)
PREFIJOS_CAMBIO_MATERIAL: tuple[str, ...] = (
    "scripts/",
    "plantilla/.agents/skills/",
    "plantilla/scripts/",
)
RUTAS_CAMBIO_MATERIAL: frozenset[str] = frozenset(
    {"plantilla/configuracion_plantilla.json"}
)


def ejecutar_git(argumentos: list[str]) -> subprocess.CompletedProcess[str]:
    """Ejecuta Git con salida textual y el repositorio autorizado."""
    return subprocess.run(
        ["git", "-c", f"safe.directory={RAIZ.as_posix()}", *argumentos],
        cwd=RAIZ,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def rutas_cambiadas(base: str | None) -> set[str]:
    """Obtiene cambios locales y, cuando se declara, cambios contra una base Git."""
    rutas: set[str] = set()
    estado = ejecutar_git(["status", "--porcelain", "--untracked-files=all"])
    if estado.returncode == 0:
        for linea in estado.stdout.splitlines():
            ruta = linea[3:].strip().replace("\\", "/")
            if " -> " in ruta:
                ruta = ruta.split(" -> ", 1)[1]
            if ruta:
                rutas.add(ruta)
    if base and set(base) != {"0"}:
        diferencia = ejecutar_git(["diff", "--name-only", f"{base}...HEAD"])
        if diferencia.returncode != 0:
            raise ValueError(
                "No se pudo comparar la base Git declarada: "
                + diferencia.stderr.strip()
            )
        rutas.update(
            linea.strip().replace("\\", "/")
            for linea in diferencia.stdout.splitlines()
            if linea.strip()
        )
    return rutas


def es_cambio_material(ruta: str) -> bool:
    """Determina si una ruta exige sincronizacion documental."""
    return ruta in RUTAS_CAMBIO_MATERIAL or ruta.startswith(PREFIJOS_CAMBIO_MATERIAL)


def validar_documentacion_cambio(rutas: set[str]) -> list[str]:
    """Exige los documentos de estado cuando cambia implementacion material."""
    if not any(es_cambio_material(ruta) for ruta in rutas):
        return []
    faltantes = sorted(RUTAS_DOCUMENTACION_OBLIGATORIA - rutas)
    return [
        "Un cambio material no actualizo: " + ", ".join(faltantes)
    ] if faltantes else []


def extraer_referencias_scripts(ruta: Path) -> set[str]:
    """Extrae rutas de scripts citadas en un documento textual."""
    contenido = ruta.read_text(encoding="utf-8")
    return {coincidencia.group(1) for coincidencia in PATRON_SCRIPT.finditer(contenido)}


def validar_dependencias_skills(rutas_gestionadas: set[str]) -> list[str]:
    """Comprueba existencia e instalacion de scripts citados por las Skills."""
    errores: list[str] = []
    raiz_skills = RAIZ / "plantilla" / ".agents" / "skills"
    for skill in sorted(raiz_skills.rglob("SKILL.md")):
        for referencia in sorted(extraer_referencias_scripts(skill)):
            ruta_plantilla = RAIZ / "plantilla" / Path(referencia)
            ruta_framework = RAIZ / Path(referencia)
            if not ruta_plantilla.is_file() and not ruta_framework.is_file():
                errores.append(
                    f"{skill.relative_to(RAIZ).as_posix()} cita una ruta inexistente: {referencia}"
                )
            if ruta_plantilla.is_file() and referencia not in rutas_gestionadas:
                errores.append(
                    f"La dependencia de Skill no esta administrada: {referencia}"
                )
    return errores


def validar_referencias_documentales() -> list[str]:
    """Rechaza scripts inexistentes citados por la documentacion principal."""
    errores: list[str] = []
    for documento in (RAIZ / "README.md", RAIZ / "PROJECT_STATE.md"):
        for referencia in sorted(extraer_referencias_scripts(documento)):
            existe = (RAIZ / Path(referencia)).is_file() or (
                RAIZ / "plantilla" / Path(referencia)
            ).is_file()
            if not existe:
                errores.append(
                    f"{documento.name} cita una ruta inexistente: {referencia}"
                )
    return errores


def ejecutar_comando(nombre: str, argumentos: list[str]) -> list[str]:
    """Ejecuta una comprobacion y devuelve un fallo compacto cuando corresponde."""
    resultado = subprocess.run(
        argumentos,
        cwd=RAIZ,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if resultado.returncode == 0:
        print(f"OK: {nombre}")
        return []
    salida = (resultado.stdout + resultado.stderr).strip()
    return [f"{nombre} fallo:\n{salida}"]


def validar_cierre(base: str | None, ejecutar_pruebas: bool) -> list[str]:
    """Reune validaciones estaticas, documentales y ejecutables del cierre."""
    errores = validar(RAIZ)
    configuracion = cargar_configuracion(
        RAIZ / "plantilla" / "configuracion_plantilla.json"
    )
    rutas_gestionadas = set(configuracion["archivos_gestionados"])
    errores.extend(validar_dependencias_skills(rutas_gestionadas))
    errores.extend(validar_referencias_documentales())
    errores.extend(validar_documentacion_cambio(rutas_cambiadas(base)))
    argumentos_diff = ["diff", "--check"]
    if base and set(base) != {"0"}:
        argumentos_diff.append(f"{base}...HEAD")
    resultado_diff = ejecutar_git(argumentos_diff)
    if resultado_diff.returncode != 0:
        errores.append("Git detecto errores de formato:\n" + resultado_diff.stdout.strip())
    if ejecutar_pruebas:
        errores.extend(
            ejecutar_comando(
                "Suite Python",
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "pruebas",
                    "-p",
                    "prueba_*.py",
                ],
            )
        )
    return errores


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz del cierre reproducible."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument(
        "--base",
        default=os.environ.get("BASE_CAMBIO") or None,
        help="Revision Git base para validar los archivos cambiados en CI.",
    )
    analizador.add_argument("--omitir-pruebas", action="store_true")
    return analizador.parse_args()


def main() -> int:
    """Informa todas las causas que impiden declarar cerrado el cambio."""
    argumentos = crear_argumentos()
    try:
        errores = validar_cierre(argumentos.base, not argumentos.omitir_pruebas)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: no se pudo validar el cierre: {error}", file=sys.stderr)
        return 1
    if errores:
        print("Cierre de cambio invalido:", file=sys.stderr)
        for error in errores:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Cierre de cambio valido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
