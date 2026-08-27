#!/usr/bin/env bash
# Delega la inicializacion en la unica implementacion soportada.

set -euo pipefail

directorio_script="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
inicializador="$directorio_script/inicializar_proyecto.py"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$inicializador" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$inicializador" "$@"
fi

echo "ERROR: Python no esta disponible en PATH." >&2
exit 1
