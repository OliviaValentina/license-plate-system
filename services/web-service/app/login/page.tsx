"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LoginError, useAuth } from "../auth/AuthContext";
import { useLanguage } from "../i18n/LanguageContext";

const inputClass =
  "mt-1 w-full rounded-xl border-2 border-[var(--border)] bg-[var(--page)] px-3 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none";

/** Only allow redirects to paths on this site, never to another origin. */
function safeNext(next: string | null): string {
  return next && next.startsWith("/") && !next.startsWith("//") ? next : "/internal";
}

function LoginForm() {
  const { t } = useLanguage();
  const a = t.auth;
  const { user, login } = useAuth();
  const router = useRouter();
  const next = safeNext(useSearchParams().get("next"));

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(username, password);
      router.push(next);
      router.refresh();
    } catch (err) {
      setError(err instanceof LoginError && err.status === 401 ? a.invalidCredentials : a.unavailable);
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="rounded-3xl border-2 border-[var(--border)] border-b-4 border-b-[var(--accent)] bg-[var(--surface-1)] p-6 shadow-sm sm:p-8">
      <h1 className="font-display text-2xl font-bold tracking-tight text-[var(--text-primary)]">
        {a.title}
      </h1>
      <p className="mt-1 text-sm text-[var(--text-secondary)]">{a.subtitle}</p>

      {user && (
        <p className="mt-4 rounded-xl bg-[var(--page)] px-3 py-2 text-sm text-[var(--text-secondary)]">
          {a.alreadyLoggedIn} ({user.username})
        </p>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block text-sm font-bold text-[var(--text-primary)]">
          {a.username}
          <input
            type="text"
            name="username"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className={inputClass}
          />
          <span className="mt-1 block text-xs font-normal text-[var(--text-secondary)]">
            {a.usernameHint}
          </span>
        </label>

        <label className="block text-sm font-bold text-[var(--text-primary)]">
          {a.password}
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />
        </label>

        {error && (
          <p
            role="alert"
            className="rounded-xl border-2 border-[var(--status-critical)] px-3 py-2 text-sm text-[var(--status-critical)]"
          >
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-full bg-[var(--accent)] px-6 py-3 font-display text-sm font-bold text-white shadow-[0_4px_0_0_var(--brand-plum)] transition-transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-none disabled:opacity-60"
        >
          {submitting ? a.submitting : a.submit}
        </button>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[var(--page)]">
      <main className="mx-auto max-w-md px-4 py-16 sm:py-24">
        <Suspense>
          <LoginForm />
        </Suspense>
      </main>
    </div>
  );
}
