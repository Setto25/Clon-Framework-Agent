# Stack: mobile-flutter

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos moviles multiplataforma con Flutter y Dart.
**Basado en:** [spjoshis/claude-code-plugins](https://github.com/spjoshis/claude-code-plugins) (plugin flutter-development, MIT). Adaptado: fusionado, reordenado a TDD, comprimido, traducido y alineado con las reglas del framework.

## Que agrega al core

- Skills: `flutter-state-management`, `flutter-performance`, `flutter-animations`
- Reglas adicionales de implementacion (ver abajo)
- Terminos tecnicos del stack

## Estructura

```
stacks/mobile-flutter/
├── LEEME.md
├── skills/
│   ├── flutter-state-management/   # BLoC, Riverpod, Provider, criterio de seleccion
│   ├── flutter-performance/        # Optimizacion de widgets, memoria, rendering
│   └── flutter-animations/         # Implicitas, explicitas, hero, physics
└── domain-packs/                   # Extensiones futuras (ej: firebase, mapas)
```

## Reglas adicionales de implementacion

Estas reglas complementan la seccion "Forma de implementacion" del prompt base:

- Usa `const` en todo widget que no dependa de estado mutable.
- Prefiere `StatelessWidget` sobre `StatefulWidget` siempre que sea posible.
- Separa logica de negocio de la UI: ningun `Bloc`, `Notifier` o `Controller` debe importar `material.dart`.
- Usa `ListView.builder` para listas de longitud variable — nunca construir todos los items de golpe.
- Dispose todo controller, subscription y stream en `dispose()`.
- Usa `RepaintBoundary` para aislar widgets con animaciones costosas.
- No mezclar multiples soluciones de state management en el mismo proyecto sin justificacion documentada.
- Prueba logica de estado con `bloc_test` o `ProviderContainer` antes de probar la UI.

## Terminos tecnicos del stack

Estos terminos se conservan en ingles dentro de proyectos que activen este stack:

| Termino | NO usar | Contexto |
|---|---|---|
| `widget` | `componente_visual` | Unidad basica de UI en Flutter |
| `StatelessWidget` / `StatefulWidget` | — | Clases base del framework |
| `BuildContext` | — | API del framework |
| `scaffold` | `andamio` | Widget estructural |
| `provider` | `proveedor` | Patron de inyeccion |
| `bloc` | — | Business Logic Component |
| `stream` | `flujo` | Programacion reactiva |
| `future` | — | Promesa asincrona en Dart |
| `isolate` | — | Concurrencia en Dart |
| `mixin` | — | Composicion en Dart |
| `sealed class` | — | Patron de estados en Dart 3+ |
| `hot reload` | — | Funcionalidad del framework |
| `pubspec` | — | Archivo de dependencias |
| `devtools` | — | Herramientas de diagnostico |

## Adaptacion a {{IDIOMA_NOMBRES}}

Los nombres del framework Flutter (`StatelessWidget`, `BlocProvider`, `AnimationController`) se conservan tal cual. Los nombres de **negocio** del proyecto SI se escriben en {{IDIOMA_NOMBRES}}:

```dart
// Correcto: terminos Flutter en ingles + negocio en idioma del proyecto
class BlocPedidos extends Bloc<EventoPedido, EstadoPedido> { ... }
class PaginaCarrito extends StatelessWidget { ... }
class NotificadorUsuarios extends AsyncNotifier<List<Usuario>> { ... }

// Incorrecto: todo en ingles cuando el proyecto usa español
class OrdersBloc extends Bloc<OrderEvent, OrderState> { ... }
```

## Como instalar

La instalacion es automatica via `$iniciar-proyecto`. Si necesitas hacerlo manualmente:

```bash
mv .agents/skills/stacks/mobile-flutter/skills/flutter-state-management/ .agents/skills/
mv .agents/skills/stacks/mobile-flutter/skills/flutter-performance/ .agents/skills/
mv .agents/skills/stacks/mobile-flutter/skills/flutter-animations/ .agents/skills/
```

Luego agregar las reglas adicionales a la seccion correspondiente de `AGENTS.md`.
