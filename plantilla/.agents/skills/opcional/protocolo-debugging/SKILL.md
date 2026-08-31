---
name: protocolo-debugging
description: Obliga al agente a usar un método científico de debugging (logs, trazabilidad, test fallido) en lugar de intentar adivinar los errores.
---

# Skill: Protocolo de Debugging Estricto

## Regla de Oro

**NUNCA intentes adivinar la causa de un bug ni cambies código "para probar si funciona".**

## Flujo de Resolución de Errores

Cuando te enfrentes a un error, una excepción o un comportamiento inesperado, debes seguir estrictamente este flujo:

1. **Aislar:** Encuentra la manera exacta de reproducir el error consistentemente mediante un test, script mínimo o paso manual.
2. **Instrumentar:** Añade instrucciones de trazabilidad (como `console.log`, `print`, `logging`, o herramientas nativas del ecosistema) en el código alrededor de la zona sospechosa. Captura el estado (variables, parámetros de entrada, salidas) justo antes de que ocurra el error.
3. **Observar:** Ejecuta el código instrumentado, lee y analiza la salida real.
4. **Hipotetizar:** Basándote EXCLUSIVAMENTE en la evidencia obtenida de los logs en el paso anterior, formula el problema exacto.
5. **Corregir:** Modifica el código para solucionar el error basándote en la hipótesis demostrada.
6. **Limpiar:** Elimina todos los logs e instrumentación temporal introducida en el paso 2.
7. **Documentar (Condicional):** Verifica si el problema resuelto cumple con los criterios de la Skill Core `lecciones-aprendidas` (requirió 2+ intentos fallidos y la causa raíz no era trivial ni obvia desde el stacktrace original). Si cumple con sus reglas, regístralo allí. NUNCA documentes errores triviales como typos o fallos de sintaxis.

## Anti-Patrones Prohibidos

- ❌ Editar múltiples archivos a la vez buscando "dónde está el error".
- ❌ Asumir el valor o estructura de una variable que viene de una API o estado externo sin inspeccionarlo primero.
- ❌ Borrar código defensivo (try-catch, assertions) sin entender por qué estaba ahí.
