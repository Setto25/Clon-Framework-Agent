---
name: diseno-ui-web
description: Reglas estrictas de diseño, anti-AI-slop, tokens semánticos, multi-theming y micro-interacciones para Next.js / Tailwind CSS.
---

# Skill: Diseño UI/UX Web (Anti-Slop & Taste)

Esta Skill impone estándares de diseño de alta calidad, erradicando las interfaces genéricas ("AI slop") mediante el uso estricto de tokens semánticos, *multi-theming* nativo y micro-interacciones pulidas.

## 1. El Problema (AI Slop a Evitar)

Por defecto, la IA produce interfaces mediocres. **Bajo ninguna circunstancia** debes implementar los siguientes anti-patrones:
- **Colores planos hardcodeados:** Prohibido usar clases directas de Tailwind (ej. `bg-blue-500` o `text-gray-600`) para estructurar la aplicación.
- **Degradados genéricos:** Prohibido el típico degradado "morado a azul" (`from-purple-500 to-blue-500`).
- **Cartas idénticas flotantes:** Prohibido hacer *landings* con tres tarjetas blancas genéricas, un icono circular flotando encima y texto gris aburrido.
- **Falta de contraste:** Todo texto debe cumplir ratio WCAG 2.1 (4.5:1). Prohibido usar textos grises ilegibles (`text-gray-400` sobre fondos blancos).
- **Tipografía por defecto:** Prohibido dejar la fuente por defecto del navegador.

## 2. Sistema de Tokens Semánticos

Para soportar *multi-theming* (claro, oscuro, paletas dinámicas), todo el diseño debe basarse en variables CSS semánticas inyectadas en la configuración de Tailwind (`tailwind.config.ts`).

### Clases permitidas (Roles Semánticos)
Siempre usa los roles semánticos definidos. Ejemplos de uso obligatorio:
- **Fondos:** `bg-background` (fondo principal), `bg-surface` o `bg-card` (tarjetas y contenedores elevados).
- **Textos:** `text-foreground` (texto principal), `text-muted-foreground` (texto secundario).
- **Bordes:** `border-border` o `border-muted` (divisores sutiles).
- **Marca/Acción:** `bg-primary text-primary-foreground`, `bg-accent text-accent-foreground`.

## 3. Multi-Theming (next-themes)

La aplicación debe soportar cambio de temas dinámico y sin parpadeo (*hydration flash*).

1. **Instalar dependencias:** `npm install next-themes`
2. **Configurar el Provider:**
   Envuelve la aplicación (en `app/layout.tsx` o `providers.tsx`) con `<ThemeProvider attribute="class" defaultTheme="system" enableSystem>` (o `attribute="data-theme"` si se usan múltiples paletas).
3. **Definir Paletas en `global.css`:**
   ```css
   @layer base {
     :root {
       --background: 0 0% 100%; /* OKLCH o HSL moderno */
       --foreground: 240 10% 3.9%;
       --primary: 240 5.9% 10%;
       --primary-foreground: 0 0% 98%;
       /* ...otros tokens... */
     }
     .dark {
       --background: 240 10% 3.9%;
       --foreground: 0 0% 98%;
       --primary: 0 0% 98%;
       --primary-foreground: 240 5.9% 10%;
     }
     [data-theme="vibrant"] {
       /* Configuración de paleta opcional para temas alegres */
     }
   }
   ```

## 4. El "Toque Premium" (Taste)

Aplica siempre estos principios para que la interfaz se sienta cara y profesional:

- **Modo Oscuro Real (Superficies Elevadas):** El modo oscuro no es solo "fondo negro". Usa fondos oscuros (`#0a0a0a`), pero las tarjetas deben tener un gris sutil (`#171717`) con bordes finos semitransparentes (`border-white/10`) y sombras internas ligeras (efecto *glassmorphism*).
- **Micro-interacciones completas:** TODO elemento interactivo (botones, enlaces, cards clickeables) DEBE tener estados:
  - `hover:` (cambio sutil de color o leve traslación/escala).
  - `active:` (escala hacia abajo `active:scale-95`).
  - `focus-visible:` (anillo de foco accesible `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`).
  - `disabled:` (opacidad reducida `disabled:opacity-50 disabled:cursor-not-allowed`).
- **Estados de Carga y Vacíos:**
  - Nunca dejes la pantalla en blanco mientras cargas. Usa *skeleton loaders* (`animate-pulse bg-muted`) o *shimmer effects*.
  - Los estados vacíos (ej. listas sin elementos) deben tener un icono sutil, un título claro, descripción gris y una acción primaria (botón).
- **Tipografía Moderna:** Exige el uso de `next/font/google` con tipografías como `Geist`, `Inter`, `Outfit` o `Plus Jakarta Sans`. Usa un tracking sutil (ej. `tracking-tight` para títulos).
- **Espaciado rítmico:** Usa la escala de espaciado estándar (4, 8, 12, 16, 24, 32, 48px).

## 5. Iconografía y Animaciones

- **Iconos:** Sugiere el uso de `lucide-react` (`npm install lucide-react`). Es ligero, moderno y *tree-shakeable*. No uses librerías pesadas obsoletas.
- **Animaciones CSS Nativas:** Usa las transiciones fluidas de Tailwind: `transition-all duration-200 ease-out`.
- **Framer Motion (Opcional):** Si el proyecto requiere animaciones complejas (aparición en scroll, orquestaciones), sugiere usar `framer-motion` o `motion/react`, pero NO lo instales a menos que el usuario lo confirme explícitamente.

## 6. Proceso de Implementación para el Agente

Al aplicar esta Skill en un requerimiento de frontend:
1. Configura primero la tipografía y los tokens en `tailwind.config.ts` y `global.css`.
2. Instala y configura `next-themes`.
3. Al crear componentes, piensa en sus 4 estados (idle, hover, loading, empty).
4. No intentes reinventar *shadcn/ui*, pero usa sus mismos principios de diseño (tokens de Radix UI o similares).
