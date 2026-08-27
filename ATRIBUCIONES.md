# Atribuciones y procedencia

**Ultima revision:** 2026-08-26
**Estado:** Inventario incompleto; Skills congeladas

## 1. Proposito

Este archivo registra la procedencia conocida del material incorporado o adaptado en `agent-framework`. Su objetivo es impedir que una futura distribucion atribuya una licencia o una autoria que no se encuentre demostrada.

Este registro no reemplaza los avisos de licencia exigidos por cada fuente. Cuando una fuente se confirme, se debe conservar su aviso original en la forma que indique su licencia.

## 2. Politica temporal

- No se modifican, agregan ni eliminan Skills mientras su procedencia se encuentre en revision.
- No se publica una licencia global sobre el conjunto completo hasta delimitar el contenido original y el contenido derivado.
- No se prepara una distribucion comercial de las Skills con procedencia pendiente.
- Los defectos encontrados dentro de una Skill congelada se registran sin editar su contenido.
- Una Skill solo sale de la congelacion cuando dispone de fuente, revision o commit, licencia comprobada y descripcion de las modificaciones realizadas.

## 3. Inventario conocido

El inventario mecanico reproducible vive en `auditoria/inventario_skills.json`. Registra los 32 archivos congelados, los 17 manifiestos `SKILL.md`, sus tamaños, sus huellas SHA-256 y las declaraciones locales de procedencia detectadas. `scripts/inventariar_skills.py` lo regenera sin escribir dentro de `.agents/skills`, y la suite automatica exige coincidencia byte por byte.

| Grupo | Procedencia declarada | Estado de licencia | Tratamiento |
|---|---|---|---|
| Core historico y firmware ESP32 | Extraido del proyecto personal `entrevoces` | Pendiente de confirmar autoria exclusiva | Congelado hasta completar inventario |
| `mobile-flutter` | Adaptado de `spjoshis/claude-code-plugins`, plugin `flutter-development` | La declaracion MIT local no pudo verificarse en el arbol publico revisado | No distribuir comercialmente; conservar sin cambios |
| `backend-fastapi` | Declarado como creado para este framework, con influencia posible de plugins evaluados | Procedencia detallada no registrada | Congelado hasta reconstruir trazabilidad |
| `frontend-nextjs` | Declarado como creado para este framework, con influencia posible de `nodejs-development` | Fuente y licencia exactas no registradas | Congelado hasta reconstruir trazabilidad |
| `ia-llm` | Declarado como creado para este framework, con influencia posible de `rag-cli` y `custom-plugin-ai-engineer` | Fuentes y licencias exactas no registradas | Congelado hasta reconstruir trazabilidad |
| `delegar-entre-agentes` | Extraido del proyecto personal `entrevoces` | Pendiente de confirmar autoria exclusiva | Congelado hasta completar inventario |

## 4. Fuente externa identificada

### spjoshis/claude-code-plugins

- Repositorio: https://github.com/spjoshis/claude-code-plugins
- Componente declarado: `flutter-development`.
- Material local relacionado: `flutter-state-management`, `flutter-performance` y `flutter-animations`.
- Transformaciones declaradas localmente: fusion, reordenamiento hacia TDD, compresion, traduccion y alineacion con las reglas del framework.
- Hallazgo: el arbol publico revisado el 2026-08-26 no mostro un archivo de licencia visible. La referencia local a MIT queda pendiente de evidencia primaria.

## 5. Datos que faltan por cada fuente

1. URL exacta del repositorio o paquete.
2. Revision, tag o commit utilizado.
3. Archivo o declaracion de licencia aplicable.
4. Aviso de copyright que deba conservarse.
5. Archivos locales derivados o inspirados por la fuente.
6. Descripcion de los cambios realizados.
7. Decision final: conservar, obtener permiso, reemplazar o retirar antes de distribuir.

## 6. Condicion para agregar una licencia raiz

La licencia raiz se definira cuando el inventario permita separar con claridad:

- contenido original que puede licenciar el propietario del framework;
- contenido externo compatible que requiere conservar avisos;
- contenido cuya redistribucion no esta demostrada y debe reemplazarse o excluirse.
