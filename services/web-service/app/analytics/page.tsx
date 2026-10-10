"use client";

import { useCallback, useEffect, useState } from "react";
import { Card } from "./components/Card";
import { Filters } from "./components/Filters";
import { StatTile } from "./components/StatTile";
import { RushHourChart } from "./components/RushHourChart";
import { WeekdayTrendsChart } from "./components/WeekdayTrendsChart";
import { MonthlyTrendsChart } from "./components/MonthlyTrendsChart";
import { DurationOfStayChart } from "./components/DurationOfStayChart";
import { VisitTrendsChart } from "./components/VisitTrendsChart";
import {
  getDurationOfStay,
  getFilterOptions,
  getMonthlyTrends,
  getRushHour,
  getVisitTrends,
  getWeekdayTrends,
} from "./lib/api";
import type {
  DurationOfStayPoint,
  FilterOptions,
  HourlyVisitPoint,
  MonthlyVisitPoint,
  StatsFilters,
  VisitTrendPoint,
  WeekdayVisitPoint,
} from "./lib/types";
import { useLanguage } from "../i18n/LanguageContext";
import { usePreferences } from "../preferences/PreferencesContext";

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const { includeSynthetic } = usePreferences();
  const a = t.analytics;

  const [dateRange, setDateRange] = useState<Omit<StatsFilters, "includeSynthetic">>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const filters: StatsFilters = { ...dateRange, includeSynthetic };
  // Visit-trends-by-dimension charts always show the full breakdown, so they
  // deliberately ignore the vehicle type / country / municipality filters -
  // only the date range and synthetic-data toggle apply to them.
  const trendFilters: StatsFilters = {
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
    includeSynthetic,
  };

  const [durationOfStay, setDurationOfStay] = useState<DurationOfStayPoint[]>([]);
  const [rushHour, setRushHour] = useState<HourlyVisitPoint[]>([]);
  const [monthlyTrends, setMonthlyTrends] = useState<MonthlyVisitPoint[]>([]);
  const [weekdayTrends, setWeekdayTrends] = useState<WeekdayVisitPoint[]>([]);
  const [visitTrendsByVehicleType, setVisitTrendsByVehicleType] = useState<VisitTrendPoint[]>([]);
  const [visitTrendsByCountry, setVisitTrendsByCountry] = useState<VisitTrendPoint[]>([]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [duration, rush, monthly, weekday, byVehicleType, byCountry] = await Promise.all([
        getDurationOfStay(filters),
        getRushHour(filters),
        getMonthlyTrends(filters),
        getWeekdayTrends(filters),
        getVisitTrends({ ...trendFilters, groupBy: "vehicle_type" }),
        getVisitTrends({ ...trendFilters, groupBy: "country_code" }),
      ]);
      setDurationOfStay(duration);
      setRushHour(rush);
      setMonthlyTrends(monthly);
      setWeekdayTrends(weekday);
      setVisitTrendsByVehicleType(byVehicleType);
      setVisitTrendsByCountry(byCountry);
    } catch {
      setError(a.error);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateRange, includeSynthetic, a.error]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    getFilterOptions(includeSynthetic)
      .then(setFilterOptions)
      .catch(() => setFilterOptions(undefined));
  }, [includeSynthetic]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch("/api/stats/refresh", { method: "POST" });
      await loadData();
    } finally {
      setRefreshing(false);
    }
  };

  const totalVisits = rushHour.reduce((sum, d) => sum + d.visit_count, 0);
  const busiestHour = rushHour.reduce(
    (best, d) => (d.visit_count > (best?.visit_count ?? -1) ? d : best),
    undefined as HourlyVisitPoint | undefined
  );
  const avgDuration =
    durationOfStay.length > 0
      ? durationOfStay.reduce((sum, d) => sum + d.avg_duration_minutes, 0) /
        durationOfStay.length
      : null;
  const busiestWeekday = weekdayTrends.reduce(
    (best, d) => (d.visit_count > (best?.visit_count ?? -1) ? d : best),
    undefined as WeekdayVisitPoint | undefined
  );

  return (
    <div className="min-h-screen bg-[var(--page)]">
      <div className="border-b-4 border-[var(--accent)]/30 bg-[var(--chocolate)]">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-8">
          <h1 className="font-display text-lg font-bold tracking-tight text-[var(--chocolate-ink)]">
            {a.title}
          </h1>
          <p className="text-sm text-[var(--chocolate-ink)] opacity-80">{a.subtitle}</p>
        </div>
      </div>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-8">
        <div className="mb-6 sm:mb-4 flex items-center justify-between gap-4">
          <Filters
            filters={dateRange}
            onChange={setDateRange}
            filterOptions={filterOptions}
          />
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="mb-6 shrink-0 rounded-full border-2 border-[var(--border)] bg-[var(--surface-1)] px-4 py-1.5 text-xs font-bold text-[var(--text-secondary)] transition-colors hover:bg-[var(--page)] disabled:opacity-50"
          >
            {refreshing ? a.refreshLoading : a.refreshIdle}
          </button>
        </div>

        {error && (
          <div className="mb-6 rounded-2xl border-2 border-[var(--status-critical)] bg-[var(--surface-1)] px-4 py-3 text-sm text-[var(--status-critical)]">
            {error}
          </div>
        )}

        <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatTile
            label={a.stats.totalVisits}
            value={loading ? "—" : totalVisits.toLocaleString()}
          />
          <StatTile
            label={a.stats.busiestHour}
            value={
              loading || !busiestHour
                ? "—"
                : `${String(busiestHour.hour_of_day).padStart(2, "0")}:00`
            }
            detail={
              busiestHour
                ? `${busiestHour.visit_count.toLocaleString()} ${a.stats.visitsSuffix}`
                : undefined
            }
          />
          <StatTile
            label={a.stats.avgDuration}
            value={
              loading || avgDuration === null
                ? "—"
                : `${Math.round(avgDuration)} ${a.stats.minutesSuffix}`
            }
          />
          <StatTile
            label={a.stats.busiestDay}
            value={
              loading || !busiestWeekday
                ? "—"
                : a.weekdays[busiestWeekday.day_of_week - 1]
            }
            detail={
              busiestWeekday
                ? `${busiestWeekday.visit_count.toLocaleString()} ${a.stats.visitsSuffix}`
                : undefined
            }
          />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card title={a.charts.rushHourTitle} subtitle={a.charts.rushHourSubtitle}>
            <RushHourChart data={rushHour} />
          </Card>
          <Card title={a.charts.weekdayTitle} subtitle={a.charts.weekdaySubtitle}>
            <WeekdayTrendsChart data={weekdayTrends} />
          </Card>
          <Card title={a.charts.durationTitle} subtitle={a.charts.durationSubtitle}>
            <DurationOfStayChart data={durationOfStay} />
          </Card>
          <Card title={a.charts.monthlyTitle} subtitle={a.charts.monthlySubtitle}>
            <MonthlyTrendsChart data={monthlyTrends} />
          </Card>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card
            title={a.charts.visitTrendsVehicleTypeTitle}
            subtitle={a.charts.visitTrendsVehicleTypeSubtitle}
          >
            <VisitTrendsChart data={visitTrendsByVehicleType} />
          </Card>
          <Card
            title={a.charts.visitTrendsCountryTitle}
            subtitle={a.charts.visitTrendsCountrySubtitle}
          >
            <VisitTrendsChart data={visitTrendsByCountry} />
          </Card>
        </div>
      </main>
    </div>
  );
}
