#!/usr/bin/env python3
"""Comprueba el flujo publico de creacion sin modificar la plantilla fuente."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
CREADOR = RAIZ_FRAMEWORK / "scripts" / "crear_proyecto.py"
CONFIGURACION_EJEMPLO = RAIZ_FRAMEWORK / "ejemplos" / "configuracion_proyecto.ejemplo.json"
SKILLS_ORIGEN = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"
ADAPTADOR_BASH = RAIZ_FRAMEWORK / "plantilla" / "scripts" / "inicializar_proyecto.sh"
PLANTILLA = RAIZ_FRAMEWORK / "plantilla"
CORE_AUTOMATICO: set[str] = {"cerrar-modulo", "lecciones-aprendidas", "probar-e2e"}
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
        ruta.write_text(
            json.dumps(datos, ensure_ascii=False),
            encoding="utf-8",
            newline="\n",
        )
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
        estado: object = json.loads((destino / ".estado-plantilla.json").read_text(encoding="utf-8"))
        self.assertIsInstance(estado, dict)
        instaladas = estado.get("skills_instaladas") if isinstance(estado, dict) else None
        self.assertEqual(set(instaladas) if isinstance(instaladas, list) else set(), CORE_AUTOMATICO)
        registro = (destino / "documentacion" / "REGISTRO_CAMBIOS.md").read_text(encoding="utf-8")
        self.assertIn("agent-framework 0.2.0-alpha.6", registro)
        for nombre in CORE_AUTOMATICO:
            with self.subTest(skill_registrada=nombre):
                self.assertIn(f"- `{nombre}`", registro)
        self.assertNotIn("Stack backend-fastapi + skill fastapi-setup", registro)

    def test_instala_solo_skills_adicionales_confirmadas(self) -> None:
        """Confirma una seleccion mixta de core, stack y Skill opcional."""
        destino = self.raiz_temporal / "proyecto-seleccionado"
        adicionales = {"fastapi-setup", "evaluar-agente", "delegar-entre-agentes"}
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
                "evaluar-agente",
                "--skill",
                "delegar-entre-agentes",
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
        self.assertFalse(
            (destino / ".agents" / "skills" / "stacks" / "frontend-nextjs").exists()
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
        archivo_externo.write_text(
            "Este contenido debe permanecer fuera de la copia.\n",
            encoding="utf-8",
            newline="\n",
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
                    contrato["version_contrato"] = 3
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
                ruta_contrato.write_text(
                    json.dumps(contrato, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
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
        ruta_configuracion.write_text(
            json.dumps(configuracion, ensure_ascii=False),
            encoding="utf-8",
            newline="\n",
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

    def test_inicializacion_directa_revierte_git_si_env_no_esta_protegido(self) -> None:
        """Confirma que un fallo posterior a git init restaure la copia manual."""
        destino = self.copiar_plantilla("copia-gitignore-invalido")
        (destino / ".gitignore").write_text(
            "# Configuracion deliberadamente invalida para la prueba.\n",
            encoding="utf-8",
            newline="\n",
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
        ruta_infraestructura.write_text(
            "Bloquea deliberadamente la creacion del directorio de registros.\n",
            encoding="utf-8",
            newline="\n",
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
