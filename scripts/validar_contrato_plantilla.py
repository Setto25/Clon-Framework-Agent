#!/usr/bin/env python3
"""Valida que la plantilla use solamente placeholders declarados."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TypedDict, cast


class CampoPlaceholder(TypedDict):
    """Representa la configuracion validada de un placeholder."""

    obligatorio: bool
    origen: str
    descripcion: str


class ConfiguracionPlantilla(TypedDict):
    """Representa el contrato validado de la plantilla."""

    version_contrato: int
    version_framework: str
    sintaxis_placeholder: str
    rutas_excluidas: list[str]
    archivos_incluidos: list[str]
    placeholders: dict[str, CampoPlaceholder]


PATRON_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def cargar_json_sin_duplicados(contenido: str, nombre: str) -> object:
    """Carga JSON y rechaza claves duplicadas en cualquier objeto."""
    def construir_objeto(pares: list[tuple[str, object]]) -> dict[str, object]:
        resultado: dict[str, object] = {}
        for clave, valor in pares:
            if clave in resultado:
                raise ValueError(f"{nombre} contiene una clave duplicada: {clave}")
            resultado[clave] = valor
        return resultado

    return cast(object, json.loads(contenido, object_pairs_hook=construir_objeto))


def exigir_diccionario(valor: object, nombre: str) -> dict[str, object]:
    """Verifica que un valor JSON sea un objeto."""
    if not isinstance(valor, dict):
        raise ValueError(f"{nombre} debe ser un objeto JSON")
    return cast(dict[str, object], valor)


def exigir_lista_cadenas(valor: object, nombre: str) -> list[str]:
    """Verifica que un valor JSON sea una lista de cadenas."""
    if not isinstance(valor, list) or not all(isinstance(item, str) for item in valor):
        raise ValueError(f"{nombre} debe ser una lista de cadenas")
    return cast(list[str], valor)


def cargar_configuracion(ruta: Path) -> ConfiguracionPlantilla:
    """Carga y valida la estructura minima del contrato."""
    contenido = cargar_json_sin_duplicados(ruta.read_text(encoding="utf-8"), str(ruta))
    datos = exigir_diccionario(contenido, "configuracion")

    version = datos.get("version_contrato")
    version_framework = datos.get("version_framework")
    sintaxis = datos.get("sintaxis_placeholder")
    if not isinstance(version, int) or version < 1:
        raise ValueError("version_contrato debe ser un entero positivo")
    if not isinstance(version_framework, str) or not version_framework:
        raise ValueError("version_framework debe ser una cadena no vacia")
    if not isinstance(sintaxis, str) or not sintaxis:
        raise ValueError("sintaxis_placeholder debe ser una cadena no vacia")

    campos_sin_validar = exigir_diccionario(datos.get("placeholders"), "placeholders")
    campos: dict[str, CampoPlaceholder] = {}
    for clave, valor in campos_sin_validar.items():
        if not PATRON_PLACEHOLDER.fullmatch(f"{{{{{clave}}}}}"):
            raise ValueError(f"Nombre de placeholder invalido: {clave}")
        campo = exigir_diccionario(valor, f"placeholders.{clave}")
        obligatorio = campo.get("obligatorio")
        origen = campo.get("origen")
        descripcion = campo.get("descripcion")
        if not isinstance(obligatorio, bool):
            raise ValueError(f"placeholders.{clave}.obligatorio debe ser booleano")
        if not isinstance(origen, str) or not origen:
            raise ValueError(f"placeholders.{clave}.origen debe ser una cadena no vacia")
        if not isinstance(descripcion, str) or not descripcion:
            raise ValueError(f"placeholders.{clave}.descripcion debe ser una cadena no vacia")
        campos[clave] = CampoPlaceholder(
            obligatorio=obligatorio,
            origen=origen,
            descripcion=descripcion,
        )

    return ConfiguracionPlantilla(
        version_contrato=version,
        version_framework=version_framework,
        sintaxis_placeholder=sintaxis,
        rutas_excluidas=exigir_lista_cadenas(datos.get("rutas_excluidas"), "rutas_excluidas"),
        archivos_incluidos=exigir_lista_cadenas(datos.get("archivos_incluidos"), "archivos_incluidos"),
        placeholders=campos,
    )


def resolver_archivos(raiz: Path, patrones: list[str]) -> tuple[list[Path], list[str]]:
    """Resuelve los patrones declarados y reporta los que no encuentran archivos."""
    archivos: set[Path] = set()
    faltantes: list[str] = []
    for patron in patrones:
        coincidencias = [ruta for ruta in raiz.glob(patron) if ruta.is_file()]
        if not coincidencias:
            faltantes.append(patron)
        archivos.update(coincidencias)
    return sorted(archivos), faltantes


def recopilar_usos(archivos: list[Path]) -> dict[str, list[Path]]:
    """Recopila los archivos donde aparece cada placeholder."""
    usos: dict[str, list[Path]] = {}
    for archivo in archivos:
        contenido = archivo.read_text(encoding="utf-8")
        for clave in PATRON_PLACEHOLDER.findall(contenido):
            usos.setdefault(clave, []).append(archivo)
    return usos


def validar(raiz_repositorio: Path) -> list[str]:
    """Valida el contrato y devuelve los errores encontrados."""
    raiz_plantilla = raiz_repositorio / "plantilla"
    ruta_configuracion = raiz_plantilla / "configuracion_plantilla.json"
    configuracion = cargar_configuracion(ruta_configuracion)
    archivos, patrones_faltantes = resolver_archivos(
        raiz_plantilla,
        configuracion["archivos_incluidos"],
    )
    usos = recopilar_usos(archivos)
    declarados = set(configuracion["placeholders"])
    encontrados = set(usos)

    errores: list[str] = []
    errores.extend(f"El patron no encontro archivos: {patron}" for patron in patrones_faltantes)
    errores.extend(
        f"Placeholder no declarado: {clave} ({', '.join(str(ruta.relative_to(raiz_repositorio)) for ruta in usos[clave])})"
        for clave in sorted(encontrados - declarados)
    )
    errores.extend(
        f"Placeholder declarado sin uso: {clave}"
        for clave in sorted(declarados - encontrados)
    )
    return errores


def main() -> int:
    """Ejecuta la validacion desde la raiz del repositorio."""
    raiz_repositorio = Path(__file__).resolve().parent.parent
    try:
        errores = validar(raiz_repositorio)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: no se pudo validar el contrato: {error}", file=sys.stderr)
        return 1

    if errores:
        print("Contrato de plantilla invalido:", file=sys.stderr)
        for error in errores:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Contrato de plantilla valido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
