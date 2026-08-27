#!/usr/bin/env python3
"""
Inicializa un nuevo proyecto a partir de la plantilla del framework agentico.
Uso: python scripts/inicializar_proyecto.py <nombre-proyecto> [idioma-nombres]
"""

import sys
import re
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Fuerza UTF-8 en stdout para que los checkmarks (✓ ⚠) funcionen en terminales
# Windows (cp1252 por defecto en PowerShell/cmd). Sin esto falla con UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    # --- Configuracion ---
    if len(sys.argv) < 2:
        print("Uso: python scripts/inicializar_proyecto.py <nombre-proyecto> [idioma-nombres]")
        print("  nombre-proyecto: Nombre del proyecto (ej: entrevoces, miapp)")
        print("  idioma-nombres:  Idioma para nombres de archivos (default: español)")
        sys.exit(1)

    nombre_proyecto = sys.argv[1]
    idioma_nombres = sys.argv[2] if len(sys.argv) > 2 else "español"
    raiz = Path.cwd()

    print(f"=== Inicializando proyecto: {nombre_proyecto} ===")
    print(f"    Idioma de nombres: {idioma_nombres}")
    print()

    # --- Validacion 1: Centinela ---
    centinela = raiz / ".plantilla-framework"
    if not centinela.exists():
        print("ERROR: No se encontró .plantilla-framework en el directorio actual.")
        print("       Este script solo debe ejecutarse dentro de una copia limpia de la plantilla.")
        print(f"       Directorio actual: {raiz}")
        sys.exit(1)

    # --- Validacion 2: Git limpio ---
    git_dir = raiz / ".git"
    if git_dir.exists():
        resultado = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=raiz
        )
        if resultado.stdout.strip():
            print("ERROR: El árbol de trabajo tiene cambios sin commitear.")
            print("       Haz commit o stash antes de inicializar, para poder revertir con git checkout si algo falla.")
            print()
            print("Archivos con cambios:")
            print(resultado.stdout)
            sys.exit(1)

    # --- Paso 1: Reemplazar placeholders ---
    print("[1/7] Reemplazando placeholders automáticos...")

    # Más agresivo que bash (tr '-' '_'): reemplaza CUALQUIER carácter no alfanumérico por '_'.
    # Para nombres de proyecto normales es equivalente; difiere con espacios u otros símbolos (ej: "mi app" → "MI_APP").
    prefijo_variables = re.sub(r'[^A-Z0-9_]', '_', nombre_proyecto.upper())

    reemplazos = {
        "NOMBRE_PROYECTO":   nombre_proyecto,
        "IDIOMA_NOMBRES":    idioma_nombres,
        "PROYECTO":          nombre_proyecto,
        "PREFIJO_VARIABLES": prefijo_variables,
    }

    extensiones = {".md", ".yaml", ".sh", ".py"}
    archivos_modificados = []

    for archivo in sorted(raiz.rglob("*")):
        if not archivo.is_file():
            continue
        if archivo.suffix not in extensiones:
            continue
        # Saltar el propio script y el .sh deprecado (contiene {{$p}} y {{placeholders}}
        # como literales de código bash, no como placeholders reales del proyecto).
        if archivo.resolve() == Path(__file__).resolve():
            continue
        if archivo.name == "inicializar_proyecto.sh":
            continue

        try:
            contenido = archivo.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        contenido_nuevo = contenido
        for placeholder, valor in reemplazos.items():
            # re.escape() equivale a \Q...\E de perl — sanitiza metacaracteres del placeholder.
            # Usar callable en re.sub hace que el valor de reemplazo sea literal (no se interpreta como regex).
            patron = r"\{\{" + re.escape(placeholder) + r"\}\}"
            contenido_nuevo = re.sub(patron, lambda m, v=valor: v, contenido_nuevo)

        if contenido_nuevo != contenido:
            archivo.write_text(contenido_nuevo, encoding="utf-8")
            archivos_modificados.append(archivo.relative_to(raiz))
            print(f"    ✓ {archivo.relative_to(raiz)}")

    if not archivos_modificados:
        print("    (ningún archivo con placeholders encontrado)")

    # --- Paso 2: Crear .env desde ejemplo ---
    print()
    print("[2/7] Configurando entorno...")

    env_file    = raiz / ".env"
    env_ejemplo = raiz / ".env.ejemplo"

    if not env_file.exists() and env_ejemplo.exists():
        shutil.copy(env_ejemplo, env_file)
        print("    ✓ .env creado desde .env.ejemplo")
        print("    ⚠ Edita .env con tus valores reales antes de continuar")
    else:
        print("    - .env ya existe o .env.ejemplo no encontrado")

    # --- Paso 3: Crear directorios faltantes ---
    print()
    print("[3/7] Creando directorios...")

    directorios = [
        "documentacion",
        "infraestructura/registros",
        "scripts",
    ]

    for d in directorios:
        ruta = raiz / Path(d)
        ruta.mkdir(parents=True, exist_ok=True)
        print(f"    ✓ {d}/")

    # --- Paso 4: Inicializar git ---
    print()
    print("[4/7] Verificando repositorio git...")

    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=raiz, check=True)
        print("    ✓ Repositorio git inicializado")
    else:
        print("    - Repositorio git ya existe")

    # --- Paso 5: Eliminar centinela ---
    print()
    print("[5/7] Limpiando archivos de plantilla...")
    # missing_ok=True equivale al rm -f del bash: no falla si el archivo ya no existe.
    centinela.unlink(missing_ok=True)
    print("    ✓ .plantilla-framework eliminado")

    # --- Paso 6: Generar catalogo de skills ---
    print()
    print("[6/7] Descubriendo skills disponibles...")

    skills_dir    = raiz / ".agents" / "skills"
    catalogo_path = skills_dir / "catalogo_skills.json"

    def extraer_frontmatter(skill_md: Path) -> dict:
        """Extrae name y description del bloque --- YAML del SKILL.md."""
        try:
            lineas = skill_md.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, PermissionError):
            return {}

        en_frontmatter = False
        datos = {}
        for linea in lineas:
            if linea.strip() == "---":
                if not en_frontmatter:
                    en_frontmatter = True
                    continue
                else:
                    break
            if en_frontmatter:
                if linea.startswith("name:"):
                    datos["nombre"] = linea[5:].strip().strip('"')
                elif linea.startswith("description:"):
                    datos["descripcion"] = linea[12:].strip().strip('"')
        return datos

    catalogo = {
        "generado": datetime.now().isoformat(),
        "proyecto": nombre_proyecto,
        "core":     [],
        "opcional": [],
        "stacks":   [],
    }

    if skills_dir.exists():
        # Core: skills sueltos bajo .agents/skills/ (excluir stacks/ y opcional/)
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if skill_dir.name in ("stacks", "opcional"):
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                datos = extraer_frontmatter(skill_md)
                datos["ruta"] = str(skill_dir.relative_to(raiz))
                catalogo["core"].append(datos)

        # Opcional
        opcional_dir = skills_dir / "opcional"
        if opcional_dir.exists():
            for skill_dir in sorted(opcional_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    datos = extraer_frontmatter(skill_md)
                    datos["ruta"] = str(skill_dir.relative_to(raiz))
                    catalogo["opcional"].append(datos)

        # Stacks
        stacks_dir = skills_dir / "stacks"
        if stacks_dir.exists():
            for stack_dir in sorted(stacks_dir.iterdir()):
                if not stack_dir.is_dir():
                    continue

                # Descripcion del stack desde LEEME.md
                descripcion_stack = ""
                leeme = stack_dir / "LEEME.md"
                if leeme.exists():
                    for linea in leeme.read_text(encoding="utf-8").splitlines():
                        if linea.startswith("**Para:**"):
                            descripcion_stack = linea[9:].strip()
                            break

                skills_stack = []

                # Skills bajo stack_dir/skills/*/
                sub_skills_dir = stack_dir / "skills"
                if sub_skills_dir.exists():
                    for skill_dir in sorted(sub_skills_dir.iterdir()):
                        if not skill_dir.is_dir():
                            continue
                        skill_md = skill_dir / "SKILL.md"
                        if skill_md.exists():
                            datos = extraer_frontmatter(skill_md)
                            datos["ruta"] = str(skill_dir.relative_to(raiz))
                            skills_stack.append(datos)

                # Skills directamente bajo stack_dir/ (fuera de skills/), igual que el bash original.
                # Cubre el caso futuro donde un skill viva en stack_dir/<nombre>/SKILL.md
                # en vez de stack_dir/skills/<nombre>/SKILL.md.
                for skill_dir in sorted(stack_dir.iterdir()):
                    if not skill_dir.is_dir():
                        continue
                    if skill_dir.name in ("domain-packs", "skills"):
                        continue
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        datos = extraer_frontmatter(skill_md)
                        datos["ruta"] = str(skill_dir.relative_to(raiz))
                        skills_stack.append(datos)

                catalogo["stacks"].append({
                    "stack":       stack_dir.name,
                    "descripcion": descripcion_stack,
                    "skills":      skills_stack,
                })

    catalogo_path.parent.mkdir(parents=True, exist_ok=True)
    catalogo_path.write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"    ✓ Catálogo generado: {catalogo_path.relative_to(raiz)}")

    total_core    = len(catalogo["core"])
    total_opcional = len(catalogo["opcional"])
    total_stacks  = len(catalogo["stacks"])
    print(f"\n    Resumen de skills descubiertos:")
    print(f"      Core (siempre activas):  {total_core} skills")
    print(f"      Opcional:                {total_opcional} skills")
    print(f"      Stacks disponibles:      {total_stacks}")
    print()
    print(f"    El agente usará este catálogo para preguntar qué activar.")
    print(f"    También puedes revisarlo manualmente: {catalogo_path.relative_to(raiz)}")

    # --- Paso 7: Reporte de placeholders pendientes ---
    print()
    print("[7/7] Verificando placeholders que requieren configuración manual...")

    pendientes: dict = {}
    patron_placeholder = re.compile(r"\{\{[^}]+\}\}")

    for archivo in sorted(raiz.rglob("*")):
        if not archivo.is_file():
            continue
        if archivo.suffix not in extensiones:
            continue
        if archivo.resolve() == Path(__file__).resolve():
            continue
        if archivo.name == "inicializar_proyecto.sh":
            continue
        try:
            contenido = archivo.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for match in patron_placeholder.findall(contenido):
            pendientes.setdefault(match, [])
            ruta_rel = str(archivo.relative_to(raiz))
            if ruta_rel not in pendientes[match]:
                pendientes[match].append(ruta_rel)

    if pendientes:
        print()
        print("    Placeholders pendientes (requieren input manual o del agente):")
        print()
        print(f"    {'PLACEHOLDER':<40} ARCHIVO(S)")
        print(f"    {'---':<40} ---")
        for placeholder, archivos in sorted(pendientes.items()):
            sufijo = f"  (+{len(archivos) - 10} mas)" if len(archivos) > 10 else ""
            print(f"    {placeholder:<40} {', '.join(archivos[:10])}{sufijo}")
    else:
        print("    ✓ No quedan placeholders pendientes")

    # --- Resumen final ---
    print()
    print(f"=== Proyecto {nombre_proyecto} inicializado ===")
    print()
    print("Siguiente paso:")
    print("  1. Edita .env con tus valores reales")
    print("  2. Invoca $iniciar-proyecto con tu agente para completar placeholders y seleccionar skills")
    print(f"     (el agente leerá {catalogo_path.relative_to(raiz)} para saber qué preguntar)")
    print("  3. O rellena los {{placeholders}} manualmente y mueve skills a mano")
    print(f"  4. Haz: git add -A && git commit -m 'init: proyecto {nombre_proyecto} desde plantilla'")


if __name__ == "__main__":
    main()
