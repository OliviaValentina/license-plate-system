export const SERIES_COLORS = [
  "var(--series-1)",
  "var(--series-2)",
  "var(--series-3)",
  "var(--series-4)",
  "var(--series-5)",
  "var(--series-6)",
  "var(--series-7)",
  "var(--series-8)",
];

// Fixed, colorblind-validated colors per season (see --season-* in
// globals.css) so a given season always looks the same regardless of which
// seasons are present in the current data. Keys match the lowercase season
// strings the analytics-service returns (see ingestion_handler.py).
const SEASON_COLORS: Record<string, string> = {
  winter: "var(--season-winter)",
  spring: "var(--season-spring)",
  summer: "var(--season-summer)",
  autumn: "var(--season-fall)",
};

const FALLBACK_SEASON_COLOR = "var(--series-8)";

export function colorForSeason(season: string): string {
  return SEASON_COLORS[season] ?? FALLBACK_SEASON_COLOR;
}

// Canonical season keys as returned by the API, in fixed order — used to
// translate a season into the active locale's display label.
export const SEASON_KEYS = ["winter", "spring", "summer", "autumn"];
