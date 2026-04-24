"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  AdminProtectedRoute,
  adminListUsers,
  useAdminAuth,
} from "@pamfilico/admin-auth-react";

interface UserRow {
  id: string;
  email: string | null;
  name: string | null;
  created_at: string | null;
}

function UsersInner() {
  const { token, logout, apiConfig } = useAdminAuth();
  const router = useRouter();
  const [rows, setRows] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    (async () => {
      const r = await adminListUsers(apiConfig, token, { pageSize: 50 });
      const body = r.data as { data?: UserRow[] } | undefined;
      setRows(body?.data ?? []);
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
        <h1 style={{ margin: 0 }}>Admin users</h1>
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
        <table data-testid="admin-users-table" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
              <th>Email</th>
              <th>Name</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((u) => (
              <tr key={u.id} style={{ borderBottom: "1px solid #eee" }}>
                <td>{u.email}</td>
                <td>{u.name}</td>
                <td>{u.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function AdminUsersPage() {
  const router = useRouter();
  return (
    <AdminProtectedRoute redirect={(path) => router.replace(path)} fallback={<div>Checking auth…</div>}>
      <UsersInner />
    </AdminProtectedRoute>
  );
}
