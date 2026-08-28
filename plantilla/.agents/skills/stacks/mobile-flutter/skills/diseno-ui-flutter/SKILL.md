---
name: diseno-ui-flutter
description: Reglas estrictas de diseño, anti-AI-slop, multi-theming dinámico y feeling nativo (animaciones/haptics) para Flutter.
---

# Skill: Diseño UI/UX Flutter (Anti-Slop & Taste)

Esta Skill eleva la calidad visual de las aplicaciones Flutter, desterrando el código genérico generado por IA ("AI slop") y aplicando sistemas robustos de *multi-theming*, respuesta háptica y animaciones fluidas que dan sensación de app premium nativa.

## 1. El Problema (AI Slop a Evitar)

**Bajo ninguna circunstancia** debes implementar los siguientes anti-patrones en Flutter:
- **Colores hardcodeados:** Prohibido usar `Colors.blue`, `Colors.grey[300]` o `#HEX` directos en los Widgets.
- **Estructuras genéricas (Look 2018):** Prohibido hacer un `Scaffold` plano con un `AppBar` azul sólido y tarjetas grises planas.
- **Elevaciones duras:** Evita usar el `elevation: 4` por defecto. Las sombras modernas son sutiles y difusas.
- **Cero respuesta táctil:** Prohibido tener botones y listas estáticas sin *splash* de tinta (*ink well*) o respuesta de vibración en toques clave.
- **Márgenes mágicos:** Prohibido usar padding/margins con números arbitrarios (ej. `13.0`, `7.0`).

## 2. Multi-Theming Dinámico y Semantic Tokens

Toda la aplicación debe reaccionar automáticamente al cambio de temas y estar preparada para paletas personalizadas (Ej: Dark Mode, Rosa/Celeste, Vibrante).

### Reglas de ThemeData y ColorScheme
1. **Configuración Central:** Usa `ColorScheme.fromSeed(...)` o define paletas estrictas. Nunca inyectes colores directos.
2. **Referencia en Widgets:** Todo color en la app debe provenir de `Theme.of(context).colorScheme.X`.
   - Fondo de pantalla: `colorScheme.surface`
   - Texto principal: `colorScheme.onSurface`
   - Tarjetas/Superficies elevadas: `colorScheme.surfaceContainer` (Material 3)
   - Marca/Acción: `colorScheme.primary`
3. **ThemeExtensions (Opcional avanzado):** Para colores o dimensiones que no encajen en `ColorScheme`, crea extensiones `ThemeExtension` tipadas de forma estricta.

### Persistencia del Tema
- Implementa lógica de estado (Provider, Riverpod, BLoC o ValueNotifier) para cambiar el tema en caliente.
- Sugiere instalar `shared_preferences` (`flutter pub add shared_preferences`) para guardar la elección del usuario (Claro/Oscuro/Sistema o paleta personalizada). (Si el proyecto ya usa Hive/Isar, usa esa DB en su lugar).

## 3. Feeling Nativo y Micro-interacciones (Taste)

Para que la aplicación se sienta *premium*, debes implementar:

- **Haptic Feedback:**
  Añade retroalimentación física sutil en interacciones importantes.
  ```dart
  import 'package:flutter/services.dart';
  // En eventos onTap de botones principales, tarjetas, o switches:
  HapticFeedback.lightImpact();
  // En validaciones de éxito o error:
  HapticFeedback.mediumImpact();
  ```
- **Animaciones Implícitas Fluidas:**
  En lugar de cambios bruscos de estado, usa contenedores animados:
  - `AnimatedContainer` (para cambios de tamaño/color).
  - `AnimatedSwitcher` o `AnimatedCrossFade` (para alternar widgets).
  - Define duraciones rápidas (200-300ms) y curvas naturales (`Curves.easeInOutCubic` o `Curves.easeOutExpo`).
- **Transiciones de Pantalla Cinematográficas:**
  Usa `Hero` animations para compartir elementos visuales (ej. imágenes o avatares) entre una lista y su página de detalles.
- **Botones y Superficies Vivas:**
  Usa `InkWell` con `borderRadius` alineado al contenedor para asegurar que el *splash* de Material se pinte correctamente y comunique que la superficie es interactiva.

## 4. Estructura, Layout y Carga

- **Manejo de Bordes y Pantallas Modernas:**
  Usa `SafeArea` donde corresponda. Maneja bien los *notches* (muescas) y *Dynamic Island*. No dejes que las listas se corten abruptamente; usa `padding` inferior en `ListView` para que el scroll pase por debajo de elementos flotantes.
- **Skeleton Loaders (Shimmer):**
  Nunca dejes una pantalla blanca ni uses solo un `CircularProgressIndicator` solitario centrado para cargar datos masivos. Sugiere implementar un efecto *Shimmer* para simular la estructura de los datos mientras cargan (ej. usando el package `shimmer` o un `CustomPainter` animado).
- **Estados Vacíos Ilustrados:**
  Si una lista o búsqueda no tiene resultados, muestra un estado vacío amigable (Icono/Imagen desaturada, Título principal, Subtítulo descriptivo, y un Call-to-Action si aplica).

## 5. Proceso de Implementación para el Agente

Al usar esta Skill:
1. Construye el esqueleto de `ThemeData` claro y oscuro antes de empezar a maquetar.
2. Asegura que los componentes base usen `Theme.of(context)` para colores y textstyles.
3. Añade `HapticFeedback` a las acciones clave.
4. Siempre pregunta al usuario qué State Management prefiere para orquestar el cambio dinámico del tema si no se ha definido uno.
