"use client";

import { useLanguage } from "../i18n/LanguageContext";

const cardColors = ["var(--accent)", "var(--brand-teal)", "var(--brand-pink)"];

export function InternalContent({ username }: { username: string }) {
  const { t } = useLanguage();
  const i = t.internal;

  return (
    <div className="min-h-screen bg-[var(--page)]">
      <div className="border-b-4 border-[var(--accent)]/30 bg-[var(--chocolate)]">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-8">
          <p className="font-display text-xs font-semibold uppercase tracking-[0.2em] text-[var(--chocolate-ink)] opacity-80">
            {i.eyebrow}
          </p>
          <h1 className="font-display text-lg font-bold tracking-tight text-[var(--chocolate-ink)]">
            {i.title}
          </h1>
          <p className="text-sm text-[var(--chocolate-ink)] opacity-80">{i.subtitle}</p>
        </div>
      </div>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-8">
        <p className="font-display text-xl font-bold text-[var(--text-primary)]">
          {i.welcome}, {username}!
        </p>

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {i.cards.map((card, index) => (
            <div
              key={card.title}
              className="rounded-3xl border-2 border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-sm"
              style={{ borderBottomColor: cardColors[index % cardColors.length], borderBottomWidth: 4 }}
            >
              <h2 className="font-display text-base font-bold text-[var(--text-primary)]">
                {card.title}
              </h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">{card.body}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
