"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "lps-include-synthetic";

interface PreferencesContextValue {
  includeSynthetic: boolean;
  setIncludeSynthetic: (value: boolean) => void;
}

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const [includeSynthetic, setIncludeSyntheticState] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === "true" || stored === "false") {
        setIncludeSyntheticState(stored === "true");
      }
    } catch {
      // localStorage unavailable — fall back to default
    }
  }, []);

  const setIncludeSynthetic = (value: boolean) => {
    setIncludeSyntheticState(value);
    try {
      localStorage.setItem(STORAGE_KEY, String(value));
    } catch {
      // ignore
    }
  };

  const value = useMemo(
    () => ({ includeSynthetic, setIncludeSynthetic }),
    [includeSynthetic]
  );

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences(): PreferencesContextValue {
  const ctx = useContext(PreferencesContext);
  if (!ctx) {
    throw new Error("usePreferences must be used within a PreferencesProvider");
  }
  return ctx;
}
