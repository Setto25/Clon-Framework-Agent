---
name: cerrar-modulo
description: Cierra y documenta un módulo terminado después de implementar cualquier componente del proyecto. Usar cuando las pruebas ya pasaron o el usuario aprobó un módulo, para verificar evidencia, actualizar PROJECT_STATE.md, plan, documentación técnica y registro de cambios, y fijar el siguiente paso. No usar para marcar trabajo incompleto como terminado.
---

# Cerrar módulo

## Puerta de cierre

1. Confirmar que exista un criterio de aceptación explícito.
2. Ejecutar obligatoriamente `scripts/validar_cierre_tarea.py . --solo-verificaciones --salida-evidencia documentacion/EVIDENCIA_CIERRE.json` antes de escribir una declaración de cierre.
3. Detener el cierre si el comando devuelve un codigo distinto de cero, `FALLIDO`, `NO_EJECUTADO` o `NO_DISPONIBLE` bloqueante. Una explicacion del agente no sustituye el codigo observado.
   Si falla una puerta, se corrige su comando o el codigo; no se elimina el script ni la verificacion para reducir la cobertura exigida.
4. Revisar el diff o la lista exacta de archivos modificados solo despues de aprobar la prevalidacion.

## Actualización obligatoria

1. Actualizar `PROJECT_STATE.md` con fecha, estado, implementación, tecnologías y versiones, rutas, ejecución, pruebas, riesgos y siguiente paso.
2. Actualizar `documentacion/PLAN_DESARROLLO.md` marcando únicamente tareas comprobadas.
3. Actualizar `documentacion/DOCUMENTACION_TECNICA.md` si cambió el funcionamiento o la ubicación.
4. Agregar una entrada nueva y acumulativa a `documentacion/REGISTRO_CAMBIOS.md`.
5. Revisar `documentacion/GUIA_OPERACION.md`; actualizarla cuando el cambio altere operación, arquitectura, datos, secretos, API, dispositivo, diagnóstico o escalamiento. Si no aplica, registrar explícitamente esa evaluación en la entrega.
6. Ejecutar nuevamente `scripts/validar_cierre_tarea.py` con los archivos y documentos actualizados reales. El script ejecuta todas las verificaciones del contrato o las inferidas; `--comando-prueba` solo agrega evidencia y no sustituye las puertas declaradas. No declarar terminado si devuelve un código distinto de cero.

## Comando

```powershell
python scripts/validar_cierre_tarea.py . `
  --archivo-modificado "<ruta modificada>" `
  --documento-actualizado "PROJECT_STATE.md" `
  --documento-actualizado "documentacion/PLAN_DESARROLLO.md" `
  --documento-actualizado "documentacion/REGISTRO_CAMBIOS.md" `
  --guia-operacion-revisada `
  --salida-evidencia documentacion/EVIDENCIA_CIERRE.json
```

Agregar `--documentacion-tecnica-aplica` y declarar `documentacion/DOCUMENTACION_TECNICA.md` cuando el cambio altere funcionamiento, ubicacion o contrato tecnico. Configurar `contrato_validacion.json` a partir de `contrato_validacion.ejemplo.json` para monorepos y puertas explicitas. Sin manifiesto, la cobertura queda marcada como inferida y cualquier modulo sin verificacion impide el cierre.

La CI de GitHub ejecuta `scripts/validar_integridad_proyecto.py` como puerta estatica independiente. Un proyecto alojado en otro proveedor integra ese mismo comando con `--base` y la revision Git base. Las pruebas ejecutables permanecen a cargo de `validar_cierre_tarea.py`.

## Salida

Entregar resultado funcional, comandos ejecutados con directorio y codigo de salida, documentación actualizada, deuda conocida y siguiente acción concreta. Diferenciar fallos del modelo, prompt, Skill, herramienta, script y proyecto; no atribuir una causa sin evidencia.
