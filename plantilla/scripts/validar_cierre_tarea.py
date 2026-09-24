#!/usr/bin/env python3
"""Impide cierres sin ejecutar todas las verificaciones deterministas aplicables."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Optional, TypedDict

from contrato_validacion import (
    NOMBRE_CONTRATO,
    Comprobacion,
    EstadoVerificacion,
    ResultadoVerificacion,
    ejecutar_comprobacion,
    validar_comando,
)
from diagnosticar_tarea import diagnosticar
from verificar_memoria_proyecto import ResultadoVerificacion as ResultadoMemoria, verificar


DOCUMENTOS_MINIMOS: tuple[str, ...] = (
    "PROJECT_STATE.md",
    "documentacion/PLAN_DESARROLLO.md",
    "documentacion/REGISTRO_CAMBIOS.md",
)
DOCUMENTO_TECNICO = "documentacion/DOCUMENTACION_TECNICA.md"
CRITERIOS_CONSERVADORES: list[EstadoVerificacion] = [
    "FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"
]


class EvidenciaComando(TypedDict):
    """Conserva compatibilidad con el formato historico de pruebas."""

    comando: str
    directorio: str
    codigo: Optional[int]
    estado: str
    duracion_segundos: float
    salida: str


class ResultadoCierre(TypedDict):
    """Representa toda la evidencia objetiva de una puerta de cierre."""

    valido: bool
    solo_verificaciones: bool
    cobertura: str
    contrato: str | None
    memoria: ResultadoMemoria | None
    archivos_modificados: list[str]
    documentos_declarados: list[str]
    guia_operacion_revisada: bool
    verificaciones: list[ResultadoVerificacion]
    pruebas: list[EvidenciaComando]
    documentacion_habilitada: bool
    errores: list[str]


def crear_argumentos() -> argparse.Namespace:
    """Define una interfaz compatible que prioriza el contrato versionado."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("raiz", nargs="?", type=Path, default=Path.cwd())
    analizador.add_argument(
        "--comando-prueba",
        action="append",
        default=[],
        help="Comando adicional ejecutado sin shell desde la raiz; se puede repetir.",
    )
    analizador.add_argument("--archivo-modificado", action="append", default=[])
    analizador.add_argument("--documento-actualizado", action="append", default=[])
    analizador.add_argument("--documentacion-tecnica-aplica", action="store_true")
    analizador.add_argument("--guia-operacion-revisada", action="store_true")
    analizador.add_argument(
        "--solo-verificaciones",
        action="store_true",
        help="Ejecuta la precondicion antes de permitir declaraciones documentales de cierre.",
    )
    analizador.add_argument(
        "--salida-evidencia",
        type=Path,
        default=None,
        help="Guarda el JSON comprobable dentro del proyecto, incluso cuando el cierre falla.",
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


def separar_comando(comando: str) -> list[str]:
    """Convierte una entrada heredada en argv y rechaza sintaxis de shell."""
    if not comando.strip():
        raise ValueError("El comando de prueba esta vacio")
    partes = shlex.split(comando, posix=os.name != "nt")
    partes = [parte.strip('"') for parte in partes]
    return validar_comando(partes, "--comando-prueba")


def ejecutar_comandos_manuales(raiz: Path, comandos: list[str]) -> list[ResultadoVerificacion]:
    """Ejecuta comprobaciones adicionales sin permitir que sustituyan el contrato."""
    resultados: list[ResultadoVerificacion] = []
    for indice, comando in enumerate(comandos, start=1):
        comprobacion = Comprobacion(
            identificador=f"manual-{indice}",
            tipo="contrato",
            modulo="raiz",
            directorio=".",
            comando=separar_comando(comando),
            obligatoria=True,
            bloquea_cierre=True,
            timeout_segundos=300,
            origen="MANUAL",
        )
        resultados.append(ejecutar_comprobacion(raiz, comprobacion))
    return resultados


def convertir_pruebas(resultados: list[ResultadoVerificacion]) -> list[EvidenciaComando]:
    """Expone codigo, directorio y duracion en el campo de compatibilidad."""
    return [
        EvidenciaComando(
            comando=resultado["comando_texto"],
            directorio=resultado["directorio"],
            codigo=resultado["codigo_salida"],
            estado=resultado["estado"],
            duracion_segundos=resultado["duracion_segundos"],
            salida=resultado["evidencia"],
        )
        for resultado in resultados
    ]


def documentos_del_contrato(raiz: Path) -> set[str]:
    """Obtiene documentos obligatorios ya validados por el diagnostico."""
    ruta = raiz / NOMBRE_CONTRATO
    if not ruta.is_file():
        return set(DOCUMENTOS_MINIMOS)
    datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(datos, dict) or not isinstance(datos.get("documentos_obligatorios"), list):
        raise ValueError("El contrato no expone documentos_obligatorios validos")
    return set(DOCUMENTOS_MINIMOS) | {
        str(item) for item in datos["documentos_obligatorios"] if isinstance(item, str)
    }


def validar_cierre(
    raiz: Path,
    comandos: list[str],
    archivos: list[str],
    documentos: list[str],
    documentacion_tecnica_aplica: bool,
    guia_operacion_revisada: bool,
    solo_verificaciones: bool = False,
) -> ResultadoCierre:
    """Ejecuta todas las puertas antes de habilitar el cierre documental."""
    raiz_resuelta = raiz.expanduser().resolve()
    if not raiz_resuelta.is_dir():
        raise ValueError("La raiz del proyecto no existe o no es un directorio")
    diagnostico = diagnosticar(raiz_resuelta)
    verificaciones = list(diagnostico["verificaciones"])
    verificaciones.extend(ejecutar_comandos_manuales(raiz_resuelta, comandos))
    errores: list[str] = []
    for resultado in verificaciones:
        if resultado["estado"] in CRITERIOS_CONSERVADORES and (
            resultado["obligatoria"]
            or resultado["bloquea_cierre"]
            or resultado["estado"] == "NO_EJECUTADO"
        ):
            prefijo = "Fallo la prueba" if resultado["estado"] == "FALLIDO" else resultado["estado"]
            errores.append(
                f"{prefijo}: {resultado['identificador']} "
                f"({resultado['directorio']}, codigo={resultado['codigo_salida']})"
            )
    if not any(resultado["estado"] == "APROBADO" for resultado in verificaciones):
        errores.append("No existe ninguna verificacion ejecutada y aprobada")

    memoria: ResultadoMemoria | None = None
    archivos_normalizados: list[str] = []
    documentos_normalizados: list[str] = []
    if not solo_verificaciones:
        archivos_normalizados = validar_rutas(raiz_resuelta, archivos, "--archivo-modificado")
        documentos_normalizados = validar_rutas(
            raiz_resuelta, documentos, "--documento-actualizado"
        )
        faltantes = documentos_del_contrato(raiz_resuelta) - set(documentos_normalizados)
        if documentacion_tecnica_aplica and DOCUMENTO_TECNICO not in documentos_normalizados:
            faltantes.add(DOCUMENTO_TECNICO)
        memoria = verificar(raiz_resuelta)
        if not memoria["valido"]:
            errores.append("La memoria del proyecto no es valida")
        if faltantes:
            errores.append("Faltan documentos declarados: " + ", ".join(sorted(faltantes)))
        if not guia_operacion_revisada:
            errores.append("Debe declararse la revision de GUIA_OPERACION.md")
    return ResultadoCierre(
        valido=not errores,
        solo_verificaciones=solo_verificaciones,
        cobertura=diagnostico["cobertura"],
        contrato=diagnostico["contrato"],
        memoria=memoria,
        archivos_modificados=archivos_normalizados,
        documentos_declarados=documentos_normalizados,
        guia_operacion_revisada=guia_operacion_revisada,
        verificaciones=verificaciones,
        pruebas=convertir_pruebas(verificaciones),
        documentacion_habilitada=not errores,
        errores=list(dict.fromkeys(errores)),
    )


def escribir_evidencia(raiz: Path, ruta: Path, resultado: ResultadoCierre) -> Path:
    """Publica evidencia JSON atomicamente dentro del proyecto."""
    raiz_resuelta = raiz.resolve()
    destino = ruta if ruta.is_absolute() else raiz_resuelta / ruta
    destino = destino.resolve()
    try:
        destino.relative_to(raiz_resuelta)
    except ValueError as error:
        raise ValueError("La salida de evidencia debe quedar dentro del proyecto") from error
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{destino.name}.temporal")
    temporal.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporal, destino)
    return destino


