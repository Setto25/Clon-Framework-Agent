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
echo "[1/7] Reemplazando placeholders automáticos..."

# Descubrir dinámicamente todos los archivos con placeholders
mapfile -t ARCHIVOS_CON_PLACEHOLDERS < <(grep -rl "{{" --include="*.md" --include="*.yaml" --include="*.sh" 2>/dev/null | sort)

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
    reemplazar_placeholder "$archivo" "PREFIJO_VARIABLES" "$(echo "$NOMBRE_PROYECTO" | tr '[:lower:]' '[:upper:]' | tr '-' '_')"
    echo "    ✓ $archivo"
  fi
done

# --- Paso 2: Crear .env desde ejemplo ---
echo ""
echo "[2/7] Configurando entorno..."

if [ ! -f ".env" ] && [ -f ".env.ejemplo" ]; then
  cp .env.ejemplo .env
  echo "    ✓ .env creado desde .env.ejemplo"
  echo "    ⚠ Edita .env con tus valores reales antes de continuar"
else
  echo "    - .env ya existe o .env.ejemplo no encontrado"
fi

# --- Paso 3: Crear estructura de directorios faltantes ---
echo ""
echo "[3/7] Creando directorios..."

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
echo "[4/7] Verificando repositorio git..."

if [ ! -d ".git" ]; then
  git init
  echo "    ✓ Repositorio git inicializado"
else
  echo "    - Repositorio git ya existe"
fi

# --- Paso 5: Eliminar centinela ---
echo ""
echo "[5/7] Limpiando archivos de plantilla..."
rm -f .plantilla-framework
echo "    ✓ .plantilla-framework eliminado"

# --- Paso 6: Descubrir y catalogar skills disponibles ---
echo ""
echo "[6/7] Descubriendo skills disponibles..."

CATALOGO=".agents/skills/catalogo_skills.json"
SKILLS_DIR=".agents/skills"

# Función: extraer descripción del frontmatter YAML de un SKILL.md
extraer_descripcion() {
  local skill_md="$1"
  # Extrae el campo description: del frontmatter YAML (entre ---)
  sed -n '/^---$/,/^---$/p' "$skill_md" | grep -m1 "^description:" | sed 's/^description:[[:space:]]*//'
}

# Función: extraer nombre del frontmatter YAML de un SKILL.md
extraer_nombre() {
  local skill_md="$1"
  sed -n '/^---$/,/^---$/p' "$skill_md" | grep -m1 "^name:" | sed 's/^name:[[:space:]]*//'
}

# Iniciar JSON
echo '{' > "$CATALOGO"
echo '  "generado": "'$(date -Iseconds)'",' >> "$CATALOGO"
echo '  "proyecto": "'"$NOMBRE_PROYECTO"'",' >> "$CATALOGO"

