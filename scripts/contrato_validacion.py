#!/usr/bin/env python3
"""Carga y ejecuta contratos deterministas de validacion de proyectos."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Literal, Optional, TypedDict, cast


EstadoVerificacion = Literal[
    "APROBADO", "FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"
]
OrigenVerificacion = Literal["DECLARADO", "INFERIDO", "MANUAL"]


class VerificacionContrato(TypedDict):
    """Declara una comprobacion reproducible de un modulo."""

    identificador: str
    tipo: str
    comando: list[str]
    obligatoria: bool
    bloquea_cierre: bool
    timeout_segundos: int


class ModuloContrato(TypedDict):
    """Agrupa verificaciones que comparten un directorio de trabajo."""

    nombre: str
    directorio: str
    verificaciones: list[VerificacionContrato]


class ContratoValidacion(TypedDict):
    """Representa el manifiesto versionado de validacion del proyecto."""

    version_contrato: int
    modulos: list[ModuloContrato]
    documentos_obligatorios: list[str]
    criterios_bloqueo: list[EstadoVerificacion]


class Comprobacion(TypedDict):
    """Representa una comprobacion lista para ejecutar."""

    identificador: str
    tipo: str
    modulo: str
    directorio: str
    comando: list[str]
    obligatoria: bool
    bloquea_cierre: bool
    timeout_segundos: int
    origen: OrigenVerificacion


class ResultadoVerificacion(TypedDict):
    """Conserva evidencia observable de una comprobacion ejecutada."""

    identificador: str
    tipo: str
    modulo: str
    directorio: str
    comando: list[str]
    comando_texto: str
    obligatoria: bool
    bloquea_cierre: bool
    timeout_segundos: int
    origen: OrigenVerificacion
    estado: EstadoVerificacion
    codigo_salida: Optional[int]
    duracion_segundos: float
    evidencia: str


VERSION_CONTRATO_SOPORTADA = 1
NOMBRE_CONTRATO = "contrato_validacion.json"
MAXIMO_BYTES_CONTRATO = 1024 * 1024
LIMITE_EVIDENCIA = 4000
TIPOS_VERIFICACION: frozenset[str] = frozenset(
    {
        "unitarias",
        "integracion",
        "e2e",
        "tipos",
        "lint",
        "build",
        "migraciones",
        "schema",
        "contrato",
    }
)
EJECUTABLES_PERMITIDOS: frozenset[str] = frozenset(
    {
        "alembic",
        "cargo",
        "dart",
        "flutter",
        "go",
        "mypy",
        "node",
        "npm",
        "npx",
        "pnpm",
        "poetry",
        "pytest",
        "python",
        "python3",
        "ruff",
        "uv",
        "yarn",
    }
)
CLAVES_CONTRATO = frozenset(
    {"version_contrato", "modulos", "documentos_obligatorios", "criterios_bloqueo"}
)
CLAVES_MODULO = frozenset({"nombre", "directorio", "verificaciones"})
CLAVES_VERIFICACION = frozenset(
    {
        "identificador",
        "tipo",
        "comando",
        "obligatoria",
        "bloquea_cierre",
        "timeout_segundos",
    }
)
ESTADOS_BLOQUEABLES: frozenset[str] = frozenset(
    {"FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"}
)
OPERADORES_SHELL: frozenset[str] = frozenset(
    {"&&", "||", ";", "|", ">", ">>", "<", "2>", "2>>"}
)


def cargar_json_sin_duplicados(contenido: str, nombre: str) -> object:
    """Carga JSON y rechaza claves repetidas en cualquier nivel."""
    def construir(pares: list[tuple[str, object]]) -> dict[str, object]:
        resultado: dict[str, object] = {}
        for clave, valor in pares:
            if clave in resultado:
                raise ValueError(f"{nombre} contiene una clave duplicada: {clave}")
            resultado[clave] = valor
        return resultado

    return cast(object, json.loads(contenido, object_pairs_hook=construir))


def exigir_objeto(valor: object, nombre: str) -> dict[str, object]:
    """Exige un objeto JSON."""
    if not isinstance(valor, dict):
        raise ValueError(f"{nombre} debe ser un objeto JSON")
    return cast(dict[str, object], valor)


def exigir_lista(valor: object, nombre: str) -> list[object]:
    """Exige una lista JSON."""
    if not isinstance(valor, list):
        raise ValueError(f"{nombre} debe ser una lista")
    return cast(list[object], valor)


def exigir_lista_cadenas(valor: object, nombre: str) -> list[str]:
    """Exige una lista de cadenas no vacias."""
    elementos = exigir_lista(valor, nombre)
    if not all(isinstance(item, str) and item.strip() for item in elementos):
        raise ValueError(f"{nombre} debe contener cadenas no vacias")
    return cast(list[str], elementos)


def exigir_claves(datos: dict[str, object], esperadas: frozenset[str], nombre: str) -> None:
    """Rechaza campos desconocidos y campos requeridos ausentes."""
    faltantes = sorted(esperadas - set(datos))
    desconocidas = sorted(set(datos) - esperadas)
    if faltantes:
        raise ValueError(f"{nombre} no declara: {', '.join(faltantes)}")
    if desconocidas:
        raise ValueError(f"{nombre} contiene campos desconocidos: {', '.join(desconocidas)}")


def validar_ruta_relativa(texto: str, nombre: str) -> str:
    """Valida una ruta POSIX relativa sin segmentos ambiguos."""
    ruta = PurePosixPath(texto)
    if (
        not texto
        or "\\" in texto
        or ruta.is_absolute()
        or ".." in ruta.parts
        or "." in ruta.parts
    ):
        raise ValueError(f"{nombre} contiene una ruta insegura: {texto}")
    return ruta.as_posix()


def resolver_directorio(raiz: Path, relativa: str) -> Path:
    """Resuelve y confina un directorio declarado al proyecto."""
    ruta_relativa = Path() if relativa == "." else Path(validar_ruta_relativa(relativa, "directorio"))
    resuelta = (raiz / ruta_relativa).resolve()
    try:
        resuelta.relative_to(raiz)
    except ValueError as error:
        raise ValueError(f"El directorio sale del proyecto: {relativa}") from error
    if not resuelta.is_dir():
        raise ValueError(f"El directorio declarado no existe: {relativa}")
    return resuelta


def validar_comando(comando: list[str], nombre: str) -> list[str]:
    """Rechaza comandos vacios, ejecutables desconocidos y sintaxis de shell."""
    if not comando or not all(isinstance(parte, str) and parte.strip() for parte in comando):
        raise ValueError(f"{nombre}.comando debe contener argumentos no vacios")
    ejecutable = Path(comando[0]).name.casefold()
    if ejecutable.endswith(".exe") or ejecutable.endswith(".cmd"):
        ejecutable = Path(ejecutable).stem
    if ejecutable not in EJECUTABLES_PERMITIDOS:
        raise ValueError(f"{nombre} usa un ejecutable desconocido: {comando[0]}")
    if any(parte in OPERADORES_SHELL for parte in comando):
        raise ValueError(f"{nombre} no admite operadores de shell")
    return comando


def cargar_contrato(ruta: Path, raiz: Path) -> ContratoValidacion:
    """Carga y valida por completo un contrato de validacion."""
    informacion = ruta.stat()
    if not stat.S_ISREG(informacion.st_mode) or informacion.st_size > MAXIMO_BYTES_CONTRATO:
        raise ValueError("El contrato debe ser regular y no superar 1 MiB")
    datos = exigir_objeto(
        cargar_json_sin_duplicados(ruta.read_text(encoding="utf-8"), str(ruta)),
        "contrato",
    )
    exigir_claves(datos, CLAVES_CONTRATO, "contrato")
    if datos.get("version_contrato") != VERSION_CONTRATO_SOPORTADA:
        raise ValueError(
            f"version_contrato no soportada: {datos.get('version_contrato')}"
        )

    raiz_resuelta = raiz.resolve()
    modulos: list[ModuloContrato] = []
    identificadores: set[str] = set()
    comandos_vistos: set[tuple[str, tuple[str, ...]]] = set()
    nombres_modulos: set[str] = set()
    for indice_modulo, valor_modulo in enumerate(exigir_lista(datos.get("modulos"), "modulos")):
        modulo = exigir_objeto(valor_modulo, f"modulos[{indice_modulo}]")
        exigir_claves(modulo, CLAVES_MODULO, f"modulos[{indice_modulo}]")
        nombre = modulo.get("nombre")
        directorio = modulo.get("directorio")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError(f"modulos[{indice_modulo}].nombre debe ser una cadena no vacia")
        if nombre in nombres_modulos:
            raise ValueError(f"Nombre de modulo duplicado: {nombre}")
        nombres_modulos.add(nombre)
        if not isinstance(directorio, str):
            raise ValueError(f"modulos[{indice_modulo}].directorio debe ser una cadena")
        resolver_directorio(raiz_resuelta, directorio)
        verificaciones: list[VerificacionContrato] = []
        for indice_verificacion, valor_verificacion in enumerate(
            exigir_lista(modulo.get("verificaciones"), f"modulos[{indice_modulo}].verificaciones")
        ):
            etiqueta = f"modulos[{indice_modulo}].verificaciones[{indice_verificacion}]"
            verificacion = exigir_objeto(valor_verificacion, etiqueta)
            exigir_claves(verificacion, CLAVES_VERIFICACION, etiqueta)
            identificador = verificacion.get("identificador")
            tipo = verificacion.get("tipo")
            comando_crudo = exigir_lista_cadenas(verificacion.get("comando"), f"{etiqueta}.comando")
            comando = validar_comando(comando_crudo, etiqueta)
            obligatoria = verificacion.get("obligatoria")
            bloquea = verificacion.get("bloquea_cierre")
            timeout = verificacion.get("timeout_segundos")
            if not isinstance(identificador, str) or not identificador.strip():
                raise ValueError(f"{etiqueta}.identificador debe ser una cadena no vacia")
            if identificador in identificadores:
                raise ValueError(f"Identificador de verificacion duplicado: {identificador}")
            identificadores.add(identificador)
            if not isinstance(tipo, str) or tipo not in TIPOS_VERIFICACION:
                raise ValueError(f"{etiqueta}.tipo es desconocido: {tipo}")
            if not isinstance(obligatoria, bool) or not isinstance(bloquea, bool):
                raise ValueError(f"{etiqueta} debe declarar booleanos de obligatoriedad y bloqueo")
            if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 3600:
                raise ValueError(f"{etiqueta}.timeout_segundos debe estar entre 1 y 3600")
            clave_comando = (directorio, tuple(comando))
            if clave_comando in comandos_vistos:
                raise ValueError(f"Comando duplicado en el contrato: {' '.join(comando)}")
            comandos_vistos.add(clave_comando)
            verificaciones.append(
                VerificacionContrato(
                    identificador=identificador,
                    tipo=tipo,
                    comando=comando,
                    obligatoria=obligatoria,
                    bloquea_cierre=bloquea,
                    timeout_segundos=timeout,
                )
            )
        if not verificaciones:
            raise ValueError(f"El modulo {nombre} no declara verificaciones")
        modulos.append(
            ModuloContrato(nombre=nombre, directorio=directorio, verificaciones=verificaciones)
        )

    if not modulos:
        raise ValueError("El contrato debe declarar al menos un modulo con verificaciones")
    documentos = exigir_lista_cadenas(datos.get("documentos_obligatorios"), "documentos_obligatorios")
    if len(documentos) != len(set(documentos)):
        raise ValueError("documentos_obligatorios contiene rutas duplicadas")
    documentos = [validar_ruta_relativa(ruta, "documentos_obligatorios") for ruta in documentos]
    criterios_crudos = exigir_lista_cadenas(datos.get("criterios_bloqueo"), "criterios_bloqueo")
    if len(criterios_crudos) != len(set(criterios_crudos)):
        raise ValueError("criterios_bloqueo contiene estados duplicados")
    if not set(criterios_crudos).issubset(ESTADOS_BLOQUEABLES):
        raise ValueError("criterios_bloqueo contiene un estado desconocido")
    if not {"FALLIDO", "NO_DISPONIBLE"}.issubset(set(criterios_crudos)):
        raise ValueError("FALLIDO y NO_DISPONIBLE siempre deben bloquear el cierre")
    criterios = cast(list[EstadoVerificacion], criterios_crudos)
    return ContratoValidacion(
        version_contrato=VERSION_CONTRATO_SOPORTADA,
        modulos=modulos,
        documentos_obligatorios=documentos,
        criterios_bloqueo=criterios,
    )


def comprobaciones_contrato(contrato: ContratoValidacion) -> list[Comprobacion]:
    """Aplana los modulos de un contrato validado."""
    return [
        Comprobacion(
            identificador=verificacion["identificador"],
            tipo=verificacion["tipo"],
            modulo=modulo["nombre"],
            directorio=modulo["directorio"],
            comando=verificacion["comando"],
            obligatoria=verificacion["obligatoria"],
            bloquea_cierre=verificacion["bloquea_cierre"],
            timeout_segundos=verificacion["timeout_segundos"],
            origen="DECLARADO",
        )
        for modulo in contrato["modulos"]
        for verificacion in modulo["verificaciones"]
    ]


def resolver_ejecutable(comando: list[str]) -> list[str] | None:
    """Resuelve ejecutables portables sin delegar interpretacion a un shell."""
    nombre = Path(comando[0]).name.casefold()
    if nombre in {"python", "python3", "python.exe", "python3.exe"}:
        return [sys.executable, *comando[1:]]
    candidatos = [comando[0]]
    if os.name == "nt" and not comando[0].lower().endswith((".exe", ".cmd", ".bat")):
        candidatos = [f"{comando[0]}.cmd", f"{comando[0]}.exe", comando[0]]
    for candidato in candidatos:
        ruta = shutil.which(candidato)
        if ruta:
            return [ruta, *comando[1:]]
    return None


def comando_texto(comando: list[str]) -> str:
    """Representa un argv sin reconstruir sintaxis ejecutable de shell."""
    return subprocess.list2cmdline(comando)


def ejecutar_comprobacion(raiz: Path, comprobacion: Comprobacion) -> ResultadoVerificacion:
    """Ejecuta una comprobacion y conserva codigo, duracion y evidencia acotada."""
    directorio = resolver_directorio(raiz.resolve(), comprobacion["directorio"])
    ejecutable = resolver_ejecutable(comprobacion["comando"])
    if ejecutable is None:
        return ResultadoVerificacion(
            **comprobacion,
            comando_texto=comando_texto(comprobacion["comando"]),
            estado="NO_DISPONIBLE",
            codigo_salida=None,
            duracion_segundos=0.0,
            evidencia=f"No se encontro el ejecutable: {comprobacion['comando'][0]}",
        )
    inicio = time.monotonic()
    try:
        resultado = subprocess.run(
            ejecutable,
            cwd=directorio,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=comprobacion["timeout_segundos"],
        )
    except subprocess.TimeoutExpired as error:
        duracion = round(time.monotonic() - inicio, 3)
        salida = "".join(
            parte.decode("utf-8", errors="replace") if isinstance(parte, bytes) else parte or ""
            for parte in (error.stdout, error.stderr)
        )
        return ResultadoVerificacion(
            **comprobacion,
            comando_texto=comando_texto(comprobacion["comando"]),
            estado="FALLIDO",
            codigo_salida=124,
            duracion_segundos=duracion,
            evidencia=(salida + "\nTimeout de validacion").strip()[-LIMITE_EVIDENCIA:],
        )
    duracion = round(time.monotonic() - inicio, 3)
    salida = (resultado.stdout + resultado.stderr).strip()
    estado: EstadoVerificacion = "APROBADO" if resultado.returncode == 0 else "FALLIDO"
    if resultado.returncode != 0 and (
        "No module named" in salida or "command not found" in salida.casefold()
    ):
        estado = "NO_DISPONIBLE"
    return ResultadoVerificacion(
        **comprobacion,
        comando_texto=comando_texto(comprobacion["comando"]),
        estado=estado,
        codigo_salida=resultado.returncode,
        duracion_segundos=duracion,
        evidencia=salida[-LIMITE_EVIDENCIA:],
    )


def resultado_no_ejecutado(
    identificador: str,
    modulo: str,
    directorio: str,
    origen: OrigenVerificacion,
    evidencia: str,
    obligatoria: bool = False,
) -> ResultadoVerificacion:
    """Construye una evidencia explicita para ausencia de cobertura ejecutable."""
    return ResultadoVerificacion(
        identificador=identificador,
        tipo="contrato",
        modulo=modulo,
        directorio=directorio,
        comando=[],
        comando_texto="",
        obligatoria=obligatoria,
        bloquea_cierre=obligatoria,
        timeout_segundos=1,
        origen=origen,
        estado="NO_EJECUTADO",
        codigo_salida=None,
        duracion_segundos=0.0,
        evidencia=evidencia,
    )


def bloquea_resultado(
    resultado: ResultadoVerificacion,
    criterios: list[EstadoVerificacion],
) -> bool:
    """Decide el bloqueo usando datos del contrato y no una explicacion textual."""
    return (
        resultado["estado"] in criterios
        and (resultado["obligatoria"] or resultado["bloquea_cierre"])
    )
