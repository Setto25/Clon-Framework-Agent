# Skills opcionales

Skills que **no se incluyen por defecto** al inicializar un proyecto nuevo.
Copiar manualmente a `.agents/skills/` solo cuando el problema que resuelven se manifieste.

## Criterio de inclusión aquí (no en core)

- El skill resuelve un problema que no todos los proyectos tienen.
- No hay evidencia de uso recurrente en los primeros hitos del proyecto origen.
- Incluirlo desde el día uno agrega ruido sin valor demostrado.

## Cómo activar un skill opcional

```bash
cp -r .agents/skills/opcional/<nombre-skill> .agents/skills/
```

Luego verificar que `AGENTS.md` lo referencia si es necesario.
