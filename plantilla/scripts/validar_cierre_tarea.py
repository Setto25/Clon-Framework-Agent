#!/usr/bin/env python3
"""Verifica evidencia reproducible antes de declarar terminada una tarea material."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, TypedDict

from verificar_memoria_proyecto import ResultadoVerificacion, verificar


LIMITE_SALIDA = 6000
DOCUMENTOS_MINIMOS: tuple[str, ...] = (
    "PROJECT_STATE.md",
    "documentacion/PLAN_DESARROLLO.md",
    "documentacion/REGISTRO_CAMBIOS.md",
)
DOCUMENTO_TECNICO = "documentacion/DOCUMENTACION_TECNICA.md"


class ResultadoComando(TypedDict):
    """Representa una prueba ejecutada durante el cierre."""

    comando: str
    codigo: int
    salida: str


class ResultadoCierre(TypedDict):
    """Representa la evidencia comprobable de una tarea cerrada."""

    valido: bool
    memoria: ResultadoVerificacion
    archivos_modificados: list[str]
    documentos_declarados: list[str]
    guia_operacion_revisada: bool
    pruebas: list[ResultadoComando]
    errores: list[str]


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz de cierre aplicable a proyectos generados."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("raiz", nargs="?", type=Path, default=Path.cwd())
    analizador.add_argument(
        "--comando-prueba",
        action="append",
        default=[],
        help="Comando de prueba que se ejecutara desde la raiz; se puede repetir.",
    )
    analizador.add_argument(
        "--archivo-modificado",
        action="append",
        default=[],
        help="Ruta relativa de un archivo modificado durante la tarea; se puede repetir.",
    )
    analizador.add_argument(
        "--documento-actualizado",
        action="append",
        default=[],
        help="Ruta relativa de un documento actualizado; se puede repetir.",
    )
    analizador.add_argument(
        "--documentacion-tecnica-aplica",
        action="store_true",
        help="Exige declarar la actualizacion de DOCUMENTACION_TECNICA.md.",
    )
    analizador.add_argument(
        "--guia-operacion-revisada",
        action="store_true",
        help="Confirma que GUIA_OPERACION.md fue actualizada o evaluada como no aplicable.",
    )
    analizador.add_argument("--json", action="store_true", dest="salida_json")
    return analizador.parse_args()


def resolver_ruta(raiz: Path, relativa: str) -> str:
    """Confina una ruta declarada a un archivo regular dentro del proyecto."""
    candidata = Path(relativa)
    if not relativa or candidata.is_absolute():
        raise ValueError(f"La ruta debe ser relativa: {relativa}")
    resuelta = (raiz / candidata).resolve()
    try:
        normalizada = resuelta.relative_to(raiz)
    except ValueError as error:
        raise ValueError(f"La ruta sale del proyecto: {relativa}") from error
    if not resuelta.is_file():
        raise ValueError(f"La ruta no existe o no es regular: {relativa}")
    return normalizada.as_posix()


def validar_rutas(raiz: Path, rutas: list[str], nombre: str) -> list[str]:
    """Valida rutas unicas declaradas como evidencia de cierre."""
    if not rutas:
        raise ValueError(f"Se requiere al menos una opcion {nombre}")
    normalizadas = [resolver_ruta(raiz, ruta) for ruta in rutas]
    if len(normalizadas) != len(set(normalizadas)):
        raise ValueError(f"{nombre} no puede repetir rutas")
    return normalizadas


def ejecutar_prueba(comando: str, raiz: Path) -> ResultadoComando:
    """Ejecuta una prueba declarada y conserva una salida acotada."""
    if not comando.strip():
        return ResultadoComando(comando=comando, codigo=1, salida="El comando de prueba esta vacio")
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            cwd=raiz,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return ResultadoComando(
            comando=comando,
            codigo=1,
            salida="La prueba supero el limite de 300 segundos",
        )
    salida = (resultado.stdout + resultado.stderr).strip()
    return ResultadoComando(comando=comando, codigo=resultado.returncode, salida=salida[-LIMITE_SALIDA:])


def validar_cierre(
    raiz: Path,
    comandos: list[str],
    archivos: list[str],
    documentos: list[str],
    documentacion_tecnica_aplica: bool,
    guia_operacion_revisada: bool,
) -> ResultadoCierre:
    """Reune memoria, pruebas y registros para una puerta de cierre objetiva."""
    raiz_resuelta = raiz.expanduser().resolve()
    if not raiz_resuelta.is_dir():
        raise ValueError("La raiz del proyecto no existe o no es un directorio")
    if not comandos:
        raise ValueError("Se requiere al menos una opcion --comando-prueba")
    archivos_normalizados = validar_rutas(raiz_resuelta, archivos, "--archivo-modificado")
    documentos_normalizados = validar_rutas(
        raiz_resuelta, documentos, "--documento-actualizado"
    )
    faltantes = set(DOCUMENTOS_MINIMOS) - set(documentos_normalizados)
    if documentacion_tecnica_aplica and DOCUMENTO_TECNICO not in documentos_normalizados:
        faltantes.add(DOCUMENTO_TECNICO)
    memoria = verificar(raiz_resuelta)
    pruebas = [ejecutar_prueba(comando, raiz_resuelta) for comando in comandos]
    errores: list[str] = []
    if not memoria["valido"]:
        errores.append("La memoria del proyecto no es valida")
    if faltantes:
        errores.append("Faltan documentos declarados: " + ", ".join(sorted(faltantes)))
    if not guia_operacion_revisada:
        errores.append("Debe declararse la revision de GUIA_OPERACION.md")
    for prueba in pruebas:
        if prueba["codigo"] != 0:
            errores.append(f"Fallo la prueba: {prueba['comando']}")
    return ResultadoCierre(
        valido=not errores,
        memoria=memoria,
        archivos_modificados=archivos_normalizados,
        documentos_declarados=documentos_normalizados,
        guia_operacion_revisada=guia_operacion_revisada,
        pruebas=pruebas,
        errores=errores,
    )


def imprimir_texto(resultado: ResultadoCierre) -> None:
    """Presenta un resumen apto para revisar el cierre en la terminal."""
    for prueba in resultado["pruebas"]:
        estado = "OK" if prueba["codigo"] == 0 else "FALLO"
        print(f"[{estado}] {prueba['comando']}")
    if resultado["valido"]:
        print("Cierre de tarea valido.")
        return
    print("Cierre de tarea invalido:")
    for error in resultado["errores"]:
        print(f"- {error}")


def main() -> int:
    """Ejecuta la puerta y diferencia una entrada invalida de un cierre rechazado."""
    argumentos = crear_argumentos()
    try:
        resultado = validar_cierre(
            argumentos.raiz,
            argumentos.comando_prueba,
            argumentos.archivo_modificado,
            argumentos.documento_actualizado,
            argumentos.documentacion_tecnica_aplica,
            argumentos.guia_operacion_revisada,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if argumentos.salida_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        imprimir_texto(resultado)
    return 0 if resultado["valido"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
