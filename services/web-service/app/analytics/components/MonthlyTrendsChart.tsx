"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MonthlyVisitPoint } from "../lib/types";
import { colorForSeason } from "../lib/colors";
import { ChartTooltip } from "./ChartTooltip";
import { useLanguage } from "../../i18n/LanguageContext";
import type { Translations } from "../../i18n/translations";

function seasonLabel(season: string, seasons: Translations["analytics"]["seasons"]): string {
  return (seasons as Record<string, string>)[season] ?? season;
}

export function MonthlyTrendsChart({ data }: { data: MonthlyVisitPoint[] }) {
  const { t } = useLanguage();
  const months = t.analytics.months;
  const seasons = t.analytics.seasons;

  const sorted = [...data].sort((a, b) => a.year - b.year || a.month - b.month);
  const chartData = sorted.map((d) => ({
    label: `${months[d.month - 1]} '${String(d.year).slice(2)}`,
    visit_count: d.visit_count,
    season: d.season,
  }));

  const seasonKeys = Array.from(new Set(sorted.map((d) => d.season)));

  if (data.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">{t.analytics.charts.noData}</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--grid-line)" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={{ stroke: "var(--axis-line)" }}
          tick={false}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          width={36}
        />
        <Tooltip
          cursor={{ fill: "var(--grid-line)", opacity: 0.4 }}
          content={({ active, payload }) => {
            const point = payload?.[0]?.payload as
              | { visit_count: number; season: string }
              | undefined;
            return (
              <ChartTooltip
                active={active}
                label={point ? seasonLabel(point.season, seasons) : undefined}
                rows={
                  point
                    ? [
                        {
                          name: t.analytics.charts.visitsTooltip,
                          value: String(point.visit_count),
                          color: colorForSeason(point.season),
                        },
                      ]
                    : []
                }
              />
            );
          }}
        />
        <Legend
          payload={seasonKeys.map((season) => ({
            value: seasonLabel(season, seasons),
            type: "square",
            color: colorForSeason(season),
          }))}
          wrapperStyle={{ fontSize: 11, color: "var(--text-secondary)" }}
        />
        <Bar dataKey="visit_count" radius={[3, 3, 0, 0]} maxBarSize={22}>
          {chartData.map((entry) => (
            <Cell key={entry.label} fill={colorForSeason(entry.season)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
