export interface Dictionary {
  nav: {
    home: string;
    analytics: string;
    internal: string;
  };
  home: {
    eyebrow: string;
    title: string;
    subtitle: string;
    cta: string;
    features: {
      recognitionTitle: string;
      recognitionBody: string;
      analyticsTitle: string;
      analyticsBody: string;
      alertsTitle: string;
      alertsBody: string;
    };
  };
  analytics: {
    title: string;
    subtitle: string;
    refreshIdle: string;
    refreshLoading: string;
    error: string;
    filters: {
      last7: string;
      last30: string;
      last90: string;
      lastYear: string;
      allTime: string;
      includeSynthetic: string;
      allVehicleTypes: string;
      allCountries: string;
      allMunicipalities: string;
    };
    stats: {
      totalVisits: string;
      busiestHour: string;
      avgDuration: string;
      busiestDay: string;
      visitsSuffix: string;
      minutesSuffix: string;
    };
    charts: {
      rushHourTitle: string;
      rushHourSubtitle: string;
      weekdayTitle: string;
      weekdaySubtitle: string;
      durationTitle: string;
      durationSubtitle: string;
      monthlyTitle: string;
      monthlySubtitle: string;
      visitTrendsVehicleTypeTitle: string;
      visitTrendsVehicleTypeSubtitle: string;
      visitTrendsCountryTitle: string;
      visitTrendsCountrySubtitle: string;
      noData: string;
      avg: string;
      median: string;
      range: string;
      minutesAxis: string;
      visitsTooltip: string;
    };
    weekdays: string[];
    months: string[];
    seasons: {
      winter: string;
      spring: string;
      summer: string;
      autumn: string;
    };
  };
  auth: {
    menuLogin: string;
    menuLogout: string;
    signedInAs: string;
    title: string;
    subtitle: string;
    username: string;
    usernameHint: string;
    password: string;
    submit: string;
    submitting: string;
    invalidCredentials: string;
    unavailable: string;
    alreadyLoggedIn: string;
  };
  internal: {
    eyebrow: string;
    title: string;
    subtitle: string;
    welcome: string;
    cards: { title: string; body: string }[];
  };
}

