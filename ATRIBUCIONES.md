# Atribuciones y procedencia

**Ultima revision:** 2026-08-28
**Estado:** Inventario incompleto; uso personal y redistribucion bloqueada

## 1. Proposito

Este archivo registra la procedencia conocida del material incorporado o adaptado en `agent-framework`. Su objetivo es impedir que una futura distribucion atribuya una licencia o una autoria que no se encuentre demostrada.

Este registro no reemplaza los avisos de licencia exigidos por cada fuente. Cuando una fuente se confirme, se debe conservar su aviso original en la forma que indique su licencia.

## 2. Politica temporal

- Se permiten correcciones tecnicas para uso personal cuando conservan la procedencia conocida y quedan registradas en el inventario.
- No se elimina ninguna Skill sin confirmacion explicita del propietario del proyecto.
- No se publica una licencia global sobre el conjunto completo hasta delimitar el contenido original y el contenido derivado.
- No se prepara una distribucion comercial de las Skills con procedencia pendiente.
- Cada modificacion debe regenerar el inventario, ejecutar las pruebas y conservar las fuentes declaradas.
- Una Skill solo puede redistribuirse cuando dispone de fuente, revision o commit, licencia comprobada y descripcion de las modificaciones realizadas.

## 3. Inventario conocido

El inventario mecanico reproducible vive en `auditoria/inventario_skills.json`. Registra los archivos auditados, los 18 manifiestos `SKILL.md`, sus tamaños, sus huellas SHA-256 y las declaraciones locales de procedencia detectadas. `scripts/inventariar_skills.py` lo regenera sin escribir dentro de `.agents/skills`, y la suite automatica exige coincidencia byte por byte.

| Grupo | Procedencia declarada | Estado de licencia | Tratamiento |
|---|---|---|---|
| Core historico y firmware ESP32 | Extraido del proyecto personal `entrevoces` | Pendiente de confirmar autoria exclusiva | Uso personal; no redistribuir hasta completar inventario |
| `mobile-flutter` | Adaptado de `spjoshis/claude-code-plugins`, plugin `flutter-development` | La declaracion MIT local no pudo verificarse en el arbol publico revisado | No distribuir comercialmente; conservar sin cambios |
| `backend-fastapi` | Declarado como creado para este framework, con influencia posible de plugins evaluados | Procedencia detallada no registrada | Uso personal; reconstruir trazabilidad antes de redistribuir |
| `frontend-nextjs` | Declarado como creado para este framework, con influencia posible de `nodejs-development` | Fuente y licencia exactas no registradas | Uso personal; reconstruir trazabilidad antes de redistribuir |
| `ia-llm` | Declarado como creado para este framework, con influencia posible de `rag-cli` y `custom-plugin-ai-engineer` | Fuentes y licencias exactas no registradas | Uso personal; reconstruir trazabilidad antes de redistribuir |
| `delegar-entre-agentes` | Extraido del proyecto personal `entrevoces` | Pendiente de confirmar autoria exclusiva | Uso personal; no redistribuir hasta completar inventario |
| `seguridad-backend` | Redaccion original para este framework; consulta OWASP ASVS 5.0.0, OWASP API Security Top 10 2023, OWASP REST Security Cheat Sheet y documentacion oficial de FastAPI | Contenido local original; fuentes usadas como criterio y enlazadas sin copiar texto normativo | Conservar enlaces, versiones y fecha de consulta; reevaluar cuando cambien los estandares |

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