# --- Core skills (siempre activas) ---
echo '  "core": [' >> "$CATALOGO"
FIRST=true
for skill_dir in "$SKILLS_DIR"/*/; do
  # Saltar stacks/, opcional/, y la propia carpeta iniciar-proyecto despues de init
  skill_nombre=$(basename "$skill_dir")
  if [[ "$skill_nombre" == "stacks" || "$skill_nombre" == "opcional" ]]; then
    continue
  fi
  skill_md="$skill_dir/SKILL.md"
  if [ -f "$skill_md" ]; then
    nombre=$(extraer_nombre "$skill_md")
    descripcion=$(extraer_descripcion "$skill_md")
    if [ "$FIRST" = true ]; then FIRST=false; else echo ',' >> "$CATALOGO"; fi
    printf '    {"nombre": "%s", "ruta": "%s", "descripcion": "%s"}' \
      "$nombre" "$skill_dir" "$descripcion" >> "$CATALOGO"
  fi
done
echo '' >> "$CATALOGO"
echo '  ],' >> "$CATALOGO"

# --- Skills opcionales ---
echo '  "opcional": [' >> "$CATALOGO"
FIRST=true
if [ -d "$SKILLS_DIR/opcional" ]; then
  for skill_dir in "$SKILLS_DIR/opcional"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_md="$skill_dir/SKILL.md"
    if [ -f "$skill_md" ]; then
      nombre=$(extraer_nombre "$skill_md")
      descripcion=$(extraer_descripcion "$skill_md")
      if [ "$FIRST" = true ]; then FIRST=false; else echo ',' >> "$CATALOGO"; fi
      printf '    {"nombre": "%s", "ruta": "%s", "descripcion": "%s"}' \
        "$nombre" "$skill_dir" "$descripcion" >> "$CATALOGO"
    fi
  done
fi
echo '' >> "$CATALOGO"
echo '  ],' >> "$CATALOGO"

# --- Stacks (agrupados por stack) ---
echo '  "stacks": [' >> "$CATALOGO"
FIRST_STACK=true
if [ -d "$SKILLS_DIR/stacks" ]; then
  for stack_dir in "$SKILLS_DIR/stacks"/*/; do
    [ -d "$stack_dir" ] || continue
    stack_nombre=$(basename "$stack_dir")

    # Leer descripción del stack desde LEEME.md si existe
    stack_descripcion=""
    if [ -f "$stack_dir/LEEME.md" ]; then
      # Tomar la línea "**Para:**" del LEEME como descripción corta
      stack_descripcion=$(grep -m1 "^\*\*Para:\*\*" "$stack_dir/LEEME.md" | sed 's/\*\*Para:\*\*[[:space:]]*//' || echo "")
    fi

    # Descubrir skills dentro del stack (excluir domain-packs/ y skills/)
    SKILLS_EN_STACK=""
    FIRST_SKILL=true
    for sub_skill_dir in "$stack_dir"*/; do
      [ -d "$sub_skill_dir" ] || continue
      local_nombre=$(basename "$sub_skill_dir")
      [[ "$local_nombre" == "domain-packs" || "$local_nombre" == "skills" ]] && continue
      sub_skill_md="$sub_skill_dir/SKILL.md"
      if [ -f "$sub_skill_md" ]; then
        nombre=$(extraer_nombre "$sub_skill_md")
        descripcion=$(extraer_descripcion "$sub_skill_md")
        if [ "$FIRST_SKILL" = true ]; then FIRST_SKILL=false; else SKILLS_EN_STACK+=","; fi
        SKILLS_EN_STACK+=$(printf '\n        {"nombre": "%s", "ruta": "%s", "descripcion": "%s"}' \
          "$nombre" "$sub_skill_dir" "$descripcion")
      fi
    done

    # También buscar un nivel más profundo: stack/skills/nombre-skill/SKILL.md
    if [ -d "$stack_dir/skills" ]; then
      for sub_skill_dir in "$stack_dir/skills"/*/; do
        [ -d "$sub_skill_dir" ] || continue
        sub_skill_md="$sub_skill_dir/SKILL.md"
        if [ -f "$sub_skill_md" ]; then
          nombre=$(extraer_nombre "$sub_skill_md")
          descripcion=$(extraer_descripcion "$sub_skill_md")
          if [ "$FIRST_SKILL" = true ]; then FIRST_SKILL=false; else SKILLS_EN_STACK+=","; fi
          SKILLS_EN_STACK+=$(printf '\n        {"nombre": "%s", "ruta": "%s", "descripcion": "%s"}' \
            "$nombre" "$sub_skill_dir" "$descripcion")
        fi
      done
    fi

    if [ "$FIRST_STACK" = true ]; then FIRST_STACK=false; else echo ',' >> "$CATALOGO"; fi
    printf '    {\n      "stack": "%s",\n      "descripcion": "%s",\n      "skills": [%s\n      ]\n    }' \
      "$stack_nombre" "$stack_descripcion" "$SKILLS_EN_STACK" >> "$CATALOGO"
  done
fi
echo '' >> "$CATALOGO"
echo '  ]' >> "$CATALOGO"
echo '}' >> "$CATALOGO"

echo "    ✓ Catálogo generado: $CATALOGO"

# Resumen para el usuario
TOTAL_CORE=$(grep -c '"nombre"' <<< "$(sed -n '/"core"/,/]/p' "$CATALOGO")" 2>/dev/null || echo 0)
TOTAL_OPCIONAL=$(grep -c '"nombre"' <<< "$(sed -n '/"opcional"/,/]/p' "$CATALOGO")" 2>/dev/null || echo 0)
TOTAL_STACKS=$(grep -c '"stack"' "$CATALOGO" 2>/dev/null || echo 0)

echo ""
echo "    Resumen de skills descubiertos:"
echo "      Core (siempre activas):  $(grep -o '"nombre"' "$CATALOGO" | head -20 | wc -l) skills en total"
echo "      Stacks disponibles:      $TOTAL_STACKS"
echo ""
echo "    El agente usará este catálogo para preguntar qué activar."
echo "    También puedes revisarlo manualmente: $CATALOGO"

# --- Paso 7: Reportar placeholders pendientes (requieren input manual) ---
echo ""
echo "[7/7] Verificando placeholders que requieren configuración manual..."

# Buscar dinámicamente los placeholders restantes
RESTANTES=$(grep -roh "{{[^}]*}}" --include="*.md" --include="*.yaml" 2>/dev/null | sort -u || true)

if [ -n "$RESTANTES" ]; then
  echo ""
  echo "    Placeholders pendientes (requieren input manual o del agente):"
  echo ""
  printf "    %-40s %s\n" "PLACEHOLDER" "ARCHIVO(S)"
  printf "    %-40s %s\n" "---" "---"

  echo "$RESTANTES" | while read -r placeholder; do
    UBICACIONES=$(grep -rl "$placeholder" --include="*.md" --include="*.yaml" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
    printf "    %-40s %s\n" "$placeholder" "$UBICACIONES"
  done
else
  echo "    ✓ No quedan placeholders pendientes"
fi

echo ""
echo "=== Proyecto $NOMBRE_PROYECTO inicializado ==="
echo ""
echo "Siguiente paso:"
echo "  1. Edita .env con tus valores reales"
echo "  2. Invoca \$iniciar-proyecto con tu agente para completar placeholders y seleccionar skills"
echo "     (el agente leerá $CATALOGO para saber qué preguntar)"
echo "  3. O rellena los {{placeholders}} manualmente y mueve skills a mano"
echo "  4. Haz git add -A && git commit -m 'init: proyecto $NOMBRE_PROYECTO desde plantilla'"
