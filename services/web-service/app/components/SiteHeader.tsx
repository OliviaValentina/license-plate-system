"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "../i18n/LanguageContext";
import { ProfileMenu } from "./ProfileMenu";

export function SiteHeader() {
  const { t } = useLanguage();
  const pathname = usePathname();

  const links = [
    { href: "/", label: t.nav.home },
    { href: "/analytics", label: t.nav.analytics },
  ];

  return (
    <header className="sticky top-0 z-10 border-b-4 border-[var(--accent)] bg-[var(--chocolate)]">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-8">
        <Link
          href="/"
          className="font-display text-xl font-bold tracking-tight text-[var(--chocolate-ink)]"
        >
          License Plate System
        </Link>

        <nav className="flex items-center gap-1">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-full px-4 py-1.5 text-sm font-bold transition-colors ${
                  active
                    ? "bg-[var(--accent)] text-white"
                    : "text-[var(--chocolate-ink)] hover:bg-black/10"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <ProfileMenu />
      </div>
    </header>
  );
}
