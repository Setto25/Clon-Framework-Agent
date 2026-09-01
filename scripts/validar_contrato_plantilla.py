#!/usr/bin/env python3
"""Valida que la plantilla use solamente placeholders declarados."""

from __future__ import annotations

import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
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
    archivos_gestionados: list[str]
    placeholders: dict[str, CampoPlaceholder]


PATRON_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
PATRON_VERSION_FRAMEWORK = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
VERSION_CONTRATO_SOPORTADA = 3
SINTAXIS_PLACEHOLDER_SOPORTADA = "{{CLAVE}}"
ORIGENES_PERMITIDOS: frozenset[str] = frozenset({"usuario", "derivado", "predeterminado"})
CLAVES_CONTRATO: frozenset[str] = frozenset(
    {
        "version_contrato",
        "version_framework",
        "sintaxis_placeholder",
        "rutas_excluidas",
        "archivos_incluidos",
        "archivos_gestionados",
        "placeholders",
    }
)
CLAVES_CAMPO_PLACEHOLDER: frozenset[str] = frozenset({"obligatorio", "origen", "descripcion"})
MAXIMO_BYTES_JSON = 1024 * 1024


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


def leer_json_limitado(ruta: Path, nombre: str) -> str:
    """Lee solamente archivos JSON regulares dentro del limite permitido."""
    informacion = ruta.stat()
    if not stat.S_ISREG(informacion.st_mode):
        raise ValueError(f"{nombre} debe ser un archivo regular")
    with ruta.open("rb") as flujo:
        contenido = flujo.read(MAXIMO_BYTES_JSON + 1)
    if len(contenido) > MAXIMO_BYTES_JSON:
        raise ValueError(f"{nombre} supera el maximo de {MAXIMO_BYTES_JSON} bytes")
    return contenido.decode("utf-8")


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


def exigir_claves_exactas(
    datos: dict[str, object],
    esperadas: frozenset[str],
    nombre: str,
) -> None:
    """Rechaza claves faltantes o desconocidas en un objeto contractual."""
    presentes = set(datos)
    faltantes = sorted(esperadas - presentes)
    desconocidas = sorted(presentes - esperadas)
    if faltantes:
        raise ValueError(f"{nombre} no declara las claves requeridas: {', '.join(faltantes)}")
    if desconocidas:
        raise ValueError(f"{nombre} contiene claves desconocidas: {', '.join(desconocidas)}")


def validar_rutas_contrato(rutas: list[str], nombre: str) -> list[str]:
    """Valida rutas relativas y reproducibles declaradas por el contrato."""
    if not rutas:
        raise ValueError(f"{nombre} no puede estar vacio")
    duplicadas = sorted({ruta for ruta in rutas if rutas.count(ruta) > 1})
    if duplicadas:
        raise ValueError(f"{nombre} contiene rutas duplicadas: {', '.join(duplicadas)}")
    for ruta in rutas:
        ruta_pura = PurePosixPath(ruta)
        if not ruta or "\\" in ruta or ruta_pura.is_absolute() or ".." in ruta_pura.parts:
            raise ValueError(f"{nombre} contiene una ruta no portable o insegura: {ruta}")
    return rutas


def cargar_configuracion(ruta: Path) -> ConfiguracionPlantilla:
    """Carga y valida la estructura minima del contrato."""
    contenido = cargar_json_sin_duplicados(leer_json_limitado(ruta, "contrato"), str(ruta))
    datos = exigir_diccionario(contenido, "configuracion")
    exigir_claves_exactas(datos, CLAVES_CONTRATO, "configuracion")

    version = datos.get("version_contrato")
    version_framework = datos.get("version_framework")
    sintaxis = datos.get("sintaxis_placeholder")
    if version != VERSION_CONTRATO_SOPORTADA:
        raise ValueError(
            f"version_contrato no soportada: {version}. Se esperaba {VERSION_CONTRATO_SOPORTADA}"
        )
    if not isinstance(version_framework, str) or PATRON_VERSION_FRAMEWORK.fullmatch(version_framework) is None:
        raise ValueError("version_framework debe usar una version semantica valida")
    if sintaxis != SINTAXIS_PLACEHOLDER_SOPORTADA:
        raise ValueError(
            f"sintaxis_placeholder no soportada: {sintaxis}. "
            f"Se esperaba {SINTAXIS_PLACEHOLDER_SOPORTADA}"
        )

    campos_sin_validar = exigir_diccionario(datos.get("placeholders"), "placeholders")
    campos: dict[str, CampoPlaceholder] = {}
    for clave, valor in campos_sin_validar.items():
        if not PATRON_PLACEHOLDER.fullmatch(f"{{{{{clave}}}}}"):
            raise ValueError(f"Nombre de placeholder invalido: {clave}")
        campo = exigir_diccionario(valor, f"placeholders.{clave}")
        exigir_claves_exactas(campo, CLAVES_CAMPO_PLACEHOLDER, f"placeholders.{clave}")
        obligatorio = campo.get("obligatorio")
        origen = campo.get("origen")
        descripcion = campo.get("descripcion")
        if not isinstance(obligatorio, bool):
            raise ValueError(f"placeholders.{clave}.obligatorio debe ser booleano")
        if not isinstance(origen, str) or origen not in ORIGENES_PERMITIDOS:
            raise ValueError(
                f"placeholders.{clave}.origen debe ser uno de: "
                + ", ".join(sorted(ORIGENES_PERMITIDOS))
            )
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError(f"placeholders.{clave}.descripcion debe ser una cadena no vacia")
        campos[clave] = CampoPlaceholder(
            obligatorio=obligatorio,
            origen=origen,
            descripcion=descripcion,
        )

    rutas_excluidas = validar_rutas_contrato(
        exigir_lista_cadenas(datos.get("rutas_excluidas"), "rutas_excluidas"),
        "rutas_excluidas",
    )
    archivos_incluidos = validar_rutas_contrato(
        exigir_lista_cadenas(datos.get("archivos_incluidos"), "archivos_incluidos"),
        "archivos_incluidos",
    )
    archivos_gestionados = validar_rutas_contrato(
        exigir_lista_cadenas(datos.get("archivos_gestionados"), "archivos_gestionados"),
        "archivos_gestionados",
    )
    if any(
        any(caracter in ruta for caracter in "*?[]")
        for ruta in archivos_gestionados
    ):
        raise ValueError("archivos_gestionados solo admite rutas exactas")
    return ConfiguracionPlantilla(
        version_contrato=version,
        version_framework=version_framework,
        sintaxis_placeholder=sintaxis,
        rutas_excluidas=rutas_excluidas,
        archivos_incluidos=archivos_incluidos,
        archivos_gestionados=archivos_gestionados,
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
    gestionados, gestionados_faltantes = resolver_archivos(
        raiz_plantilla,
        configuracion["archivos_gestionados"],
    )
    errores.extend(
        f"El archivo gestionado no existe: {patron}"
        for patron in gestionados_faltantes
    )
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
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
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
