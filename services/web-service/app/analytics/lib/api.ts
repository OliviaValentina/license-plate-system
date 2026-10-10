import type {
  DurationOfStayPoint,
  FilterOptions,
  HourlyVisitPoint,
  MonthlyVisitPoint,
  StatsFilters,
  VisitTrendPoint,
  VisitTrendsFilters,
  WeekdayVisitPoint,
} from "./types";

function buildQuery(filters: StatsFilters): string {
  const params = new URLSearchParams();
  params.set("include_synthetic", String(filters.includeSynthetic));
  if (filters.startDate) params.set("start_date", filters.startDate);
  if (filters.endDate) params.set("end_date", filters.endDate);
  if (filters.vehicleType) params.set("vehicle_type", filters.vehicleType);
  if (filters.countryCode) params.set("country_code", filters.countryCode);
  if (filters.municipality) params.set("municipality", filters.municipality);
  return params.toString();
}

async function fetchSeries<T>(endpoint: string, filters: StatsFilters): Promise<T[]> {
  const res = await fetch(`/api/stats/${endpoint}?${buildQuery(filters)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load ${endpoint} (${res.status})`);
  }
  const data = await res.json();
  return data.series as T[];
}

export function getDurationOfStay(filters: StatsFilters) {
  return fetchSeries<DurationOfStayPoint>("duration-of-stay", filters);
}

export function getRushHour(filters: StatsFilters) {
  return fetchSeries<HourlyVisitPoint>("rush-hour", filters);
}

export function getMonthlyTrends(filters: StatsFilters) {
  return fetchSeries<MonthlyVisitPoint>("monthly-trends", filters);
}

export function getWeekdayTrends(filters: StatsFilters) {
  return fetchSeries<WeekdayVisitPoint>("weekday-trends", filters);
}

export function getVisitTrends(filters: VisitTrendsFilters) {
  const params = new URLSearchParams(buildQuery(filters));
  if (filters.groupBy) params.set("group_by", filters.groupBy);
  return fetch(`/api/stats/visit-trends?${params.toString()}`, { cache: "no-store" }).then(
    async (res) => {
      if (!res.ok) throw new Error(`Failed to load visit-trends (${res.status})`);
      const data = await res.json();
      return data.series as VisitTrendPoint[];
    }
  );
}

export async function getFilterOptions(includeSynthetic: boolean): Promise<FilterOptions> {
  const params = new URLSearchParams();
  params.set("include_synthetic", String(includeSynthetic));
  const res = await fetch(`/api/stats/filter-options?${params.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load filter-options (${res.status})`);
  }
  return res.json();
}
