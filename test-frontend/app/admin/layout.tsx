"use client";

import { AdminAuthProvider } from "@pamfilico/admin-auth-react";

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:5098";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminAuthProvider apiConfig={{ backendUrl }}>
      <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>{children}</div>
    </AdminAuthProvider>
  );
}
