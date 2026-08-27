# Lecciones aprendidas — general (tooling / entorno)

Lecciones transversales que aplican a todos los stacks, sin importar la tecnologia del proyecto.

| # | Sintoma | Causa raiz | Fecha |
|---|---|---|---|
| 1 | `bash script.sh` falla con `WSL_E_DEFAULT_DISTRO_NOT_FOUND` | PowerShell resuelve `bash` al ejecutable de WSL en vez del de Git for Windows | 2026-08-26 |
| 2 | Un archivo de `plantilla/` no aparece en el reemplazo de placeholders pese a tener el placeholder correcto | `cp -r` de Git Bash no copió el archivo — la copia resultó silenciosamente incompleta | 2026-08-26 |

---

### bash script.sh falla con WSL_E_DEFAULT_DISTRO_NOT_FOUND en Windows

- **Contexto**: correr un script `.sh` desde PowerShell en un proyecto que usa Git for Windows
- **Error**: `WSL_E_DEFAULT_DISTRO_NOT_FOUND` — PowerShell encontro `bash.exe` pero era el de WSL, que no tiene distribucion Linux configurada
- **Causa raiz**: cuando WSL esta instalado pero no configurado, PowerShell resuelve el comando `bash` al `bash.exe` de WSL (`C:\Windows\System32\bash.exe`) en vez del de Git for Windows (`C:\Program Files\Git\bin\bash.exe`). El orden del PATH determina cual gana.
- **Solucion**: dos alternativas:
  1. Abrir Git Bash directamente como aplicacion (desde el menu Inicio o el explorador) y correr el script desde ahi.
  2. Llamar la ruta completa desde PowerShell: `& "C:\Program Files\Git\bin\bash.exe" -c "bash scripts/mi-script.sh"`
- **Intentos fallidos**: correr `bash scripts/mi-script.sh` directo desde PowerShell — falla porque resuelve al bash de WSL.
- **Aplica a**: cualquier proyecto con scripts `.sh` en entorno Windows con Git for Windows + WSL instalados simultaneamente.

---

### cp -r de Git Bash no copia todos los archivos de .agents/rules/ — copia silenciosamente incompleta

- **Contexto**: durante el dry-run de validacion del script `inicializar_proyecto.py`, se copio `plantilla/` a un directorio temporal usando `cp -r` de Git Bash. El script corrio hasta el final sin errores, pero `.agents/rules/claude.md` no aparecio en la Fase 1 de reemplazo de placeholders, pese a contener `{{NOMBRE_PROYECTO}}` y `{{PREFIJO_VARIABLES}}`. El archivo ausente contiene toda la formalizacion de superpowers del framework — un bug aparentemente critico.
- **Error**: ausencia silenciosa — ningun mensaje de error, el script termino exitosamente, pero un archivo clave no fue procesado.
- **Intentos fallidos**:
  1. Se sospecho de una exclusion en el script Python que capturara `rules/` — descartado: no existe ninguna.
  2. Se sospecho de que `rglob` de Python no detectara el archivo por diferencias de casing (`claude.md` vs `CLAUDE.md`) — descartado: prueba directa sobre `plantilla/` confirmo que `rglob` lo encuentra correctamente.
- **Causa raiz**: el problema estaba en el metodo de copia, no en el script. Prueba A/B confirmatoria:
  - `cp -r` de Git Bash → 17 archivos en Fase 1, **sin** `claude.md`
  - `Copy-Item -Recurse -Force` de PowerShell → 18 archivos en Fase 1, **con** `claude.md`
  - `cp -r` de Git Bash no copio `claude.md` desde `.agents/rules/` en Windows.
- **Solucion**: usar siempre `Copy-Item` de PowerShell para instanciar la plantilla en Windows, no `cp -r` de Git Bash — incluso para copias simples de carpetas. El README ya recomienda `Copy-Item` como metodo principal; el bug solo afecto una prueba manual con una herramienta distinta a la recomendada.
- **Verificacion recomendada**: tras cualquier copia de `plantilla/`, confirmar archivos criticos con:
  ```powershell
  Get-ChildItem -Path ".agents\rules\" -Force
  ```
  Si falta algun archivo esperado, repetir la copia con `Copy-Item`, no con `cp`.
- **Aplica a**: cualquier proyecto en Windows que copie `plantilla/` a un directorio nuevo. Especial atencion a archivos en directorios ocultos (`.agents/`) con nombres en casing mixto.
