#!/usr/bin/env python3
"""Crea un proyecto nuevo desde la plantilla mediante una operacion segura."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from catalogo_skills import CORE_AUTOMATICO, RegistroSkill, descubrir_skills


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
TIEMPO_MAXIMO_INICIALIZACION_SEGUNDOS = 120


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz del creador de proyectos."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("destino", type=Path, help="Directorio nuevo que recibira el proyecto")
    analizador.add_argument("nombre_proyecto", help="Nombre visible del proyecto")
    analizador.add_argument("--idioma", default="español", help="Idioma de nombres y documentacion")
    analizador.add_argument("--configuracion", type=Path, help="Archivo JSON con valores por placeholder")
    analizador.add_argument("--valor", action="append", default=[], metavar="CLAVE=VALOR")
    analizador.add_argument(
        "--skill",
        action="append",
        default=[],
        metavar="NOMBRE",
        help="Skill adicional confirmada; se puede repetir",
    )
    analizador.add_argument("--permitir-pendientes", action="store_true")
    analizador.add_argument("--sin-env", action="store_true")
    return analizador.parse_args()


def esta_dentro(ruta: Path, posible_contenedor: Path) -> bool:
    """Determina si una ruta queda dentro de otra ruta."""
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
    """Rechaza redirecciones y montajes que saquen contenido del arbol esperado."""
    if es_enlace_o_reparse(raiz):
        raise ValueError("La raiz de la plantilla no puede ser un enlace o reparse point")
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
                    raise ValueError(
                        f"La plantilla supera el maximo de {MAXIMO_ENTRADAS_ARBOL} entradas"
                    )
                if entrada.name in NOMBRES_ARTEFACTOS_GENERADOS or entrada.name.endswith(
                    SUFIJOS_ARTEFACTOS_GENERADOS
                ):
                    raise ValueError(f"La plantilla contiene un artefacto generado no permitido: {relativa}")
                if es_enlace_o_reparse(ruta):
                    raise ValueError(f"La plantilla contiene un enlace o reparse point no permitido: {relativa}")
                informacion = ruta.lstat()
                if stat.S_ISREG(informacion.st_mode) and informacion.st_mode & (
                    stat.S_ISUID | stat.S_ISGID
                ):
                    raise ValueError(f"La plantilla contiene permisos especiales no permitidos: {relativa}")
                if informacion.st_dev != dispositivo_raiz:
                    raise ValueError(f"La plantilla cruza a otro sistema de archivos: {relativa}")
                ruta_resuelta = ruta.resolve(strict=True)
                if not esta_dentro(ruta_resuelta, raiz_resuelta):
                    raise ValueError(f"La plantilla contiene una ruta fuera de su raiz: {relativa}")
                if stat.S_ISREG(informacion.st_mode):
                    if informacion.st_size > MAXIMO_BYTES_ARCHIVO:
                        raise ValueError(
                            f"La plantilla contiene un archivo mayor a {MAXIMO_BYTES_ARCHIVO} bytes: {relativa}"
                        )
                    bytes_contados += informacion.st_size
                    if bytes_contados > MAXIMO_BYTES_TOTALES:
                        raise ValueError(
                            f"La plantilla supera el maximo total de {MAXIMO_BYTES_TOTALES} bytes"
                        )
                elif not stat.S_ISDIR(informacion.st_mode):
                    raise ValueError(f"La plantilla contiene un archivo especial no permitido: {relativa}")
                if stat.S_ISDIR(informacion.st_mode) and relativa not in rutas_omitidas:
                    recorrer(ruta)

    recorrer(raiz_resuelta)


def normalizar_permisos_arbol(raiz: Path) -> None:
    """Retira permisos especiales y garantiza escritura del propietario."""
    rutas = [raiz, *sorted(raiz.rglob("*"))]
    for ruta in rutas:
        informacion = ruta.lstat()
        modo = stat.S_IMODE(informacion.st_mode)
        modo &= ~(stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX)
        modo |= stat.S_IRUSR | stat.S_IWUSR
        if stat.S_ISDIR(informacion.st_mode):
            modo |= stat.S_IXUSR
        os.chmod(ruta, modo)


def validar_destino(destino: Path, raiz_framework: Path) -> tuple[Path, Path]:
    """Valida que el destino sea nuevo, externo al framework y tenga padre existente."""
    destino_lexico = Path(os.path.abspath(os.fspath(destino.expanduser())))
    if os.path.lexists(destino_lexico):
        raise ValueError(f"El destino ya existe, incluso como enlace: {destino_lexico}")
    destino_absoluto = destino_lexico.resolve()
    padre = destino_absoluto.parent
    if not padre.is_dir():
        raise ValueError(f"El directorio padre no existe: {padre}")
    raiz_framework_resuelta = raiz_framework.resolve(strict=True)
    if esta_dentro(destino_lexico, raiz_framework_resuelta) or esta_dentro(
        destino_absoluto,
        raiz_framework_resuelta,
    ):
        raise ValueError("El destino no puede quedar dentro del repositorio agent-framework")
    return destino_absoluto, padre


def construir_comando_inicializador(
    destino_temporal: Path,
    argumentos: argparse.Namespace,
    skills_seleccionadas: list[str],
) -> list[str]:
    """Construye el comando del inicializador interno sin utilizar un shell."""
    comando = [
        sys.executable,
        str(destino_temporal / "scripts" / "inicializar_proyecto.py"),
        argumentos.nombre_proyecto,
        argumentos.idioma,
    ]
    if argumentos.configuracion is not None:
        comando.extend(["--configuracion", str(argumentos.configuracion.expanduser().resolve())])
    for valor in argumentos.valor:
        comando.extend(["--valor", valor])
    for nombre_skill in skills_seleccionadas:
        comando.extend(["--skill-seleccionada", nombre_skill])
    if argumentos.permitir_pendientes:
        comando.append("--permitir-pendientes")
    if argumentos.sin_env:
        comando.append("--sin-env")
    return comando


def seleccionar_skills(
    catalogo: list[RegistroSkill],
    solicitadas: list[str],
) -> tuple[list[RegistroSkill], list[str]]:
    """Combina el core automatico con la seleccion explicita validada."""
    por_nombre = {registro["nombre"]: registro for registro in catalogo}
    nombres_solicitados = [nombre.strip() for nombre in solicitadas if nombre.strip()]
    desconocidos = sorted(set(nombres_solicitados) - set(por_nombre))
    if desconocidos:
        disponibles = ", ".join(sorted(por_nombre))
        raise ValueError(
            f"Skills desconocidas: {', '.join(desconocidos)}. Disponibles: {disponibles}"
        )
    nombres = list(CORE_AUTOMATICO)
    nombres.extend(sorted(set(nombres_solicitados) - set(CORE_AUTOMATICO)))
    return [por_nombre[nombre] for nombre in nombres], nombres


def ignorar_almacen_skills(origen: Path) -> Callable[[str, list[str]], set[str]]:
    """Construye un filtro que excluye solo el almacen completo de Skills."""
    padre_skills = (origen / ".agents").resolve()

    def ignorar(directorio: str, nombres: list[str]) -> set[str]:
        ruta = Path(directorio).resolve()
        if ruta == padre_skills and "skills" in nombres:
            return {"skills"}
        return set()

    return ignorar


def instalar_skills(
    raiz_origen: Path,
    raiz_destino: Path,
    seleccionadas: list[RegistroSkill],
) -> None:
    """Copia exclusivamente las Skills autorizadas y sus reglas de stack."""
    stacks_copiados: set[str] = set()
    for registro in seleccionadas:
        origen_skill = raiz_origen / registro["ruta"]
        if registro["categoria"] == "stack":
            stack = registro["stack"]
            if stack is None:
                raise ValueError(f"La Skill {registro['nombre']} no declara stack")
            destino_stack = raiz_destino / "stacks" / stack
            destino_skill = destino_stack / "skills" / registro["nombre"]
            if stack not in stacks_copiados:
                leeme = raiz_origen / "stacks" / stack / "LEEME.md"
                if not leeme.is_file():
                    raise ValueError(f"Falta LEEME.md para el stack {stack}")
                destino_stack.mkdir(parents=True, exist_ok=True)
                shutil.copy2(leeme, destino_stack / "LEEME.md")
                stacks_copiados.add(stack)
        else:
            destino_skill = raiz_destino / registro["nombre"]
        shutil.copytree(origen_skill, destino_skill, copy_function=shutil.copy2)


def eliminar_temporal(destino_temporal: Path, padre: Path) -> None:
    """Elimina solamente el temporal validado dentro de su padre previsto."""
    if not destino_temporal.exists():
        return
    temporal_resuelto = destino_temporal.resolve()
    if temporal_resuelto.parent != padre or not temporal_resuelto.name.startswith(".proyecto-temporal-"):
        raise ValueError(f"Se rechazo eliminar un temporal inesperado: {temporal_resuelto}")
    shutil.rmtree(temporal_resuelto)


def publicar_temporal(destino_temporal: Path, destino: Path, padre: Path) -> None:
    """Publica el temporal solo si el destino continua libre y bien delimitado."""
    temporal_resuelto = destino_temporal.resolve(strict=True)
    if temporal_resuelto.parent != padre or not temporal_resuelto.name.startswith(".proyecto-temporal-"):
        raise ValueError(f"Se rechazo publicar un temporal inesperado: {temporal_resuelto}")
    if os.path.lexists(destino):
        raise ValueError(f"El destino aparecio durante la creacion y no sera reemplazado: {destino}")
    os.replace(temporal_resuelto, destino)


def crear_proyecto(argumentos: argparse.Namespace) -> tuple[Path, list[str]]:
    """Copia, inicializa y publica localmente el proyecto de forma atomica."""
    raiz_framework = Path(__file__).resolve().parent.parent
    origen = raiz_framework / "plantilla"
    validar_arbol_sin_enlaces(origen)
    raiz_skills_origen = origen / ".agents" / "skills"
    catalogo = descubrir_skills(raiz_skills_origen)
    skills_seleccionadas, nombres_skills = seleccionar_skills(catalogo, argumentos.skill)
    destino, padre = validar_destino(argumentos.destino, raiz_framework)
    destino_temporal = Path(tempfile.mkdtemp(prefix=".proyecto-temporal-", dir=padre))
    try:
        shutil.copytree(
            origen,
            destino_temporal,
            dirs_exist_ok=True,
            copy_function=shutil.copy2,
            ignore=ignorar_almacen_skills(origen),
        )
        instalar_skills(
            raiz_skills_origen,
            destino_temporal / ".agents" / "skills",
            skills_seleccionadas,
        )
        normalizar_permisos_arbol(destino_temporal)
        comando = construir_comando_inicializador(destino_temporal, argumentos, nombres_skills)
        subprocess.run(
            comando,
            cwd=destino_temporal,
            check=True,
            timeout=TIEMPO_MAXIMO_INICIALIZACION_SEGUNDOS,
        )
        publicar_temporal(destino_temporal, destino, padre)
    except (OSError, subprocess.SubprocessError, ValueError):
        eliminar_temporal(destino_temporal, padre)
        raise
    return destino, nombres_skills


def main() -> int:
    """Ejecuta la creacion y comunica el destino resultante."""
    argumentos = crear_argumentos()
    try:
        destino, nombres_skills = crear_proyecto(argumentos)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Proyecto creado en: {destino}")
    print("Skills instaladas: " + ", ".join(nombres_skills))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
