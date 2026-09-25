"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HourlyVisitPoint } from "../lib/types";
import { ChartTooltip } from "./ChartTooltip";
import { useLanguage } from "../../i18n/LanguageContext";

function formatHour(hour: number): string {
  return `${String(hour).padStart(2, "0")}:00`;
}

export function RushHourChart({ data }: { data: HourlyVisitPoint[] }) {
  const { t } = useLanguage();

  const chartData = Array.from({ length: 24 }, (_, hour) => {
    const point = data.find((d) => d.hour_of_day === hour);
    return {
      hour,
      label: formatHour(hour),
      visit_count: point?.visit_count ?? 0,
    };
  });

  if (data.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">{t.analytics.charts.noData}</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--grid-line)" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={{ stroke: "var(--axis-line)" }}
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          interval={2}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          width={36}
        />
        <Tooltip
          cursor={{ fill: "var(--grid-line)", opacity: 0.4 }}
          content={({ active, label, payload }) => (
            <ChartTooltip
              active={active}
              label={label}
              rows={
                payload?.map((p) => ({
                  name: t.analytics.charts.visitsTooltip,
                  value: String(p.value),
                  color: "var(--accent)",
                })) ?? []
              }
            />
          )}
        />
        <Bar dataKey="visit_count" fill="var(--accent)" radius={[4, 4, 0, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  );
}
