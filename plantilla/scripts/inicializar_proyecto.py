#!/usr/bin/env python3
"""Inicializa una copia de la plantilla mediante su contrato declarado."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
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
    placeholders: dict[str, CampoPlaceholder]


PATRON_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
PATRON_NOMBRE_SKILL = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
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


def cargar_contrato(ruta: Path) -> ContratoPlantilla:
    """Carga el contrato y valida su estructura minima."""
    contenido = cargar_json_sin_duplicados(ruta.read_text(encoding="utf-8"), str(ruta))
    datos = exigir_diccionario(contenido, "contrato")
    version_contrato = datos.get("version_contrato")
    version_framework = datos.get("version_framework")
    sintaxis = datos.get("sintaxis_placeholder")
    if not isinstance(version_contrato, int) or version_contrato < 1:
        raise ValueError("version_contrato debe ser un entero positivo")
    if not isinstance(version_framework, str) or not version_framework:
        raise ValueError("version_framework debe ser una cadena no vacia")
    if not isinstance(sintaxis, str) or not sintaxis:
        raise ValueError("sintaxis_placeholder debe ser una cadena no vacia")

    campos_crudos = exigir_diccionario(datos.get("placeholders"), "placeholders")
    campos: dict[str, CampoPlaceholder] = {}
    for clave, valor in campos_crudos.items():
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
        campos[clave] = CampoPlaceholder(obligatorio=obligatorio, origen=origen, descripcion=descripcion)

    return ContratoPlantilla(
        version_contrato=version_contrato,
        version_framework=version_framework,
        sintaxis_placeholder=sintaxis,
        rutas_excluidas=exigir_lista_cadenas(datos.get("rutas_excluidas"), "rutas_excluidas"),
        archivos_incluidos=exigir_lista_cadenas(datos.get("archivos_incluidos"), "archivos_incluidos"),
        placeholders=campos,
    )


def normalizar_valor(valor: object, clave: str) -> str:
    """Convierte un valor de configuracion a texto reproducible."""
    if isinstance(valor, str):
        return valor.strip()
    if isinstance(valor, list) and all(isinstance(item, str) for item in valor):
        elementos = cast(list[str], valor)
        return "\n".join(f"- {elemento.strip()}" for elemento in elementos if elemento.strip())
    raise ValueError(f"El valor de {clave} debe ser una cadena o una lista de cadenas")


def cargar_valores(ruta: Path | None) -> dict[str, str]:
    """Carga valores de proyecto desde un archivo JSON opcional."""
    if ruta is None:
        return {}
    contenido = cargar_json_sin_duplicados(ruta.read_text(encoding="utf-8"), str(ruta))
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
        resultado[clave_limpia] = valor.strip()
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
        if contenido_nuevo != contenido:
            cambios[archivo] = contenido_nuevo
    return cambios


def escribir_cambios(cambios: dict[Path, str], raiz: Path) -> None:
    """Escribe cambios con respaldo temporal y restaura ante un fallo."""
    with tempfile.TemporaryDirectory(prefix="respaldo-inicializacion-") as directorio_temporal:
        respaldo = Path(directorio_temporal)
        for archivo in cambios:
            destino_respaldo = respaldo / archivo.relative_to(raiz)
            destino_respaldo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo, destino_respaldo)
        try:
            for archivo, contenido in cambios.items():
                temporal = archivo.with_name(f".{archivo.name}.temporal")
                temporal.write_text(contenido, encoding="utf-8", newline="\n")
                os.replace(temporal, archivo)
        except OSError:
            for archivo in cambios:
                origen_respaldo = respaldo / archivo.relative_to(raiz)
                if origen_respaldo.exists():
                    shutil.copy2(origen_respaldo, archivo)
            raise


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
    )


def verificar_git(raiz: Path) -> None:
    """Inicializa Git o rechaza cambios rastreados preexistentes."""
    directorio_git = raiz / ".git"
    if not directorio_git.exists():
        ejecutar_git(["init"], raiz)
        return
    referencia = ejecutar_git(["rev-parse", "--verify", "HEAD"], raiz, comprobar=False)
    if referencia.returncode != 0:
        return
    cambios_trabajo = ejecutar_git(["diff", "--quiet"], raiz, comprobar=False)
    cambios_preparados = ejecutar_git(["diff", "--cached", "--quiet"], raiz, comprobar=False)
    if cambios_trabajo.returncode == 1 or cambios_preparados.returncode == 1:
        raise ValueError("El repositorio contiene cambios rastreados sin confirmar")
    if cambios_trabajo.returncode not in (0, 1) or cambios_preparados.returncode not in (0, 1):
        raise ValueError("Git no pudo comprobar el estado del repositorio")


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
        contrato = cargar_contrato(raiz / "configuracion_plantilla.json")
        skills_instaladas = validar_skills_instaladas(raiz, argumentos.skill_seleccionada)
        valores = cargar_valores(argumentos.configuracion)
        if argumentos.nombre_proyecto:
            valores["NOMBRE_PROYECTO"] = argumentos.nombre_proyecto
        if argumentos.idioma_nombres:
            valores["IDIOMA_NOMBRES"] = argumentos.idioma_nombres
        valores.update(analizar_valores_directos(argumentos.valor))
        valores["VERSION_FRAMEWORK"] = contrato["version_framework"]
        valores["LISTA_SKILLS_INSTALADAS"] = "\n".join(
            f"- `{nombre}`" for nombre in skills_instaladas
        )
        valores_completos, pendientes = completar_valores(contrato, valores, argumentos.permitir_pendientes)
        archivos = resolver_archivos(raiz, contrato["archivos_incluidos"])
        cambios = preparar_cambios(archivos, valores_completos)

        verificar_git(raiz)
        verificar_env_ignorado(raiz)
        escribir_cambios(cambios, raiz)
        for directorio in ("documentacion", "infraestructura/registros", "scripts"):
            (raiz / directorio).mkdir(parents=True, exist_ok=True)

        env_ejemplo = raiz / ".env.ejemplo"
        env_destino = raiz / ".env"
        if not argumentos.sin_env and not env_destino.exists():
            shutil.copy2(env_ejemplo, env_destino)

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
        }
        (raiz / ".estado-plantilla.json").write_text(
            json.dumps(estado_plantilla, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        centinela.unlink()

        restantes: dict[str, list[str]] = {}
        for archivo in archivos:
            for clave in PATRON_PLACEHOLDER.findall(archivo.read_text(encoding="utf-8")):
                restantes.setdefault(clave, []).append(str(archivo.relative_to(raiz)))
        if restantes:
            detalle = "; ".join(f"{clave}: {', '.join(rutas)}" for clave, rutas in sorted(restantes.items()))
            raise ValueError(f"Quedaron placeholders configurables sin resolver: {detalle}")

    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, subprocess.SubprocessError) as error:
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
