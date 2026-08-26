#!/bin/bash
# Inicializa un nuevo proyecto a partir de la plantilla del framework agéntico.
# Uso: ./scripts/inicializar_proyecto.sh <nombre-proyecto> [idioma-nombres]

set -euo pipefail

# --- Configuración ---
NOMBRE_PROYECTO="${1:-}"
IDIOMA_NOMBRES="${2:-español}"

if [ -z "$NOMBRE_PROYECTO" ]; then
  echo "Uso: $0 <nombre-proyecto> [idioma-nombres]"
  echo "  nombre-proyecto: Nombre del proyecto (ej: entrevoces, miapp)"
  echo "  idioma-nombres:  Idioma para nombres de archivos (default: español)"
  exit 1
fi

# --- Validación 1: Centinela de plantilla ---
if [ ! -f ".plantilla-framework" ]; then
  echo "ERROR: No se encontró .plantilla-framework en el directorio actual."
  echo "       Este script solo debe ejecutarse dentro de una copia limpia de la plantilla."
  echo "       Directorio actual: $(pwd)"
  exit 1
fi

# --- Validación 2: Git limpio ---
if [ -d ".git" ]; then
  ESTADO_GIT=$(git status --porcelain 2>/dev/null || true)
  if [ -n "$ESTADO_GIT" ]; then
    echo "ERROR: El árbol de trabajo tiene cambios sin commitear."
    echo "       Haz commit o stash antes de inicializar, para poder revertir con git checkout si algo falla."
    echo ""
    echo "Archivos con cambios:"
    echo "$ESTADO_GIT"
    exit 1
  fi
fi

echo "=== Inicializando proyecto: $NOMBRE_PROYECTO ==="
echo "    Idioma de nombres: $IDIOMA_NOMBRES"
echo ""

# --- Paso 1: Reemplazar placeholders automáticos ---
echo "[1/6] Reemplazando placeholders automáticos..."

ARCHIVOS_CON_PLACEHOLDERS=(
  "AGENTS.md"
  "PROJECT_STATE.md"
  ".agents/rules/excepciones_nominales.md"
  ".agents/skills/cerrar-modulo/SKILL.md"
  ".agents/skills/evaluar-agente/SKILL.md"
  ".agents/skills/probar-e2e/SKILL.md"
  ".agents/skills/opcional/delegar-entre-agentes/SKILL.md"
  "documentacion/prompts/PROMPT_SISTEMA_BASE.md"
  "documentacion/prompts/PROMPT_DELTA_CLAUDE.md"
  "documentacion/prompts/PROMPT_DELTA_ANTIGRAVITY.md"
  "documentacion/prompts/PROMPT_DELTA_CODEX.md"
  "documentacion/REGISTRO_CAMBIOS.md"
  "documentacion/INDICE_LECTURA_AGENTES.md"
  ".env.ejemplo"
)

# Reemplazo seguro con perl (escapa caracteres especiales en búsqueda Y reemplazo)
reemplazar_placeholder() {
  local archivo="$1"
  local placeholder="$2"
  local valor="$3"
  perl -pi -e '
    BEGIN { $p = shift; $v = shift; }
    s/\Q{{$p}}\E/$v/g;
  ' "$placeholder" "$valor" "$archivo"
}

for archivo in "${ARCHIVOS_CON_PLACEHOLDERS[@]}"; do
  if [ -f "$archivo" ]; then
    reemplazar_placeholder "$archivo" "NOMBRE_PROYECTO" "$NOMBRE_PROYECTO"
    reemplazar_placeholder "$archivo" "IDIOMA_NOMBRES" "$IDIOMA_NOMBRES"
    reemplazar_placeholder "$archivo" "PROYECTO" "$NOMBRE_PROYECTO"
    reemplazar_placeholder "$archivo" "PREFIJO_VARIABLES" "$(echo "$NOMBRE_PROYECTO" | tr '[:lower:]' '[:upper:]')"
    echo "    ✓ $archivo"
  fi
done

# --- Paso 2: Crear .env desde ejemplo ---
echo ""
echo "[2/6] Configurando entorno..."

if [ ! -f ".env" ] && [ -f ".env.ejemplo" ]; then
  cp .env.ejemplo .env
  echo "    ✓ .env creado desde .env.ejemplo"
  echo "    ⚠ Edita .env con tus valores reales antes de continuar"
