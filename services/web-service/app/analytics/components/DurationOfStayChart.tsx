"use client";

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DurationOfStayPoint } from "../lib/types";
import { ChartTooltip } from "./ChartTooltip";
import { useLanguage } from "../../i18n/LanguageContext";

function formatDate(dateStr: string, locale: "en" | "de"): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString(locale === "de" ? "de-DE" : "en-US", {
    month: "short",
    day: "numeric",
  });
}

export function DurationOfStayChart({ data }: { data: DurationOfStayPoint[] }) {
  const { locale, t } = useLanguage();
  const charts = t.analytics.charts;

  const chartData = [...data]
    .sort((a, b) => a.visit_date.localeCompare(b.visit_date))
    .map((d) => ({
      label: formatDate(d.visit_date, locale),
      avg: Math.round(d.avg_duration_minutes * 10) / 10,
      median: Math.round(d.median_duration_minutes * 10) / 10,
      range: [
        Math.round(d.min_duration_minutes * 10) / 10,
        Math.round(d.max_duration_minutes * 10) / 10,
      ] as [number, number],
    }));

  if (data.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">{charts.noData}</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
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
          width={40}
          label={{
            value: charts.minutesAxis,
            angle: -90,
            position: "insideLeft",
            fill: "var(--text-muted)",
            fontSize: 11,
          }}
        />
        <Tooltip
          cursor={{ stroke: "var(--axis-line)", strokeWidth: 1 }}
          content={({ active, label, payload }) => {
            const point = payload?.[0]?.payload as
              | { avg: number; median: number; range: [number, number] }
              | undefined;
            return (
              <ChartTooltip
                active={active}
                label={label}
                rows={
                  point
                    ? [
                        { name: charts.avg, value: `${point.avg} min`, color: "var(--series-1)" },
                        {
                          name: charts.median,
                          value: `${point.median} min`,
                          color: "var(--series-2)",
                        },
                        {
                          name: charts.range,
                          value: `${point.range[0]}–${point.range[1]} min`,
                          color: "var(--text-muted)",
                        },
                      ]
                    : []
                }
              />
            );
          }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "var(--text-secondary)" }} />
        <Area
          dataKey="range"
          name={charts.range}
          fill="var(--series-1)"
          fillOpacity={0.08}
          stroke="none"
          isAnimationActive={false}
        />
        <Line
          type="monotone"
          dataKey="avg"
          name={charts.avg}
          stroke="var(--series-1)"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="median"
          name={charts.median}
          stroke="var(--series-2)"
          strokeWidth={2}
          dot={false}
          strokeDasharray="4 3"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
