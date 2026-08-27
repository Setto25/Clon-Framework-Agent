---
name: lecciones-aprendidas
description: Memoria persistente de errores resueltos con dificultad (2+ intentos fallidos). Evita repetir ciclos de depuracion ya resueltos. Consultar antes de depurar un error que podria estar registrado.
---

# Lecciones aprendidas

## Cuando usar

- **Consultar**: antes de depurar un error que parece familiar o que involucra integracion entre componentes.
- **Registrar**: tras resolver un error que requirio 2 o mas intentos fallidos.

## Como consultar

1. Identificar el stack del error (backend-fastapi, mobile-flutter, frontend-nextjs, firmware-esp32, ia-llm). Si es un problema de tooling o entorno que aplica a todos los stacks, usar `referencias/general.md`.
2. Leer `referencias/<stack>.md` o `referencias/general.md`.
3. Buscar por sintoma o componente involucrado.
4. Si hay match, aplicar la solucion documentada directamente.

## Como registrar

Cuando un error se resuelve tras 2+ intentos fallidos:

1. Agregar entrada en `referencias/<stack>.md` (o `referencias/general.md` si aplica a todos los stacks) con el formato de esa tabla.
2. Agregar fila en la tabla indice de abajo.

## Tabla indice

| # | Stack | Sintoma (breve) | Archivo referencia |
|---|---|---|---|
| 1 | general | `bash script.sh` falla con `WSL_E_DEFAULT_DISTRO_NOT_FOUND` en Windows | `referencias/general.md` |
| 2 | general | Archivo de `plantilla/` ausente en reemplazo de placeholders pese a tener el placeholder correcto | `referencias/general.md` |

## Formato de entrada en referencias/<stack>.md

Cada entrada sigue esta estructura:

```markdown
### [Sintoma breve en una linea]

- **Contexto**: que se estaba haciendo cuando aparecio
- **Error**: mensaje o comportamiento observado
- **Causa raiz**: por que ocurria realmente
- **Solucion**: que lo resolvio
- **Intentos fallidos**: que se probo antes y por que no funciono
```

## Reglas

- No registrar errores triviales (typos, imports faltantes, errores de sintaxis obvia).
- Solo registrar cuando la causa raiz NO era obvia desde el mensaje de error.
- Mantener las entradas concisas — el valor esta en la causa raiz y la solucion, no en la narrativa.
