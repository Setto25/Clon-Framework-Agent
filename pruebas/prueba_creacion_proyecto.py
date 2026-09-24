#!/usr/bin/env python3
"""Comprueba el flujo publico de creacion sin modificar la plantilla fuente."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
CREADOR = RAIZ_FRAMEWORK / "scripts" / "crear_proyecto.py"
AGREGADOR_SKILLS = RAIZ_FRAMEWORK / "scripts" / "agregar_skills.py"
CONFIGURACION_EJEMPLO = RAIZ_FRAMEWORK / "ejemplos" / "configuracion_proyecto.ejemplo.json"
SKILLS_ORIGEN = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"
ADAPTADOR_BASH = RAIZ_FRAMEWORK / "plantilla" / "scripts" / "inicializar_proyecto.sh"
PLANTILLA = RAIZ_FRAMEWORK / "plantilla"
CORE_AUTOMATICO: set[str] = {
    "cerrar-modulo",
    "lecciones-aprendidas",
    "optimizar-contexto",
    "probar-e2e",
}
PATRON_NOMBRE_SKILL = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)


def ejecutar(argumentos: list[str], raiz: Path = RAIZ_FRAMEWORK) -> subprocess.CompletedProcess[str]:
    """Ejecuta un proceso con salida UTF-8 capturada."""
    entorno = dict(os.environ)
    entorno["PYTHONUTF8"] = "1"
    return subprocess.run(
        argumentos,
        cwd=raiz,
        env=entorno,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def escribir_texto_lf(ruta: Path, contenido: str) -> None:
    """Escribe texto UTF-8 con saltos LF sin depender de APIs posteriores a Python 3.9."""
    with ruta.open("w", encoding="utf-8", newline="\n") as flujo:
        flujo.write(contenido)


def calcular_huellas(raiz: Path) -> dict[str, str]:
    """Calcula las huellas SHA-256 de todos los archivos de una ruta."""
    return {
        archivo.relative_to(raiz).as_posix(): hashlib.sha256(archivo.read_bytes()).hexdigest()
        for archivo in sorted(raiz.rglob("*"))
        if archivo.is_file()
    }


def descubrir_skills(raiz: Path) -> dict[str, Path]:
    """Relaciona cada nombre de Skill con su directorio instalado."""
    resultado: dict[str, Path] = {}
    for manifiesto in sorted(raiz.rglob("SKILL.md")):
        coincidencia = PATRON_NOMBRE_SKILL.search(manifiesto.read_text(encoding="utf-8"))
        if coincidencia is None:
            raise AssertionError(f"Manifiesto sin nombre: {manifiesto}")
        nombre = coincidencia.group(1).strip().strip("\"'")
        if nombre in resultado:
            raise AssertionError(f"Nombre de Skill duplicado: {nombre}")
        resultado[nombre] = manifiesto.parent
    return resultado


def cargar_modulo_creador() -> ModuleType:
    """Carga el creador y permite probar sus limites sin ejecutar la CLI."""
    ruta_scripts = str(CREADOR.parent)
    sys.path.insert(0, ruta_scripts)
    try:
        especificacion = importlib.util.spec_from_file_location("crear_proyecto_pruebas", CREADOR)
        if especificacion is None or especificacion.loader is None:
            raise RuntimeError("No se pudo cargar scripts/crear_proyecto.py")
        modulo = importlib.util.module_from_spec(especificacion)
        especificacion.loader.exec_module(modulo)
        return modulo
    finally:
        sys.path.remove(ruta_scripts)


class PruebasCreacionProyecto(unittest.TestCase):
    """Verifica los casos criticos del creador de proyectos."""

    temporal: tempfile.TemporaryDirectory[str]
    raiz_temporal: Path

    def setUp(self) -> None:
        """Crea un directorio aislado para cada prueba."""
        self.temporal = tempfile.TemporaryDirectory(prefix="agent-framework-pruebas-")
        self.raiz_temporal = Path(self.temporal.name)

    def tearDown(self) -> None:
        """Elimina la instancia aislada al terminar cada prueba."""
        self.temporal.cleanup()

    def crear_completo(self, nombre_directorio: str = "proyecto-completo") -> Path:
        """Crea una instancia completa mediante la configuracion publicada."""
        destino = self.raiz_temporal / nombre_directorio
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto de Prueba",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        return destino

    def copiar_plantilla(self, nombre_directorio: str) -> Path:
        """Copia la plantilla completa para probar el inicializador interno."""
        destino = self.raiz_temporal / nombre_directorio
        shutil.copytree(PLANTILLA, destino, copy_function=shutil.copy2)
        return destino

    def inicializar_git(self, destino: Path, confirmar: bool) -> str | None:
        """Crea un repositorio temporal y confirma su contenido cuando se solicita."""
        resultado_inicio = ejecutar(["git", "init"], destino)
        self.assertEqual(
            resultado_inicio.returncode,
            0,
            resultado_inicio.stdout + resultado_inicio.stderr,
        )
        if not confirmar:
            return None
        resultado_agregar = ejecutar(["git", "add", "."], destino)
        self.assertEqual(
            resultado_agregar.returncode,
            0,
            resultado_agregar.stdout + resultado_agregar.stderr,
        )
        resultado_commit = ejecutar(
            [
                "git",
                "-c",
                "user.name=Pruebas agent-framework",
                "-c",
                "user.email=pruebas@example.invalid",
                "commit",
                "-m",
                "Registra plantilla sin inicializar",
            ],
            destino,
        )
        self.assertEqual(
            resultado_commit.returncode,
            0,
            resultado_commit.stdout + resultado_commit.stderr,
        )
        resultado_head = ejecutar(["git", "rev-parse", "HEAD"], destino)
        self.assertEqual(resultado_head.returncode, 0, resultado_head.stderr)
        return resultado_head.stdout.strip()

    def escribir_configuracion(
        self,
        nombre_archivo: str,
        valores_adicionales: dict[str, object],
    ) -> Path:
        """Crea una variante aislada de la configuracion publicada."""
        datos: object = json.loads(CONFIGURACION_EJEMPLO.read_text(encoding="utf-8"))
        self.assertIsInstance(datos, dict)
        if not isinstance(datos, dict):
            raise AssertionError("La configuracion de ejemplo no es un objeto JSON")
        datos.update(valores_adicionales)
        ruta = self.raiz_temporal / nombre_archivo
        escribir_texto_lf(ruta, json.dumps(datos, ensure_ascii=False))
        return ruta

    def test_crea_proyecto_completo_y_protege_entorno(self) -> None:
        """Confirma una instancia valida con Git, memoria y entorno protegido."""
        destino = self.crear_completo()
        verificador = destino / "scripts" / "verificar_memoria_proyecto.py"
        resultado_memoria = ejecutar([sys.executable, str(verificador), str(destino), "--json"], destino)
        self.assertEqual(resultado_memoria.returncode, 0, resultado_memoria.stdout + resultado_memoria.stderr)
        informe: object = json.loads(resultado_memoria.stdout)
        self.assertIsInstance(informe, dict)
        self.assertTrue(informe["valido"] if isinstance(informe, dict) else False)
        self.assertTrue((destino / ".git").is_dir())
        self.assertTrue((destino / ".env").is_file())
        resultado_ignorado = ejecutar(["git", "check-ignore", ".env"], destino)
        self.assertEqual(resultado_ignorado.returncode, 0, resultado_ignorado.stdout + resultado_ignorado.stderr)
        skills_origen = descubrir_skills(SKILLS_ORIGEN)
        skills_destino = descubrir_skills(destino / ".agents" / "skills")
        self.assertEqual(set(skills_destino), CORE_AUTOMATICO)
        for nombre, ruta_destino in skills_destino.items():
            with self.subTest(skill=nombre):
                self.assertEqual(calcular_huellas(skills_origen[nombre]), calcular_huellas(ruta_destino))
        adaptadores_claude = {
            ruta.parent.name: ruta
            for ruta in (destino / ".claude" / "skills").glob("*/SKILL.md")
        }
        self.assertEqual(set(adaptadores_claude), CORE_AUTOMATICO)
        for nombre, ruta_adaptador in adaptadores_claude.items():
            with self.subTest(adaptador_claude=nombre):
                contenido_adaptador = ruta_adaptador.read_text(encoding="utf-8")
                self.assertIn("adaptador-generado-por-agent-framework", contenido_adaptador)
                self.assertIn("../../../.agents/skills/", contenido_adaptador)
        estado: object = json.loads((destino / ".estado-plantilla.json").read_text(encoding="utf-8"))
        self.assertIsInstance(estado, dict)
        instaladas = estado.get("skills_instaladas") if isinstance(estado, dict) else None
        self.assertEqual(set(instaladas) if isinstance(instaladas, list) else set(), CORE_AUTOMATICO)
        huellas_gestionadas = estado.get("huellas_gestionadas") if isinstance(estado, dict) else None
        self.assertIsInstance(huellas_gestionadas, dict)
        if isinstance(huellas_gestionadas, dict):
            self.assertIn("scripts/diagnosticar_tarea.py", huellas_gestionadas)
            self.assertIn("scripts/contrato_validacion.py", huellas_gestionadas)
            self.assertIn("contrato_validacion.ejemplo.json", huellas_gestionadas)
            self.assertIn("scripts/verificar_memoria_proyecto.py", huellas_gestionadas)
            self.assertIn("scripts/validar_cierre_tarea.py", huellas_gestionadas)
            self.assertIn("scripts/validar_integridad_proyecto.py", huellas_gestionadas)
            self.assertIn(".github/workflows/validacion-proyecto.yml", huellas_gestionadas)
            self.assertIn("scripts/generar_indice_contexto.py", huellas_gestionadas)
            self.assertIn("scripts/sincronizar_adaptadores_agentes.py", huellas_gestionadas)
            self.assertIn(".claude/skills/optimizar-contexto/SKILL.md", huellas_gestionadas)
            self.assertIn(".agents/skills/optimizar-contexto/SKILL.md", huellas_gestionadas)
            self.assertIn(
                ".agents/skills/optimizar-contexto/referencias/modo_extendido.md",
                huellas_gestionadas,
            )
            self.assertIn(
                ".agents/skills/optimizar-contexto/referencias/modo_arquitectonico.md",
                huellas_gestionadas,
            )
        self.assertTrue((destino / "scripts" / "generar_indice_contexto.py").is_file())
        self.assertTrue((destino / "scripts" / "diagnosticar_tarea.py").is_file())
        self.assertTrue((destino / "scripts" / "validar_cierre_tarea.py").is_file())
        self.assertTrue((destino / "scripts" / "validar_integridad_proyecto.py").is_file())
        self.assertTrue((destino / ".github" / "workflows" / "validacion-proyecto.yml").is_file())
        self.assertTrue((destino / "scripts" / "contrato_validacion.py").is_file())
        self.assertTrue((destino / "contrato_validacion.ejemplo.json").is_file())
        self.assertTrue((destino / "CLAUDE.md").is_file())
        self.assertTrue(
            (destino / ".agents" / "rules" / "00-contexto-framework.md").is_file()
        )
        registro = (destino / "documentacion" / "REGISTRO_CAMBIOS.md").read_text(encoding="utf-8")
        self.assertIn("agent-framework 0.2.0-alpha.18", registro)
        for nombre in CORE_AUTOMATICO:
            with self.subTest(skill_registrada=nombre):
                self.assertIn(f"- `{nombre}`", registro)
        self.assertNotIn("Stack backend-fastapi + skill fastapi-setup", registro)

    def test_rechaza_escape_multilinea_literal_de_powershell(self) -> None:
        """Rechaza un valor que PowerShell no convirtio en salto de linea real."""
        destino = self.raiz_temporal / "proyecto-escape-powershell"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Escape",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
                "--valor",
                "LISTA_OBLIGATORIOS=- Primera tarea`n- Segunda tarea",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("--configuracion", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_instala_solo_skills_adicionales_confirmadas(self) -> None:
        """Confirma una seleccion mixta de core, stack y Skill opcional."""
        destino = self.raiz_temporal / "proyecto-seleccionado"
        adicionales = {
            "fastapi-setup",
            "seguridad-backend",
            "evaluar-agente",
            "delegar-entre-agentes",
            "desarrollar-servidores-mcp",
        }
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Seleccionado",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
                "--skill",
                "fastapi-setup",
                "--skill",
                "seguridad-backend",
                "--skill",
                "evaluar-agente",
                "--skill",
                "delegar-entre-agentes",
                "--skill",
                "desarrollar-servidores-mcp",
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        skills_origen = descubrir_skills(SKILLS_ORIGEN)
        skills_destino = descubrir_skills(destino / ".agents" / "skills")
        self.assertEqual(set(skills_destino), CORE_AUTOMATICO | adicionales)
        for nombre, ruta_destino in skills_destino.items():
            with self.subTest(skill=nombre):
                self.assertEqual(calcular_huellas(skills_origen[nombre]), calcular_huellas(ruta_destino))
        self.assertTrue(
            (destino / ".agents" / "skills" / "stacks" / "backend-fastapi" / "LEEME.md").is_file()
        )
        adaptadores = {
            ruta.parent.name
            for ruta in (destino / ".claude" / "skills").glob("*/SKILL.md")
        }
        self.assertEqual(adaptadores, CORE_AUTOMATICO | adicionales)
        self.assertFalse(
            (destino / ".agents" / "skills" / "stacks" / "frontend-nextjs").exists()
        )
        referencia_mcp = (
            destino
            / ".agents"
            / "skills"
            / "stacks"
            / "ia-llm"
            / "skills"
            / "desarrollar-servidores-mcp"
            / "referencias"
            / "arquitectura_servidor.md"
        )
        self.assertTrue(referencia_mcp.is_file())

    def test_agrega_skill_confirmada_a_proyecto_inicializado(self) -> None:
        """Confirma la instalacion posterior de una Skill con referencias."""
        destino = self.crear_completo("proyecto-con-skill-agregada")
        resultado = ejecutar(
            [
                sys.executable,
                str(AGREGADOR_SKILLS),
                str(destino),
                "--skill",
                "desarrollar-servidores-mcp",
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        skills_origen = descubrir_skills(SKILLS_ORIGEN)
        skills_destino = descubrir_skills(destino / ".agents" / "skills")
        self.assertEqual(set(skills_destino), CORE_AUTOMATICO | {"desarrollar-servidores-mcp"})
        self.assertEqual(
            calcular_huellas(skills_origen["desarrollar-servidores-mcp"]),
            calcular_huellas(skills_destino["desarrollar-servidores-mcp"]),
        )
        adaptador = destino / ".claude" / "skills" / "desarrollar-servidores-mcp" / "SKILL.md"
        self.assertTrue(adaptador.is_file())
        self.assertIn(
            "../../../.agents/skills/stacks/ia-llm/skills/desarrollar-servidores-mcp/SKILL.md",
            adaptador.read_text(encoding="utf-8"),
        )
        estado: object = json.loads((destino / ".estado-plantilla.json").read_text(encoding="utf-8"))
        self.assertIsInstance(estado, dict)
        instaladas = estado.get("skills_instaladas") if isinstance(estado, dict) else None
        self.assertEqual(set(instaladas) if isinstance(instaladas, list) else set(), set(skills_destino))
        historial = estado.get("actualizaciones_skills") if isinstance(estado, dict) else None
        self.assertIsInstance(historial, list)

    def test_rechaza_skill_ya_instalada_sin_alterar_estado(self) -> None:
        """Impide repetir una Skill y conserva la instancia sin cambios."""
        destino = self.crear_completo("proyecto-con-skill-existente")
        estado_antes = (destino / ".estado-plantilla.json").read_bytes()
        resultado = ejecutar(
            [
                sys.executable,
                str(AGREGADOR_SKILLS),
                str(destino),
                "--skill",
                "cerrar-modulo",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual((destino / ".estado-plantilla.json").read_bytes(), estado_antes)

    def test_agrega_varias_skills_del_mismo_stack(self) -> None:
        """Conserva el LEEME cuando incorpora un stack completo por primera vez."""
        destino = self.crear_completo("proyecto-con-stack-agregado")
        resultado = ejecutar(
            [
                sys.executable,
                str(AGREGADOR_SKILLS),
                str(destino),
                "--skill",
                "desarrollar-firmware",
                "--skill",
                "diagnosticar-hardware",
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        skills_destino = descubrir_skills(destino / ".agents" / "skills")
        self.assertTrue({"desarrollar-firmware", "diagnosticar-hardware"}.issubset(skills_destino))
        self.assertTrue(
            (destino / ".agents" / "skills" / "stacks" / "firmware-esp32" / "LEEME.md").is_file()
        )

    def test_rechaza_una_skill_desconocida_sin_publicar_destino(self) -> None:
        """Confirma que una seleccion invalida falle antes de copiar la plantilla."""
        destino = self.raiz_temporal / "proyecto-skill-invalida"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Invalido",
                "--permitir-pendientes",
                "--skill",
                "skill-inexistente",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("Skills desconocidas", resultado.stderr)
        self.assertFalse(destino.exists())
        self.assertEqual(list(self.raiz_temporal.glob(".proyecto-temporal-*")), [])

    def test_adaptador_bash_no_duplica_la_inicializacion(self) -> None:
        """Confirma que el respaldo Bash delegue sin administrar Skills."""
        contenido = ADAPTADOR_BASH.read_text(encoding="utf-8")
        self.assertIn("inicializar_proyecto.py", contenido)
        self.assertIn("exec python", contenido)
        for fragmento in ("catalogo_skills.json", "mv .agents", "perl -pi", "grep -rl"):
            with self.subTest(fragmento=fragmento):
                self.assertNotIn(fragmento, contenido)

    def test_escapa_nombre_visible_en_dotenv(self) -> None:
        """Confirma que comillas y comentarios no alteren PROJECT_NAME."""
        destino = self.raiz_temporal / "proyecto-nombre-especial"
        nombre = 'Proyecto "Especial" #1'
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                nombre,
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        contenido_env = (destino / ".env").read_text(encoding="utf-8")
        self.assertIn('PROJECT_NAME="Proyecto \\"Especial\\" #1"', contenido_env)

    def test_rechaza_nombre_con_salto_de_linea(self) -> None:
        """Impide que el nombre visible inyecte otra linea de configuracion."""
        destino = self.raiz_temporal / "proyecto-nombre-invalido"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Valido\nVARIABLE_INYECTADA=1",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("caracteres de control", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_valor_derivado_en_configuracion(self) -> None:
        """Impide que una entrada externa suplante metadatos derivados."""
        destino = self.raiz_temporal / "proyecto-derivado-externo"
        configuracion = self.escribir_configuracion(
            "configuracion-derivada.json",
            {"VERSION_FRAMEWORK": "9.9.9"},
        )
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Derivado",
                "--configuracion",
                str(configuracion),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("valores derivados no se aceptan", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_clave_repetida_entre_fuentes(self) -> None:
        """Impide precedencias silenciosas entre JSON y argumentos directos."""
        destino = self.raiz_temporal / "proyecto-clave-repetida"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Repetido",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
                "--valor",
                "ZONA_HORARIA=UTC",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("ZONA_HORARIA se definio mas de una vez", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_clave_repetida_en_valores_directos(self) -> None:
        """Impide que dos argumentos directos oculten una seleccion anterior."""
        destino = self.raiz_temporal / "proyecto-valor-repetido"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Repetido",
                "--permitir-pendientes",
                "--valor",
                "ZONA_HORARIA=UTC",
                "--valor",
                "ZONA_HORARIA=America/Santiago",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("--valor repite la clave: ZONA_HORARIA", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_control_unicode_en_configuracion(self) -> None:
        """Impide insertar controles Unicode invisibles en los artefactos."""
        destino = self.raiz_temporal / "proyecto-control-unicode"
        configuracion = self.escribir_configuracion(
            "configuracion-control.json",
            {"DESCRIPCION_OBJETIVO": "Texto visible\u202eoculto"},
        )
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Control",
                "--configuracion",
                str(configuracion),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("caracteres de control no permitidos", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_enlace_externo_en_copia_manual(self) -> None:
        """Impide que la inicializacion lea contenido enlazado fuera de la copia."""
        destino = self.copiar_plantilla("copia-enlace-externo")
        archivo_externo = self.raiz_temporal / "contenido-externo.txt"
        escribir_texto_lf(
            archivo_externo,
            "Este contenido debe permanecer fuera de la copia.\n",
        )
        enlace = destino / "enlace-externo.txt"
        try:
            enlace.symlink_to(archivo_externo)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"El entorno no permite crear enlaces simbolicos: {error}")
        huellas_antes = calcular_huellas(destino)
        contenido_externo_antes = archivo_externo.read_bytes()
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Enlace",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("enlace o reparse point no permitido", resultado.stderr)
        self.assertEqual(calcular_huellas(destino), huellas_antes)
        self.assertEqual(archivo_externo.read_bytes(), contenido_externo_antes)
        self.assertFalse((destino / ".git").exists())

    def test_rechaza_destino_existente_como_enlace_roto(self) -> None:
        """Impide publicar sobre un nombre ocupado por un enlace roto."""
        objetivo_inexistente = self.raiz_temporal / "objetivo-inexistente"
        destino = self.raiz_temporal / "destino-enlace-roto"
        try:
            destino.symlink_to(objetivo_inexistente, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"El entorno no permite crear enlaces simbolicos: {error}")
        self.assertFalse(destino.exists())
        self.assertTrue(os.path.lexists(destino))
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Enlace Roto",
                "--permitir-pendientes",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("existe, incluso como enlace", resultado.stderr)
        self.assertTrue(os.path.lexists(destino))
        self.assertFalse(objetivo_inexistente.exists())
        self.assertEqual(list(self.raiz_temporal.glob(".proyecto-temporal-*")), [])

    def test_rechaza_destino_aparecido_antes_de_publicar(self) -> None:
        """Confirma que la publicacion tardia no reemplace un destino nuevo."""
        modulo = cargar_modulo_creador()
        temporal = self.raiz_temporal / ".proyecto-temporal-publicacion"
        destino = self.raiz_temporal / "destino-aparecido"
        padre_lexico = self.raiz_temporal / ".." / self.raiz_temporal.name
        temporal.mkdir()
        destino.mkdir()
        with self.assertRaisesRegex(ValueError, "aparecio durante la creacion"):
            modulo.publicar_temporal(temporal, destino, padre_lexico)
        self.assertTrue(temporal.is_dir())
        self.assertTrue(destino.is_dir())

    def test_normaliza_permisos_del_temporal(self) -> None:
        """Confirma que la copia publicada quede editable por su propietario."""
        modulo = cargar_modulo_creador()
        temporal = self.raiz_temporal / "temporal-permisos"
        temporal.mkdir()
        archivo = temporal / "solo-lectura.txt"
        escribir_texto_lf(archivo, "Contenido preservado.\n")
        contenido_antes = archivo.read_bytes()
        archivo.chmod(stat.S_IREAD)
        modulo.normalizar_permisos_arbol(temporal)
        self.assertTrue(stat.S_IMODE(archivo.stat().st_mode) & stat.S_IWUSR)
        self.assertEqual(archivo.read_bytes(), contenido_antes)

    def test_aplica_limites_acumulados_del_arbol(self) -> None:
        """Confirma limites de cantidad y tamaño total sin consumir recursos reales."""
        modulo = cargar_modulo_creador()
        arbol = self.raiz_temporal / "arbol-limitado"
        arbol.mkdir()
        (arbol / "a.txt").write_text("a", encoding="utf-8")
        (arbol / "b.txt").write_text("b", encoding="utf-8")
        with mock.patch.object(modulo, "MAXIMO_ENTRADAS_ARBOL", 1):
            with self.assertRaisesRegex(ValueError, "supera el maximo de 1 entradas"):
                modulo.validar_arbol_sin_enlaces(arbol)
        with mock.patch.object(modulo, "MAXIMO_BYTES_TOTALES", 1):
            with self.assertRaisesRegex(ValueError, "supera el maximo total de 1 bytes"):
                modulo.validar_arbol_sin_enlaces(arbol)

    def test_rechaza_cache_generada_en_copia_manual(self) -> None:
        """Impide inicializar residuos ignorados que una copia manual incluiria."""
        destino = self.copiar_plantilla("copia-cache-generada")
        cache = destino / "scripts" / "__pycache__"
        cache.mkdir()
        (cache / "residuo.pyc").write_bytes(b"bytecode no confiable")
        huellas_antes = calcular_huellas(destino)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Cache",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("artefacto generado no permitido", resultado.stderr)
        self.assertEqual(calcular_huellas(destino), huellas_antes)
        self.assertFalse((destino / ".git").exists())

    def test_rechaza_archivo_excesivo_en_copia_manual(self) -> None:
        """Impide consumir recursos sin limite al inspeccionar una copia manipulada."""
        destino = self.copiar_plantilla("copia-archivo-excesivo")
        archivo_grande = destino / "archivo-excesivo.bin"
        with archivo_grande.open("wb") as flujo:
            flujo.truncate(20 * 1024 * 1024 + 1)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Grande",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("archivo mayor", resultado.stderr)
        self.assertEqual(archivo_grande.stat().st_size, 20 * 1024 * 1024 + 1)
        self.assertTrue((destino / ".plantilla-framework").is_file())
        self.assertFalse((destino / ".git").exists())

    def test_rechaza_archivo_administrado_solo_lectura(self) -> None:
        """Devuelve un error claro antes de modificar una copia no escribible."""
        destino = self.copiar_plantilla("copia-solo-lectura")
        archivo = destino / ".env.ejemplo"
        archivo.chmod(stat.S_IREAD)
        try:
            resultado = ejecutar(
                [
                    sys.executable,
                    str(destino / "scripts" / "inicializar_proyecto.py"),
                    "Proyecto Lectura",
                    "español",
                    "--configuracion",
                    str(CONFIGURACION_EJEMPLO),
                ],
                destino,
            )
            self.assertNotEqual(resultado.returncode, 0)
            self.assertIn("no permite escritura del propietario", resultado.stderr)
            self.assertTrue((destino / ".plantilla-framework").is_file())
            self.assertFalse((destino / ".git").exists())
        finally:
            archivo.chmod(stat.S_IREAD | stat.S_IWRITE)

    def test_rechaza_configuracion_json_excesiva(self) -> None:
        """Impide cargar en memoria una configuracion externa sin limite."""
        destino = self.raiz_temporal / "proyecto-json-excesivo"
        configuracion = self.raiz_temporal / "configuracion-excesiva.json"
        with configuracion.open("wb") as flujo:
            flujo.truncate(1024 * 1024 + 1)
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto JSON",
                "--configuracion",
                str(configuracion),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("configuracion de proyecto supera el maximo", resultado.stderr)
        self.assertFalse(destino.exists())
        self.assertEqual(list(self.raiz_temporal.glob(".proyecto-temporal-*")), [])

    def test_rechaza_valor_de_configuracion_excesivo(self) -> None:
        """Impide multiplicar contenido desproporcionado durante los reemplazos."""
        destino = self.raiz_temporal / "proyecto-valor-excesivo"
        configuracion = self.escribir_configuracion(
            "configuracion-valor-excesivo.json",
            {"DESCRIPCION_OBJETIVO": "x" * 100_001},
        )
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Valor",
                "--configuracion",
                str(configuracion),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("supera el maximo de 100000 caracteres", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_rechaza_contratos_incompatibles_sin_escribir(self) -> None:
        """Confirma que versiones, rutas, claves y origenes fallen sin mutar."""
        casos = (
            ("version-futura", "version_contrato no soportada"),
            ("version-framework-invalida", "version_framework debe usar una version semantica valida"),
            ("clave-desconocida", "contrato contiene claves desconocidas"),
            ("ruta-insegura", "ruta no portable o insegura"),
            ("ruta-duplicada", "rutas duplicadas"),
            ("origen-desconocido", "origen debe ser uno de"),
            ("origen-no-textual", "origen debe ser uno de"),
        )
        for caso, mensaje in casos:
            with self.subTest(caso=caso):
                destino = self.copiar_plantilla(f"copia-contrato-{caso}")
                ruta_contrato = destino / "configuracion_plantilla.json"
                contrato: object = json.loads(ruta_contrato.read_text(encoding="utf-8"))
                self.assertIsInstance(contrato, dict)
                if not isinstance(contrato, dict):
                    raise AssertionError("El contrato publicado no es un objeto JSON")
                if caso == "version-futura":
                    contrato["version_contrato"] = 4
                elif caso == "version-framework-invalida":
                    contrato["version_framework"] = "version futura"
                elif caso == "clave-desconocida":
                    contrato["campo_inesperado"] = True
                elif caso in {"ruta-insegura", "ruta-duplicada"}:
                    archivos_incluidos = contrato.get("archivos_incluidos")
                    self.assertIsInstance(archivos_incluidos, list)
                    if not isinstance(archivos_incluidos, list):
                        raise AssertionError("El contrato no declara archivos_incluidos")
                    if caso == "ruta-insegura":
                        archivos_incluidos.append("../secreto.md")
                    else:
                        archivos_incluidos.append(archivos_incluidos[0])
                else:
                    placeholders = contrato.get("placeholders")
                    self.assertIsInstance(placeholders, dict)
                    if not isinstance(placeholders, dict):
                        raise AssertionError("El contrato no declara placeholders")
                    zona_horaria = placeholders.get("ZONA_HORARIA")
                    self.assertIsInstance(zona_horaria, dict)
                    if not isinstance(zona_horaria, dict):
                        raise AssertionError("ZONA_HORARIA no declara un campo contractual")
                    zona_horaria["origen"] = ["usuario"] if caso == "origen-no-textual" else "externo"
                escribir_texto_lf(
                    ruta_contrato,
                    json.dumps(contrato, ensure_ascii=False, indent=2) + "\n",
                )
                huellas_antes = calcular_huellas(destino)
                resultado = ejecutar(
                    [
                        sys.executable,
                        str(destino / "scripts" / "inicializar_proyecto.py"),
                        "Proyecto Contrato",
                        "español",
                        "--configuracion",
                        str(CONFIGURACION_EJEMPLO),
                    ],
                    destino,
                )
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(mensaje, resultado.stderr)
                self.assertEqual(calcular_huellas(destino), huellas_antes)
                self.assertFalse((destino / ".git").exists())

    def test_inicializacion_directa_rechaza_placeholder_antes_de_escribir(self) -> None:
        """Confirma que contenido ambiguo no deje una copia parcialmente configurada."""
        destino = self.copiar_plantilla("copia-placeholder-invalido")
        configuracion: object = json.loads(CONFIGURACION_EJEMPLO.read_text(encoding="utf-8"))
        self.assertIsInstance(configuracion, dict)
        if isinstance(configuracion, dict):
            configuracion["SIGUIENTE_PASO"] = "Resolver {{VALOR_FUTURO}}"
        ruta_configuracion = self.raiz_temporal / "configuracion-placeholder.json"
        escribir_texto_lf(
            ruta_configuracion,
            json.dumps(configuracion, ensure_ascii=False),
        )
        huellas_antes = calcular_huellas(destino)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Directo",
                "español",
                "--configuracion",
                str(ruta_configuracion),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("reintroduce placeholders", resultado.stderr)
        self.assertEqual(calcular_huellas(destino), huellas_antes)
        self.assertFalse((destino / ".git").exists())
        self.assertFalse((destino / ".estado-plantilla.json").exists())

    def test_inicializacion_directa_acepta_repositorio_limpio_preexistente(self) -> None:
        """Conserva un repositorio limpio y aplica la configuracion sin crear otro Git."""
        destino = self.copiar_plantilla("copia-git-limpio")
        head_antes = self.inicializar_git(destino, confirmar=True)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Git Limpio",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertTrue((destino / ".git").is_dir())
        self.assertTrue((destino / ".estado-plantilla.json").is_file())
        head_despues = ejecutar(["git", "rev-parse", "HEAD"], destino)
        self.assertEqual(head_despues.returncode, 0, head_despues.stderr)
        self.assertEqual(head_despues.stdout.strip(), head_antes)

    def test_inicializacion_directa_acepta_repositorio_sin_commit(self) -> None:
        """Conserva un repositorio preexistente que todavia no contiene commits."""
        destino = self.copiar_plantilla("copia-git-sin-commit")
        self.inicializar_git(destino, confirmar=False)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Git Nuevo",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertTrue((destino / ".git").is_dir())
        self.assertTrue((destino / ".estado-plantilla.json").is_file())
        referencia = ejecutar(["git", "rev-parse", "--verify", "HEAD"], destino)
        self.assertNotEqual(referencia.returncode, 0)

    def test_inicializacion_directa_rechaza_repositorio_con_cambios(self) -> None:
        """Preserva un repositorio preexistente cuando contiene cambios rastreados."""
        destino = self.copiar_plantilla("copia-git-con-cambios")
        self.inicializar_git(destino, confirmar=True)
        ruta_gitignore = destino / ".gitignore"
        contenido_modificado = ruta_gitignore.read_text(encoding="utf-8") + "\n# Cambio de prueba.\n"
        escribir_texto_lf(ruta_gitignore, contenido_modificado)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Git Modificado",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("cambios rastreados sin confirmar", resultado.stderr)
        self.assertEqual(ruta_gitignore.read_text(encoding="utf-8"), contenido_modificado)
        self.assertTrue((destino / ".git").is_dir())
        self.assertTrue((destino / ".plantilla-framework").is_file())
        self.assertFalse((destino / ".estado-plantilla.json").exists())

    def test_inicializacion_directa_rechaza_operacion_git_activa(self) -> None:
        """Preserva la copia cuando un repositorio preexistente esta en una operacion Git."""
        destino = self.copiar_plantilla("copia-git-operacion-activa")
        self.inicializar_git(destino, confirmar=True)
        marcador = destino / ".git" / "rebase-merge"
        marcador.mkdir()
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Git Operacion",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("operacion Git activa: rebase-merge", resultado.stderr)
        self.assertTrue(marcador.is_dir())
        self.assertTrue((destino / ".plantilla-framework").is_file())
        self.assertFalse((destino / ".estado-plantilla.json").exists())

    def test_inicializacion_directa_revierte_git_si_env_no_esta_protegido(self) -> None:
        """Confirma que un fallo posterior a git init restaure la copia manual."""
        destino = self.copiar_plantilla("copia-gitignore-invalido")
        escribir_texto_lf(
            destino / ".gitignore",
            "# Configuracion deliberadamente invalida para la prueba.\n",
        )
        huellas_antes = calcular_huellas(destino)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Directo",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn(".env no esta protegido", resultado.stderr)
        self.assertEqual(calcular_huellas(destino), huellas_antes)
        self.assertFalse((destino / ".git").exists())
        self.assertTrue((destino / ".plantilla-framework").is_file())

    def test_inicializacion_directa_revierte_archivos_tras_escribir(self) -> None:
        """Confirma que un fallo tardio restaure archivos, centinela y Git."""
        destino = self.copiar_plantilla("copia-fallo-tardio")
        ruta_infraestructura = destino / "infraestructura"
        escribir_texto_lf(
            ruta_infraestructura,
            "Bloquea deliberadamente la creacion del directorio de registros.\n",
        )
        huellas_antes = calcular_huellas(destino)
        resultado = ejecutar(
            [
                sys.executable,
                str(destino / "scripts" / "inicializar_proyecto.py"),
                "Proyecto Directo",
                "español",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ],
            destino,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual(calcular_huellas(destino), huellas_antes)
        self.assertFalse((destino / ".git").exists())
        self.assertFalse((destino / ".estado-plantilla.json").exists())
        self.assertFalse((destino / ".env").exists())
        self.assertTrue((destino / ".plantilla-framework").is_file())

    def test_rechaza_memoria_con_pendientes(self) -> None:
        """Confirma que una instancia provisional no se certifique como completa."""
        destino = self.raiz_temporal / "proyecto-pendiente"
        resultado_creacion = ejecutar(
            [sys.executable, str(CREADOR), str(destino), "Proyecto Pendiente", "--permitir-pendientes"]
        )
        self.assertEqual(resultado_creacion.returncode, 0, resultado_creacion.stdout + resultado_creacion.stderr)
        verificador = destino / "scripts" / "verificar_memoria_proyecto.py"
        resultado_memoria = ejecutar([sys.executable, str(verificador), str(destino), "--json"], destino)
        self.assertNotEqual(resultado_memoria.returncode, 0)
        informe: object = json.loads(resultado_memoria.stdout)
        self.assertIsInstance(informe, dict)
        pendientes = informe.get("pendientes_inicializacion") if isinstance(informe, dict) else None
        self.assertIsInstance(pendientes, dict)
        self.assertEqual(
            set(pendientes) if isinstance(pendientes, dict) else set(),
            {
                "DESCRIPCION_OBJETIVO",
                "LISTA_EXCLUIDOS",
                "LISTA_OBLIGATORIOS",
                "REGLAS_ARQUITECTURA",
                "SIGUIENTE_PASO",
                "ZONA_HORARIA",
            },
        )

    def test_limpia_temporal_cuando_falla_la_configuracion(self) -> None:
        """Confirma que un fallo no publique ni abandone una copia parcial."""
        destino = self.raiz_temporal / "proyecto-fallido"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Fallido",
                "--valor",
                "CLAVE_INEXISTENTE=valor",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(destino.exists())
        temporales_huerfanos = list(self.raiz_temporal.glob(".proyecto-temporal-*"))
        self.assertEqual(temporales_huerfanos, [])

    def test_rechaza_sobrescribir_un_destino_existente(self) -> None:
        """Confirma que una segunda creacion no altere el proyecto existente."""
        destino = self.crear_completo()
        estado_antes = (destino / ".estado-plantilla.json").read_bytes()
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Repetido",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual((destino / ".estado-plantilla.json").read_bytes(), estado_antes)


if __name__ == "__main__":
    unittest.main()
