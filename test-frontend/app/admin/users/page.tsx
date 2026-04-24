"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  AdminProtectedRoute,
  adminFetch,
  useAdminAuth,
} from "@pamfilico/admin-auth-react";

interface WhoamiData {
  sub: string;
  role: string;
}

function WhoamiInner() {
  const { token, logout, apiConfig } = useAdminAuth();
  const router = useRouter();
  const [me, setMe] = useState<WhoamiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    (async () => {
      const r = await adminFetch<{ data?: WhoamiData }>(
        apiConfig,
        "/admin/whoami",
        { method: "GET" },
        token,
      );
      setMe(r.data?.data ?? null);
      setLoading(false);
    })();
  }, [token, apiConfig]);

  return (
    <div>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <h1 style={{ margin: 0 }}>Admin — whoami</h1>
        <button
          data-testid="admin-logout"
          onClick={() => {
            logout();
            router.replace("/admin/login");
          }}
          style={{ padding: "8px 12px", cursor: "pointer" }}
        >
          Log out
        </button>
      </header>
      {loading ? (
        <div>Loading…</div>
      ) : (
        <pre
          data-testid="admin-whoami"
          style={{ background: "#f6f6f6", padding: 16, borderRadius: 4 }}
        >
          {JSON.stringify(me, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function AdminUsersPage() {
  const router = useRouter();
  return (
    <AdminProtectedRoute
      redirect={(path) => router.replace(path)}
      fallback={<div>Checking auth…</div>}
    >
      <WhoamiInner />
    </AdminProtectedRoute>
  );
}
