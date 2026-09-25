"use client";

import type { FilterOptions, StatsFilters } from "../lib/types";
import { useLanguage } from "../../i18n/LanguageContext";

function toDateInputValue(date: Date): string {
  return date.toISOString().slice(0, 10);
}

type DateRange = Omit<StatsFilters, "includeSynthetic">;

const selectClass =
  "rounded-full border-2 border-[var(--border)] bg-[var(--surface-1)] px-3 py-1.5 text-xs font-bold text-[var(--text-secondary)] transition-colors hover:bg-[var(--page)] focus:outline-none";

export function Filters({
  filters,
  onChange,
  filterOptions,
}: {
  filters: DateRange;
  onChange: (filters: DateRange) => void;
  filterOptions?: FilterOptions;
}) {
  const { t } = useLanguage();
  const f = t.analytics.filters;

  const presets: { label: string; days: number | null }[] = [
    { label: f.last7, days: 7 },
    { label: f.last30, days: 30 },
    { label: f.last90, days: 90 },
    { label: f.allTime, days: null },
  ];

  const applyPreset = (days: number | null) => {
    if (days === null) {
      onChange({ ...filters, startDate: undefined, endDate: undefined });
      return;
    }
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);
    onChange({
      ...filters,
      startDate: toDateInputValue(start),
      endDate: toDateInputValue(end),
    });
  };

  const isActivePreset = (days: number | null) => {
    if (days === null) return !filters.startDate && !filters.endDate;
    if (!filters.startDate || !filters.endDate) return false;
    const expectedStart = new Date();
    expectedStart.setDate(expectedStart.getDate() - days);
    return filters.startDate === toDateInputValue(expectedStart);
  };

  const municipalityOptions = (filterOptions?.municipalities ?? []).filter(
    (m) => m.country_code === filters.countryCode
  );

  return (
    <div className="mb-6 flex flex-wrap items-center gap-2">
      <div className="flex flex-wrap gap-1 rounded-full border-2 border-[var(--border)] bg-[var(--surface-1)] p-1">
        {presets.map((preset) => (
          <button
            key={preset.label}
            onClick={() => applyPreset(preset.days)}
            className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
              isActivePreset(preset.days)
                ? "bg-[var(--accent)] text-white"
                : "text-[var(--text-secondary)] hover:bg-[var(--page)]"
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      {filterOptions && (
        <>
          <select
            className={selectClass}
            value={filters.vehicleType ?? ""}
            onChange={(e) => onChange({ ...filters, vehicleType: e.target.value || undefined })}
          >
            <option value="">{f.allVehicleTypes}</option>
            {filterOptions.vehicle_types.map((vt) => (
              <option key={vt} value={vt}>
                {vt}
              </option>
            ))}
          </select>

          <select
            className={selectClass}
            value={filters.countryCode ?? ""}
            onChange={(e) =>
              onChange({
                ...filters,
                countryCode: e.target.value || undefined,
                municipality: undefined,
              })
            }
          >
            <option value="">{f.allCountries}</option>
            {filterOptions.country_codes.map((cc) => (
              <option key={cc} value={cc}>
                {cc}
              </option>
            ))}
          </select>

          {filters.countryCode === "AT" && municipalityOptions.length > 0 && (
            <select
              className={selectClass}
              value={filters.municipality ?? ""}
              onChange={(e) =>
                onChange({ ...filters, municipality: e.target.value || undefined })
              }
            >
              <option value="">{f.allMunicipalities}</option>
              {municipalityOptions.map((m) => (
                <option key={m.municipality} value={m.municipality}>
                  {m.municipality}
                </option>
              ))}
            </select>
          )}
        </>
      )}
    </div>
  );
}
