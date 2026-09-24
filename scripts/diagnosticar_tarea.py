#!/usr/bin/env python3
"""Prediagnostica verificaciones declaradas o inferidas en proyectos y monorepos."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

if __package__:
    from .contrato_validacion import (
        NOMBRE_CONTRATO,
        Comprobacion,
        ContratoValidacion,
        ResultadoVerificacion,
        bloquea_resultado,
        cargar_contrato,
        comprobaciones_contrato,
        ejecutar_comprobacion,
        resultado_no_ejecutado,
    )
else:
    from contrato_validacion import (
        NOMBRE_CONTRATO,
        Comprobacion,
        ContratoValidacion,
        ResultadoVerificacion,
        bloquea_resultado,
        cargar_contrato,
        comprobaciones_contrato,
        ejecutar_comprobacion,
        resultado_no_ejecutado,
    )


class Fallo(TypedDict, total=False):
    """Representa un fallo individual extraido de una salida conocida."""

    nombre: str
    archivo: str
    linea: int
    tipo: str
    esperado: str
    obtenido: str
    descripcion: str


class Diagnostico(TypedDict):
    """Representa el diagnostico completo y su cobertura observable."""

    directorio: str
    cobertura: str
    contrato: str | None
    verificaciones: list[ResultadoVerificacion]
    todas_aprobadas: bool
    total_fallos: int
    archivos_candidatos: list[str]
    confianza: str
    bloquea_cierre: bool
    contexto_agente: str


PATRON_FALLO_UNITTEST = re.compile(
    r"^(?:FAIL|ERROR): (\S+) \(([^)]+)\)\n(.*?)\n-{40,}\n(.*?)(?=\n(?:FAIL|ERROR|OK|FAILED|\Z))",
    re.MULTILINE | re.DOTALL,
)
PATRON_ASERCION_UNITTEST = re.compile(r"Assert\w+Error:\s*(.+?)$", re.MULTILINE)
PATRON_LINEA_UNITTEST = re.compile(r'File "([^"]+)", line (\d+)')
PATRON_FALLO_NODE_SIMPLE = re.compile(r"^✖ (.+?) \([\d.]+(?:ms|s)\)\s*$", re.MULTILINE)
PATRON_RESUMEN_PYTEST = re.compile(r"(?P<cantidad>\d+) failed")
PATRON_RESUMEN_UNITTEST = re.compile(r"FAILED \((?P<detalle>[^)]*)\)")
PATRON_CONTEO_UNITTEST = re.compile(r"(?:failures|errors)=(?P<cantidad>\d+)")
PATRON_CODIGO_HTTP = re.compile(r"(\d{3})\s*!=\s*(\d{3})")
PATRON_RUTA_SALIDA = re.compile(
    r"(?P<ruta>(?:[A-Za-z]:)?[^\s\"'<>|:]+(?:[\\/][^\s\"'<>|:]+)*\.(?:py|js|mjs|cjs|ts|tsx|html|css))(?:[:(](?P<linea>\d+))?"
)
PATRON_IMPORT_JAVASCRIPT = re.compile(
    r"(?:from\s+|import\s*\()?[\"'](?P<ruta>\.{1,2}/[^\"']+)[\"']"
)
DIRECTORIOS_EXCLUIDOS: frozenset[str] = frozenset(
    {
        ".git", ".kilo", ".mypy_cache", ".next", ".pytest_cache", ".ruff_cache",
        ".tox", ".venv", "__pycache__", "build", "coverage", "dist",
        "htmlcov", "node_modules", "out", "site-packages", "vendor",
    }
)
EXTENSIONES_CANDIDATAS: frozenset[str] = frozenset(
    {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".html", ".css"}
)
MARCADORES_MODULO: frozenset[str] = frozenset(
    {"alembic.ini", "package.json", "pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"}
)
GESTORES_LOCK: dict[str, str] = {
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
}


def analizar_fallos_unittest(salida: str) -> list[Fallo]:
    """Extrae fallos estructurados de unittest y pytest compatible."""
    fallos: list[Fallo] = []
    for coincidencia in PATRON_FALLO_UNITTEST.finditer(salida):
        traza = coincidencia.group(4)
        fallo: Fallo = {"nombre": coincidencia.group(1), "tipo": "AssertionError"}
        linea = PATRON_LINEA_UNITTEST.search(traza)
        if linea:
            fallo["archivo"] = linea.group(1)
            fallo["linea"] = int(linea.group(2))
        asercion = PATRON_ASERCION_UNITTEST.search(traza)
        if asercion:
            fallo["descripcion"] = asercion.group(1).strip()
            codigos = PATRON_CODIGO_HTTP.search(asercion.group(1))
            if codigos:
                fallo["obtenido"] = codigos.group(1)
                fallo["esperado"] = codigos.group(2)
        fallos.append(fallo)
    return fallos


def analizar_fallos_node(salida: str) -> list[Fallo]:
    """Extrae los nombres unicos de fallos informados por node --test."""
    nombres: list[str] = []
    for coincidencia in PATRON_FALLO_NODE_SIMPLE.finditer(salida):
        nombre = coincidencia.group(1)
        if nombre not in nombres:
            nombres.append(nombre)
    return [Fallo(nombre=nombre, tipo="AssertionError") for nombre in nombres]


def contar_fallos_observados(salida: str) -> int:
    """Cuenta fallos resumidos aunque una traza individual resulte ambigua."""
    cantidades: list[int] = [
        int(coincidencia.group("cantidad"))
        for coincidencia in PATRON_RESUMEN_PYTEST.finditer(salida)
    ]
    for resumen in PATRON_RESUMEN_UNITTEST.finditer(salida):
        cantidades.append(
            sum(
                int(coincidencia.group("cantidad"))
                for coincidencia in PATRON_CONTEO_UNITTEST.finditer(resumen.group("detalle"))
            )
        )
    return max(cantidades, default=0)


def ruta_excluida(ruta: Path) -> bool:
    """Indica si una ruta pertenece a dependencias, cache o artefactos generados."""
    return any(parte.casefold() in DIRECTORIOS_EXCLUIDOS for parte in ruta.parts)


def recorrer_archivos(raiz: Path) -> list[Path]:
    """Recorre archivos sin entrar en directorios excluidos."""
    archivos: list[Path] = []

    def recorrer(directorio: Path) -> None:
        """Agrega archivos de un directorio sin seguir enlaces simbolicos."""
        try:
            entradas = sorted(os.scandir(directorio), key=lambda entrada: entrada.name.casefold())
        except OSError:
            return
        for entrada in entradas:
            if entrada.name.casefold() in DIRECTORIOS_EXCLUIDOS or entrada.is_symlink():
                continue
            ruta = Path(entrada.path)
            if entrada.is_dir(follow_symlinks=False):
                recorrer(ruta)
            elif entrada.is_file(follow_symlinks=False):
                archivos.append(ruta)

    recorrer(raiz)
    return archivos


def descubrir_modulos(raiz: Path) -> list[Path]:
    """Descubre raices ejecutables anidadas mediante configuraciones y pruebas."""
    archivos = recorrer_archivos(raiz)
    modulos = {archivo.parent for archivo in archivos if archivo.name in MARCADORES_MODULO}
    carpetas_pruebas = {
        archivo.parent.parent
        for archivo in archivos
        if archivo.parent.name in {"pruebas", "tests"}
        and archivo.name.startswith(("prueba_", "test_"))
    }
    for carpeta in carpetas_pruebas:
        if not any(modulo == carpeta or modulo in carpeta.parents for modulo in modulos):
            modulos.add(carpeta)
    return sorted(modulos or {raiz}, key=lambda ruta: ruta.relative_to(raiz).as_posix())


def crear_comprobacion(
    raiz: Path,
    modulo: Path,
    identificador: str,
    tipo: str,
    comando: list[str],
) -> Comprobacion:
    """Crea una comprobacion inferida con directorio relativo portable."""
    relativa = modulo.relative_to(raiz).as_posix() or "."
    nombre_modulo = relativa if relativa != "." else "raiz"
    return Comprobacion(
        identificador=f"{nombre_modulo}:{identificador}",
        tipo=tipo,
        modulo=nombre_modulo,
        directorio=relativa,
        comando=comando,
        obligatoria=True,
        bloquea_cierre=True,
        timeout_segundos=300,
        origen="INFERIDO",
    )


def cargar_scripts_npm(ruta: Path) -> dict[str, str]:
    """Carga scripts npm validos sin aceptar estructuras ambiguas."""
    try:
        datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(datos, dict) or not isinstance(datos.get("scripts"), dict):
        return {}
    scripts = datos["scripts"]
    return {
        str(nombre): str(comando)
        for nombre, comando in scripts.items()
        if isinstance(nombre, str) and isinstance(comando, str) and comando.strip()
    }


def leer_paquete(ruta: Path) -> dict[str, object]:
    """Carga la configuracion del paquete para reconocer stack y gestor."""
    try:
        datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return datos if isinstance(datos, dict) else {}


def es_nextjs(datos: dict[str, object]) -> bool:
    """Reconoce Next.js en las dependencias declaradas del modulo."""
    return any(
        isinstance(datos.get(clave), dict) and "next" in datos[clave]
        for clave in ("dependencies", "devDependencies")
    )


def resolver_gestor_paquetes(modulo: Path, datos: dict[str, object]) -> tuple[str, list[str]]:
    """Selecciona el gestor declarado y detecta lockfiles contradictorios."""
    declaracion = datos.get("packageManager")
    declarado = declaracion.split("@", 1)[0] if isinstance(declaracion, str) else None
    encontrados = {
        gestor for nombre, gestor in GESTORES_LOCK.items() if (modulo / nombre).is_file()
    }
    problemas: list[str] = []
    if declarado and declarado not in set(GESTORES_LOCK.values()):
        problemas.append(f"El gestor declarado no esta soportado: {declarado}")
    if len(encontrados) > 1:
        problemas.append("Existen lockfiles de gestores distintos")
    if declarado and encontrados and any(gestor != declarado for gestor in encontrados):
        problemas.append("packageManager contradice el lockfile presente")
    gestor = declarado if declarado in set(GESTORES_LOCK.values()) else next(iter(sorted(encontrados)), "npm")
    return gestor, problemas


def descubrir_comprobaciones(raiz: Path) -> tuple[list[Comprobacion], list[Path]]:
    """Infiere pruebas y puertas de calidad desde cada modulo descubierto."""
    comprobaciones: list[Comprobacion] = []
    sin_cobertura: list[Path] = []
    modulos = descubrir_modulos(raiz)
    for modulo in modulos:
        archivos = [archivo for archivo in recorrer_archivos(modulo) if not ruta_excluida(archivo)]
        propias: list[Comprobacion] = []
        configuracion_python = ""
        for nombre in ("pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"):
            ruta = modulo / nombre
            if ruta.is_file():
                configuracion_python += ruta.read_text(encoding="utf-8", errors="replace") + "\n"
        pruebas_python = [
            archivo for archivo in archivos
            if archivo.suffix == ".py"
            and archivo.name.startswith(("prueba_", "test_"))
            and not any(otro != modulo and otro in archivo.parents for otro in modulos)
        ]
        if pruebas_python:
            usa_pytest = "pytest" in configuracion_python.casefold() or any(
                archivo.name.startswith("test_") for archivo in pruebas_python
            )
            if usa_pytest:
                propias.append(crear_comprobacion(raiz, modulo, "pruebas-python", "unitarias", ["python", "-m", "pytest", "-q"]))
            else:
                carpeta = next((nombre for nombre in ("pruebas", "tests") if (modulo / nombre).is_dir()), ".")
                propias.append(crear_comprobacion(raiz, modulo, "pruebas-python", "unitarias", ["python", "-m", "unittest", "discover", "-s", carpeta, "-p", "*.py"]))
        if "[tool.mypy" in configuracion_python.casefold() or (modulo / "mypy.ini").is_file():
            propias.append(crear_comprobacion(raiz, modulo, "tipos-python", "tipos", ["python", "-m", "mypy", "."]))
        if "[tool.ruff" in configuracion_python.casefold() or (modulo / "ruff.toml").is_file():
            propias.append(crear_comprobacion(raiz, modulo, "lint-python", "lint", ["python", "-m", "ruff", "check", "."]))
        if (modulo / "alembic.ini").is_file():
            propias.append(crear_comprobacion(raiz, modulo, "migraciones", "migraciones", ["alembic", "check"]))

        paquete = modulo / "package.json"
        scripts = cargar_scripts_npm(paquete) if paquete.is_file() else {}
        gestor = resolver_gestor_paquetes(modulo, leer_paquete(paquete))[0] if paquete.is_file() else "npm"
        for nombre, tipo in (
            ("test", "unitarias"), ("test:integration", "integracion"),
            ("test:e2e", "e2e"), ("lint", "lint"),
            ("typecheck", "tipos"), ("build", "build"),
        ):
            if nombre in scripts:
                propias.append(crear_comprobacion(raiz, modulo, nombre.replace(":", "-"), tipo, [gestor, "run", nombre]))
        pruebas_node = [
            archivo for archivo in archivos
            if archivo.suffix in {".mjs", ".cjs", ".js"}
            and archivo.name.startswith(("prueba_", "test_"))
        ]
        if pruebas_node and "test" not in scripts:
            rutas = [archivo.relative_to(modulo).as_posix() for archivo in pruebas_node]
            propias.append(crear_comprobacion(raiz, modulo, "pruebas-node", "unitarias", ["node", "--test", *rutas]))
        if propias:
            comprobaciones.extend(propias)
        else:
            sin_cobertura.append(modulo)
    return comprobaciones, sin_cobertura


def descubrir_ejecutores(directorio: Path) -> list[tuple[str, list[str]]]:
    """Conserva la interfaz historica y expone los ejecutores inferidos."""
    comprobaciones, _ = descubrir_comprobaciones(directorio.resolve())
    ejecutores: list[tuple[str, list[str]]] = []
    for comprobacion in comprobaciones:
        comando = comprobacion["comando"]
        if "unittest" in comando:
            nombre = "unittest"
        elif "pytest" in comando:
            nombre = "pytest"
        elif comando and comando[0] == "node":
            nombre = "node"
        else:
            nombre = comprobacion["tipo"]
        ejecutores.append((nombre, comando))
    return ejecutores


def resolver_ruta_observada(raiz: Path, directorio: Path, texto: str) -> Path | None:
    """Resuelve una ruta citada por una herramienta y la confina al proyecto."""
    candidata = Path(texto)
    opciones = [candidata] if candidata.is_absolute() else [directorio / candidata, raiz / candidata]
    for opcion in opciones:
        resuelta = opcion.resolve()
        try:
            relativa = resuelta.relative_to(raiz)
        except ValueError:
            continue
        if resuelta.is_file() and not ruta_excluida(relativa):
            return resuelta
    return None


def importar_candidatos_python(raiz: Path, modulo: Path, prueba: Path) -> set[Path]:
    """Resuelve imports locales de una prueba sin importar ni ejecutar el modulo."""
    candidatos: set[Path] = set()
    try:
        arbol = ast.parse(prueba.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, SyntaxError):
        return candidatos
    nombres: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    for nombre in nombres:
        relativa = Path(*nombre.split("."))
        for base in (modulo, raiz):
            for candidata in (base / relativa.with_suffix(".py"), base / relativa / "__init__.py"):
                if candidata.is_file() and not ruta_excluida(candidata.relative_to(raiz)):
                    candidatos.add(candidata.resolve())
    return candidatos


def importar_candidatos_javascript(raiz: Path, prueba: Path) -> set[Path]:
    """Resuelve imports relativos citados por una prueba JavaScript o TypeScript."""
    candidatos: set[Path] = set()
    try:
        contenido = prueba.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return candidatos
    for coincidencia in PATRON_IMPORT_JAVASCRIPT.finditer(contenido):
        base = (prueba.parent / coincidencia.group("ruta")).resolve()
        for candidata in [base, *[base.with_suffix(extension) for extension in EXTENSIONES_CANDIDATAS]]:
            try:
                relativa = candidata.relative_to(raiz)
            except ValueError:
                continue
            if candidata.is_file() and not ruta_excluida(relativa):
                candidatos.add(candidata)
    return candidatos


def archivos_modificados(raiz: Path) -> set[Path]:
    """Obtiene archivos modificados de Git sin alterar el arbol de trabajo."""
    resultado = subprocess.run(
        ["git", "-c", f"safe.directory={raiz.as_posix()}", "status", "--porcelain", "--untracked-files=all"],
        cwd=raiz,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultado.returncode != 0:
        return set()
    modificados: set[Path] = set()
    for linea in resultado.stdout.splitlines():
        texto = linea[3:].split(" -> ")[-1].strip()
        ruta = resolver_ruta_observada(raiz, raiz, texto)
        if ruta and ruta.suffix in EXTENSIONES_CANDIDATAS:
            modificados.add(ruta)
    return modificados


def buscar_candidatos(
    directorio: Path,
    fallos: list[Fallo] | None = None,
    resultados: list[ResultadoVerificacion] | None = None,
) -> list[str]:
    """Deriva candidatos solo de trazas, imports o cambios locales relacionados."""
    raiz = directorio.resolve()
    candidatos: set[Path] = set()
    rutas_prueba: set[Path] = set()
    for resultado in resultados or []:
        modulo = raiz if resultado["directorio"] == "." else raiz / resultado["directorio"]
        for coincidencia in PATRON_RUTA_SALIDA.finditer(resultado["evidencia"]):
            ruta = resolver_ruta_observada(raiz, modulo, coincidencia.group("ruta"))
            if ruta is None:
                continue
            relativa_observada = ruta.relative_to(raiz)
            if ruta.name.startswith(("prueba_", "test_")) or any(
                parte in {"pruebas", "tests"} for parte in relativa_observada.parts
            ):
                rutas_prueba.add(ruta)
            elif ruta.suffix in EXTENSIONES_CANDIDATAS:
                candidatos.add(ruta)
    for fallo in fallos or []:
        archivo = fallo.get("archivo")
        if archivo:
            ruta = resolver_ruta_observada(raiz, raiz, archivo)
            if ruta:
                rutas_prueba.add(ruta)
    for prueba in rutas_prueba:
        if prueba.suffix == ".py":
            candidatos.update(importar_candidatos_python(raiz, prueba.parent.parent, prueba))
        else:
            candidatos.update(importar_candidatos_javascript(raiz, prueba))
    if not candidatos and resultados:
        modulos_fallidos = {resultado["directorio"] for resultado in resultados if resultado["estado"] == "FALLIDO"}
        for modificado in archivos_modificados(raiz):
            relativa = modificado.relative_to(raiz)
            if any(modulo == "." or Path(modulo) in relativa.parents for modulo in modulos_fallidos):
                candidatos.add(modificado)
    return sorted(ruta.relative_to(raiz).as_posix() for ruta in candidatos)


def formatear_contexto(
    aprobadas: bool,
    fallos: list[Fallo],
    candidatos: list[str],
    resultados: list[ResultadoVerificacion],
) -> str:
    """Genera un resumen que diferencia estado, comando, directorio y evidencia."""
    if aprobadas and not resultados:
        return "Todas las pruebas aprobaron. No se requiere correccion."
    lineas = ["COBERTURA_EJECUTABLE: " + ("APROBADA" if aprobadas else "INCOMPLETA")]
    for resultado in resultados:
        codigo = "sin codigo" if resultado["codigo_salida"] is None else f"codigo {resultado['codigo_salida']}"
        lineas.append(
            f"[{resultado['estado']}] {resultado['identificador']} | {resultado['directorio']} | "
            f"{resultado['comando_texto'] or 'sin comando'} | {codigo} | {resultado['duracion_segundos']:.3f}s"
        )
        if resultado["evidencia"]:
            lineas.append(f"  EVIDENCIA: {' '.join(resultado['evidencia'].splitlines())[-240:]}")
    lineas.append(f"FALLOS_DETECTADOS: {len(fallos)}")
    for fallo in fallos:
        detalle = [f"- {fallo.get('nombre', 'desconocido')}"]
        if fallo.get("esperado") and fallo.get("obtenido"):
            detalle.append(f"esperado={fallo['esperado']} obtenido={fallo['obtenido']}")
        if fallo.get("descripcion"):
            detalle.append(fallo["descripcion"][:120])
        lineas.append(" | ".join(detalle))
    lineas.append("ARCHIVOS_CANDIDATOS: " + (", ".join(candidatos) if candidatos else "ninguno derivado de evidencia"))
    lineas.append("Los candidatos no confirman la causa; se debe comprobarla antes de editar.")
    return "\n".join(lineas)


def diagnosticar(directorio: Path) -> Diagnostico:
    """Ejecuta el contrato o un descubrimiento conservador desde la raiz recibida."""
    raiz = directorio.resolve()
    ruta_contrato = raiz / NOMBRE_CONTRATO
    contrato: ContratoValidacion | None = None
    cobertura = "INFERIDA"
    sin_cobertura: list[Path] = []
    if ruta_contrato.is_file():
        contrato = cargar_contrato(ruta_contrato, raiz)
        comprobaciones = comprobaciones_contrato(contrato)
        cobertura = "DECLARADA"
    else:
        comprobaciones, sin_cobertura = descubrir_comprobaciones(raiz)
    resultados = [ejecutar_comprobacion(raiz, comprobacion) for comprobacion in comprobaciones]
    for modulo in descubrir_modulos(raiz):
        paquete = modulo / "package.json"
        if not paquete.is_file():
            continue
        datos = leer_paquete(paquete)
        relativa = modulo.relative_to(raiz).as_posix() or "."
        nombre_modulo = relativa if relativa != "." else "raiz"
        gestor, problemas = resolver_gestor_paquetes(modulo, datos)
        for indice, problema in enumerate(problemas, start=1):
            resultados.append(resultado_no_ejecutado(
                f"{nombre_modulo}:gestor-{indice}", nombre_modulo, relativa,
                "INFERIDO", problema, obligatoria=True,
            ))
        for resultado in list(resultados):
            comando = resultado["comando"]
            if resultado["directorio"] == relativa and comando and comando[0] in {"npm", "pnpm", "yarn"} and comando[0] != gestor:
                resultados.append(resultado_no_ejecutado(
                    f"{nombre_modulo}:gestor-comando", nombre_modulo, relativa,
                    "INFERIDO", f"El comando usa {comando[0]} y el proyecto usa {gestor}.",
                    obligatoria=True,
                ))
                break
        if es_nextjs(datos):
            tipos = {
                resultado["tipo"] for resultado in resultados
                if resultado["directorio"] == relativa
                and resultado["obligatoria"] and resultado["bloquea_cierre"]
            }
            for tipo in ("lint", "build"):
                if tipo not in tipos:
                    resultados.append(resultado_no_ejecutado(
                        f"{nombre_modulo}:{tipo}-ausente", nombre_modulo, relativa,
                        "INFERIDO", f"Next.js requiere una verificacion {tipo} declarada y ejecutable.",
                        obligatoria=True,
                    ))
    if not comprobaciones:
        resultados.append(
            resultado_no_ejecutado(
                "sin-cobertura", "raiz", ".", "DECLARADO" if contrato else "INFERIDO",
                "No se declararon ni descubrieron verificaciones ejecutables; no equivale a pruebas aprobadas.",
                obligatoria=contrato is not None,
            )
        )
    for modulo in sin_cobertura:
        relativa = modulo.relative_to(raiz).as_posix() or "."
        resultados.append(
            resultado_no_ejecutado(
                f"{relativa}:sin-pruebas", relativa if relativa != "." else "raiz", relativa,
                "INFERIDO", "El modulo no contiene una verificacion reconocible; la cobertura es inferida.",
            )
        )
    fallos: list[Fallo] = []
    for resultado in resultados:
        if resultado["estado"] != "FALLIDO":
            continue
        extraidos = analizar_fallos_unittest(resultado["evidencia"])
        if not extraidos and resultado["tipo"] == "unitarias":
            extraidos = analizar_fallos_node(resultado["evidencia"])
        cantidad_observada = contar_fallos_observados(resultado["evidencia"])
        while len(extraidos) < cantidad_observada:
            extraidos.append(
                Fallo(
                    nombre=f"{resultado['identificador']}:fallo-{len(extraidos) + 1}",
                    tipo="FalloResumido",
                )
            )
        fallos.extend(extraidos or [Fallo(nombre=resultado["identificador"], tipo="ComandoFallido")])
    candidatos = buscar_candidatos(raiz, resultados=resultados)
    ejecutadas = [resultado for resultado in resultados if resultado["estado"] != "NO_EJECUTADO"]
    todas_aprobadas = bool(ejecutadas) and all(resultado["estado"] == "APROBADO" for resultado in resultados)
    criterios = contrato["criterios_bloqueo"] if contrato else ["FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"]
    bloqueo = any(bloquea_resultado(resultado, criterios) for resultado in resultados)
    confianza = "media" if candidatos and fallos else "alta" if todas_aprobadas else "baja"
    return Diagnostico(
        directorio=str(raiz), cobertura=cobertura,
        contrato=str(ruta_contrato) if contrato else None,
        verificaciones=resultados, todas_aprobadas=todas_aprobadas,
        total_fallos=len(fallos), archivos_candidatos=candidatos,
        confianza=confianza, bloquea_cierre=bloqueo,
        contexto_agente=formatear_contexto(todas_aprobadas, fallos, candidatos, resultados),
    )


def main() -> int:
    """Diagnostica verificaciones y propaga fallos mediante el codigo de salida."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("directorio", type=Path)
    analizador.add_argument("--formato", choices=("json", "texto"), default="texto")
    analizador.add_argument("--salida", type=Path, default=None)
    argumentos = analizador.parse_args()
    if not argumentos.directorio.is_dir():
        print(f"ERROR: {argumentos.directorio} no es un directorio", file=sys.stderr)
        return 1
    try:
        resultado = diagnosticar(argumentos.directorio)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    contenido = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n" if argumentos.formato == "json" else resultado["contexto_agente"] + "\n"
    if argumentos.salida:
        argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
        argumentos.salida.write_text(contenido, encoding="utf-8")
        print(f"Diagnostico guardado en: {argumentos.salida}")
    else:
        sys.stdout.buffer.write(contenido.encode("utf-8"))
    return 2 if resultado["bloquea_cierre"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
