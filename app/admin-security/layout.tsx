// app/admin-security/layout.tsx
import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Admin Sécurité - TeamSquare",
  description: "Centre de contrôle de sécurité et surveillance des modèles IA",
  robots: "noindex, nofollow", // Empêcher l'indexation par les moteurs de recherche
}

export default function AdminSecurityLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="admin-security-layout">
      {children}
    </div>
  )
}