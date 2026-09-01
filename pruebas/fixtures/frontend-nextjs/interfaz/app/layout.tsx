import type { Metadata } from "next";
import type { JSX, ReactNode } from "react";

export const metadata: Metadata = {
  title: "Validación de agent-framework",
  description: "Fixture mínimo para comprobar test, lint y build.",
};

interface PropiedadesDisposicion {
  children: ReactNode;
}

export default function DisposicionRaiz({ children }: PropiedadesDisposicion): JSX.Element {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
