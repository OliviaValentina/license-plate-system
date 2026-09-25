export function Card({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-3xl border-2 border-[var(--border)] bg-[var(--surface-1)] p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="font-display text-sm font-bold text-[var(--text-primary)]">{title}</h2>
        {subtitle && (
          <p className="text-xs text-[var(--text-secondary)]">{subtitle}</p>
        )}
      </div>
      {children}
    </section>
  );
}
