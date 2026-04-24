"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAdminAuth } from "@pamfilico/admin-auth-react";

export default function AdminLogin() {
  const { login } = useAdminAuth();
  const router = useRouter();
  const [username, setUsername] = useState("theadmin");
  const [password, setPassword] = useState("thepassword");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const r = await login(username, password);
    setSubmitting(false);
    if (r.ok) {
      router.replace("/admin/users");
    } else {
      setError(r.message ?? "Login failed");
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      data-testid="admin-login-form"
      style={{ display: "flex", flexDirection: "column", gap: 12, maxWidth: 320 }}
    >
      <h1>Admin login</h1>
      <label>
        Username
        <input
          data-testid="admin-login-username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ width: "100%", padding: 8, marginTop: 4 }}
        />
      </label>
      <label>
        Password
        <input
          data-testid="admin-login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", padding: 8, marginTop: 4 }}
        />
      </label>
      <button
        data-testid="admin-login-submit"
        disabled={submitting}
        style={{ padding: "10px 16px", cursor: "pointer" }}
      >
        {submitting ? "…" : "Sign in"}
      </button>
      {error && (
        <div data-testid="admin-login-error" style={{ color: "crimson" }}>
          {error}
        </div>
      )}
    </form>
  );
}
