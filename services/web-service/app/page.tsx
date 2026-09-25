"use client";

import Link from "next/link";
import { useLanguage } from "./i18n/LanguageContext";

export default function Home() {
  const { t } = useLanguage();

  const features = [
    {
      icon: "🚘",
      title: t.home.features.recognitionTitle,
      body: t.home.features.recognitionBody,
      color: "var(--accent)",
    },
    {
      icon: "📊",
      title: t.home.features.analyticsTitle,
      body: t.home.features.analyticsBody,
      color: "var(--brand-teal)",
    },
    {
      icon: "🔔",
      title: t.home.features.alertsTitle,
      body: t.home.features.alertsBody,
      color: "var(--brand-pink)",
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--page)]">
      <main className="mx-auto max-w-5xl px-4 py-16 sm:px-8 sm:py-24">
        <div className="text-center">
          <p className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
            {t.home.eyebrow}
          </p>
          <h1 className="font-display mt-3 text-4xl font-bold tracking-tight text-[var(--text-primary)] sm:text-5xl">
            {t.home.title}
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-base text-[var(--text-secondary)]">
            {t.home.subtitle}
          </p>
          <Link
            href="/analytics"
            className="mt-8 inline-block rounded-full bg-[var(--accent)] px-6 py-3 font-display text-sm font-bold text-white shadow-[0_4px_0_0_var(--brand-plum)] transition-transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-none"
          >
            {t.home.cta} →
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-5 sm:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-3xl border-2 border-[var(--border)] bg-[var(--surface-1)] p-6 text-center shadow-sm"
              style={{ borderBottomColor: feature.color, borderBottomWidth: 4 }}
            >
              <div className="text-3xl">{feature.icon}</div>
              <h2 className="font-display mt-3 text-base font-bold text-[var(--text-primary)]">
                {feature.title}
              </h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                {feature.body}
              </p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
