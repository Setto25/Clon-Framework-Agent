#!/usr/bin/env python3
"""Comprueba memoria y puertas declaradas sin ejecutar dependencias del proyecto."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

if __package__:
    from .contrato_validacion import NOMBRE_CONTRATO, cargar_contrato
    from .diagnosticar_tarea import (
        cargar_scripts_npm,
        descubrir_modulos,
        es_nextjs,
        leer_paquete,
        resolver_gestor_paquetes,
    )
    from .verificar_memoria_proyecto import verificar
else:
    from contrato_validacion import NOMBRE_CONTRATO, cargar_contrato
    from diagnosticar_tarea import (
        cargar_scripts_npm,
        descubrir_modulos,
        es_nextjs,
        leer_paquete,
        resolver_gestor_paquetes,
    )
    from verificar_memoria_proyecto import verificar


DOCUMENTOS_CIERRE: frozenset[str] = frozenset(
    {"PROJECT_STATE.md", "documentacion/PLAN_DESARROLLO.md", "documentacion/REGISTRO_CAMBIOS.md"}
)
EXTENSIONES_CODIGO: frozenset[str] = frozenset(
    {".py", ".js", ".jsx", ".ts", ".tsx", ".dart", ".ino", ".cpp", ".c", ".h", ".css", ".html"}
)


def rutas_cambiadas(raiz: Path, base: str) -> set[str]:
    """Obtiene los archivos de la revision Git sin modificar el repositorio."""
    argumentos = ["diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "HEAD"] if set(base) == {"0"} else [
        "diff", "--name-only", f"{base}...HEAD"
    ]
    resultado = subprocess.run(
        ["git", "-c", f"safe.directory={raiz.as_posix()}", *argumentos],
        cwd=raiz, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if resultado.returncode != 0:
        raise ValueError("No se pudo comparar la base Git: " + resultado.stderr.strip())
    return {linea.replace("\\", "/") for linea in resultado.stdout.splitlines() if linea.strip()}


def validar_integridad(raiz: Path, base: str | None = None) -> list[str]:
    """Detecta memoria pendiente, puertas omitidas y cambios sin registro."""
    raiz = raiz.resolve()
    errores: list[str] = []
    memoria = verificar(raiz)
    if not memoria["valido"]:
        errores.append("La memoria del proyecto conserva archivos ausentes, vacios o pendientes de plantilla")

    ruta_contrato = raiz / NOMBRE_CONTRATO
    contrato = cargar_contrato(ruta_contrato, raiz) if ruta_contrato.is_file() else None
    for modulo in descubrir_modulos(raiz):
        paquete = modulo / "package.json"
        if not paquete.is_file():
            continue
        datos = leer_paquete(paquete)
        relativa = modulo.relative_to(raiz).as_posix() or "."
        gestor, problemas = resolver_gestor_paquetes(modulo, datos)
        errores.extend(f"{relativa}: {problema}" for problema in problemas)
        scripts = cargar_scripts_npm(paquete)
        verificaciones = [
            verificacion
            for item in contrato["modulos"] if item["directorio"] == relativa
            for verificacion in item["verificaciones"]
        ] if contrato else []
        for verificacion in verificaciones:
            comando = verificacion["comando"]
            if len(comando) >= 3 and comando[0] in {"npm", "pnpm", "yarn"} and comando[1] == "run":
                if comando[0] != gestor:
                    errores.append(f"{relativa}: {verificacion['identificador']} usa {comando[0]} y el proyecto usa {gestor}")
                if comando[2] not in scripts:
                    errores.append(f"{relativa}: el script {comando[2]} del contrato no existe en package.json")
        if not es_nextjs(datos):
            continue
        if contrato:
            tipos = {
                verificacion["tipo"]
                for verificacion in verificaciones
                if verificacion["obligatoria"] and verificacion["bloquea_cierre"]
            }
        else:
            tipos = set(scripts)
        for tipo in ("lint", "build"):
            if tipo not in tipos:
                errores.append(f"{relativa}: falta la puerta obligatoria {tipo} de Next.js")

    if base:
        rutas = rutas_cambiadas(raiz, base)
        if any(Path(ruta).suffix in EXTENSIONES_CODIGO or Path(ruta).name == "package.json" for ruta in rutas):
            faltantes = DOCUMENTOS_CIERRE - rutas
            if faltantes:
                errores.append("El cambio de codigo no actualizo: " + ", ".join(sorted(faltantes)))
    return errores


def main() -> int:
    """Ejecuta la comprobacion estatica para CI o para revision local."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("raiz", nargs="?", type=Path, default=Path.cwd())
    analizador.add_argument("--base", default=os.environ.get("BASE_CAMBIO"))
    argumentos = analizador.parse_args()
    try:
        errores = validar_integridad(argumentos.raiz, argumentos.base)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if errores:
        for error in errores:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Integridad del proyecto valida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
