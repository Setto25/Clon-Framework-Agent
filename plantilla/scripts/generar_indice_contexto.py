#!/usr/bin/env python3
"""Construye un indice local compacto de referencias para una tarea transversal."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DIRECTORIOS_EXCLUIDOS: frozenset[str] = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".next",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "resultados",
        "venv",
    }
)
MAXIMO_BYTES_ARCHIVO = 1024 * 1024
MAXIMO_TERMINOS = 8
MAXIMO_ARCHIVOS = 30
MAXIMO_FRAGMENTOS_POR_ARCHIVO = 1
MAXIMO_CARACTERES_FRAGMENTO = 180


def resolver_raiz(raiz: Path) -> Path:
    """Resuelve y valida el directorio que limita el analisis."""
    resuelta = raiz.resolve()
    if not resuelta.is_dir():
        raise ValueError("La raiz de analisis no es un directorio")
    return resuelta


def validar_terminos(terminos: list[str]) -> list[str]:
    """Normaliza terminos sin aceptar consultas vacias ni desproporcionadas."""
    normalizados: list[str] = []
    for termino in terminos:
        limpio = termino.strip()
        if not limpio or len(limpio) > 120:
            raise ValueError("Cada termino debe contener entre 1 y 120 caracteres")
        if limpio.casefold() not in {existente.casefold() for existente in normalizados}:
            normalizados.append(limpio)
    if not normalizados or len(normalizados) > MAXIMO_TERMINOS:
        raise ValueError(f"Se requieren entre 1 y {MAXIMO_TERMINOS} terminos unicos")
    return normalizados


def archivo_incluido(archivo: Path, raiz: Path) -> bool:
    """Acepta solo archivos regulares internos, acotados y no generados."""
    try:
        relativa = archivo.relative_to(raiz)
        resuelta = archivo.resolve()
        tamano = archivo.stat().st_size
    except (OSError, ValueError):
        return False
    return (
        archivo.is_file()
        and not archivo.is_symlink()
        and (resuelta == raiz or raiz in resuelta.parents)
        and not any(parte in DIRECTORIOS_EXCLUIDOS for parte in relativa.parts)
        and archivo.suffix.casefold() != ".pyc"
        and tamano <= MAXIMO_BYTES_ARCHIVO
    )


def clasificar_ruta(ruta: str) -> str:
    """Clasifica una ruta para facilitar la revision semantica posterior."""
    partes = Path(ruta).parts
    nombre = Path(ruta).name.casefold()
    sufijo = Path(ruta).suffix.casefold()
    if "pruebas" in partes or nombre.startswith("prueba_"):
        return "pruebas"
    if "auditoria" in partes or "inventario" in nombre:
        return "inventario"
    if sufijo in {".md", ".rst", ".txt"}:
        return "documentacion"
    if "scripts" in partes or sufijo in {".py", ".ps1", ".sh", ".ts", ".tsx", ".js"}:
        return "codigo"
    if sufijo in {".json", ".toml", ".yaml", ".yml", ".ini"}:
        return "configuracion"
    return "otro"


def recortar_fragmento(linea: str, posicion: int) -> str:
    """Extrae un fragmento literal corto alrededor de la primera coincidencia."""
    limpia = linea.rstrip("\r\n")
    if len(limpia) <= MAXIMO_CARACTERES_FRAGMENTO:
        return limpia
    mitad = MAXIMO_CARACTERES_FRAGMENTO // 2
    inicio = max(0, posicion - mitad)
    fin = min(len(limpia), inicio + MAXIMO_CARACTERES_FRAGMENTO)
    inicio = max(0, fin - MAXIMO_CARACTERES_FRAGMENTO)
    return limpia[inicio:fin]


def analizar_impacto(
    raiz: Path,
    terminos: list[str],
    maximo_archivos: int = MAXIMO_ARCHIVOS,
    maximo_fragmentos: int = MAXIMO_FRAGMENTOS_POR_ARCHIVO,
) -> dict[str, object]:
    """Recorre el arbol local y agrupa coincidencias sin usar un modelo."""
    raiz_resuelta = resolver_raiz(raiz)
    terminos_validos = validar_terminos(terminos)
    if maximo_archivos < 1 or maximo_archivos > 100:
        raise ValueError("maximo_archivos debe estar entre 1 y 100")
    if maximo_fragmentos < 0 or maximo_fragmentos > 3:
        raise ValueError("maximo_fragmentos debe estar entre 0 y 3")

    examinados = 0
    coincidencias_totales = 0
    archivos: list[dict[str, object]] = []
    terminos_plegados = [(termino, termino.casefold()) for termino in terminos_validos]
    for archivo in sorted(raiz_resuelta.rglob("*")):
        if not archivo_incluido(archivo, raiz_resuelta):
            continue
        examinados += 1
        try:
            lineas = archivo.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        fragmentos: list[dict[str, object]] = []
        coincidencias_archivo = 0
        for numero, linea in enumerate(lineas, start=1):
            linea_plegada = linea.casefold()
            encontrados = [
                termino
                for termino, plegado in terminos_plegados
                if plegado in linea_plegada
            ]
            if not encontrados:
                continue
            coincidencias_linea = sum(
                linea_plegada.count(plegado)
                for _, plegado in terminos_plegados
            )
            coincidencias_archivo += coincidencias_linea
            if len(fragmentos) < maximo_fragmentos:
                posiciones = [
                    linea_plegada.find(plegado)
                    for _, plegado in terminos_plegados
                    if plegado in linea_plegada
                ]
                fragmentos.append(
                    {
                        "linea": numero,
                        "texto": recortar_fragmento(linea, min(posiciones)),
                        "terminos": encontrados,
                    }
                )
        if coincidencias_archivo:
            coincidencias_totales += coincidencias_archivo
            ruta = archivo.relative_to(raiz_resuelta).as_posix()
            archivos.append(
                {
                    "ruta": ruta,
                    "categoria": clasificar_ruta(ruta),
                    "coincidencias": coincidencias_archivo,
                    "fragmentos": fragmentos,
                }
            )

    archivos.sort(key=lambda elemento: str(elemento["ruta"]))
    total_archivos = len(archivos)
    resultado: dict[str, object] = {
        "terminos": terminos_validos,
        "archivos_examinados": examinados,
        "archivos_con_coincidencias": total_archivos,
        "coincidencias": coincidencias_totales,
        "archivos": archivos[:maximo_archivos],
        "truncado": total_archivos > maximo_archivos,
    }
    resultado["caracteres_serializados"] = len(
        json.dumps(resultado, ensure_ascii=False, separators=(",", ":"))
    )
    return resultado


def main() -> int:
    """Expone el analizador como una CLI reproducible de biblioteca estandar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terminos", nargs="+", help="Terminos literales relacionados con el cambio.")
    parser.add_argument("--raiz", type=Path, default=Path.cwd())
    parser.add_argument("--maximo-archivos", type=int, default=MAXIMO_ARCHIVOS)
    parser.add_argument("--maximo-fragmentos", type=int, default=MAXIMO_FRAGMENTOS_POR_ARCHIVO)
    argumentos = parser.parse_args()
    resultado = analizar_impacto(
        argumentos.raiz,
        argumentos.terminos,
        argumentos.maximo_archivos,
        argumentos.maximo_fragmentos,
    )
    print(json.dumps(resultado, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