export const translations: Record<"en" | "de", Dictionary> = {
  en: {
    nav: {
      home: "Home",
      analytics: "Analytics",
      internal: "Internal",
    },
    home: {
      eyebrow: "Parking Lot Intelligence",
      title: "License Plate System",
      subtitle:
        "Automatic plate recognition, live occupancy, and rich visit analytics for your lot — all in one place.",
      cta: "View analytics",
      features: {
        recognitionTitle: "Automatic recognition",
        recognitionBody:
          "Plates are captured and matched the moment a vehicle enters or leaves.",
        analyticsTitle: "Rich analytics",
        analyticsBody:
          "Rush hours, weekday patterns, and duration of stay, visualized at a glance.",
        alertsTitle: "Real-time alerts",
        alertsBody:
          "Get notified the moment something needs your attention.",
      },
    },
    analytics: {
      title: "License Plate Analytics",
      subtitle: "Parking lot visit trends and traffic patterns",
      refreshIdle: "Refresh stats",
      refreshLoading: "Refreshing…",
      error: "Couldn't load analytics data. Is the analytics-service running?",
      filters: {
        last7: "Last 7 days",
        last30: "Last 30 days",
        last90: "Last 90 days",
        lastYear: "Last year",
        allTime: "All time",
        includeSynthetic: "Include synthetic demo data",
        allVehicleTypes: "All vehicle types",
        allCountries: "All countries",
        allMunicipalities: "All municipalities",
      },
      stats: {
        totalVisits: "Total visits",
        busiestHour: "Busiest hour",
        avgDuration: "Avg. duration of stay",
        busiestDay: "Busiest day",
        visitsSuffix: "visits",
        minutesSuffix: "min",
      },
      charts: {
        rushHourTitle: "Rush hour",
        rushHourSubtitle: "Visit volume by hour of day",
        weekdayTitle: "Day of week",
        weekdaySubtitle: "Visit volume by weekday",
        durationTitle: "Duration of stay",
        durationSubtitle: "Average, median, and range in minutes, per day",
        monthlyTitle: "Monthly trends",
        monthlySubtitle: "Visit volume by month, colored by season",
        visitTrendsVehicleTypeTitle: "Visit trends – vehicle types",
        visitTrendsVehicleTypeSubtitle: "Daily visits by vehicle type",
        visitTrendsCountryTitle: "Visit trends – country of origin",
        visitTrendsCountrySubtitle: "Daily visits by plate country",
        noData: "No data for this range.",
        avg: "Average",
        median: "Median",
        range: "Min–max range",
        minutesAxis: "minutes",
        visitsTooltip: "Visits",
      },
      weekdays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      months: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
      seasons: {
        winter: "Winter",
        spring: "Spring",
        summer: "Summer",
        autumn: "Autumn",
      },
    },
    auth: {
      menuLogin: "Log in",
      menuLogout: "Log out",
      signedInAs: "Signed in as",
      title: "Log in",
      subtitle: "Sign in with your Zotter account.",
      username: "Username",
      usernameHint: "Your Windows username, without the domain.",
      password: "Password",
      submit: "Log in",
      submitting: "Logging in…",
      invalidCredentials: "Wrong username or password.",
      unavailable: "Login is currently unavailable. Please try again later.",
      alreadyLoggedIn: "You are already logged in.",
    },
    internal: {
      eyebrow: "Staff only",
      title: "Internal area",
      subtitle: "This page is only visible to logged-in Zotter staff.",
      welcome: "Welcome",
      cards: [
        { title: "Notifications", body: "Placeholder for managing alert rules and recipients." },
        { title: "Data management", body: "Placeholder for exports, backups and synthetic data tools." },
        { title: "System status", body: "Placeholder for camera and service health." },
      ],
    },
  },
  de: {
    nav: {
      home: "Startseite",
      analytics: "Statistiken",
      internal: "Intern",
    },
    home: {
      eyebrow: "Parkplatz-Intelligenz",
      title: "Kennzeichen-System",
      subtitle:
        "Automatische Kennzeichenerkennung, Live-Belegung und aussagekräftige Besuchsstatistiken für Ihren Parkplatz — alles an einem Ort.",
      cta: "Statistiken ansehen",
      features: {
        recognitionTitle: "Automatische Erkennung",
        recognitionBody:
          "Kennzeichen werden erfasst und abgeglichen, sobald ein Fahrzeug ein- oder ausfährt.",
        analyticsTitle: "Umfassende Statistiken",
        analyticsBody:
          "Stoßzeiten, Wochentagsmuster und Aufenthaltsdauer auf einen Blick visualisiert.",
        alertsTitle: "Echtzeit-Benachrichtigungen",
        alertsBody:
          "Werden Sie sofort informiert, wenn Ihre Aufmerksamkeit gefragt ist.",
      },
    },
    analytics: {
      title: "Kennzeichen-Statistiken",
      subtitle: "Besuchstrends und Verkehrsmuster auf dem Parkplatz",
      refreshIdle: "Statistiken aktualisieren",
      refreshLoading: "Wird aktualisiert…",
      error:
        "Analysedaten konnten nicht geladen werden. Läuft der analytics-service?",
      filters: {
        last7: "Letzte 7 Tage",
        last30: "Letzte 30 Tage",
        last90: "Letzte 90 Tage",
        lastYear: "Letztes Jahr",
        allTime: "Gesamter Zeitraum",
        includeSynthetic: "Synthetische Demodaten einbeziehen",
        allVehicleTypes: "Alle Fahrzeugtypen",
        allCountries: "Alle Länder",
        allMunicipalities: "Alle Gemeinden",
      },
      stats: {
        totalVisits: "Besuche gesamt",
        busiestHour: "Stoßzeit",
        avgDuration: "Ø Aufenthaltsdauer",
        busiestDay: "Stärkster Tag",
        visitsSuffix: "Besuche",
        minutesSuffix: "Min",
      },
      charts: {
        rushHourTitle: "Stoßzeiten",
        rushHourSubtitle: "Besuchsaufkommen nach Tagesstunde",
        weekdayTitle: "Wochentag",
        weekdaySubtitle: "Besuchsaufkommen nach Wochentag",
        durationTitle: "Aufenthaltsdauer",
        durationSubtitle: "Durchschnitt, Median und Spanne in Minuten, pro Tag",
        monthlyTitle: "Monatstrends",
        monthlySubtitle: "Besuchsaufkommen nach Monat, eingefärbt nach Jahreszeit",
        visitTrendsVehicleTypeTitle: "Besuchstrends – Fahrzeugtypen",
        visitTrendsVehicleTypeSubtitle:
          "Tägliche Besuche nach Fahrzeugtyp (ignoriert die Fahrzeugtyp-/Länderfilter)",
        visitTrendsCountryTitle: "Besuchstrends – Herkunftsland",
        visitTrendsCountrySubtitle:
          "Tägliche Besuche nach Kennzeichenland (ignoriert die Fahrzeugtyp-/Länderfilter)",
        noData: "Keine Daten für diesen Zeitraum.",
        avg: "Durchschnitt",
        median: "Median",
        range: "Min–Max-Spanne",
        minutesAxis: "Minuten",
        visitsTooltip: "Besuche",
      },
      weekdays: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
      months: [
        "Jan",
        "Feb",
        "Mär",
        "Apr",
        "Mai",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Okt",
        "Nov",
        "Dez",
      ],
      seasons: {
        winter: "Winter",
        spring: "Frühling",
        summer: "Sommer",
        autumn: "Herbst",
      },
    },
    auth: {
      menuLogin: "Anmelden",
      menuLogout: "Abmelden",
      signedInAs: "Angemeldet als",
      title: "Anmelden",
      subtitle: "Melde dich mit deinem Zotter-Konto an.",
      username: "Benutzername",
      usernameHint: "Dein Windows-Benutzername, ohne Domäne.",
      password: "Passwort",
      submit: "Anmelden",
      submitting: "Anmeldung läuft…",
      invalidCredentials: "Benutzername oder Passwort ist falsch.",
      unavailable: "Die Anmeldung ist derzeit nicht verfügbar. Bitte versuche es später erneut.",
      alreadyLoggedIn: "Du bist bereits angemeldet.",
    },
    internal: {
      eyebrow: "Nur für Mitarbeiter",
      title: "Interner Bereich",
      subtitle: "Diese Seite ist nur für angemeldete Zotter-Mitarbeiter sichtbar.",
      welcome: "Willkommen",
      cards: [
        { title: "Benachrichtigungen", body: "Platzhalter für Alarmregeln und Empfänger." },
        { title: "Datenverwaltung", body: "Platzhalter für Exporte, Backups und synthetische Daten." },
        { title: "Systemstatus", body: "Platzhalter für den Zustand von Kameras und Diensten." },
      ],
    },
  },
};

export type Locale = "en" | "de";
export type Translations = Dictionary;
