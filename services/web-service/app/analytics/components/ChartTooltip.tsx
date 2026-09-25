"use client";

export function ChartTooltip({
  active,
  label,
  rows,
}: {
  active?: boolean;
  label?: string | number;
  rows: { name: string; value: string; color: string }[];
}) {
  if (!active || rows.length === 0) return null;

  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-sm">
      {label !== undefined && (
        <p className="mb-1 font-medium text-[var(--text-primary)]">{label}</p>
      )}
      {rows.map((row) => (
        <div key={row.name} className="flex items-center gap-2 text-[var(--text-secondary)]">
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: row.color }}
          />
          <span>{row.name}:</span>
          <span className="ml-auto font-medium tabular-nums text-[var(--text-primary)]">
            {row.value}
          </span>
        </div>
      ))}
    </div>
  );
}
