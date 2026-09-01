# Stack: mobile-flutter

**Tipo:** Stack tecnologico (Capa 2)
**Para:** Proyectos moviles multiplataforma con Flutter y Dart.
**Basado en:** [spjoshis/claude-code-plugins](https://github.com/spjoshis/claude-code-plugins), plugin `flutter-development`. La licencia de la revision usada no esta verificada. Adaptado: fusionado, reordenado a TDD, comprimido, traducido y alineado con las reglas del framework.

## Que ofrece el catalogo fuente

- Skills: `diseno-ui-flutter`, `flutter-state-management`, `flutter-performance`, `flutter-animations`
- Reglas adicionales de implementacion (ver abajo)
- Terminos tecnicos del stack

Una instancia generada contiene solamente las Skills confirmadas de esta lista.

## Estructura en el catalogo fuente

```
stacks/mobile-flutter/
├── LEEME.md
├── skills/
│   ├── diseno-ui-flutter/          # Sistema visual, temas, movimiento y respuesta tactil
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

## Adaptacion al idioma del proyecto

Los nombres del framework Flutter (`StatelessWidget`, `BlocProvider`, `AnimationController`) se conservan tal cual. Los nombres de negocio respetan el idioma declarado en `AGENTS.md`:

```dart
// Correcto: terminos Flutter en ingles + negocio en idioma del proyecto
class BlocPedidos extends Bloc<EventoPedido, EstadoPedido> { ... }
class PaginaCarrito extends StatelessWidget { ... }
class NotificadorUsuarios extends AsyncNotifier<List<Usuario>> { ... }

// Incorrecto: todo en ingles cuando el proyecto usa español
class OrdersBloc extends Bloc<OrderEvent, OrderState> { ... }
```

## Como seleccionar

Desde la raiz de `agent-framework`, cada Skill se confirma por separado al crear la instancia:

```powershell
python scripts\crear_proyecto.py <DESTINO> "<NOMBRE>" --configuracion <CONFIGURACION> --skill diseno-ui-flutter --skill flutter-state-management --skill flutter-performance --skill flutter-animations
```

No se mueven carpetas manualmente. Este `LEEME.md` no implica que todas las Skills Flutter esten instaladas.
