#!/usr/bin/env python3
"""Inicializa una copia de la plantilla mediante su contrato declarado."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import TypedDict, cast


class CampoPlaceholder(TypedDict):
    """Representa la configuracion de un placeholder."""

    obligatorio: bool
    origen: str
    descripcion: str


class ContratoPlantilla(TypedDict):
    """Representa el contrato necesario para inicializar la plantilla."""

    version_contrato: int
    version_framework: str
    sintaxis_placeholder: str
    rutas_excluidas: list[str]
    archivos_incluidos: list[str]
    archivos_gestionados: list[str]
    placeholders: dict[str, CampoPlaceholder]


PATRON_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
PATRON_NOMBRE_SKILL = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
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
ATRIBUTO_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
MAXIMO_ENTRADAS_ARBOL = 20_000
MAXIMO_BYTES_TOTALES = 100 * 1024 * 1024
MAXIMO_BYTES_ARCHIVO = 20 * 1024 * 1024
NOMBRES_ARTEFACTOS_GENERADOS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "node_modules",
        ".next",
        ".dart_tool",
        "build",
        "coverage",
        "htmlcov",
        ".DS_Store",
        "Thumbs.db",
    }
)
SUFIJOS_ARTEFACTOS_GENERADOS: tuple[str, ...] = (".pyc", ".pyo")
MAXIMO_BYTES_JSON = 1024 * 1024
MAXIMO_CARACTERES_VALOR = 100_000
def calcular_huellas_gestionadas(
    raiz: Path,
    rutas_gestionadas: list[str],
) -> dict[str, str]:
    """Registra Skills y scripts que futuras actualizaciones pueden reemplazar."""
    archivos: set[Path] = set()
    raiz_skills = raiz / ".agents" / "skills"
    archivos.update(archivo for archivo in raiz_skills.rglob("*") if archivo.is_file())
    for relativa in rutas_gestionadas:
        ruta = raiz / Path(relativa)
        if ruta.is_file():
            archivos.add(ruta)
    return {
        archivo.relative_to(raiz).as_posix(): hashlib.sha256(archivo.read_bytes()).hexdigest()
        for archivo in sorted(archivos, key=lambda ruta: ruta.relative_to(raiz).as_posix())
    }
TIEMPO_MAXIMO_GIT_SEGUNDOS = 30
MARCADORES_OPERACION_GIT: tuple[str, ...] = (
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "REBASE_HEAD",
    "rebase-merge",
    "rebase-apply",
    "BISECT_LOG",
)
VALORES_PREDETERMINADOS: dict[str, str] = {
    "ESTADO_BREVE": "Inicializando",
    "FASE_ACTIVA": "Fase 0 — Setup",
    "LISTA_DESEABLES": "- Sin elementos deseables definidos.",
    "HARDWARE_O_INFRA": "- Sin hardware o infraestructura confirmada.",
    "LISTA_DECISIONES_NUMERADA": "1. Sin decisiones tecnicas adicionales.",
    "HISTORIAL_IMPLEMENTACION": "- Sin modulos implementados todavia.",
    "LISTA_TECNOLOGIAS": "- Pendiente de definicion.",
    "BLOQUEOS": "- Sin bloqueos conocidos.",
    "EXCEPCIONES_ADICIONALES": "- Sin excepciones adicionales.",
}


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


def configurar_salida_utf8() -> None:
    """Configura UTF-8 cuando la terminal permite cambiar su codificacion."""
    reconfigurar = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigurar):
        reconfigurar(encoding="utf-8")


def exigir_diccionario(valor: object, nombre: str) -> dict[str, object]:
    """Verifica que un valor sea un objeto JSON."""
    if not isinstance(valor, dict):
        raise ValueError(f"{nombre} debe ser un objeto JSON")
    return cast(dict[str, object], valor)


def exigir_lista_cadenas(valor: object, nombre: str) -> list[str]:
    """Verifica que un valor sea una lista de cadenas."""
    if not isinstance(valor, list) or not all(isinstance(item, str) for item in valor):
        raise ValueError(f"{nombre} debe ser una lista de cadenas")
    return cast(list[str], valor)


def esta_dentro(ruta: Path, posible_contenedor: Path) -> bool:
    """Determina si una ruta resuelta permanece dentro de otra."""
    try:
        ruta.relative_to(posible_contenedor)
    except ValueError:
        return False
    return True


def es_enlace_o_reparse(ruta: Path) -> bool:
    """Detecta enlaces simbolicos y puntos de reanalisis sin seguirlos."""
    informacion = ruta.lstat()
    atributos = getattr(informacion, "st_file_attributes", 0)
    return stat.S_ISLNK(informacion.st_mode) or bool(atributos & ATRIBUTO_REPARSE_POINT)


def validar_arbol_sin_enlaces(
    raiz: Path,
    rutas_omitidas: frozenset[str] = frozenset(),
) -> None:
    """Rechaza redirecciones y montajes que saquen contenido de la copia."""
    if es_enlace_o_reparse(raiz):
        raise ValueError("La raiz de la copia no puede ser un enlace o reparse point")
    raiz_resuelta = raiz.resolve(strict=True)
    informacion_raiz = raiz_resuelta.lstat()
    dispositivo_raiz = informacion_raiz.st_dev
    entradas_contadas = 0
    bytes_contados = 0

    def recorrer(directorio: Path) -> None:
        nonlocal entradas_contadas, bytes_contados
        with os.scandir(directorio) as entradas:
            for entrada in entradas:
                ruta = Path(entrada.path)
                relativa = ruta.relative_to(raiz_resuelta).as_posix()
                entradas_contadas += 1
                if entradas_contadas > MAXIMO_ENTRADAS_ARBOL:
                    raise ValueError(f"La copia supera el maximo de {MAXIMO_ENTRADAS_ARBOL} entradas")
                if entrada.name in NOMBRES_ARTEFACTOS_GENERADOS or entrada.name.endswith(
                    SUFIJOS_ARTEFACTOS_GENERADOS
                ):
                    raise ValueError(f"La copia contiene un artefacto generado no permitido: {relativa}")
                if es_enlace_o_reparse(ruta):
                    raise ValueError(f"La copia contiene un enlace o reparse point no permitido: {relativa}")
                informacion = ruta.lstat()
                if stat.S_ISREG(informacion.st_mode) and informacion.st_mode & (
                    stat.S_ISUID | stat.S_ISGID
                ):
                    raise ValueError(f"La copia contiene permisos especiales no permitidos: {relativa}")
                if informacion.st_dev != dispositivo_raiz:
                    raise ValueError(f"La copia cruza a otro sistema de archivos: {relativa}")
                ruta_resuelta = ruta.resolve(strict=True)
                if not esta_dentro(ruta_resuelta, raiz_resuelta):
                    raise ValueError(f"La copia contiene una ruta fuera de su raiz: {relativa}")
                if stat.S_ISREG(informacion.st_mode):
                    if informacion.st_size > MAXIMO_BYTES_ARCHIVO:
                        raise ValueError(
                            f"La copia contiene un archivo mayor a {MAXIMO_BYTES_ARCHIVO} bytes: {relativa}"
                        )
                    bytes_contados += informacion.st_size
                    if bytes_contados > MAXIMO_BYTES_TOTALES:
                        raise ValueError(
                            f"La copia supera el maximo total de {MAXIMO_BYTES_TOTALES} bytes"
                        )
                elif not stat.S_ISDIR(informacion.st_mode):
                    raise ValueError(f"La copia contiene un archivo especial no permitido: {relativa}")
                if stat.S_ISDIR(informacion.st_mode) and relativa not in rutas_omitidas:
                    recorrer(ruta)

    recorrer(raiz_resuelta)


def validar_permisos_inicializacion(raiz: Path, centinela: Path, archivos: list[Path]) -> None:
    """Comprueba que los artefactos administrados permitan escritura del propietario."""
    objetivos: set[Path] = {raiz, centinela, *archivos}
    for archivo in archivos:
        actual = archivo.parent
        while esta_dentro(actual, raiz) and actual != raiz:
            objetivos.add(actual)
            actual = actual.parent
    for objetivo in sorted(objetivos):
        modo = stat.S_IMODE(objetivo.lstat().st_mode)
        if not modo & stat.S_IWUSR:
            raise ValueError(
                f"La copia no permite escritura del propietario: {objetivo.relative_to(raiz)}"
            )


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


def cargar_contrato(ruta: Path) -> ContratoPlantilla:
    """Carga el contrato y valida su estructura minima."""
    contenido = cargar_json_sin_duplicados(leer_json_limitado(ruta, "contrato"), str(ruta))
    datos = exigir_diccionario(contenido, "contrato")
    exigir_claves_exactas(datos, CLAVES_CONTRATO, "contrato")
    version_contrato = datos.get("version_contrato")
    version_framework = datos.get("version_framework")
    sintaxis = datos.get("sintaxis_placeholder")
    if version_contrato != VERSION_CONTRATO_SOPORTADA:
        raise ValueError(
            f"version_contrato no soportada: {version_contrato}. "
            f"Se esperaba {VERSION_CONTRATO_SOPORTADA}"
        )
    if not isinstance(version_framework, str) or PATRON_VERSION_FRAMEWORK.fullmatch(version_framework) is None:
        raise ValueError("version_framework debe usar una version semantica valida")
    if sintaxis != SINTAXIS_PLACEHOLDER_SOPORTADA:
        raise ValueError(
            f"sintaxis_placeholder no soportada: {sintaxis}. "
            f"Se esperaba {SINTAXIS_PLACEHOLDER_SOPORTADA}"
        )

    campos_crudos = exigir_diccionario(datos.get("placeholders"), "placeholders")
    campos: dict[str, CampoPlaceholder] = {}
    for clave, valor in campos_crudos.items():
        if PATRON_PLACEHOLDER.fullmatch(f"{{{{{clave}}}}}") is None:
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
        campos[clave] = CampoPlaceholder(obligatorio=obligatorio, origen=origen, descripcion=descripcion)

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
        any(caracter in relativa for caracter in "*?[]")
        for relativa in archivos_gestionados
    ):
        raise ValueError("archivos_gestionados solo admite rutas exactas")
    faltantes_gestionados = [
        relativa
        for relativa in archivos_gestionados
        if not (ruta.parent / Path(relativa)).is_file()
    ]
    if faltantes_gestionados:
        raise ValueError(
            "archivos_gestionados contiene rutas inexistentes: "
            + ", ".join(faltantes_gestionados)
        )
    return ContratoPlantilla(
        version_contrato=version_contrato,
        version_framework=version_framework,
        sintaxis_placeholder=sintaxis,
        rutas_excluidas=rutas_excluidas,
        archivos_incluidos=archivos_incluidos,
        archivos_gestionados=archivos_gestionados,
        placeholders=campos,
    )


def validar_caracteres_configuracion(valor: str, clave: str) -> str:
    """Normaliza saltos y rechaza controles capaces de alterar artefactos."""
    normalizado = valor.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(normalizado) > MAXIMO_CARACTERES_VALOR:
        raise ValueError(
            f"El valor de {clave} supera el maximo de {MAXIMO_CARACTERES_VALOR} caracteres"
        )
    controles = [
        caracter
        for caracter in normalizado
        if unicodedata.category(caracter).startswith("C") and caracter not in {"\n", "\t"}
    ]
    if controles:
        raise ValueError(f"El valor de {clave} contiene caracteres de control no permitidos")
    return normalizado


def normalizar_valor(valor: object, clave: str) -> str:
    """Convierte un valor de configuracion a texto reproducible."""
    if isinstance(valor, str):
        return validar_caracteres_configuracion(valor, clave)
    if isinstance(valor, list) and all(isinstance(item, str) for item in valor):
        elementos = cast(list[str], valor)
        normalizados = [validar_caracteres_configuracion(elemento, clave) for elemento in elementos]
        if any("\n" in elemento for elemento in normalizados):
            raise ValueError(f"La lista de {clave} debe contener elementos de una sola linea")
        combinado = "\n".join(f"- {elemento}" for elemento in normalizados if elemento)
        return validar_caracteres_configuracion(combinado, clave)
    raise ValueError(f"El valor de {clave} debe ser una cadena o una lista de cadenas")


def cargar_valores(ruta: Path | None) -> dict[str, str]:
    """Carga valores de proyecto desde un archivo JSON opcional."""
    if ruta is None:
        return {}
    contenido = cargar_json_sin_duplicados(
        leer_json_limitado(ruta, "configuracion de proyecto"),
        str(ruta),
    )
    datos = exigir_diccionario(contenido, "configuracion de proyecto")
    return {clave: normalizar_valor(valor, clave) for clave, valor in datos.items()}


def analizar_valores_directos(valores: list[str]) -> dict[str, str]:
    """Interpreta argumentos repetibles con formato CLAVE=VALOR."""
    resultado: dict[str, str] = {}
    for expresion in valores:
        if "=" not in expresion:
            raise ValueError(f"Valor invalido, se esperaba CLAVE=VALOR: {expresion}")
        clave, valor = expresion.split("=", 1)
        clave_limpia = clave.strip()
        if not clave_limpia or not valor.strip():
            raise ValueError(f"Valor invalido, se esperaba CLAVE=VALOR: {expresion}")
        if "`n" in valor or "`r" in valor:
            raise ValueError(
                f"--valor contiene una secuencia literal de PowerShell para {clave_limpia}; "
                "usar --configuracion con JSON para texto multilinea"
            )
        if clave_limpia in resultado:
            raise ValueError(f"--valor repite la clave: {clave_limpia}")
        resultado[clave_limpia] = validar_caracteres_configuracion(valor, clave_limpia)
    return resultado


def combinar_valores_usuario(
    contrato: ContratoPlantilla,
    configuracion: dict[str, str],
    nombre_proyecto: str | None,
    idioma_nombres: str | None,
    valores_directos: dict[str, str],
) -> dict[str, str]:
    """Combina entradas sin permitir precedencias silenciosas ni derivados externos."""
    fuentes: list[tuple[str, dict[str, str]]] = [("configuracion JSON", configuracion)]
    if nombre_proyecto is not None:
        fuentes.append(("argumento nombre_proyecto", {"NOMBRE_PROYECTO": nombre_proyecto}))
    if idioma_nombres is not None:
        fuentes.append(("argumento idioma_nombres", {"IDIOMA_NOMBRES": idioma_nombres}))
    fuentes.append(("argumentos --valor", valores_directos))

    resultado: dict[str, str] = {}
    origen_por_clave: dict[str, str] = {}
    for fuente, valores in fuentes:
        for clave, valor in valores.items():
            if clave in resultado:
                raise ValueError(
                    f"{clave} se definio mas de una vez: {origen_por_clave[clave]} y {fuente}"
                )
            resultado[clave] = validar_caracteres_configuracion(valor, clave)
            origen_por_clave[clave] = fuente

    desconocidas = sorted(set(resultado) - set(contrato["placeholders"]))
    if desconocidas:
        raise ValueError(f"Placeholders no declarados en la configuracion: {', '.join(desconocidas)}")
    derivadas = sorted(
        clave
        for clave in resultado
        if contrato["placeholders"][clave]["origen"] == "derivado"
    )
    if derivadas:
        raise ValueError(
            "Los valores derivados no se aceptan desde configuracion o CLI: "
            + ", ".join(derivadas)
        )
    return resultado


def crear_prefijo_variables(nombre_proyecto: str) -> str:
    """Deriva un prefijo portable para variables de entorno."""
    normalizado = unicodedata.normalize("NFKD", nombre_proyecto)
    sin_acentos = "".join(caracter for caracter in normalizado if not unicodedata.combining(caracter))
    prefijo = re.sub(r"[^A-Z0-9]+", "_", sin_acentos.upper()).strip("_")
    if not prefijo:
        raise ValueError("NOMBRE_PROYECTO no produce un prefijo de variables valido")
    if prefijo[0].isdigit():
        prefijo = f"PROYECTO_{prefijo}"
    return prefijo


def validar_texto_una_linea(valor: str, clave: str, longitud_maxima: int) -> str:
    """Valida un texto breve que se inserta en encabezados o configuracion."""
    limpio = valor.strip()
    if not limpio:
        raise ValueError(f"{clave} no puede estar vacio")
    if len(limpio) > longitud_maxima:
        raise ValueError(f"{clave} supera el maximo de {longitud_maxima} caracteres")
    controles = [caracter for caracter in limpio if unicodedata.category(caracter).startswith("C")]
    if controles:
        raise ValueError(f"{clave} contiene caracteres de control no permitidos")
    return limpio


def completar_valores(
    contrato: ContratoPlantilla,
    valores: dict[str, str],
    permitir_pendientes: bool,
) -> tuple[dict[str, str], list[str]]:
    """Completa derivados y predeterminados, y controla datos faltantes."""
    desconocidos = sorted(set(valores) - set(contrato["placeholders"]))
    if desconocidos:
        raise ValueError(f"Placeholders no declarados en la configuracion: {', '.join(desconocidos)}")

    resultado = dict(VALORES_PREDETERMINADOS)
    resultado.update(valores)
    nombre = validar_texto_una_linea(resultado.get("NOMBRE_PROYECTO", ""), "NOMBRE_PROYECTO", 120)
    resultado["NOMBRE_PROYECTO"] = nombre
    idioma = validar_texto_una_linea(
        resultado.get("IDIOMA_NOMBRES", "español"),
        "IDIOMA_NOMBRES",
        40,
    )
    resultado["IDIOMA_NOMBRES"] = idioma
    resultado["NOMBRE_PROYECTO_ENV"] = json.dumps(nombre, ensure_ascii=False)
    resultado["PREFIJO_VARIABLES"] = crear_prefijo_variables(nombre)
    resultado["IDENTIFICADOR_PROYECTO"] = resultado["PREFIJO_VARIABLES"].lower()
    resultado["FECHA"] = datetime.now().astimezone().date().isoformat()

    pendientes: list[str] = []
    for clave, campo in contrato["placeholders"].items():
        if resultado.get(clave, "").strip():
            continue
        if campo["obligatorio"] and not permitir_pendientes:
            pendientes.append(clave)
            continue
        resultado[clave] = f"<!-- TODO: {clave} — completar cuando se defina -->"

    if pendientes:
        raise ValueError(
            "Faltan valores obligatorios: "
            + ", ".join(sorted(pendientes))
            + ". Se puede usar --permitir-pendientes para marcarlos como TODO."
        )
    return resultado, sorted(clave for clave, valor in resultado.items() if valor.startswith("<!-- TODO:"))


def resolver_archivos(raiz: Path, patrones: list[str]) -> list[Path]:
    """Resuelve todos los archivos declarados por el contrato."""
    archivos: set[Path] = set()
    for patron in patrones:
        coincidencias = [ruta for ruta in raiz.glob(patron) if ruta.is_file()]
        if not coincidencias:
            raise ValueError(f"El patron del contrato no encontro archivos: {patron}")
        archivos.update(coincidencias)
    return sorted(archivos)


def preparar_cambios(archivos: list[Path], valores: dict[str, str]) -> dict[Path, str]:
    """Prepara todas las sustituciones antes de escribir un archivo."""
    cambios: dict[Path, str] = {}
    for archivo in archivos:
        contenido = archivo.read_text(encoding="utf-8")
        claves_encontradas = set(PATRON_PLACEHOLDER.findall(contenido))
        faltantes = claves_encontradas - set(valores)
        if faltantes:
            raise ValueError(f"{archivo} contiene placeholders sin valor: {', '.join(sorted(faltantes))}")
        contenido_nuevo = PATRON_PLACEHOLDER.sub(lambda coincidencia: valores[coincidencia.group(1)], contenido)
        reintroducidos = sorted(set(PATRON_PLACEHOLDER.findall(contenido_nuevo)))
        if reintroducidos:
            raise ValueError(
                f"Un valor reintroduce placeholders en {archivo}: {', '.join(reintroducidos)}"
            )
        if contenido_nuevo != contenido:
            cambios[archivo] = contenido_nuevo
    return cambios


def escribir_texto_lf(ruta: Path, contenido: str) -> None:
    """Escribe texto UTF-8 con saltos LF en versiones soportadas de Python."""
    with ruta.open("w", encoding="utf-8", newline="\n") as flujo:
        flujo.write(contenido)


def escribir_cambios(cambios: dict[Path, str], raiz: Path) -> None:
    """Escribe cambios con respaldo temporal y restaura ante un fallo."""
    with tempfile.TemporaryDirectory(prefix="respaldo-inicializacion-") as directorio_temporal:
        respaldo = Path(directorio_temporal)
        temporales: list[Path] = []
        for archivo in cambios:
            destino_respaldo = respaldo / archivo.relative_to(raiz)
            destino_respaldo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo, destino_respaldo)
        try:
            for archivo, contenido in cambios.items():
                temporal = archivo.with_name(f".{archivo.name}.temporal")
                temporales.append(temporal)
                escribir_texto_lf(temporal, contenido)
                os.replace(temporal, archivo)
        except OSError:
            for archivo in cambios:
                origen_respaldo = respaldo / archivo.relative_to(raiz)
                if origen_respaldo.exists():
                    shutil.copy2(origen_respaldo, archivo)
            raise
        finally:
            for temporal in temporales:
                if temporal.exists():
                    temporal.unlink()


def ejecutar_git(argumentos: list[str], raiz: Path, comprobar: bool = True) -> subprocess.CompletedProcess[str]:
    """Ejecuta Git sin utilizar un shell intermedio."""
    return subprocess.run(
        ["git", *argumentos],
        cwd=raiz,
        check=comprobar,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIEMPO_MAXIMO_GIT_SEGUNDOS,
    )


def verificar_git(raiz: Path) -> None:
    """Inicializa Git o valida un repositorio preexistente sin operaciones activas."""
    directorio_git = raiz / ".git"
    if not directorio_git.exists():
        ejecutar_git(["init"], raiz)
        return

    repositorio = ejecutar_git(["rev-parse", "--is-inside-work-tree"], raiz, comprobar=False)
    if repositorio.returncode != 0 or repositorio.stdout.strip() != "true":
        raise ValueError(".git no describe un repositorio de trabajo valido")

    for marcador in MARCADORES_OPERACION_GIT:
        resultado_ruta = ejecutar_git(["rev-parse", "--git-path", marcador], raiz, comprobar=False)
        if resultado_ruta.returncode != 0 or not resultado_ruta.stdout.strip():
            raise ValueError("Git no pudo comprobar las operaciones activas del repositorio")
        ruta_marcador = Path(resultado_ruta.stdout.strip())
        if not ruta_marcador.is_absolute():
            ruta_marcador = raiz / ruta_marcador
        if ruta_marcador.exists():
            raise ValueError(f"El repositorio contiene una operacion Git activa: {marcador}")

    estado = ejecutar_git(
        ["status", "--porcelain=v1", "--untracked-files=no"],
        raiz,
        comprobar=False,
    )
    if estado.returncode != 0:
        raise ValueError("Git no pudo comprobar el estado del repositorio")
    if estado.stdout.strip():
        raise ValueError("El repositorio contiene cambios rastreados sin confirmar")


def verificar_env_ignorado(raiz: Path) -> None:
    """Comprueba que Git ignore `.env` antes de crear el archivo."""
    resultado = ejecutar_git(["check-ignore", "--quiet", "--no-index", ".env"], raiz, comprobar=False)
    if resultado.returncode != 0:
        raise ValueError(".env no esta protegido por .gitignore")


def descubrir_nombres_skills(raiz: Path) -> list[str]:
    """Descubre los nombres declarados por las Skills instaladas."""
    nombres: set[str] = set()
    for manifiesto in sorted((raiz / ".agents" / "skills").rglob("SKILL.md")):
        contenido = manifiesto.read_text(encoding="utf-8")
        coincidencia = PATRON_NOMBRE_SKILL.search(contenido)
        if coincidencia is None:
            raise ValueError(f"La Skill no declara nombre: {manifiesto.relative_to(raiz)}")
        nombre = coincidencia.group(1).strip().strip("\"'")
        if nombre in nombres:
            raise ValueError(f"Nombre de Skill duplicado: {nombre}")
        nombres.add(nombre)
    return sorted(nombres)


def validar_skills_instaladas(raiz: Path, declaradas: list[str]) -> list[str]:
    """Verifica que la seleccion declarada coincida con los archivos presentes."""
    instaladas = descubrir_nombres_skills(raiz)
    nombres_declarados = [nombre.strip() for nombre in declaradas if nombre.strip()]
    if len(nombres_declarados) != len(set(nombres_declarados)):
        raise ValueError("La seleccion de Skills contiene nombres duplicados")
    if nombres_declarados and set(nombres_declarados) != set(instaladas):
        raise ValueError("La seleccion declarada de Skills no coincide con los archivos instalados")
    return instaladas


def eliminar_git_creado(raiz: Path) -> None:
    """Elimina exclusivamente el repositorio creado por la transaccion fallida."""
    raiz_resuelta = raiz.resolve()
    directorio_git = (raiz_resuelta / ".git").resolve()
    if directorio_git.parent != raiz_resuelta or directorio_git.name != ".git":
        raise ValueError("Se rechazo eliminar una ruta Git inesperada")
    if directorio_git.exists():
        shutil.rmtree(directorio_git)


def crear_directorios_controlados(raiz: Path, objetivos: tuple[str, ...]) -> list[Path]:
    """Crea directorios y registra cada ruta nueva para una posible reversion."""
    creados: list[Path] = []
    for objetivo in objetivos:
        actual = raiz
        for parte in Path(objetivo).parts:
            actual = actual / parte
            if not actual.exists():
                actual.mkdir()
                creados.append(actual)
    return creados


def aplicar_transaccion(
    raiz: Path,
    centinela: Path,
    cambios: dict[Path, str],
    estado_plantilla: dict[str, object],
    crear_env: bool,
) -> None:
    """Aplica la inicializacion completa y restaura la copia ante un fallo."""
    ruta_estado = raiz / ".estado-plantilla.json"
    temporal_estado = raiz / ".estado-plantilla.json.temporal"
    env_destino = raiz / ".env"
    if ruta_estado.exists() or temporal_estado.exists():
        raise ValueError("La copia contiene un estado de inicializacion previo o incompleto")

    git_existia = (raiz / ".git").exists()
    env_creado = False
    estado_creado = False
    directorios_creados: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="respaldo-transaccion-") as directorio_temporal:
        respaldo = Path(directorio_temporal)
        for archivo in (*cambios.keys(), centinela):
            destino_respaldo = respaldo / archivo.relative_to(raiz)
            destino_respaldo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo, destino_respaldo)
        try:
            verificar_git(raiz)
            verificar_env_ignorado(raiz)
            escribir_cambios(cambios, raiz)
            directorios_creados = crear_directorios_controlados(
                raiz,
                ("documentacion", "infraestructura/registros", "scripts"),
            )
            if crear_env and not env_destino.exists():
                shutil.copy2(raiz / ".env.ejemplo", env_destino)
                env_creado = True
            escribir_texto_lf(
                temporal_estado,
                json.dumps(estado_plantilla, ensure_ascii=False, indent=2) + "\n",
            )
            os.replace(temporal_estado, ruta_estado)
            estado_creado = True
            centinela.unlink()
        except (OSError, ValueError, subprocess.SubprocessError):
            for archivo in cambios:
                origen_respaldo = respaldo / archivo.relative_to(raiz)
                shutil.copy2(origen_respaldo, archivo)
            if not centinela.exists():
                shutil.copy2(respaldo / centinela.relative_to(raiz), centinela)
            if temporal_estado.exists():
                temporal_estado.unlink()
            if estado_creado and ruta_estado.exists():
                ruta_estado.unlink()
            if env_creado and env_destino.exists():
                env_destino.unlink()
            for directorio in reversed(directorios_creados):
                if directorio.exists():
                    directorio.rmdir()
            if not git_existia and (raiz / ".git").exists():
                eliminar_git_creado(raiz)
            raise


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz de linea de comandos."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("nombre_proyecto", nargs="?", help="Nombre del proyecto")
    analizador.add_argument("idioma_nombres", nargs="?", help="Idioma de nombres")
    analizador.add_argument("--configuracion", type=Path, help="Archivo JSON con valores por placeholder")
    analizador.add_argument("--valor", action="append", default=[], metavar="CLAVE=VALOR")
    analizador.add_argument(
        "--skill-seleccionada",
        action="append",
        default=[],
        metavar="NOMBRE",
        help="Skill ya instalada por el creador externo; se puede repetir",
    )
    analizador.add_argument("--permitir-pendientes", action="store_true")
    analizador.add_argument("--sin-env", action="store_true")
    return analizador.parse_args()


def main() -> int:
    """Ejecuta una inicializacion validada y reproducible."""
    configurar_salida_utf8()
    argumentos = crear_argumentos()
    raiz = Path(__file__).resolve().parent.parent
    centinela = raiz / ".plantilla-framework"

    try:
        if not centinela.exists():
            raise ValueError("Falta .plantilla-framework; la plantilla ya fue inicializada o no es una copia valida")
        validar_arbol_sin_enlaces(raiz, frozenset({".git"}))
        contrato = cargar_contrato(raiz / "configuracion_plantilla.json")
        skills_instaladas = validar_skills_instaladas(raiz, argumentos.skill_seleccionada)
        valores = combinar_valores_usuario(
            contrato,
            cargar_valores(argumentos.configuracion),
            argumentos.nombre_proyecto,
            argumentos.idioma_nombres,
            analizar_valores_directos(argumentos.valor),
        )
        valores["VERSION_FRAMEWORK"] = contrato["version_framework"]
        valores["LISTA_SKILLS_INSTALADAS"] = "\n".join(
            f"- `{nombre}`" for nombre in skills_instaladas
        )
        valores_completos, pendientes = completar_valores(contrato, valores, argumentos.permitir_pendientes)
        archivos = resolver_archivos(raiz, contrato["archivos_incluidos"])
        validar_permisos_inicializacion(raiz, centinela, archivos)
        cambios = preparar_cambios(archivos, valores_completos)

        politica_skills = (
            "core_automatico_mas_seleccion_explicita"
            if argumentos.skill_seleccionada
            else "contenido_preexistente_sin_seleccion"
        )
        estado_plantilla = {
            "version_framework": contrato["version_framework"],
            "version_contrato": contrato["version_contrato"],
            "inicializado_en": datetime.now().astimezone().isoformat(),
            "nombre_proyecto": valores_completos["NOMBRE_PROYECTO"],
            "idioma_nombres": valores_completos["IDIOMA_NOMBRES"],
            "pendientes": pendientes,
            "skills_instaladas": skills_instaladas,
            "politica_skills": politica_skills,
            "huellas_gestionadas": calcular_huellas_gestionadas(
                raiz,
                contrato["archivos_gestionados"],
            ),
        }
        aplicar_transaccion(
            raiz,
            centinela,
            cambios,
            estado_plantilla,
            crear_env=not argumentos.sin_env,
        )

    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Proyecto inicializado: {valores_completos['NOMBRE_PROYECTO']}")
    print(f"Archivos configurados: {len(cambios)}")
    print(f"Pendientes marcados: {len(pendientes)}")
    print("Skills instaladas: " + ", ".join(skills_instaladas))
    print("Siguiente paso: revisar .env y confirmar los TODO pendientes antes del primer commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