else
  echo "    - .env ya existe o .env.ejemplo no encontrado"
fi

# --- Paso 3: Crear estructura de directorios faltantes ---
echo ""
echo "[3/6] Creando directorios..."

DIRECTORIOS=(
  "documentacion"
  "infraestructura/registros"
  "scripts"
)

for dir in "${DIRECTORIOS[@]}"; do
  mkdir -p "$dir"
  echo "    ✓ $dir/"
done

# --- Paso 4: Inicializar git si no existe ---
echo ""
echo "[4/6] Verificando repositorio git..."

if [ ! -d ".git" ]; then
  git init
  echo "    ✓ Repositorio git inicializado"
else
  echo "    - Repositorio git ya existe"
fi

# --- Paso 5: Eliminar centinela ---
echo ""
echo "[5/6] Limpiando archivos de plantilla..."
rm -f .plantilla-framework
echo "    ✓ .plantilla-framework eliminado"

# --- Paso 6: Reportar placeholders pendientes (requieren input manual) ---
echo ""
echo "[6/6] Verificando placeholders que requieren configuración manual..."

PLACEHOLDERS_MANUALES=(
  "DESCRIPCION_PRODUCTO_UNA_LINEA|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Descripción corta del producto"
  "DESCRIPCION_PRODUCTO_COMPLETA|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Párrafo completo describiendo el producto"
  "OBJETIVO_INMEDIATO|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Objetivo actual del proyecto (ej: completar MVP)"
  "LISTA_PRIORIDADES_NUMERADA|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Lista 1-N con prioridades del MVP"
  "EXCLUSIONES_MVP|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Qué queda fuera del MVP"
  "SECCION_ARQUITECTURA|documentacion/prompts/PROMPT_SISTEMA_BASE.md|Diagrama y reglas de arquitectura"
  "EXCEPCIONES_ADICIONALES|.agents/rules/excepciones_nominales.md|Excepciones de naming específicas del proyecto"
)

echo ""
echo "    Los siguientes placeholders requieren tu input manual:"
echo "    (No son automatizables — dependen del contenido específico de tu proyecto)"
echo ""
printf "    %-35s %-50s %s\n" "PLACEHOLDER" "ARCHIVO" "QUÉ PONER"
printf "    %-35s %-50s %s\n" "---" "---" "---"

for entry in "${PLACEHOLDERS_MANUALES[@]}"; do
  IFS='|' read -r placeholder archivo descripcion <<< "$entry"
  printf "    %-35s %-50s %s\n" "{{$placeholder}}" "$archivo" "$descripcion"
done

# Verificar si hay algún placeholder inesperado no listado arriba
CONOCIDOS="NOMBRE_PROYECTO|IDIOMA_NOMBRES|PROYECTO|PREFIJO_VARIABLES|DESCRIPCION_PRODUCTO_UNA_LINEA|DESCRIPCION_PRODUCTO_COMPLETA|OBJETIVO_INMEDIATO|LISTA_PRIORIDADES_NUMERADA|EXCLUSIONES_MVP|SECCION_ARQUITECTURA|EXCEPCIONES_ADICIONALES"
DESCONOCIDOS=$(grep -roh "{{[^}]*}}" --include="*.md" --include="*.yaml" 2>/dev/null | sort -u | grep -vE "$CONOCIDOS" || true)

if [ -n "$DESCONOCIDOS" ]; then
  echo ""
  echo "    ⚠ Placeholders NO RECONOCIDOS encontrados (posible error en la plantilla):"
  echo "$DESCONOCIDOS" | while read -r p; do
    UBICACION=$(grep -rl "$p" --include="*.md" --include="*.yaml" 2>/dev/null | head -1)
    echo "      - $p en $UBICACION"
  done
fi

echo ""
echo "=== Proyecto $NOMBRE_PROYECTO inicializado ==="
echo ""
echo "Siguiente paso:"
echo "  1. Edita .env con tus valores reales"
echo "  2. Rellena los {{placeholders}} manuales listados arriba"
echo "  3. Haz git add -A && git commit -m 'init: proyecto $NOMBRE_PROYECTO desde plantilla'"