def imprimir_texto(resultado: ResultadoCierre) -> None:
    """Presenta estados sin convertir ausencia de cobertura en aprobacion."""
    print(f"Cobertura: {resultado['cobertura']}")
    for prueba in resultado["pruebas"]:
        print(
            f"[{prueba['estado']}] {prueba['directorio']} | {prueba['comando'] or 'sin comando'} "
            f"| codigo={prueba['codigo']} | {prueba['duracion_segundos']:.3f}s"
        )
    if resultado["valido"]:
        print("Prevalidacion aprobada." if resultado["solo_verificaciones"] else "Cierre de tarea valido.")
        return
    print("Cierre de tarea invalido:")
    for error in resultado["errores"]:
        print(f"- {error}")


def main() -> int:
    """Ejecuta la puerta y persiste evidencia cuando se solicita."""
    argumentos = crear_argumentos()
    try:
        resultado = validar_cierre(
            argumentos.raiz,
            argumentos.comando_prueba,
            argumentos.archivo_modificado,
            argumentos.documento_actualizado,
            argumentos.documentacion_tecnica_aplica,
            argumentos.guia_operacion_revisada,
            argumentos.solo_verificaciones,
        )
        if argumentos.salida_evidencia:
            escribir_evidencia(argumentos.raiz, argumentos.salida_evidencia, resultado)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if argumentos.salida_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        imprimir_texto(resultado)
    return 0 if resultado["valido"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
