export function StatTile({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="rounded-3xl border-2 border-[var(--border)] bg-[var(--surface-1)] p-5 shadow-sm">
      <p className="text-xs font-bold text-[var(--text-secondary)]">{label}</p>
      <p className="font-display mt-1 text-2xl font-bold tabular-nums text-[var(--accent)]">
        {value}
      </p>
      {detail && <p className="mt-1 text-xs text-[var(--text-muted)]">{detail}</p>}
    </div>
  );
}
