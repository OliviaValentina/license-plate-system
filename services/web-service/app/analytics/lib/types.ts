export interface DurationOfStayPoint {
  visit_date: string;
  sample_size: number;
  avg_duration_minutes: number;
  median_duration_minutes: number;
  min_duration_minutes: number;
  max_duration_minutes: number;
}

export interface HourlyVisitPoint {
  hour_of_day: number;
  visit_count: number;
}

export interface MonthlyVisitPoint {
  year: number;
  month: number;
  season: string;
  visit_count: number;
}

export interface WeekdayVisitPoint {
  day_of_week: number;
  visit_count: number;
}

export interface VisitTrendPoint {
  visit_date: string;
  group_value: string | null;
  visit_count: number;
}

export interface MunicipalityOption {
  country_code: string;
  municipality: string;
}

export interface FilterOptions {
  vehicle_types: string[];
  country_codes: string[];
  municipalities: MunicipalityOption[];
}

export type TrendGroupBy = "vehicle_type" | "country_code" | "municipality";

export interface StatsFilters {
  includeSynthetic: boolean;
  startDate?: string;
  endDate?: string;
  vehicleType?: string;
  countryCode?: string;
  municipality?: string;
}

export interface VisitTrendsFilters extends StatsFilters {
  groupBy?: TrendGroupBy;
}
