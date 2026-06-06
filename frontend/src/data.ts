import type { CurrentData } from "./types";

// Relativer Pfad (kein führender "/"), damit es auch unter dem
// GitHub-Pages-Unterpfad /<repo>/ korrekt auflöst. import.meta.env.BASE_URL
// liefert den konfigurierten Vite-base.
export async function loadCurrentData(): Promise<CurrentData> {
  const url = `${import.meta.env.BASE_URL}data/current.json`;
  const res = await fetch(url, { cache: "no-cache" });
  if (!res.ok) {
    throw new Error(`Daten konnten nicht geladen werden (HTTP ${res.status})`);
  }
  return (await res.json()) as CurrentData;
}
