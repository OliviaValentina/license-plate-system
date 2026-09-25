"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { VisitTrendPoint } from "../lib/types";
import { ChartTooltip } from "./ChartTooltip";
import { SERIES_COLORS } from "../lib/colors";
import { useLanguage } from "../../i18n/LanguageContext";

const UNGROUPED_KEY = "visit_count";

function formatDate(dateStr: string, locale: "en" | "de"): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString(locale === "de" ? "de-DE" : "en-US", {
    month: "short",
    day: "numeric",
  });
}

export function VisitTrendsChart({ data }: { data: VisitTrendPoint[] }) {
  const { locale, t } = useLanguage();
  const charts = t.analytics.charts;

  const grouped = data.some((d) => d.group_value !== null);
  const seriesKeys = grouped
    ? Array.from(new Set(data.map((d) => d.group_value ?? ""))).sort()
    : [UNGROUPED_KEY];

  const byDate = new Map<string, Record<string, string | number>>();
  for (const point of data) {
    const key = point.visit_date;
    if (!byDate.has(key)) byDate.set(key, { date: key, label: formatDate(key, locale) });
    const row = byDate.get(key)!;
    row[grouped ? point.group_value ?? "" : UNGROUPED_KEY] = point.visit_count;
  }
  const chartData = Array.from(byDate.values()).sort((a, b) =>
    String(a.date).localeCompare(String(b.date))
  );

  if (data.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">{charts.noData}</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--grid-line)" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={{ stroke: "var(--axis-line)" }}
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          width={36}
        />
        <Tooltip
          cursor={{ stroke: "var(--axis-line)", strokeWidth: 1 }}
          content={({ active, label, payload }) => (
            <ChartTooltip
              active={active}
              label={label}
              rows={
                payload
                  ?.filter((p) => p.value !== undefined)
                  .map((p) => ({
                    name: grouped ? String(p.dataKey) : charts.visitsTooltip,
                    value: String(p.value),
                    color: p.color ?? "var(--accent)",
                  })) ?? []
              }
            />
          )}
        />
        {grouped && <Legend wrapperStyle={{ fontSize: 11, color: "var(--text-secondary)" }} />}
        {seriesKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={key}
            stroke={SERIES_COLORS[index % SERIES_COLORS.length]}
            strokeWidth={2}
            dot={false}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
