"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "../auth/AuthContext";
import { useLanguage } from "../i18n/LanguageContext";
import { usePreferences } from "../preferences/PreferencesContext";

export function ProfileMenu() {
  const { locale, setLocale, t } = useLanguage();
  const { includeSynthetic, setIncludeSynthetic } = usePreferences();
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setOpen(false);
    await logout();
    // Re-runs the server-side session check, so protected pages redirect away.
    router.refresh();
  };

  const loginHref = pathname === "/login" ? "/login" : `/login?next=${encodeURIComponent(pathname)}`;

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        aria-haspopup="true"
        aria-expanded={open}
        aria-label="Profile"
        className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-[var(--accent)] bg-[var(--surface-1)] text-[var(--chocolate-ink)] transition-colors hover:bg-black/10"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="h-5 w-5"
        >
          <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2c-4.42 0-8 2.24-8 5v1a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-1c0-2.76-3.58-5-8-5Z" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-2 w-56 rounded-2xl border-2 border-[var(--border)] bg-[var(--surface-1)] p-3 shadow-lg">
          <div className="mb-3 border-b-2 border-[var(--border)] pb-3">
            {user ? (
              <>
                <p className="px-1 text-xs text-[var(--text-secondary)]">{t.auth.signedInAs}</p>
                <p className="truncate px-1 text-sm font-bold text-[var(--text-primary)]">
                  {user.username}
                </p>
                <button
                  onClick={handleLogout}
                  className="mt-2 w-full rounded-full border-2 border-[var(--border)] px-3 py-1.5 text-xs font-bold text-[var(--text-secondary)] transition-colors hover:bg-[var(--page)]"
                >
                  {t.auth.menuLogout}
                </button>
              </>
            ) : (
              <Link
                href={loginHref}
                onClick={() => setOpen(false)}
                className="block w-full rounded-full bg-[var(--accent)] px-3 py-1.5 text-center text-xs font-bold text-white transition-opacity hover:opacity-90"
              >
                {t.auth.menuLogin}
              </Link>
            )}
          </div>

          <p className="px-1 text-xs font-bold uppercase tracking-wide text-[var(--text-secondary)]">
            Language
          </p>
          <div className="mt-2 flex items-center gap-1 rounded-full border-2 border-[var(--accent)] bg-[var(--page)] p-0.5 text-xs font-bold">
            {(["en", "de"] as const).map((code) => (
              <button
                key={code}
                onClick={() => setLocale(code)}
                aria-pressed={locale === code}
                className={`flex-1 rounded-full px-2.5 py-1 uppercase tracking-wide transition-colors ${
                  locale === code
                    ? "bg-[var(--accent)] text-white"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {code}
              </button>
            ))}
          </div>

          <label className="mt-3 flex items-center gap-2 px-1 text-xs font-medium text-[var(--text-secondary)]">
            <input
              type="checkbox"
              checked={includeSynthetic}
              onChange={(e) => setIncludeSynthetic(e.target.checked)}
              className="h-3.5 w-3.5 accent-[var(--accent)]"
            />
            {t.analytics.filters.includeSynthetic}
          </label>
        </div>
      )}
    </div>
  );
}
